"""Read-only preflight network checks for DCA1000.

This module never modifies hardware state. It only inspects the local PC's
network configuration and attempts to ping the DCA1000.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class PreflightCheck:
    name: str
    status: str  # "PASS", "WARN", "FAIL", "UNKNOWN"
    detail: str


@dataclass
class PreflightReport:
    checks: list[PreflightCheck]
    overall: str  # "READY", "NOT_READY", "READY_WITH_WARNINGS"


def _run_ps_json(script: str) -> Optional[dict]:
    """Run a PowerShell script that returns JSON and parse it."""
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        f"{script} | ConvertTo-Json -Depth 3 -Compress"
    ]
    try:
        res = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True).strip()
        if not res:
            return None
        return json.loads(res)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def _as_list(value) -> list:
    """Normalize a value to a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _as_dicts(value) -> list[dict]:
    """Normalize a value to a list of dicts."""
    return [x for x in _as_list(value) if isinstance(x, dict)]


def run_dca_preflight(
    host_ip: str = "192.168.33.30",
    dca_ip: str = "192.168.33.180",
    ping_only: bool = False,
) -> PreflightReport:
    """Run DCA1000 preflight network checks."""
    checks = []
    ready = True
    warnings = False

    # 1. Local Adapter IP Check
    if not ping_only:
        script_ip = f"Get-NetIPAddress -IPAddress {host_ip} -ErrorAction SilentlyContinue | Select-Object InterfaceAlias, InterfaceIndex, PrefixLength, AddressFamily"
        ip_data_raw = _run_ps_json(script_ip)
        ip_list = _as_dicts(ip_data_raw)
        
        if ip_list:
            # prefer AddressFamily IPv4 (2), then prefix 24
            best_ip = None
            for ip in ip_list:
                family = ip.get("AddressFamily")
                if family == 2:  # IPv4
                    if ip.get("PrefixLength") == 24:
                        best_ip = ip
                        break
                    if not best_ip:
                        best_ip = ip
            if not best_ip:
                best_ip = ip_list[0]

            prefix = best_ip.get("PrefixLength", 24)
            alias = best_ip.get("InterfaceAlias", "Unknown")
            idx = best_ip.get("InterfaceIndex", "?")
            checks.append(PreflightCheck(
                name=f"Adapter IP {host_ip}/{prefix}",
                status="PASS",
                detail=f"{alias}, idx={idx}"
            ))
            adapter_alias = alias
        else:
            checks.append(PreflightCheck(
                name=f"Adapter IP {host_ip}",
                status="FAIL",
                detail="Not found on any local adapter"
            ))
            ready = False
            adapter_alias = None

        # 2. Adapter Type Check (Physical Ethernet)
        if adapter_alias:
            script_adapter = f"Get-NetAdapter -Name '{adapter_alias}' -ErrorAction SilentlyContinue | Select-Object PhysicalMediaType"
            adapter_data_raw = _run_ps_json(script_adapter)
            adapter_list = _as_dicts(adapter_data_raw)
            if adapter_list:
                media_type = adapter_list[0].get("PhysicalMediaType", "")
                if media_type == "802.3":
                    checks.append(PreflightCheck(
                        name="Adapter type",
                        status="PASS",
                        detail="Physical Ethernet"
                    ))
                else:
                    # Could be WiFi or virtual
                    checks.append(PreflightCheck(
                        name="Adapter type",
                        status="WARN",
                        detail=f"Not guaranteed physical Ethernet ({media_type or 'Unknown'})"
                    ))
                    warnings = True
            else:
                checks.append(PreflightCheck(
                    name="Adapter type",
                    status="WARN",
                    detail="Could not determine media type"
                ))
                warnings = True

        # 3. Route Check
        script_route = f"Find-NetRoute -RemoteIPAddress {dca_ip} -ErrorAction SilentlyContinue | Select-Object InterfaceAlias"
        route_data_raw = _run_ps_json(script_route)
        route_list = _as_dicts(route_data_raw)
        
        if route_list:
            # find best route
            best_route_alias = None
            for route in route_list:
                a = route.get("InterfaceAlias", "")
                if a == adapter_alias:
                    best_route_alias = a
                    break
            
            if not best_route_alias:
                for route in route_list:
                    a = route.get("InterfaceAlias", "")
                    if a:
                        best_route_alias = a
                        break

            if not best_route_alias:
                best_route_alias = "Unknown"

            if best_route_alias == adapter_alias:
                checks.append(PreflightCheck(
                    name=f"Route to {dca_ip}",
                    status="PASS",
                    detail=f"via {best_route_alias}"
                ))
            else:
                checks.append(PreflightCheck(
                    name=f"Route to {dca_ip}",
                    status="WARN",
                    detail=f"via {best_route_alias} (expected {adapter_alias})"
                ))
                warnings = True
        else:
            checks.append(PreflightCheck(
                name=f"Route to {dca_ip}",
                status="WARN",
                detail="No explicit route found"
            ))
            warnings = True

    # 4. Ping Check
    cmd_ping = ["powershell", "-NoProfile", "-Command", f"Test-Connection -ComputerName {dca_ip} -Count 2 -Quiet"]
    try:
        res = subprocess.check_output(cmd_ping, text=True).strip()
        ping_ok = res.lower() == "true"
    except subprocess.CalledProcessError:
        ping_ok = False

    # 5. ARP Check (if not ping_only)
    valid_arp = None
    if not ping_only:
        script_arp = f"Get-NetNeighbor -IPAddress {dca_ip} -ErrorAction SilentlyContinue | Select-Object LinkLayerAddress"
        arp_data_raw = _run_ps_json(script_arp)
        arp_list = _as_dicts(arp_data_raw)
        
        for a in arp_list:
            mac = a.get("LinkLayerAddress")
            if mac:
                valid_arp = mac
                break

    # Now evaluate Ping and ARP semantics together
    if ping_ok:
        checks.append(PreflightCheck(
            name=f"Ping {dca_ip}",
            status="PASS",
            detail="Replies received"
        ))
    else:
        if not ping_only and valid_arp:
            checks.append(PreflightCheck(
                name=f"Ping {dca_ip}",
                status="WARN",
                detail="No ICMP replies, but ARP resolved; DCA may still be usable over UDP"
            ))
            warnings = True
        else:
            checks.append(PreflightCheck(
                name=f"Ping {dca_ip}",
                status="FAIL",
                detail="No replies"
            ))
            ready = False

    if not ping_only:
        if valid_arp:
            checks.append(PreflightCheck(
                name=f"ARP {dca_ip}",
                status="PASS",
                detail=valid_arp.replace("-", ":")
            ))
        else:
            checks.append(PreflightCheck(
                name=f"ARP {dca_ip}",
                status="FAIL" if not ping_ok else "WARN",
                detail="No ARP entry found"
            ))
            warnings = True
            if not ping_ok:
                ready = False
            
        # 6. COM Port Conflict Check (only if ports.py available)
        try:
            from awr2944_dca.hardware.ports import scan_ports
            ports = scan_ports()
            dca_ports = [p for p in ports if p.likely_role == "dca_ftdi_candidate"]
            awr_ports = [p for p in ports if p.likely_role == "awr_rs232_candidate"]
            if dca_ports and awr_ports:
                overlap = set(p.com for p in dca_ports) & set(p.com for p in awr_ports)
                if overlap:
                    checks.append(PreflightCheck(
                        name="COM port conflict",
                        status="WARN",
                        detail=f"Overlap detected: {', '.join(overlap)}"
                    ))
                    warnings = True
                else:
                    dca_str = dca_ports[0].com if len(dca_ports) == 1 else f"{len(dca_ports)} ports"
                    awr_str = awr_ports[0].com if len(awr_ports) == 1 else f"{len(awr_ports)} ports"
                    checks.append(PreflightCheck(
                        name="COM port conflict",
                        status="PASS",
                        detail=f"DCA FTDI={dca_str}, AWR RS232={awr_str}"
                    ))
        except ImportError:
            pass

        # 7. UDP/firewall readiness (HONEST STATUS)
        checks.append(PreflightCheck(
            name="UDP/firewall readiness",
            status="UNKNOWN",
            detail="only provable after successful capture"
        ))

    overall = "READY"
    if not ready:
        overall = "NOT_READY"
    elif warnings:
        overall = "READY_WITH_WARNINGS"

    return PreflightReport(checks=checks, overall=overall)
