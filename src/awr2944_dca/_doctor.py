"""Hardware Doctor for AWR2944 + DCA1000 project health and diagnostics.

Never modifies hardware state.
"""

from __future__ import annotations

import json
import logging
import socket
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Dict, Any

from rich.console import Console

if TYPE_CHECKING:
    from awr2944_dca.lab import RadarProject


logger = logging.getLogger(__name__)


@dataclass
class CheckResult:
    name: str
    status: str          # "PASS", "WARN", "FAIL", "SKIP"
    category: str        # "OFFLINE", "DIAGNOSTIC_HARDWARE_ACCESS", "MUTATING_HARDWARE_ACCESS"
    detail: str
    required_for_capture: bool = True
    suggestion: str = ""


@dataclass
class DiscoveryReport:
    serial_ports: list[Any]
    com_ports: list[Any]
    network_adapters: list[dict]
    timestamp: str


@dataclass
class HardwareReport:
    checks: list[CheckResult]
    timestamp: str
    mode: str

    @property
    def success(self) -> bool:
        return not any(c.status == "FAIL" for c in self.checks)

    @property
    def ready_for_capture(self) -> bool:
        if self.mode == "OFFLINE_ONLY":
            return False
        for c in self.checks:
            if c.required_for_capture and c.status != "PASS":
                return False
        return True

    @property
    def warnings(self) -> list[CheckResult]:
        return [c for c in self.checks if c.status == "WARN"]

    @property
    def errors(self) -> list[CheckResult]:
        return [c for c in self.checks if c.status == "FAIL"]

    def summary(self) -> str:
        s = f"HardwareReport (Mode: {self.mode}) - Success: {self.success}, Ready for capture: {self.ready_for_capture}\n"
        for c in self.checks:
            req = "*" if c.required_for_capture else " "
            s += f"[{c.status:^4}] {req} {c.name:<30} {c.detail}\n"
        return s

    def print(self) -> None:
        console = Console()
        console.print(f"\n[bold cyan]Hardware Doctor Report[/bold cyan] (Mode: {self.mode})")
        console.print(f"Timestamp: {self.timestamp}\n")
        
        for c in self.checks:
            if c.status == "PASS":
                color = "green"
            elif c.status == "WARN":
                color = "yellow"
            elif c.status == "FAIL":
                color = "red"
            else:
                color = "bright_black"
                
            req = "*" if c.required_for_capture else " "
            console.print(f"[[{color}]{c.status:^4}[/{color}]] {req} {c.name:<30} {c.detail}")
            if c.suggestion and c.status in ("FAIL", "WARN", "SKIP"):
                console.print(f"         [italic]{c.suggestion}[/italic]")
                
        console.print("\n[bold]Summary:[/bold]")
        if self.success:
            console.print("[green]✔ No errors found.[/green]")
        else:
            console.print(f"[red]✘ Found {len(self.errors)} errors.[/red]")
            
        if self.mode != "OFFLINE_ONLY":
            if self.ready_for_capture:
                console.print("[green]✔ System is READY for capture.[/green]")
            else:
                console.print("[yellow]⚠ System is NOT fully ready for capture.[/yellow]")

    def raise_for_errors(self, strict: bool = False) -> None:
        if not self.success:
            raise RuntimeError(f"Hardware Doctor failed with {len(self.errors)} errors.\n\n{self.summary()}")
        if strict and not self.ready_for_capture:
            raise RuntimeError(f"Hardware Doctor strict mode failed: Not ready for capture.\n\n{self.summary()}")


class HardwareManager:
    """Lazy accessor for hardware inspection. No mutations."""

    def __init__(self, project: RadarProject):
        self._project = project
        self._checks: Dict[str, CheckResult] = {}
        
    def _add(self, name: str, status: str, cat: str, detail: str, req: bool = True, sugg: str = "") -> CheckResult:
        res = CheckResult(name, status, cat, detail, req, sugg)
        self._checks[name] = res
        return res

    def discover(self) -> DiscoveryReport:
        from awr2944_dca.headless_serial import discover_serial_ports
        from awr2944_dca.hardware.ports import scan_ports
        from awr2944_dca.dca.preflight import _run_ps_json, _as_dicts
        
        sp = discover_serial_ports()
        cp = scan_ports()
        
        script = "Get-NetIPAddress -ErrorAction SilentlyContinue | Select-Object InterfaceAlias, IPAddress, PrefixLength, AddressFamily"
        net_adapters = _as_dicts(_run_ps_json(script))
        
        return DiscoveryReport(
            serial_ports=sp,
            com_ports=cp,
            network_adapters=net_adapters,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    def verify(self, include_hardware: bool = True) -> HardwareReport:
        self._checks.clear()
        
        # 0. Legacy layout check
        has_project_json = (self._project.root / "project.json").exists()
        has_toml = (self._project.root / "awr2944.toml").exists()
        
        if has_project_json and not has_toml:
            self._add("legacy_project_layout", "FAIL", "OFFLINE", "Workspace uses legacy project.json format", sugg="Use 'awr init' to create a new project scaffolding instead of the SDK repository.")
            
            # Since it's legacy, just return here and SKIP the rest.
            # But the user said: "Dependent configuration/hardware checks may then SKIP."
            # So let's mark them as SKIP.
            self._add("project_structure", "SKIP", "OFFLINE", "Skipped due to legacy layout")
            self._add("portable_config_valid", "SKIP", "OFFLINE", "Skipped due to legacy layout")
            self._add("local_config_valid", "SKIP", "OFFLINE", "Skipped due to legacy layout")
            self._add("dca_control_exe_exists", "SKIP", "OFFLINE", "Skipped due to legacy layout")
            self._add("dca_record_exe_exists", "SKIP", "OFFLINE", "Skipped due to legacy layout")
            self._add("cf_json_exists", "SKIP", "OFFLINE", "Skipped due to legacy layout")
            self._add("cf_json_consistency", "SKIP", "OFFLINE", "Skipped due to legacy layout")
            self._add("no_active_session_lock", "SKIP", "OFFLINE", "Skipped due to legacy layout", req=False)
            
            if include_hardware:
                self._add("cli_com_port_exists", "SKIP", "DIAGNOSTIC_HARDWARE_ACCESS", "Skipped due to legacy layout")
                self._add("aux_com_port_exists", "SKIP", "DIAGNOSTIC_HARDWARE_ACCESS", "Skipped due to legacy layout", req=False)
                self._add("usb_xds110_identity", "SKIP", "DIAGNOSTIC_HARDWARE_ACCESS", "Skipped due to legacy layout", req=False)
                self._add("uart_prompt_responds", "SKIP", "DIAGNOSTIC_HARDWARE_ACCESS", "Skipped due to legacy layout")
                self._add("host_nic_owns_ip", "SKIP", "DIAGNOSTIC_HARDWARE_ACCESS", "Skipped due to legacy layout")
                self._add("udp_data_port_bind", "SKIP", "DIAGNOSTIC_HARDWARE_ACCESS", "Skipped due to legacy layout")
                self._add("dca_control_responds", "SKIP", "DIAGNOSTIC_HARDWARE_ACCESS", "Skipped due to legacy layout")
                
            return HardwareReport(list(self._checks.values()), datetime.now(timezone.utc).isoformat(), "LIVE_DIAGNOSTIC" if include_hardware else "OFFLINE_ONLY")
            
        # 1. Project structure
        dirs = ["captures", "profiles", ".awr2944"]
        missing = [d for d in dirs if not (self._project.root / d).exists()]
        if missing:
            self._add("project_structure", "FAIL", "OFFLINE", f"Missing: {', '.join(missing)}")
        else:
            self._add("project_structure", "PASS", "OFFLINE", "All expected directories exist")

        # 2. Portable config TOML
        portable_path = self._project.root / "awr2944.toml"
        try:
            import tomli
            with open(portable_path, "rb") as f:
                tomli.load(f)
            self._add("portable_config_valid", "PASS", "OFFLINE", "awr2944.toml parses successfully")
        except Exception as e:
            self._add("portable_config_valid", "FAIL", "OFFLINE", f"Error parsing awr2944.toml: {e}")

        # 3. Local config TOML
        local_path = self._project.root / ".awr2944" / "local.toml"
        try:
            import tomli
            with open(local_path, "rb") as f:
                tomli.load(f)
            self._add("local_config_valid", "PASS", "OFFLINE", "local.toml parses successfully")
        except Exception as e:
            self._add("local_config_valid", "FAIL", "OFFLINE", f"Error parsing local.toml: {e}")

        cfg = self._project.config

        # 4 & 5. Executables
        if cfg.local.dca_control_exe and Path(cfg.local.dca_control_exe).exists():
            self._add("dca_control_exe_exists", "PASS", "OFFLINE", cfg.local.dca_control_exe)
        else:
            self._add("dca_control_exe_exists", "FAIL", "OFFLINE", f"Not found: '{cfg.local.dca_control_exe}'")

        if cfg.local.dca_record_exe and Path(cfg.local.dca_record_exe).exists():
            self._add("dca_record_exe_exists", "PASS", "OFFLINE", cfg.local.dca_record_exe)
        else:
            self._add("dca_record_exe_exists", "FAIL", "OFFLINE", f"Not found: '{cfg.local.dca_record_exe}'")

        # 6. cf.json exists
        cf = cfg.local.cf_json_path
        if cf and Path(cf).exists():
            self._add("cf_json_exists", "PASS", "OFFLINE", cf)
        else:
            self._add("cf_json_exists", "FAIL", "OFFLINE", f"Not found: '{cf}'")

        # 7. cf.json consistency
        if self._checks.get("cf_json_exists", CheckResult("","FAIL","","")).status != "PASS" or self._checks.get("portable_config_valid", CheckResult("","FAIL","","")).status != "PASS" or self._checks.get("local_config_valid", CheckResult("","FAIL","","")).status != "PASS":
            self._add("cf_json_consistency", "SKIP", "OFFLINE", "Prerequisite cf.json or configs failed", sugg="Depends on: cf_json_exists, portable_config_valid, local_config_valid")
        else:
            try:
                cfg.validate_cf_json()
                self._add("cf_json_consistency", "PASS", "OFFLINE", "Matches TOML network settings")
            except Exception as e:
                self._add("cf_json_consistency", "FAIL", "OFFLINE", str(e))

        # 15. Session Lock
        from awr2944_dca.api._lock import HardwareLease
        from awr2944_dca.api._session import resolve_connection
        try:
            conn = resolve_connection(self._project.root)
            state, lock_info = HardwareLease.inspect_owner(
                com_port=conn.com_port,
                host_ip=conn.host_ip,
                data_port=conn.data_port,
                dca_ip=conn.dca_ip,
                cmd_port=conn.cmd_port,
            )
            
            if state == "owned_by_us":
                self._add("no_active_session_lock", "PASS", "OFFLINE", f"Session lock held by this process ({lock_info.pid})", req=False)
            elif state == "owned_by_other_live":
                self._add("no_active_session_lock", "FAIL", "OFFLINE", f"Hardware locked by live process {lock_info.pid} (Project: {lock_info.project_root})", req=False)
            elif state == "stale":
                self._add("no_active_session_lock", "WARN", "OFFLINE", f"Stale lock found from dead process {lock_info.pid} (Project: {lock_info.project_root})", req=False)
            elif state == "malformed":
                self._add("no_active_session_lock", "WARN", "OFFLINE", "Malformed lock file found", req=False)
            else:
                self._add("no_active_session_lock", "PASS", "OFFLINE", "Hardware is currently unlocked", req=False)
        except Exception as e:
            self._add("no_active_session_lock", "FAIL", "OFFLINE", f"Failed to check lock status: {e}", req=False)

        if not include_hardware:
            return HardwareReport(list(self._checks.values()), datetime.now(timezone.utc).isoformat(), "OFFLINE_ONLY")

        # 8 & 9. COM Ports exist
        from awr2944_dca.hardware.ports import scan_ports
        all_ports = {p.com for p in scan_ports()}
        
        com = cfg.local.com_port
        if not com:
            self._add("cli_com_port_exists", "FAIL", "DIAGNOSTIC_HARDWARE_ACCESS", "Not configured")
        elif com in all_ports:
            self._add("cli_com_port_exists", "PASS", "DIAGNOSTIC_HARDWARE_ACCESS", com)
        else:
            self._add("cli_com_port_exists", "FAIL", "DIAGNOSTIC_HARDWARE_ACCESS", f"{com} missing")

        aux = cfg.local.aux_com_port
        if not aux:
            self._add("aux_com_port_exists", "WARN", "DIAGNOSTIC_HARDWARE_ACCESS", "Not configured", req=False)
        elif aux in all_ports:
            self._add("aux_com_port_exists", "PASS", "DIAGNOSTIC_HARDWARE_ACCESS", aux, req=False)
        else:
            self._add("aux_com_port_exists", "WARN", "DIAGNOSTIC_HARDWARE_ACCESS", f"{aux} missing", req=False)

        # 10. USB/XDS110 identity
        if self._checks.get("cli_com_port_exists", CheckResult("","FAIL","","")).status != "PASS":
            self._add("usb_xds110_identity", "SKIP", "DIAGNOSTIC_HARDWARE_ACCESS", "CLI COM port missing", req=False, sugg="Depends on: cli_com_port_exists")
        else:
            from awr2944_dca.headless_serial import discover_serial_ports
            sp = [p for p in discover_serial_ports() if p.port == com]
            if sp and sp[0].is_xds110:
                self._add("usb_xds110_identity", "PASS", "DIAGNOSTIC_HARDWARE_ACCESS", "Matches XDS110 VID/PID", req=False)
            else:
                self._add("usb_xds110_identity", "WARN", "DIAGNOSTIC_HARDWARE_ACCESS", "Not recognized as XDS110 (could be standard serial)", req=False)

        # 11. UART Prompt
        if self._checks.get("cli_com_port_exists", CheckResult("","FAIL","","")).status != "PASS":
            self._add("uart_prompt_responds", "SKIP", "DIAGNOSTIC_HARDWARE_ACCESS", "CLI COM port missing", sugg="Depends on: cli_com_port_exists")
        else:
            try:
                import serial
                with serial.Serial(com, cfg.local.baud_rate, timeout=3.0) as ser:
                    ser.reset_input_buffer()
                    ser.write(b"\n")
                    res = ser.read_until(b"mmwDemo:/>")
                    if b"mmwDemo:/>" in res:
                        self._add("uart_prompt_responds", "PASS", "DIAGNOSTIC_HARDWARE_ACCESS", "Received mmwDemo:/>")
                    else:
                        self._add("uart_prompt_responds", "FAIL", "DIAGNOSTIC_HARDWARE_ACCESS", "TIMEOUT - No prompt received")
            except serial.SerialException as e:
                self._add("uart_prompt_responds", "FAIL", "DIAGNOSTIC_HARDWARE_ACCESS", f"BUSY or error: {e}", sugg="Check if another application has the port open.")
            except Exception as e:
                self._add("uart_prompt_responds", "FAIL", "DIAGNOSTIC_HARDWARE_ACCESS", f"Error: {e}")

        # 12. Host NIC owns IP
        host_ip = cfg.local.host_ip
        if not host_ip:
            self._add("host_nic_owns_ip", "FAIL", "DIAGNOSTIC_HARDWARE_ACCESS", "Not configured")
        else:
            from awr2944_dca.dca.preflight import run_dca_preflight
            pf = run_dca_preflight(host_ip=host_ip, dca_ip=cfg.portable.dca_ip, ping_only=True)
            from awr2944_dca.dca.preflight import _run_ps_json, _as_dicts
            script = f"Get-NetIPAddress -IPAddress {host_ip} -ErrorAction SilentlyContinue | Select-Object InterfaceAlias"
            found = _as_dicts(_run_ps_json(script))
            if found:
                self._add("host_nic_owns_ip", "PASS", "DIAGNOSTIC_HARDWARE_ACCESS", f"Bound to {found[0].get('InterfaceAlias', 'Unknown')}")
            else:
                self._add("host_nic_owns_ip", "FAIL", "DIAGNOSTIC_HARDWARE_ACCESS", f"{host_ip} not found on any local interface")

        # 14. UDP Data port bind
        if self._checks.get("host_nic_owns_ip", CheckResult("","FAIL","","")).status != "PASS":
            self._add("udp_data_port_bind", "SKIP", "DIAGNOSTIC_HARDWARE_ACCESS", "Host NIC IP check failed", sugg="Depends on: host_nic_owns_ip")
        else:
            port = cfg.portable.data_port
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind((host_ip, port))
                sock.close()
                self._add("udp_data_port_bind", "PASS", "DIAGNOSTIC_HARDWARE_ACCESS", f"{host_ip}:{port} is available")
            except OSError as e:
                self._add("udp_data_port_bind", "FAIL", "DIAGNOSTIC_HARDWARE_ACCESS", f"BUSY - Cannot bind {host_ip}:{port} ({e})")

        # 13. DCA Control responds
        if (self._checks.get("dca_control_exe_exists", CheckResult("","FAIL","","")).status != "PASS" or 
            self._checks.get("cf_json_exists", CheckResult("","FAIL","","")).status != "PASS" or 
            self._checks.get("cf_json_consistency", CheckResult("","FAIL","","")).status != "PASS" or
            self._checks.get("host_nic_owns_ip", CheckResult("","FAIL","","")).status != "PASS"):
            self._add("dca_control_responds", "SKIP", "DIAGNOSTIC_HARDWARE_ACCESS", "Prerequisites failed", sugg="Depends on: dca_control_exe_exists, cf_json_exists, cf_json_consistency, host_nic_owns_ip")
        else:
            cmd = [cfg.local.dca_control_exe, "query_sys_status", cfg.local.cf_json_path]
            try:
                t0 = datetime.now()
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                dt = (datetime.now() - t0).total_seconds()
                
                if res.returncode == 0:
                    self._add("dca_control_responds", "PASS", "DIAGNOSTIC_HARDWARE_ACCESS", f"System alive (took {dt:.2f}s)")
                else:
                    self._add("dca_control_responds", "FAIL", "DIAGNOSTIC_HARDWARE_ACCESS", f"Command failed (RC={res.returncode}): {res.stderr.strip() or res.stdout.strip()}")
            except subprocess.TimeoutExpired:
                self._add("dca_control_responds", "FAIL", "DIAGNOSTIC_HARDWARE_ACCESS", "TIMEOUT - DCA did not respond")
            except Exception as e:
                self._add("dca_control_responds", "FAIL", "DIAGNOSTIC_HARDWARE_ACCESS", f"Error: {e}")

        return HardwareReport(list(self._checks.values()), datetime.now(timezone.utc).isoformat(), "LIVE_DIAGNOSTIC")
