"""Post-connection automation (Firmware, RF, Static, Data).

Recorder/replayer architecture:
- Lua command return values and progress JSONL are authoritative for commands we run.
- Output snapshots parsed offline are the audit/status layer.
- Live UIA labels are optional hints only.

Clean-session rules:
- Do NOT run firmware-power-script twice in the same session.
- Do NOT run config scripts after PowerOff, Disconnect, failed RfEnable, or PROTOCOL ERROR.
- After any such event, require power-cycle and manual reconnect.
"""

from __future__ import annotations

import re
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Optional


from awr2944_dca.legacy_mmws.gui_connect import read_device_status, inspect_connection_tab, _find_by_auto_id


class PostConnectionGateError(RuntimeError):
    pass


@dataclass
class PostStatus:
    rs232_valid: bool = False
    bss_downloaded: bool = False
    bss_version: str = ""
    bss_patch_version: str = ""
    mss_downloaded: bool = False
    mss_version: str = ""
    mss_powered: bool = False
    bss_powered: bool = False
    rf_enabled: bool = False
    spi_connected: bool = False
    ready_for_static_config: bool = False
    smoke_config_applied: bool = False
    ready_for_dca_setup: bool = False
    ready_for_capture: bool = False

@dataclass
class GeneratedScript:
    script: str
    run_id: str
    lua_path: Path
    result_path: Path
    progress_path: Path
    dofile: str
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class RunStatus:
    run_id: str
    exists: bool = False
    success: bool = False
    error: str = ""

def load_run_result(manifest_or_run_id: str, probe_dir: Path) -> RunStatus:
    """Load the final result of a run using either a manifest file or directly the run_id result JSON."""
    manifest_path = probe_dir / f"{manifest_or_run_id}_manifest.json"
    result_path = probe_dir / f"{manifest_or_run_id}_result.json"
    
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if "result_path" in manifest:
                result_path = Path(manifest["result_path"])
        except (json.JSONDecodeError, IOError):
            pass

    if not result_path.exists():
        result_files = sorted(probe_dir.glob(f"{manifest_or_run_id}_*result.json"))
        if result_files:
            result_path = result_files[0]
            
    if result_path and result_path.exists():
        try:
            res = json.loads(result_path.read_text(encoding="utf-8"))
            if "success" in res:
                return RunStatus(
                    run_id=manifest_or_run_id,
                    exists=True,
                    success=res["success"],
                    error=res.get("error", "")
                )
        except (json.JSONDecodeError, IOError):
            pass
            
    return RunStatus(run_id=manifest_or_run_id, exists=False, success=False, error="")


# ---------------------------------------------------------------------------
# Connection gate
# ---------------------------------------------------------------------------

def connection_gate(window, vlog: Callable[[str], None]) -> dict[str, Any]:
    """Check if the manual RS232 connection gate is passed.
    
    Returns the parsed device_status dict and adds a 'gate_passed' boolean.
    Does NOT throw an exception, it is up to the caller to decide.
    """
    device_status = read_device_status(window, verbose_log=vlog)
    valid = device_status.get("valid", False)
    rs232 = device_status.get("rs232_status", "")
    
    gate_passed = valid and (rs232 == "Connected" or not rs232)
    device_status["gate_passed"] = gate_passed
    
    if gate_passed:
        vlog("Post-connection gate passed.")
    else:
        vlog(f"Post-connection gate failed. Device valid={valid}, RS232={rs232}")
        
    return device_status


# ---------------------------------------------------------------------------
# Status parsing — chronological / order-aware  (item H)
# ---------------------------------------------------------------------------

def extract_version_line(text: str, key: str) -> tuple[str | None, str | None]:
    for line in text.splitlines():
        if key in line:
            try:
                payload = line.split(key + ":(", 1)[1]
                if payload.endswith(")"):
                    payload = payload[:-1]
                return payload.strip(), line
            except IndexError:
                pass
    return None, None


def parse_post_status_text(
    doc_text: str, 
    rs232_valid: bool = False, 
    spi_connected: bool = False,
    source_name: str = "unknown_snapshot",
    snapshot_path: str = ""
) -> tuple[PostStatus, dict[str, Any]]:
    """Parse output text chronologically so later events override earlier ones.
    
    Key invalidation events:
    - PowerOff / Disconnect / "Debug Port Disconnected" clears power/RF/ready state
    - "Status: Failed" after RfEnable clears rf_enabled/bss_powered
    - "PROTOCOL ERROR" clears ready_for_static_config
    """
    status = PostStatus(rs232_valid=rs232_valid, spi_connected=spi_connected)
    matched: dict[str, str] = {}
    
    source_info: dict[str, Any] = {
        "source_type": source_name,
        "source_path": snapshot_path,
        "source_text_chars": len(doc_text) if doc_text else 0
    }
    
    if not doc_text:
        source_info["error"] = "OUTPUT_SNAPSHOT_UNREADABLE"
        return status, source_info

    # Version extraction (first-match is fine, these don't repeat in conflicting ways)
    bss_v, line_v = extract_version_line(doc_text, "BSSFwVersion")
    if bss_v:
        status.bss_version = bss_v
        matched["bss_version"] = line_v
        
    bss_p, line_p = extract_version_line(doc_text, "BSSPatchFwVersion")
    if bss_p:
        status.bss_patch_version = bss_p
        matched["bss_patch_version"] = line_p
        
    mss_v, line_mv = extract_version_line(doc_text, "MSSFwVersion")
    if mss_v:
        status.mss_version = mss_v
        matched["mss_version"] = line_mv

    # Process lines chronologically for state transitions
    lines = doc_text.splitlines()
    for line in lines:
        stripped = line.strip()
        
        # Firmware downloads
        if "ar1.DownloadBSSFw" in stripped:
            status.bss_downloaded = True
            matched["bss_download"] = stripped
        if "ar1.DownloadMSSFw" in stripped:
            status.mss_downloaded = True
            matched["mss_download"] = stripped
            
        # Version lines also confirm download
        if "BSSFwVersion:(" in stripped or "BSSPatchFwVersion:(" in stripped:
            status.bss_downloaded = True
        if "MSSFwVersion:(" in stripped:
            status.mss_downloaded = True
            
        # Power up events
        if "MSS power up done async event received!" in stripped:
            status.mss_powered = True
            matched["mss_powered"] = stripped
        if "BSS power up done async event received!" in stripped:
            status.bss_powered = True
            matched["bss_powered"] = stripped
            
        # RF Enable
        if "ar1.RfEnable" in stripped:
            status.rf_enabled = True
            matched["rf_enabled"] = stripped
            
        # Config applied
        if "ar1.FrameConfig" in stripped:
            status.smoke_config_applied = True
            matched["frame_config"] = stripped
            
        # Invalidation events — later state wins
        if "ar1.PowerOff" in stripped:
            status.mss_powered = False
            status.bss_powered = False
            status.rf_enabled = False
            status.smoke_config_applied = False
            matched["last_power_off"] = stripped
        if "ar1.Disconnect" in stripped or "Debug Port Disconnected" in stripped:
            status.mss_powered = False
            status.bss_powered = False
            status.rf_enabled = False
            status.smoke_config_applied = False
            matched["last_disconnect"] = stripped
        if "BSS Power Up async event was not received!" in stripped:
            status.bss_powered = False
            status.rf_enabled = False
            matched["bss_power_failed"] = stripped
        if "Status: Failed" in stripped and "PROTOCOL ERROR" in stripped:
            status.mss_powered = False
            status.bss_powered = False
            status.rf_enabled = False
            status.smoke_config_applied = False
            matched["protocol_error"] = stripped
        if "Status: Failed" in stripped and "INVALID INPUT" in stripped:
            status.smoke_config_applied = False
            matched["last_invalid_input"] = stripped

    status.ready_for_static_config = (
        status.rs232_valid and
        status.bss_downloaded and
        status.mss_downloaded and
        status.mss_powered and
        status.bss_powered and
        status.rf_enabled
    )
    status.ready_for_dca_setup = status.ready_for_static_config and status.smoke_config_applied
    status.ready_for_capture = False  # Set to true only after DCA setup is implemented
    
    source_info["matched_lines"] = matched
    return status, source_info


def get_post_status(window, vlog: Callable[[str], None], run_id: str, probe_dir: Path) -> tuple[dict[str, Any], PostStatus, dict[str, Any]]:
    """Check mmWave Studio state and parse output for a structured status via snapshot."""
    device_status = connection_gate(window, vlog)
    
    controls = inspect_connection_tab(window, verbose_log=vlog)
    spi_connected = False
    if controls.spi_status_label is not None:
        try:
            if controls.spi_status_label.window_text() == "Connected":
                spi_connected = True
        except Exception:
            pass

    # Dump live snapshot first
    snap_path = probe_dir / f"{run_id}_status_output_snapshot.txt"
    dump_output_snapshot(window, vlog, snap_path)
    
    doc_text = ""
    source_name = "live_snapshot"
    if snap_path.exists():
        doc_text = snap_path.read_text(encoding="utf-8")
    else:
        source_name = "live_snapshot_failed"
        
    status, source_info = parse_post_status_text(
        doc_text,
        rs232_valid=device_status.get("gate_passed", False),
        spi_connected=spi_connected,
        source_name=source_name,
        snapshot_path=str(snap_path)
    )
    
    return device_status, status, source_info


def dump_output_snapshot(window, vlog: Callable[[str], None], output_path: Path) -> None:
    """Dump full output doc text without truncation."""
    output_doc = _find_by_auto_id(window, "m_ConsoleText", vlog)
    if output_doc is None:
        controls = inspect_connection_tab(window, verbose_log=vlog)
        output_doc = controls.output_document
        
    if output_doc is None:
        vlog("Output document control not found.")
        return
        
    try:
        doc_text = output_doc.window_text()
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            f.write(doc_text)
        vlog(f"Wrote output snapshot to {output_path}")
    except Exception as e:
        vlog(f"Failed to read/write output document: {e}")


# ---------------------------------------------------------------------------
# Session auditor — dirty-session detection (chronological)
# ---------------------------------------------------------------------------

# Config commands whose failure contaminates the session
_CONFIG_FUNCTIONS = {
    "ChanNAdcConfig", "LPModConfig", "RfInit", "SetMiscConfig",
    "RfLdoBypassConfig", "SetCalMonFreqLimitConfig", "SetRFDeviceConfig",
    "RfSetCalMonFreqTxPowLimitConfig", "SetApllSynthBWCtlConfig",
    "DataPathConfig", "LvdsClkConfig", "LVDSLaneConfig",
    "ProfileConfig", "ChirpConfig", "FrameConfig", "AdvanceFrameConfig",
    "DisableTestSource", "EnableTestSource",
}


@dataclass
class SessionAudit:
    rs232_valid: bool = False
    clean_for_firmware_power: bool = False
    firmware_power_already_attempted: bool = False
    firmware_power_success: bool = False
    rf_enable_failed: bool = False
    poweroff_seen: bool = False
    disconnect_seen: bool = False
    protocol_error_seen: bool = False
    static_config_attempted: bool = False
    static_config_failed: bool = False
    requires_power_cycle: bool = False
    reason: list[str] = field(default_factory=list)
    source_type: str = "unknown"
    source_path: str = ""


def _find_session_boundary(lines: list[str]) -> int:
    """Find the latest session boundary line index.
    
    Uses the latest of:
    - Latest valid Device Status line (containing AWR2944 and / )
    - Latest Startup.lua reference
    - Latest AWR_RUN_BEGIN marker
    
    Returns 0 if no boundary found.
    """
    boundary = 0
    for i in range(len(lines) - 1, -1, -1):
        stripped = lines[i].strip()
        if "Device Status" in stripped and "AWR2944" in stripped and "/" in stripped:
            boundary = max(boundary, i)
            break  # last Device Status wins
    for i in range(len(lines) - 1, -1, -1):
        stripped = lines[i].strip()
        if "Startup.lua" in stripped:
            boundary = max(boundary, i)
            break
    return boundary


def audit_session(doc_text: str, rs232_valid: bool = False, source_type: str = "unknown", source_path: str = "") -> SessionAudit:
    """Audit output text chronologically from the latest session boundary.
    
    Detects invalidation events and determines stage readiness.
    """
    audit = SessionAudit(rs232_valid=rs232_valid, source_type=source_type, source_path=source_path)
    
    if not doc_text:
        audit.reason.append("OUTPUT_SNAPSHOT_UNREADABLE")
        return audit
    
    lines = doc_text.splitlines()
    start_idx = _find_session_boundary(lines)
    
    # Track firmware download/power/rf state chronologically
    bss_downloaded = False
    mss_downloaded = False
    power_on_seen = False
    rf_enable_seen = False
    rf_enable_ok = False
    
    ar1_pattern = re.compile(r"ar1\.([A-Za-z0-9_]+)")
    
    i = start_idx
    while i < len(lines):
        stripped = lines[i].strip()
        
        # --- Firmware/power attempts ---
        if "ar1.DownloadBSSFw" in stripped:
            audit.firmware_power_already_attempted = True
            bss_downloaded = True
        if "ar1.DownloadMSSFw" in stripped:
            audit.firmware_power_already_attempted = True
            mss_downloaded = True
        if "ar1.PowerOn" in stripped:
            audit.firmware_power_already_attempted = True
            power_on_seen = True
        if "ar1.RfEnable" in stripped:
            audit.firmware_power_already_attempted = True
            rf_enable_seen = True
            rf_enable_ok = True  # optimistic; overridden below if failure detected
        
        # --- Success indicators ---
        if "MSS power up done async event received!" in stripped:
            pass  # confirms PowerOn; we already track power_on_seen
        if "BSS power up done async event received!" in stripped:
            pass  # confirms RfEnable BSS side
        
        # --- Dirty events ---
        if "ar1.PowerOff" in stripped:
            audit.poweroff_seen = True
            audit.requires_power_cycle = True
            audit.reason.append(f"PowerOff seen at line {i+1}")
            # Invalidate firmware/power success
            power_on_seen = False
            rf_enable_ok = False
            audit.firmware_power_success = False
            
        if "ar1.Disconnect" in stripped or "Debug Port Disconnected" in stripped:
            audit.disconnect_seen = True
            audit.requires_power_cycle = True
            audit.reason.append(f"Disconnect seen at line {i+1}")
            power_on_seen = False
            rf_enable_ok = False
            audit.firmware_power_success = False
            
        if "PROTOCOL ERROR" in stripped:
            audit.protocol_error_seen = True
            audit.requires_power_cycle = True
            audit.reason.append(f"PROTOCOL ERROR at line {i+1}")
            power_on_seen = False
            rf_enable_ok = False
            audit.firmware_power_success = False
        
        if "BSS Power Up async event was not received" in stripped:
            audit.rf_enable_failed = True
            audit.requires_power_cycle = True
            audit.reason.append(f"BSS Power Up async not received at line {i+1}")
            rf_enable_ok = False
            audit.firmware_power_success = False
        
        # RfEnable failure detection: "Status: Failed" in the few lines after ar1.RfEnable
        if rf_enable_seen and "Status: Failed" in stripped:
            audit.rf_enable_failed = True
            audit.requires_power_cycle = True
            audit.reason.append(f"RfEnable Status: Failed at line {i+1}")
            rf_enable_ok = False
            audit.firmware_power_success = False
        
        # --- Config attempts and failures ---
        m = ar1_pattern.search(stripped)
        if m:
            func = m.group(1)
            if func in _CONFIG_FUNCTIONS:
                audit.static_config_attempted = True
                # Check next few lines for failure
                lookahead_end = min(i + 6, len(lines))
                for j in range(i + 1, lookahead_end):
                    la = lines[j].strip()
                    if "Status: Failed" in la:
                        audit.static_config_failed = True
                        audit.requires_power_cycle = True
                        audit.reason.append(f"{func} Status: Failed at line {j+1}")
                        break
                    if "Status: Passed" in la:
                        break
                    if ar1_pattern.search(la):
                        break  # next command, no status for this one
        
        # --- RadarAPI / GUI / WinForms errors ---
        if "[RadarAPI]: Error:" in stripped:
            audit.static_config_failed = True
            audit.requires_power_cycle = True
            audit.reason.append(f"RadarAPI error at line {i+1}: {stripped[:120]}")
        if "FREQUENCY IS NOT WITHIN VCO RANGE" in stripped:
            audit.static_config_failed = True
            audit.requires_power_cycle = True
            audit.reason.append(f"VCO frequency range error at line {i+1}")
        if "Value of '" in stripped:
            audit.static_config_failed = True
            audit.requires_power_cycle = True
            audit.reason.append(f"WinForms numeric validation error at line {i+1}: {stripped[:120]}")
        if "ProfileConfig failed" in stripped:
            audit.static_config_failed = True
            audit.requires_power_cycle = True
            audit.reason.append(f"ProfileConfig failed at line {i+1}")
        
        # --- AWR_RUN markers ---
        if "AWR_RUN_END" in stripped and "success=false" in stripped:
            audit.requires_power_cycle = True
            audit.reason.append(f"AWR_RUN_END success=false at line {i+1}")
        
        i += 1
    
    # Derived state
    audit.firmware_power_success = (
        bss_downloaded and mss_downloaded and power_on_seen and 
        rf_enable_ok and not audit.requires_power_cycle
    )
    
    audit.clean_for_firmware_power = (
        audit.rs232_valid and 
        not audit.firmware_power_already_attempted and 
        not audit.requires_power_cycle
    )
    
    return audit


def preflight_firmware(audit: SessionAudit) -> tuple[bool, list[str]]:
    """Check if the session is clean enough to run firmware-power-script.
    
    Returns (passed, reasons).
    """
    reasons: list[str] = []
    
    if not audit.rs232_valid:
        reasons.append(
            "RS232 identity gate not valid (Device Status extraction may have "
            "returned empty — use --assume-manual-connected if you have "
            "visually confirmed the connection)"
        )
    if audit.firmware_power_already_attempted:
        reasons.append("Firmware/power already attempted in this session")
    if audit.requires_power_cycle:
        reasons.extend(audit.reason)
    
    passed = len(reasons) == 0
    return passed, reasons


def preflight_config(audit: SessionAudit) -> tuple[bool, list[str]]:
    """Check if the session is clean enough to run config scripts.
    
    Returns (passed, reasons).
    """
    reasons: list[str] = []
    
    if not audit.firmware_power_success:
        reasons.append("Firmware/power sequence did not succeed in this session")
    if audit.requires_power_cycle:
        reasons.extend(audit.reason)
    if audit.static_config_failed:
        reasons.append("A prior config command failed in this session")
    
    passed = len(reasons) == 0
    return passed, reasons


# ---------------------------------------------------------------------------
# Jupyter API contract (TODO — enforce when Jupyter wrapper is built)
# ---------------------------------------------------------------------------
#
# When the Jupyter/notebook API wrapper is implemented, the following
# contract MUST be enforced:
#
#   sess.generate_firmware_power() MUST call preflight_firmware()
#   sess.generate_config_script()  MUST call preflight_config()
#
#   Any Jupyter method that generates hardware-changing Lua MUST either:
#     a) pass its preflight gate, OR
#     b) require force=True with an explicit warning
#
# This prevents users from accidentally running firmware or config on a
# dirty session from a notebook cell without realizing the session state.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# AR1 command extraction and classification (items B, D, F)
# ---------------------------------------------------------------------------

@dataclass
class AR1Command:
    line_number: int
    timestamp: str
    raw_line: str
    function_name: str
    args_text: str
    category: str
    observed_status: str = "unknown"        # "passed" | "failed" | "unknown"
    observed_error_type: str | None = None  # "INVALID INPUT" | "PROTOCOL ERROR" | None
    normalized_category: str = ""           # Current taxonomy classification

    def __post_init__(self):
        if not self.normalized_category:
            self.normalized_category = _classify_ar1(self.function_name)


_AR1_CATEGORIES = {
    "connection": {
        "Connect", "Calling_IsConnected", "SOPControl", "FullReset",
        "frequencyBandSelection", "SelectChipVersion", "deviceVariantSelection",
        "SaveSettings", "Disconnect",
    },
    "firmware": {
        "DownloadBSSFw", "GetBSSFwVersion", "GetBSSPatchFwVersion",
        "DownloadMSSFw", "GetMSSFwVersion",
    },
    "power_rf": {"PowerOn", "PowerOff", "RfEnable"},
    "static_config": {"ChanNAdcConfig", "LPModConfig", "RfInit", "SetMiscConfig"},
    "rf_static_config": {
        "RfLdoBypassConfig", "SetCalMonFreqLimitConfig", "SetRFDeviceConfig",
        "RfSetCalMonFreqTxPowLimitConfig", "SetApllSynthBWCtlConfig",
    },
    "data_config": {"DataPathConfig", "LvdsClkConfig", "LVDSLaneConfig"},
    "profile_chirp_frame": {
        "ProfileConfig", "ChirpConfig", "FrameConfig", "AdvanceFrameConfig",
    },
    "sensor_control": {"StartFrame", "StopFrame", "SensorStart", "SensorStop"},
    "test_source": {"DisableTestSource", "EnableTestSource"},
    "dca_capture": {
        "CaptureCardConfig_EthInit", "CaptureCardConfig_Mode",
        "CaptureCardConfig_PacketDelay", "CaptureCardConfig_StartRecord",
        "CaptureCardConfig_StopRecord", "SelectCaptureDevice",
    },
}


# Known AWR2944 argument counts for signature validation
AWR2944_ARG_COUNTS: dict[str, int] = {
    "ChanNAdcConfig": 11,
    "DataPathConfig": 3,
    "LvdsClkConfig": 2,
    "LVDSLaneConfig": 8,
    "LPModConfig": 2,
    "RfLdoBypassConfig": 1,
    "SetCalMonFreqLimitConfig": 3,
    "SetRFDeviceConfig": 7,
    "RfSetCalMonFreqTxPowLimitConfig": 13,
    "SetApllSynthBWCtlConfig": 7,
    "ProfileConfig": 23,
    "ChirpConfig": 11,
    "FrameConfig": 7,
    "DisableTestSource": 1,
}


def _classify_ar1(func_name: str) -> str:
    for cat, funcs in _AR1_CATEGORIES.items():
        if func_name in funcs:
            return cat
    return "unknown"


def _count_top_level_args(args_text: str) -> int:
    """Count top-level comma-separated arguments, handling nested parens/quotes."""
    if not args_text.strip():
        return 0
    depth = 0
    in_str = False
    count = 1
    for ch in args_text:
        if ch == '"' and depth == 0:
            in_str = not in_str
        elif not in_str:
            if ch in '(':
                depth += 1
            elif ch in ')':
                depth -= 1
            elif ch == ',' and depth == 0:
                count += 1
    return count


def validate_command_signature(cmd: AR1Command) -> list[str]:
    """Check if command has the expected number of args for AWR2944."""
    warnings = []
    expected = AWR2944_ARG_COUNTS.get(cmd.function_name)
    if expected is not None:
        actual = _count_top_level_args(cmd.args_text)
        if actual != expected:
            warnings.append(
                f"{cmd.function_name}: expected {expected} args, got {actual} "
                f"(args: {cmd.args_text[:80]})"
            )
    return warnings


def extract_ar1_commands(doc_text: str, after_device_status: bool = True) -> list[AR1Command]:
    """Parse mmWave Studio Output text for ar1.* commands with status observation."""
    commands: list[AR1Command] = []
    
    lines = doc_text.splitlines()
    start_idx = 0
    if after_device_status:
        for i in range(len(lines) - 1, -1, -1):
            if "Device Status" in lines[i] and "/" in lines[i]:
                start_idx = i
                break

    # e.g. "[13:08:49] [RadarAPI]: ar1.DownloadBSSFw("C:\...", 0)"
    pattern = re.compile(r"(\[\d{2}:\d{2}:\d{2}\])\s*\[RadarAPI\]:\s*ar1\.([A-Za-z0-9_]+)\((.*)\)")
    
    for i in range(start_idx, len(lines)):
        line = lines[i]
        m = pattern.search(line)
        if m:
            ts, func, args = m.groups()
            cat = _classify_ar1(func)
            
            # Look ahead in the next few lines for status/error
            obs_status = "unknown"
            obs_error = None
            lookahead_end = min(i + 6, len(lines))
            for j in range(i + 1, lookahead_end):
                la = lines[j].strip()
                if "Status: Passed" in la:
                    obs_status = "passed"
                    break
                if "Status: Failed" in la:
                    obs_status = "failed"
                    if "INVALID INPUT" in la:
                        obs_error = "INVALID INPUT"
                    elif "PROTOCOL ERROR" in la:
                        obs_error = "PROTOCOL ERROR"
                    break
                # async events count as pass
                if "async event received!" in la and "was not received" not in la:
                    obs_status = "passed"
                    break
                if "async event was not received" in la:
                    obs_status = "failed"
                    break
                # Next ar1 command means no status for this one
                if pattern.search(la):
                    break
            
            commands.append(AR1Command(
                line_number=i+1,
                timestamp=ts,
                raw_line=line.strip(),
                function_name=func,
                args_text=args,
                category=cat,
                observed_status=obs_status,
                observed_error_type=obs_error,
                normalized_category=cat,
            ))
            
    return commands


def inspect_extracted_commands(commands: list[AR1Command]) -> dict[str, Any]:
    """Analyze extracted commands: counts, signatures, missing, failures."""
    
    required = {
        "ChanNAdcConfig", "LPModConfig", "RfInit", "DataPathConfig",
        "LVDSLaneConfig", "ProfileConfig", "ChirpConfig", "FrameConfig",
    }
    
    cat_counts: dict[str, int] = {}
    func_list: list[str] = []
    unknown_funcs: list[str] = []
    warnings: list[str] = []
    found_funcs: set[str] = set()
    sig_warnings: list[str] = []
    
    passed_cmds: list[dict] = []
    failed_cmds: list[dict] = []
    reclassified_cmds: list[dict] = []
    
    for cmd in commands:
        cat_counts[cmd.normalized_category] = cat_counts.get(cmd.normalized_category, 0) + 1
        func_list.append(cmd.function_name)
        found_funcs.add(cmd.function_name)
        
        if cmd.category != cmd.normalized_category:
            reclassified_cmds.append({
                "function": cmd.function_name,
                "original_category": cmd.category,
                "normalized_category": cmd.normalized_category
            })
            
        if cmd.normalized_category == "unknown":
            unknown_funcs.append(cmd.function_name)
            
        sig_warnings.extend(validate_command_signature(cmd))
        
        cmd_info = {
            "function": cmd.function_name,
            "args_preview": cmd.args_text[:80],
            "observed_status": cmd.observed_status,
            "observed_error_type": cmd.observed_error_type,
            "line": cmd.line_number,
        }
        if cmd.observed_status == "failed":
            failed_cmds.append(cmd_info)
        elif cmd.observed_status == "passed":
            passed_cmds.append(cmd_info)
    
    missing = required - found_funcs
    if missing:
        warnings.append(f"Missing required commands: {', '.join(sorted(missing))}")
    
    return {
        "total_commands": len(commands),
        "category_counts": cat_counts,
        "ordered_functions": func_list,
        "unknown_functions": unknown_funcs,
        "missing_required": sorted(missing),
        "passed_commands": passed_cmds,
        "failed_commands": failed_cmds,
        "reclassified_commands": reclassified_cmds,
        "signature_warnings": sig_warnings,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Shared Lua helpers — valid JSON logging (items G, 5)
# ---------------------------------------------------------------------------

def _lua_log_progress() -> str:
    """Return the standard Lua logProgress function with proper JSON quoting.
    
    Handles numeric, nil, and string return values correctly so every JSONL
    line is valid JSON.
    """
    return "\n".join([
        'local function jsonEscape(s)',
        '    if type(s) ~= "string" then s = tostring(s) end',
        r"    s = s:gsub('\\', '\\\\')",
        r'    s = s:gsub("\"", "\\\"")',
        r"    s = s:gsub('\n', '\\n')",
        r"    s = s:gsub('\r', '\\r')",
        r"    s = s:gsub('\t', '\\t')",
        '    return s',
        'end',
        'local function logProgress(func, ret, ok, err)',
        '    local f = io.open(progress_path, "a")',
        '    if f then',
        '        local ret_str',
        '        if ret == nil then',
        '            ret_str = "null"',
        '        elseif type(ret) == "number" then',
        '            ret_str = tostring(ret)',
        '        else',
        '            ret_str = "\\"" .. jsonEscape(ret) .. "\\""',
        '        end',
        '        local err_str = ""',
        '        if err ~= nil then',
        '            err_str = string.format(\', "err": "%s"\', jsonEscape(err))',
        '        end',
        '        f:write(\'{"ts": "\' .. os.date(\'%X\') .. \'", "cmd": "\' .. func .. \'", "ret": \' .. ret_str .. \', "ok": \' .. tostring(ok) .. err_str .. \'}\\n\')',
        '        f:close()',
        '    end',
        'end',
    ])


def _atomic_write_manifest(
    run_id: str,
    stage: str,
    lua_path: Path,
    result_path: Path,
    progress_path: Path,
) -> None:
    """Atomically write a run manifest JSON for observability tools."""
    import datetime
    
    manifest = {
        "run_id": run_id,
        "stage": stage,
        "lua_path": str(lua_path.resolve()),
        "result_path": str(result_path.resolve()),
        "progress_path": str(progress_path.resolve()),
        "dofile": f"dofile([[{lua_path.resolve()}]])",
        "created_at": datetime.datetime.now().isoformat()
    }
    
    probe_dir = lua_path.parent
    final_path = probe_dir / f"{run_id}_manifest.json"
    tmp_path = probe_dir / f"{run_id}_manifest.json.tmp"
    
    tmp_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    tmp_path.replace(final_path)


def _lua_result_init_and_save(run_id: str, out_path_str: str) -> str:
    """Return Lua code to initialize the result table and saveResult function."""
    return "\n".join([
        'local function jsonEscape(s)',
        '    if type(s) ~= "string" then s = tostring(s) end',
        r"    s = s:gsub('\\', '\\\\')",
        r'    s = s:gsub("\"", "\\\"")',
        r"    s = s:gsub('\n', '\\n')",
        r"    s = s:gsub('\r', '\\r')",
        r"    s = s:gsub('\t', '\\t')",
        '    return s',
        'end',
        f'local out_path = [[{out_path_str}]]',
        'local result = {',
        f'    run_id = "{run_id}",',
        '    executed = true,',
        '    success = false,',
        '    error = "",',
        '    warnings = {}',
        '}',
        '',
        'local function saveResult()',
        '    local f = io.open(out_path, "w")',
        '    if f then',
        '        local w_str = "["',
        '        for i, w in ipairs(result.warnings) do',
        '            w_str = w_str .. \'\"\' .. jsonEscape(w) .. \'\"\'',
        '            if i < #result.warnings then w_str = w_str .. ", " end',
        '        end',
        '        w_str = w_str .. "]"',
        '        f:write(string.format(\'{"run_id": "%s", "executed": %s, "success": %s, "error": "%s", "warnings": %s}\\n\',',
        '            result.run_id, tostring(result.executed), tostring(result.success), jsonEscape(result.error), w_str))',
        '        f:close()',
        '    end',
        'end',
    ])


def _lua_safe_call() -> str:
    """Return the standard Lua safeCall function (returns false on critical fail).
    
    Expects `run_id` and `run_stage` local variables to be defined in the
    calling script for AWR_RUN_END marker emission.
    """
    return "\n".join([
        'local function safeCall(funcName, func, critical)',
        '    local ok, ret = pcall(func)',
        '    local err = nil',
        '    if not ok then err = ret; ret = nil end',
        '    logProgress(funcName, ret, ok, err)',
        '    if not ok or (type(ret) == "number" and ret ~= 0) then',
        '        if funcName == "DisableTestSource" and ret == -1 then',
        '            table.insert(result.warnings, "DisableTestSource returned -1; likely benign if Test Source Already Disabled.")',
        '            return true',
        '        end',
        '        if critical then',
        '            result.error = funcName .. " failed: " .. tostring(err or ret)',
        '            saveResult()',
        '            print("AWR_RUN_END run_id=" .. run_id .. " stage=" .. run_stage .. " success=false")',
        '            return false',
        '        else',
        '            table.insert(result.warnings, funcName .. " failed: " .. tostring(err or ret))',
        '        end',
        '    end',
        '    return true',
        'end',
    ])


# ---------------------------------------------------------------------------
# Lua script generation — replay from extracted commands
# ---------------------------------------------------------------------------

def generate_replay_lua(commands: list[AR1Command], run_id: str, out_path: Path, categories: set[str] | None = None) -> str:
    """Generate a safe replay script from extracted commands."""
    prog_path = out_path.with_name(out_path.name.replace('.lua', '_progress.jsonl')).resolve().as_posix()
    
    lines = [
        f"-- AR1 Replay Script (run_id: {run_id})",
        f'local progress_path = [[{prog_path}]]',
        "",
        _lua_log_progress(),
        "",
        "local ok, ret, err",
    ]
    
    for cmd in commands:
        if categories and cmd.category not in categories:
            continue
        if not categories and cmd.category == "connection":
            continue  # default exclude connection
            
        lines.append(f"-- line {cmd.line_number}: {cmd.timestamp}")
        arg_str = cmd.args_text.replace('\\', '\\\\').replace('"', '\\"')
        
        lines.append(f"ok, ret = pcall(function() return ar1.{cmd.function_name}({cmd.args_text}) end)")
        lines.append(f"if not ok then err = ret; ret = nil else err = nil end")
        lines.append(f'logProgress("{cmd.function_name}", ret, ok, err)')
        lines.append(f"if not ok or (ret and type(ret) == 'number' and ret ~= 0) then")
        lines.append(f"    print('Error in {cmd.function_name}: ' .. tostring(err or ret))")
        lines.append(f"    return -- abort replay script on error")
        lines.append(f"end")
        lines.append("")
        
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Deterministic firmware/power script
# ---------------------------------------------------------------------------

def generate_firmware_power_script(run_id: str, lua_path: Path) -> GeneratedScript:
    """Deterministic firmware/power sequence."""
    
    prog_path = lua_path.with_name(f"{run_id}_firmware_power_progress.jsonl")
    result_path = lua_path.with_name(f"{run_id}_firmware_power_result.json")
    
    _atomic_write_manifest(run_id, "firmware_power", lua_path, result_path, prog_path)
    
    log_fn = _lua_log_progress()
    res_fn = _lua_result_init_and_save(run_id, result_path.resolve().as_posix())
    safe_fn = _lua_safe_call()
    
    script = f"""\
-- Firmware & Power Sequence
-- run_id: {run_id}
-- WARNING: Do NOT run this script twice in the same session.

local run_id = "{run_id}"
local run_stage = "firmware_power"
local progress_path = [[{prog_path.resolve().as_posix()}]]

{res_fn}

{log_fn}

{safe_fn}

print("AWR_RUN_BEGIN run_id=" .. run_id .. " stage=" .. run_stage)

-- 1. BSS Firmware
local bss_path = [[C:\\ti\\mmwave_studio_03_01_04_04\\rf_eval_firmware\\radarss\\xwr29xx_radarss_rprc.bin]]
if not safeCall("DownloadBSSFw", function() return ar1.DownloadBSSFw(bss_path) end, true) then return end
RSTD.Sleep(1000)

safeCall("GetBSSFwVersion", function() return ar1.GetBSSFwVersion() end, false)
safeCall("GetBSSPatchFwVersion", function() return ar1.GetBSSPatchFwVersion() end, false)

-- 2. MSS Firmware
local mss_path = [[C:\\ti\\mmwave_studio_03_01_04_04\\rf_eval_firmware\\masterss\\awr2xxx_mmwave_full_mss_rprc.bin]]
if not safeCall("DownloadMSSFw", function() return ar1.DownloadMSSFw(mss_path) end, true) then return end
RSTD.Sleep(1000)

safeCall("GetMSSFwVersion", function() return ar1.GetMSSFwVersion() end, false)

-- 3. Power On
if not safeCall("PowerOn", function() return ar1.PowerOn(0, 1000, 0, 0) end, true) then return end
RSTD.Sleep(2000)

-- 4. RF Enable
if not safeCall("RfEnable", function() return ar1.RfEnable() end, true) then return end
RSTD.Sleep(1000)

-- Final verifications
safeCall("GetMSSFwVersion", function() return ar1.GetMSSFwVersion() end, false)
safeCall("GetBSSFwVersion", function() return ar1.GetBSSFwVersion() end, false)
safeCall("GetBSSPatchFwVersion", function() return ar1.GetBSSPatchFwVersion() end, false)

result.success = true
saveResult()
print("AWR_RUN_END run_id=" .. run_id .. " stage=" .. run_stage .. " success=true")
"""
    return GeneratedScript(
        script=script,
        run_id=run_id,
        lua_path=lua_path,
        result_path=result_path,
        progress_path=prog_path,
        dofile=f"dofile([[{lua_path.resolve()}]])"
    )


# ---------------------------------------------------------------------------
# AR1 help probe (unchanged)
# ---------------------------------------------------------------------------

def generate_ar1_help_probe(run_id: str, result_path: Path) -> str:
    """Probe types for likely data/capture commands."""
    funcs = [
        "ChanNAdcConfig", "LPModConfig", "RfInit", "DataPathConfig",
        "LvdsClkConfig", "LVDSLaneConfig", "ProfileConfig", "ChirpConfig",
        "FrameConfig", "StartFrame", "StopFrame", "SensorStart", "SensorStop",
        "CaptureCardConfig_EthInit", "CaptureCardConfig_Mode",
        "CaptureCardConfig_PacketDelay", "CaptureCardConfig_StartRecord",
        "CaptureCardConfig_StopRecord", "SetDataConfig", "GetDataConfig",
        "RfLdoBypassConfig", "SetCalMonFreqLimitConfig", "SetRFDeviceConfig",
        "RfSetCalMonFreqTxPowLimitConfig", "SetApllSynthBWCtlConfig",
        "DisableTestSource", "EnableTestSource",
    ]
    
    lines = [
        f"-- AR1 Help Probe Script",
        f"-- run_id: {run_id}",
        f"local out_path = [[{result_path.resolve().as_posix()}]]",
        "local f = io.open(out_path, 'w')",
        "if not f then return end"
    ]
    
    for fn in funcs:
        lines.append(f"pcall(function()")
        lines.append(f"    f:write('{fn}: type=' .. type(ar1.{fn}) .. ', tostring=' .. tostring(ar1.{fn}) .. '\\n')")
        lines.append(f"end)")
        
    lines.append("f:close()")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# DEPRECATED: generate_smoke_config_script (item A)
# Uses experimental guessed TI-baseline arguments.
# Not recommended for AWR2944 until validated.
# Use generate_smoke_from_extracted or generate_smoke_known_awr2944 instead.
# ---------------------------------------------------------------------------

def generate_smoke_config_script(run_id: str, yaml_path: str | None, out_path: Path) -> tuple[str, dict[str, Any]]:
    """[DEPRECATED] Generate a simple static/data/sensor Lua script.
    
    WARNING: This uses experimental guessed TI-baseline arguments that have
    incorrect signatures for AWR2944 (e.g. ChanNAdcConfig takes 11 args, not 10).
    Use generate_smoke_from_extracted() or generate_smoke_known_awr2944() instead.
    """
    out_path_str = out_path.resolve().as_posix()
    prog_path_str = out_path.with_name(out_path.stem + "_progress.jsonl").resolve().as_posix()
    
    cfg = None
    source = "ti_baseline"
    warnings = ["DEPRECATED: This script uses guessed TI-baseline args. Not recommended for AWR2944."]
    
    if yaml_path:
        from awr2944_dca.config import RadarConfig
        try:
            cfg = RadarConfig.from_yaml(Path(yaml_path))
            source = "capture_yaml"
        except Exception as e:
            warnings.append(f"Failed to load YAML {yaml_path}: {e}")
            
    def _get(path: str, default: str) -> str:
        if not cfg:
            return default
        keys = path.split('.')
        val = cfg.model_dump()
        try:
            for k in keys:
                val = val[k]
            if val is None:
                raise KeyError
            return str(val)
        except (KeyError, TypeError):
            warnings.append(f"Missing {path} in YAML, using baseline: {default}")
            return default

    args = {
        "ChanNAdcConfig": "1, 1, 1, 1, 1, 1, 1, 2, 1, 0",
        "LPModConfig": "0, 0",
        "RfInit": "",
        "DataPathConfig": "1, 1, 0",
        "LvdsClkConfig": "1, 1",
        "LVDSLaneConfig": "1, 1, 1, 1, 0, 0, 0, 0",
        "ProfileConfig": f"0, 77.0, 100, 7.0, 60.0, 0, 0, 0, 0, 0, 0, { _get('profile.freq_slope_const', '29.982') }, 0, { _get('profile.num_adc_samples', '256') }, { _get('profile.adc_sample_rate', '10000') }, 0, 0, 30",
        "ChirpConfig_0": "0, 0, 0, 0, 0, 0, 0, 1, 1, 0",
        "FrameConfig": "0, 0, 10, 128, 40.0, 0, 0, 1"
    }
    
    log_fn = _lua_log_progress()
    
    script = f"""\
-- [DEPRECATED] Smoke Config Script (Static/Data/Sensor)
-- WARNING: Uses experimental guessed baselines. Not recommended for AWR2944.
-- config_source: {source}
-- yaml_path: {yaml_path or 'none'}
-- run_id: {run_id}

local progress_path = [[{prog_path_str}]]

{log_fn}

local function safeCall(funcName, argStr, func)
    local ok, ret = pcall(func)
    local err = nil
    if not ok then err = ret; ret = nil end
    logProgress(funcName, ret, ok, err)
    if not ok or (type(ret) == 'number' and ret ~= 0) then
        print("Critical failure in " .. funcName .. ": " .. tostring(err or ret))
        return false
    end
    return true
end

-- 1. Static Config
if not safeCall("ChanNAdcConfig", "{args['ChanNAdcConfig']}", function() return ar1.ChanNAdcConfig({args['ChanNAdcConfig']}) end) then return end
if not safeCall("LPModConfig", "{args['LPModConfig']}", function() return ar1.LPModConfig({args['LPModConfig']}) end) then return end
if not safeCall("RfInit", "{args['RfInit']}", function() return ar1.RfInit({args['RfInit']}) end) then return end
RSTD.Sleep(1000)

-- 2. Data Config
if not safeCall("DataPathConfig", "{args['DataPathConfig']}", function() return ar1.DataPathConfig({args['DataPathConfig']}) end) then return end
if not safeCall("LvdsClkConfig", "{args['LvdsClkConfig']}", function() return ar1.LvdsClkConfig({args['LvdsClkConfig']}) end) then return end
if not safeCall("LVDSLaneConfig", "{args['LVDSLaneConfig']}", function() return ar1.LVDSLaneConfig({args['LVDSLaneConfig']}) end) then return end

-- 3. Sensor Config
if not safeCall("ProfileConfig", "{args['ProfileConfig']}", function() return ar1.ProfileConfig({args['ProfileConfig']}) end) then return end
if not safeCall("ChirpConfig", "{args['ChirpConfig_0']}", function() return ar1.ChirpConfig({args['ChirpConfig_0']}) end) then return end
if not safeCall("FrameConfig", "{args['FrameConfig']}", function() return ar1.FrameConfig({args['FrameConfig']}) end) then return end

print("Smoke config applied successfully.")
"""
    result = {
        "run_id": run_id,
        "source": source,
        "yaml_path": yaml_path,
        "warnings": warnings,
        "args": args
    }
    return script, result


# ---------------------------------------------------------------------------
# Smoke from extracted commands (items C, E, 3)
# ---------------------------------------------------------------------------

_SMOKE_INCLUDE_CATEGORIES = {
    "static_config", "rf_static_config", "data_config",
    "profile_chirp_frame", "test_source",
}

_SMOKE_EXCLUDE_CATEGORIES = {
    "connection", "firmware", "power_rf", "dca_capture", "sensor_control"
}

_SMOKE_CRITICAL_COMMANDS = {
    "ChanNAdcConfig", "LPModConfig", "RfLdoBypassConfig", "SetCalMonFreqLimitConfig",
    "SetRFDeviceConfig", "RfSetCalMonFreqTxPowLimitConfig", "SetApllSynthBWCtlConfig",
    "RfInit", "DataPathConfig", "LVDSLaneConfig", "ProfileConfig", "ChirpConfig", "FrameConfig"
}

def generate_smoke_from_extracted(
    commands: list[AR1Command],
    run_id: str,
    out_path: Path,
    commands_json_path: str = "unknown",
    include_failed: bool = False,
    include_unknown: bool = False,
) -> tuple[str, dict[str, Any]]:
    """Generate a reproducible Lua config script from extracted commands.
    
    Includes standard categories (static, rf_static, data, profile, test_source).
    Excludes connection, firmware, power_rf, and dca_capture.
    Filters out commands that failed in the source log by default
    unless include_failed=True.
    """
    prog_path = out_path.with_name(out_path.stem + "_progress.jsonl")
    res_path = out_path.with_name(out_path.stem + "_result.json")
    
    _atomic_write_manifest(run_id, "smoke_config", out_path, res_path, prog_path)
    
    log_fn = _lua_log_progress()
    res_fn = _lua_result_init_and_save(run_id, res_path.resolve().as_posix())
    safe_fn = _lua_safe_call()
    
    header_lines = [
        f"-- Smoke Config from Extracted Commands",
        f"-- source: {commands_json_path}",
        f"-- run_id: {run_id}",
        f"-- include_failed: {include_failed}",
        f"-- include_unknown: {include_unknown}",
        "",
        f'local run_id = "{run_id}"',
        f'local run_stage = "smoke_config"',
        f'local progress_path = [[{prog_path.resolve().as_posix()}]]',
        "",
        res_fn,
        "",
        log_fn,
        "",
        safe_fn,
        "",
        'print("AWR_RUN_BEGIN run_id=" .. run_id .. " stage=" .. run_stage)',
        "",
    ]
    
    included: list[dict] = []
    skipped: list[dict] = []
    sig_warnings: list[str] = []
    
    cmd_lines: list[str] = []
    for cmd in commands:
        # Category filter
        allowed_cats = set(_SMOKE_INCLUDE_CATEGORIES)
        if include_unknown:
            allowed_cats.add("unknown")
            
        if cmd.normalized_category not in allowed_cats:
            skipped.append({"function": cmd.function_name, "reason": f"category={cmd.normalized_category}"})
            continue
            
        # Failed filter
        if cmd.observed_status == "failed" and not include_failed:
            skipped.append({"function": cmd.function_name, "reason": f"observed_status=failed ({cmd.observed_error_type})"})
            continue
        
        # Signature check
        sig_warnings.extend(validate_command_signature(cmd))
        
        # Generate
        status_comment = ""
        if cmd.observed_status == "failed":
            status_comment = f" -- WARNING: observed_status=failed in source log ({cmd.observed_error_type})"
        elif cmd.observed_status == "unknown":
            status_comment = " -- observed_status=unknown in source log"
            
        cmd_lines.append(f"-- {cmd.timestamp} line {cmd.line_number}{status_comment}")
        is_critical = "true" if cmd.function_name in _SMOKE_CRITICAL_COMMANDS else "false"
        cmd_lines.append(f'if not safeCall("{cmd.function_name}", function() return ar1.{cmd.function_name}({cmd.args_text}) end, {is_critical}) then return end')
        cmd_lines.append("")
        
        included.append({
            "function": cmd.function_name,
            "args_preview": cmd.args_text[:80],
            "observed_status": cmd.observed_status,
        })
    
    cmd_lines.append('print("Smoke config from extracted commands completed successfully.")')
    cmd_lines.append('result.success = true')
    cmd_lines.append('saveResult()')
    cmd_lines.append('print("AWR_RUN_END run_id=" .. run_id .. " stage=" .. run_stage .. " success=true")')
    
    script = "\n".join(header_lines + cmd_lines)
    
    result = {
        "run_id": run_id,
        "included_commands": included,
        "skipped_commands": skipped,
        "signature_warnings": sig_warnings,
    }
    
    return script, result


# ---------------------------------------------------------------------------
# Frozen GUI-derived AWR2944 commands — LITERAL REPLAY ONLY
# ---------------------------------------------------------------------------
#
# These are the EXACT strings emitted by mmWave Studio 3.1.4.4 GUI for AWR2944.
# DO NOT convert units, change values, reformat, or reconstruct these.
# They are frozen golden strings. Any modification will break the radar.
#
# Known bad patterns that MUST NOT appear:
#   SetCalMonFreqLimitConfig(760   — GUI uses 76/81 (x10 GHz), not 760/810
#   RfSetCalMonFreqTxPowLimitConfig(760  — same issue
#   DataPathConfig(1, 1, 0)        — GUI uses bitmask 513, 1216644097
#   LPModConfig(0, 1)              — GUI uses (0, 0)
#   FrameConfig(0, 0, 8, 128, 40, 0, 0)  — last arg is 1, not 0
#   ProfileConfig(0, 77, ..., 29.982     — GUI uses 13 zeros before 29.982
#

@dataclass
class ValidatedFrozenConfig:
    name: str
    validation_label: str
    firmware_run_id: str
    config_run_id: str
    git_commit: str
    commands: list[str]


VALIDATED_AWR2944_SMOKE_V0 = ValidatedFrozenConfig(
    name="awr2944_smoke_v0",
    validation_label="First clean positive post-connection validation",
    firmware_run_id="da0ce6de",
    config_run_id="3ecac52f",
    git_commit="5786958c04ade2c8e43b26364d8ce5d8643819dc",
    commands=[
        "ChanNAdcConfig(1, 1, 0, 0, 1, 1, 0, 0, 2, 0, 0)",
        "LPModConfig(0, 0)",
        "RfLdoBypassConfig(0x0)",
        "SetCalMonFreqLimitConfig(76,81,0)",
        "SetRFDeviceConfig(5, 0, 0, 0, 0, 0, 0)",
        "RfSetCalMonFreqTxPowLimitConfig(76, 76, 76, 76, 81, 81, 81, 81, 0, 0, 0, 0,0)",
        "SetApllSynthBWCtlConfig(1, 4, 3, 9, 18, 1, 4)",
        "RfInit()",
        "DataPathConfig(513, 1216644097, 0)",
        "LVDSLaneConfig(0, 1, 0, 0, 0, 1, 0, 0)",
        "ProfileConfig(0, 77, 100, 6, 60, 0, 0, 0, 0, 0, 0, 0, 0, 29.982, 0, 256, 10000, 2216755200, 0, 30, 0, 0, 0)",
        "ChirpConfig(0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0)",
        "FrameConfig(0, 0, 8, 128, 40, 0, 1)",
    ]
)

# Known bad patterns — used for regression verification
_KNOWN_BAD_PATTERNS = [
    "SetCalMonFreqLimitConfig(760",
    "RfSetCalMonFreqTxPowLimitConfig(760",
    "DataPathConfig(1, 1, 0)",
    "LPModConfig(0, 1)",
    "FrameConfig(0, 0, 8, 128, 40, 0, 0)",
    "ProfileConfig(0, 77, 100, 6, 60, 0, 0, 0, 0, 0, 0, 29.982",
]


def _parse_frozen_command(cmd_line: str) -> tuple[str, str]:
    """Parse 'FuncName(args)' into ('FuncName', 'args')."""
    paren = cmd_line.index("(")
    func = cmd_line[:paren]
    args = cmd_line[paren + 1:].rstrip(")")
    return func, args


def generate_smoke_known_awr2944(run_id: str, out_path: Path) -> GeneratedScript:
    """Generate a smoke config script using frozen GUI-derived AWR2944 commands.
    
    These are LITERAL copies of what mmWave Studio 3.1.4.4 emits for AWR2944.
    The argument strings are used verbatim  no conversion, no defaults.
    """
    prog_path = out_path.with_name(out_path.stem + "_progress.jsonl")
    res_path = out_path.with_name(out_path.stem + "_result.json")
    
    _atomic_write_manifest(run_id, "smoke_config", out_path, res_path, prog_path)
    
    log_fn = _lua_log_progress()
    res_fn = _lua_result_init_and_save(run_id, res_path.resolve().as_posix())
    safe_fn = _lua_safe_call()
    
    header = [
        f"-- GUI-Derived AWR2944 Smoke Config (FROZEN LITERAL REPLAY)",
        f"-- These are exact GUI-emitted commands. DO NOT modify arguments.",
        f"-- source: frozen_gui_derived_awr2944",
        f"-- replay_validated: true",
        f"-- run_id: {run_id}",
        "",
        f'local run_id = "{run_id}"',
        f'local run_stage = "smoke_config"',
        f'local progress_path = [[{prog_path.resolve().as_posix()}]]',
        "",
        res_fn,
        "",
        log_fn,
        "",
        safe_fn,
        "",
        'print("AWR_RUN_BEGIN run_id=" .. run_id .. " stage=" .. run_stage)',
        "",
    ]
    
    body = []
    commands_meta: list[dict] = []
    for cmd_line in VALIDATED_AWR2944_SMOKE_V0.commands:
        func, args = _parse_frozen_command(cmd_line)
        
        is_critical = "true" if func in _SMOKE_CRITICAL_COMMANDS else "false"
        body.append(f'if not safeCall("{func}", function() return ar1.{cmd_line} end, {is_critical}) then return end')
        
        # Add sleep after RfInit
        if func == "RfInit":
            body.append("RSTD.Sleep(1000)")
        body.append("")
        
        commands_meta.append({"function": func, "frozen_args": args})
    
    body.append('print("GUI-derived AWR2944 smoke config completed successfully.")')
    body.append('result.success = true')
    body.append('saveResult()')
    body.append('print("AWR_RUN_END run_id=" .. run_id .. " stage=" .. run_stage .. " success=true")')
    
    script = "\n".join(header + body)
    
    result = {
        "run_id": run_id,
        "source": "frozen_gui_derived_awr2944",
        "replay_validated": True,
        "validation_label": VALIDATED_AWR2944_SMOKE_V0.validation_label,
        "warnings": [],
        "commands": commands_meta,
    }
    return GeneratedScript(
        script=script,
        run_id=run_id,
        lua_path=out_path,
        result_path=res_path,
        progress_path=prog_path,
        dofile=f"dofile([[{out_path.resolve()}]])",
        metadata=result
    )
