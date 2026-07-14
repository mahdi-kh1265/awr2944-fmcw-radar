"""Ethernet pairing and configuration for DCA1000 connections.

Separates pure logic (snapshot diffing, candidate selection) from
hardware-touching functions (PowerShell calls) for testability.

Machine-local pairing is stored in ``.local/eth_pairing.json``
(gitignored), while shared DCA profile lives in ``project.json``.
"""

from __future__ import annotations

import datetime
import json
import subprocess
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class AdapterInfo:
    """Network adapter snapshot entry."""
    interface_alias: str
    interface_index: int
    status: str  # "Up", "Disconnected"
    link_speed: str
    mac_address: str
    ipv4_addresses: list[str] = field(default_factory=list)
    has_default_gateway: bool = False
    has_dns: bool = False
    media_type: str = ""  # "802.3", "Native 802.11"


@dataclass
class EthernetSnapshot:
    """Immutable snapshot of all network adapters at a point in time."""
    adapters: list[AdapterInfo]
    timestamp: str = ""


@dataclass
class EthernetPairing:
    """Machine-local paired adapter identity."""
    interface_alias: str = ""
    interface_index: int = 0
    interface_guid: str = ""
    host_adapter_mac: str = ""
    paired_at: str = ""
    pre_pairing_snapshot: dict | None = None


@dataclass
class PairingSession:
    """In-progress pairing session (between begin and finish)."""
    before: EthernetSnapshot
    after: EthernetSnapshot | None = None
    candidates: list[AdapterInfo] = field(default_factory=list)
    selected: AdapterInfo | None = None


# ---------------------------------------------------------------------------
# Local pairing file
# ---------------------------------------------------------------------------

_LOCAL_DIR = ".local"
_PAIRING_FILE = "eth_pairing.json"


def _pairing_path(project_root: Path) -> Path:
    return project_root / _LOCAL_DIR / _PAIRING_FILE


def _ensure_local_gitignored(project_root: Path) -> None:
    """Ensure .local/ is in .gitignore."""
    gi = project_root / ".gitignore"
    rule = ".local/"
    if gi.exists():
        content = gi.read_text(encoding="utf-8")
        if rule in content:
            return
    with open(gi, "a", encoding="utf-8") as f:
        f.write(f"\n# Machine-local hardware pairing (not shared)\n{rule}\n")


def load_pairing(project_root: Path) -> EthernetPairing | None:
    """Load machine-local pairing, or None if not paired."""
    path = _pairing_path(project_root)
    if not path.exists():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    return EthernetPairing(**{
        k: raw[k] for k in EthernetPairing.__dataclass_fields__
        if k in raw
    })


def save_pairing(project_root: Path, pairing: EthernetPairing) -> Path:
    """Save machine-local pairing to .local/eth_pairing.json."""
    local_dir = project_root / _LOCAL_DIR
    local_dir.mkdir(parents=True, exist_ok=True)
    _ensure_local_gitignored(project_root)
    path = _pairing_path(project_root)
    path.write_text(
        json.dumps(asdict(pairing), indent=2, default=str),
        encoding="utf-8",
    )
    return path


def remove_pairing(project_root: Path) -> None:
    """Delete machine-local pairing file."""
    path = _pairing_path(project_root)
    if path.exists():
        path.unlink()


# ---------------------------------------------------------------------------
# Pure functions (testable without hardware)
# ---------------------------------------------------------------------------

def snapshot_from_dicts(raw_list: list[dict]) -> EthernetSnapshot:
    """Build an EthernetSnapshot from raw PowerShell adapter dicts."""
    adapters = []
    for d in raw_list:
        adapters.append(AdapterInfo(
            interface_alias=d.get("InterfaceAlias", d.get("interface_alias", "Unknown")),
            interface_index=d.get("InterfaceIndex", d.get("interface_index", 0)),
            status=d.get("Status", d.get("status", "Unknown")),
            link_speed=d.get("LinkSpeed", d.get("link_speed", "")),
            mac_address=d.get("MacAddress", d.get("mac_address", "")),
            ipv4_addresses=d.get("IPv4Addresses", d.get("ipv4_addresses", [])),
            has_default_gateway=d.get("HasDefaultGateway", d.get("has_default_gateway", False)),
            has_dns=d.get("HasDns", d.get("has_dns", False)),
            media_type=d.get("MediaType", d.get("media_type", "")),
        ))
    return EthernetSnapshot(
        adapters=adapters,
        timestamp=datetime.datetime.now().isoformat(),
    )


def diff_snapshots(
    before: EthernetSnapshot,
    after: EthernetSnapshot,
) -> list[AdapterInfo]:
    """Find adapters that are new or changed from disconnected to up.

    Returns list of candidate adapters from the ``after`` snapshot.
    """
    before_by_mac = {a.mac_address: a for a in before.adapters}
    candidates = []

    for a in after.adapters:
        prev = before_by_mac.get(a.mac_address)
        if prev is None:
            # Newly appeared adapter
            candidates.append(a)
        elif (
            prev.status.lower() in ("disconnected", "not present")
            and a.status.lower() == "up"
        ):
            # Status changed from disconnected to up
            candidates.append(a)

    return candidates


def select_candidate(
    candidates: list[AdapterInfo],
    force: bool = False,
) -> AdapterInfo:
    """Pick a single DCA adapter candidate from the diff results.

    Raises:
        ValueError: If no candidates, ambiguous candidates, or
            candidate is unsafe (Wi-Fi, has gateway) without force.
    """
    if not candidates:
        raise ValueError(
            "No new or changed adapters detected. "
            "Make sure the DCA1000 Ethernet cable was plugged in between snapshots."
        )

    # Filter out Wi-Fi
    wired = [
        a for a in candidates
        if "wi-fi" not in a.interface_alias.lower()
        and "wireless" not in a.interface_alias.lower()
        and "802.11" not in a.media_type.lower()
    ]

    rejected_wifi = len(candidates) - len(wired)
    if not wired:
        raise ValueError(
            f"All {len(candidates)} detected adapter(s) are Wi-Fi. "
            "DCA1000 requires a wired Ethernet connection."
        )

    # Filter out adapters with default gateway (unless forced)
    if not force:
        safe = [a for a in wired if not a.has_default_gateway]
        if not safe:
            aliases = [a.interface_alias for a in wired]
            raise ValueError(
                f"All candidate adapters have a default gateway (internet route): "
                f"{aliases}. This is likely your internet connection, not DCA1000. "
                f"Use force=True to override."
            )
        wired = safe

    if len(wired) > 1:
        aliases = [
            f"  - {a.interface_alias} (idx={a.interface_index}, mac={a.mac_address})"
            for a in wired
        ]
        raise ValueError(
            f"Ambiguous: {len(wired)} candidate adapters detected. "
            f"Unplug other Ethernet cables and retry:\n" + "\n".join(aliases)
        )

    return wired[0]


def build_configure_commands(
    adapter: AdapterInfo,
    host_ip: str = "192.168.33.30",
    prefix_length: int = 24,
) -> list[str]:
    """Build PowerShell commands to configure the adapter for DCA1000.

    Returns a list of PowerShell command strings.
    """
    idx = adapter.interface_index
    alias = adapter.interface_alias
    commands = [
        # Remove existing IPs
        (
            f"Get-NetIPAddress -InterfaceIndex {idx} -AddressFamily IPv4 "
            f"-ErrorAction SilentlyContinue | Remove-NetIPAddress -Confirm:$false "
            f"-ErrorAction SilentlyContinue"
        ),
        # Remove default gateway
        (
            f"Remove-NetRoute -InterfaceIndex {idx} -DestinationPrefix '0.0.0.0/0' "
            f"-Confirm:$false -ErrorAction SilentlyContinue"
        ),
        # Set static IP
        (
            f"New-NetIPAddress -InterfaceIndex {idx} -IPAddress '{host_ip}' "
            f"-PrefixLength {prefix_length} -ErrorAction Stop"
        ),
        # Clear DNS
        (
            f"Set-DnsClientServerAddress -InterfaceIndex {idx} "
            f"-ResetServerAddresses -ErrorAction SilentlyContinue"
        ),
    ]
    return commands


# ---------------------------------------------------------------------------
# Hardware-touching functions
# ---------------------------------------------------------------------------

_SNAPSHOT_PS_SCRIPT = """\
$ErrorActionPreference = 'SilentlyContinue'
$adapters = Get-NetAdapter | Where-Object { $_.Virtual -eq $false -and $_.MacAddress }

$results = @()
foreach ($a in $adapters) {
    $idx = $a.InterfaceIndex
    $ips = @(Get-NetIPAddress -InterfaceIndex $idx -AddressFamily IPv4 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty IPAddress)
    $routes = (Get-NetRoute -InterfaceIndex $idx -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue)
    $dns = @(Get-DnsClientServerAddress -InterfaceIndex $idx -AddressFamily IPv4 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ServerAddresses)

    $obj = @{
        InterfaceAlias = $a.Name
        InterfaceIndex = $idx
        Status = [string]$a.Status
        LinkSpeed = [string]$a.LinkSpeed
        MacAddress = $a.MacAddress
        IPv4Addresses = $ips
        HasDefaultGateway = if ($routes) { $true } else { $false }
        HasDns = if ($dns -and $dns.Count -gt 0) { $true } else { $false }
        MediaType = [string]$a.MediaType
    }
    $results += $obj
}

$results | ConvertTo-Json -Depth 3 -Compress
"""


def take_snapshot() -> EthernetSnapshot:
    """Take a live snapshot of network adapters via PowerShell."""
    try:
        output = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", _SNAPSHOT_PS_SCRIPT],
            text=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        ).strip()

        if not output:
            return EthernetSnapshot(adapters=[])

        data = json.loads(output)
        if isinstance(data, dict):
            data = [data]

        return snapshot_from_dicts(data)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return EthernetSnapshot(adapters=[])


def apply_configuration(commands: list[str]) -> list[dict]:
    """Execute PowerShell configuration commands. Returns results."""
    results = []
    for cmd in commands:
        try:
            subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", cmd],
                text=True,
                stderr=subprocess.STDOUT,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            results.append({"command": cmd, "success": True, "error": ""})
        except subprocess.CalledProcessError as e:
            results.append({"command": cmd, "success": False, "error": str(e.output)})
    return results


def check_adapter_status(pairing: EthernetPairing, host_ip: str = "192.168.33.30") -> dict:
    """Check if the paired adapter still has the correct IP."""
    try:
        snapshot = take_snapshot()
        for a in snapshot.adapters:
            if a.interface_index == pairing.interface_index:
                has_ip = host_ip in a.ipv4_addresses
                return {
                    "found": True,
                    "status": a.status,
                    "has_correct_ip": has_ip,
                    "ipv4_addresses": a.ipv4_addresses,
                    "ready": a.status.lower() == "up" and has_ip,
                }
        return {"found": False, "status": "not_found", "has_correct_ip": False, "ready": False}
    except Exception as e:
        return {"found": False, "status": f"error: {e}", "has_correct_ip": False, "ready": False}


# ---------------------------------------------------------------------------
# Two-step pairing workflow
# ---------------------------------------------------------------------------

def begin_pairing(snapshot_fn=None) -> PairingSession:
    """Step 1: Take a 'before' snapshot.

    Call this BEFORE plugging in the DCA1000 Ethernet cable.
    Returns a PairingSession to pass to ``finish_pairing()``.

    Args:
        snapshot_fn: Optional callable returning EthernetSnapshot
            (for testing). Defaults to ``take_snapshot()``.
    """
    fn = snapshot_fn or take_snapshot
    before = fn()
    return PairingSession(before=before)


def finish_pairing(
    session: PairingSession,
    project_root: Path,
    *,
    host_ip: str = "192.168.33.30",
    prefix_length: int = 24,
    force: bool = False,
    apply: bool = False,
    snapshot_fn=None,
    apply_fn=None,
) -> dict:
    """Step 2: Take an 'after' snapshot, detect the DCA adapter, optionally configure.

    Call this AFTER plugging in the DCA1000 Ethernet cable.

    Args:
        session: The PairingSession from ``begin_pairing()``.
        project_root: Project root directory.
        host_ip: IP address to assign to the host adapter.
        prefix_length: Subnet prefix length.
        force: Allow adapters with default gateway.
        apply: If True, actually configure the adapter. If False, dry-run only.
        snapshot_fn: Optional callable for testing.
        apply_fn: Optional callable for testing.

    Returns:
        Dict with pairing results, commands, and whether apply was performed.
    """
    fn = snapshot_fn or take_snapshot
    after = fn()
    session.after = after

    # Diff
    candidates = diff_snapshots(session.before, after)
    session.candidates = candidates

    # Select
    selected = select_candidate(candidates, force=force)
    session.selected = selected

    # Build commands
    commands = build_configure_commands(selected, host_ip, prefix_length)

    # Save pairing
    pairing = EthernetPairing(
        interface_alias=selected.interface_alias,
        interface_index=selected.interface_index,
        interface_guid="",  # populated if available
        host_adapter_mac=selected.mac_address,
        paired_at=datetime.datetime.now().isoformat(),
        pre_pairing_snapshot=asdict(session.before),
    )
    save_pairing(Path(project_root).resolve(), pairing)

    result = {
        "paired": True,
        "adapter": asdict(selected),
        "pairing": asdict(pairing),
        "commands": commands,
        "applied": False,
        "apply_results": [],
    }

    # Apply if requested
    if apply:
        afn = apply_fn or apply_configuration
        apply_results = afn(commands)
        result["applied"] = True
        result["apply_results"] = apply_results

    return result


def pair(
    project_root: Path,
    *,
    force: bool = False,
    apply: bool = False,
    before_snapshot: EthernetSnapshot | None = None,
    after_snapshot: EthernetSnapshot | None = None,
) -> dict:
    """Convenience: begin + finish pairing in one call.

    For testing, pass before_snapshot and after_snapshot directly.
    For interactive use, caller should prompt between begin and finish.
    """
    if before_snapshot:
        session = PairingSession(before=before_snapshot)
    else:
        session = begin_pairing()

    snapshot_fn = (lambda: after_snapshot) if after_snapshot else None

    return finish_pairing(
        session,
        project_root,
        force=force,
        apply=apply,
        snapshot_fn=snapshot_fn,
    )
