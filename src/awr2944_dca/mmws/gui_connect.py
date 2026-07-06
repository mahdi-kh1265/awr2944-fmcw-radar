"""GUI-button automation for the mmWave Studio Connection tab.

Uses pywinauto (UIA backend) to click actual GUI controls, reproducing the
exact manual flow that reliably connects to the AWR2944 hardware.

Architecture rationale:
  Lua ar1.Connect() is NOT equivalent to the GUI RS232 Connect button.
  ar1.Connect() can return 0 with invalid device identity (0x0/TEST/QM/SOP:Inv)
  or return 3 after a valid manual GUI Set(1). The internal GUI methods
  (m_btnRS232Conct_Click, iRs232ConnectDisconnect, ConnectBegin, iPostConnect)
  are present in AR1xController.ConnectTab but are NOT exposed through the
  ar1 Lua table.  Therefore, GUI-button automation is the only reliable path.
"""

from __future__ import annotations

import ctypes
import json
import re
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional


# ---------------------------------------------------------------------------
# Elevation detection
# ---------------------------------------------------------------------------

def _is_admin() -> bool:
    """Return True if the current process has administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0  # type: ignore[attr-defined]
    except Exception:
        return False


def _is_process_elevated(pid: int) -> bool:
    """Best-effort check if a process is running elevated.

    If we cannot open the process, we assume it is elevated (conservative).
    """
    import ctypes.wintypes
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    TOKEN_QUERY = 0x0008

    kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
    advapi32 = ctypes.windll.advapi32  # type: ignore[attr-defined]

    proc_handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not proc_handle:
        # Cannot open process — likely elevated and we are not
        return True

    try:
        token_handle = ctypes.wintypes.HANDLE()
        if not advapi32.OpenProcessToken(proc_handle, TOKEN_QUERY, ctypes.byref(token_handle)):
            return True  # conservative

        try:
            # TokenElevation = 20
            elevation = ctypes.c_uint(0)
            ret_len = ctypes.c_uint(0)
            advapi32.GetTokenInformation(
                token_handle, 20, ctypes.byref(elevation),
                ctypes.sizeof(elevation), ctypes.byref(ret_len)
            )
            return elevation.value != 0
        finally:
            kernel32.CloseHandle(token_handle)
    finally:
        kernel32.CloseHandle(proc_handle)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ControlInfo:
    """Snapshot of a discovered GUI control."""
    name: str
    class_name: str
    control_type: str
    auto_id: str
    text: str
    rect: tuple[int, int, int, int]
    depth: int = 0


@dataclass
class ConnectionControls:
    """References to key Connection tab controls."""
    frequency_radio: Any = None       # m_RadioBtn77GHzRadarDev
    device_variant_group: Any = None  # m_grpDeviceVariantTypes
    device_variant_radio: Any = None  # AWR29xx/XWR2944 radio/button inside group
    device_variant_candidates: list[tuple[str, str]] = field(default_factory=list)  # [(auto_id, text), ...]
    set_button: Any = None            # m_btnSetSop
    com_combo: Any = None             # m_cboComPort
    baud_combo: Any = None            # m_cboBaudRate
    rs232_connect_button: Any = None  # m_btnConnect
    refresh_ports_button: Any = None  # m_btnRefreshPorts
    device_status_label: Any = None
    rs232_status_label: Any = None    # m_lblRS232UARTConnectivityStatus
    spi_status_label: Any = None      # m_lblSPIConnectivityStatus
    output_log: Any = None
    output_document: Any = None       # frmOutput -> m_ConsoleText
    radarapi_window: Any = None       # frmAR1Main
    missing: list[str] = field(default_factory=list)

    @property
    def all_required_found(self) -> bool:
        """True if all controls needed for click-flow are present."""
        return (
            self.set_button is not None
            and self.rs232_connect_button is not None
        )


@dataclass
class ClickFlowResult:
    """Result from a GUI click-flow run."""
    status: str
    device_status_text: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass
class WindowCandidate:
    """A candidate window found during enumeration."""
    pid: int
    title: str
    process_name: str
    exe_path: str
    rect_str: str
    matched: bool
    attach_ok: bool
    failure_reason: str


# ---------------------------------------------------------------------------
# Attach to mmWave Studio — robust enumeration
# ---------------------------------------------------------------------------

_MMWAVE_TITLE_PATTERNS = [
    re.compile(r"mmwave\s*studio", re.IGNORECASE),
    re.compile(r"mmwave", re.IGNORECASE),
]


def _enumerate_uia_windows(
    verbose_log: Callable[[str], None] | None = None,
) -> list[WindowCandidate]:
    """Enumerate all top-level UIA windows and classify candidates."""
    vlog = verbose_log or (lambda s: None)
    candidates: list[WindowCandidate] = []

    try:
        from pywinauto import Desktop  # type: ignore[import-untyped]
        desktop = Desktop(backend="uia")
        windows = desktop.windows()
    except Exception as e:
        vlog(f"Desktop enumeration failed: {e}")
        return candidates

    for w in windows:
        try:
            pid = w.process_id()
            title = w.window_text() or ""
        except Exception:
            continue

        # Get process info
        proc_name = ""
        exe_path = ""
        try:
            import psutil
            proc = psutil.Process(pid)
            proc_name = proc.name()
            exe_path = proc.exe()
        except Exception:
            pass

        # Get rect
        rect_str = "(?,?,?,?)"
        try:
            r = w.rectangle()
            rect_str = f"(L{r.left},T{r.top},R{r.right},B{r.bottom})"
        except Exception:
            pass

        # Check if this looks like mmWave Studio
        matched = False
        for pat in _MMWAVE_TITLE_PATTERNS:
            if pat.search(title):
                matched = True
                break
        if not matched and proc_name.lower() in ("mmwavestudio.exe",):
            matched = True

        candidates.append(WindowCandidate(
            pid=pid, title=title, process_name=proc_name,
            exe_path=exe_path, rect_str=rect_str,
            matched=matched, attach_ok=False, failure_reason="",
        ))

    vlog(f"Enumerated {len(candidates)} top-level windows, "
         f"{sum(1 for c in candidates if c.matched)} matched mmWave Studio")
    return candidates


def _write_window_diagnostics(
    candidates: list[WindowCandidate],
    probe_dir: Path,
    verbose_log: Callable[[str], None] | None = None,
):
    """Write diagnostics file with all discovered windows."""
    vlog = verbose_log or (lambda s: None)
    diag_path = probe_dir / "gui_connect_windows.txt"
    probe_dir.mkdir(parents=True, exist_ok=True)

    with open(diag_path, "w", encoding="utf-8") as f:
        f.write(f"mmWave Studio Window Enumeration\n")
        f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Python is admin: {_is_admin()}\n")
        f.write("=" * 100 + "\n\n")
        for c in candidates:
            marker = ">>> MATCH <<<" if c.matched else ""
            f.write(
                f"PID={c.pid}  title={c.title!r}  process={c.process_name!r}  "
                f"exe={c.exe_path!r}  rect={c.rect_str}  "
                f"matched={c.matched}  attach_ok={c.attach_ok}  "
                f"failure={c.failure_reason!r}  {marker}\n"
            )

    vlog(f"Wrote window diagnostics to {diag_path}")


def attach_mmwave_studio(
    pid: int | None = None,
    title_regex: str | None = None,
    probe_dir: Path | None = None,
    verbose_log: Callable[[str], None] | None = None,
):
    """Attach to a running mmWaveStudio.exe via pywinauto UIA backend.

    Attach strategies (in order):
    1. If pid is given, attach directly by PID.
    2. If title_regex is given, enumerate UIA windows and match.
    3. Otherwise, enumerate UIA windows and match known mmWave Studio patterns.

    Returns (Application, top_window).
    Raises RuntimeError with descriptive messages on failure.
    Always writes ti/probe_logs/gui_connect_windows.txt on failure.
    """
    vlog = verbose_log or (lambda s: None)
    if probe_dir is None:
        probe_dir = Path("ti") / "probe_logs"
    probe_dir.mkdir(parents=True, exist_ok=True)

    try:
        from pywinauto import Application  # type: ignore[import-untyped]
    except ImportError:
        raise RuntimeError(
            "pywinauto is not installed. Install with: "
            "python -m pip install -e \".[automation]\""
        )

    target_pid: int | None = pid

    # --- Strategy 1: Direct PID ---
    if target_pid is not None:
        vlog(f"Attaching directly by PID={target_pid}")
        if _is_process_elevated(target_pid) and not _is_admin():
            raise RuntimeError(
                "mmWave Studio appears to be running as administrator. "
                "Re-run this PowerShell terminal as administrator, then retry."
            )
        try:
            app = Application(backend="uia").connect(process=target_pid, timeout=10)
            main_window = app.top_window()
            vlog(f"Attached to PID={target_pid}: {main_window.window_text()!r}")
            # Always write diagnostics
            candidates = _enumerate_uia_windows(verbose_log=vlog)
            for c in candidates:
                if c.pid == target_pid:
                    c.matched = True
                    c.attach_ok = True
            _write_window_diagnostics(candidates, probe_dir, vlog)
            return app, main_window
        except Exception as e:
            # Write diagnostics on failure too
            candidates = _enumerate_uia_windows(verbose_log=vlog)
            _write_window_diagnostics(candidates, probe_dir, vlog)
            raise RuntimeError(
                f"UIA attach failed for PID={target_pid}: {e}. "
                "Verify the PID is correct and mmWave Studio is running."
            )

    # --- Strategy 2/3: Enumerate windows ---
    candidates = _enumerate_uia_windows(verbose_log=vlog)

    # Apply title_regex filter if given
    if title_regex is not None:
        pat = re.compile(title_regex, re.IGNORECASE)
        for c in candidates:
            c.matched = bool(pat.search(c.title))
        vlog(f"Applied title_regex={title_regex!r}, "
             f"{sum(1 for c in candidates if c.matched)} matched")

    matched = [c for c in candidates if c.matched]

    if not matched:
        _write_window_diagnostics(candidates, probe_dir, vlog)
        raise RuntimeError(
            "Could not find mmWave Studio window. "
            "See ti/probe_logs/gui_connect_windows.txt for all discovered windows. "
            "Try: --pid <PID> or --title-regex \".*mmWave.*\""
        )

    # Try to attach to each matched candidate
    last_error = ""
    for c in matched:
        vlog(f"Trying PID={c.pid} title={c.title!r}")

        # Elevation check
        if _is_process_elevated(c.pid) and not _is_admin():
            c.failure_reason = "elevation mismatch"
            vlog(f"  Elevation mismatch for PID={c.pid}")
            continue

        try:
            app = Application(backend="uia").connect(process=c.pid, timeout=10)
            main_window = app.top_window()
            c.attach_ok = True
            vlog(f"  Attached to PID={c.pid}: {main_window.window_text()!r}")
            _write_window_diagnostics(candidates, probe_dir, vlog)
            return app, main_window
        except Exception as e:
            c.failure_reason = str(e)
            last_error = str(e)
            vlog(f"  Attach failed for PID={c.pid}: {e}")

    # All candidates failed
    _write_window_diagnostics(candidates, probe_dir, vlog)

    # Check if it's an elevation issue across all candidates
    all_elevation = all(c.failure_reason == "elevation mismatch" for c in matched)
    if all_elevation:
        raise RuntimeError(
            "mmWave Studio appears to be running as administrator. "
            "Re-run this PowerShell terminal as administrator, then retry."
        )

    raise RuntimeError(
        f"Could not attach to mmWave Studio window. "
        f"Found {len(matched)} candidate(s) but UIA attach failed. "
        f"Last error: {last_error}. "
        f"See ti/probe_logs/gui_connect_windows.txt for details. "
        f"Try: --pid <PID>"
    )


# ---------------------------------------------------------------------------
# Control tree dump — deep, targeting RadarAPI subtree
# ---------------------------------------------------------------------------

def dump_control_tree(
    window,
    output_path: Path,
    max_depth: int = 15,
    verbose_log: Callable[[str], None] | None = None,
) -> int:
    """Recursively dump the control tree to a text file.

    Targets known child windows specifically:
    - frmMain (top window)
    - frmAR1Main / RadarAPI (Connection tab controls)
    - frmOutput (Output log)
    - frmLuaShell (Lua Shell)

    Returns the total number of controls dumped.
    """
    vlog = verbose_log or (lambda s: None)
    count = 0

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"mmWave Studio Control Tree Dump\n")
        f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        try:
            f.write(f"Window: {window.window_text()!r}\n")
            f.write(f"AutoID: {window.automation_id()!r}\n")
        except Exception:
            pass
        f.write(f"Max depth: {max_depth}\n")
        f.write("=" * 100 + "\n\n")

        def _dump_recursive(ctrl, depth: int = 0):
            nonlocal count
            if depth > max_depth:
                return
            indent = "  " * depth
            try:
                class_name = ctrl.class_name()
            except Exception:
                class_name = "<unknown>"
            try:
                ctrl_type = ctrl.control_type()
            except Exception:
                ctrl_type = "<unknown>"
            try:
                auto_id = ctrl.automation_id()
            except Exception:
                auto_id = ""
            try:
                text = ctrl.window_text()
                if len(text) > 200:
                    text = text[:200] + "..."
            except Exception:
                text = ""
            try:
                rect = ctrl.rectangle()
                rect_str = f"(L{rect.left},T{rect.top},R{rect.right},B{rect.bottom})"
            except Exception:
                rect_str = "(?,?,?,?)"

            line = (
                f"{indent}[{ctrl_type}] class={class_name!r} "
                f"auto_id={auto_id!r} text={text!r} rect={rect_str}\n"
            )
            f.write(line)
            count += 1

            try:
                children = ctrl.children()
            except Exception:
                children = []

            for child in children:
                _dump_recursive(child, depth + 1)

        # Dump full tree from top window
        f.write("--- FULL TREE (from top window) ---\n\n")
        _dump_recursive(window)

        # Also specifically dump known child windows by auto_id
        known_children = [
            ("frmAR1Main", "RadarAPI"),
            ("frmOutput", "Output"),
            ("frmLuaShell", "Lua Shell"),
        ]
        for auto_id, label in known_children:
            f.write(f"\n\n--- SUBTREE: {label} (auto_id={auto_id!r}) ---\n\n")
            try:
                child_win = window.child_window(auto_id=auto_id)
                if child_win.exists():
                    _dump_recursive(child_win.wrapper_object(), 0)
                else:
                    f.write(f"  [NOT FOUND]\n")
            except Exception as e:
                f.write(f"  [ERROR: {e}]\n")

    vlog(f"Dumped {count} controls to {output_path}")
    return count


# ---------------------------------------------------------------------------
# Control discovery — direct auto_id lookup (no control_type filtering)
# ---------------------------------------------------------------------------

# Known auto_ids from the real mmWave Studio 3.1.4.4 control tree.
# WindowsForms controls report control_type as <unknown>, so we NEVER filter
# by control_type.  Instead, we search by exact auto_id.
_KNOWN_CONTROLS: dict[str, tuple[str, str]] = {
    # (auto_id, human label)
    "m_RadioBtn77GHzRadarDev": ("frequency_radio", "77 GHz radio button"),
    "m_btnSetSop":             ("set_button", "Set(1) button"),
    "m_cboComPort":            ("com_combo", "COM port selector"),
    "m_cboBaudRate":           ("baud_combo", "Baud rate selector"),
    "m_btnConnect":            ("rs232_connect_button", "RS232 Connect button"),
    "m_btnRefreshPorts":       ("refresh_ports_button", "Refresh Ports button"),
    "m_lblRS232UARTConnectivityStatus": ("rs232_status_label", "RS232 status label"),
    "m_lblSPIConnectivityStatus":       ("spi_status_label", "SPI status label"),
}


def _find_by_auto_id(
    root,
    auto_id: str,
    verbose_log: Callable[[str], None] | None = None,
) -> Any | None:
    """Find a control by automation_id using child_window().

    Returns the wrapper object or None.
    """
    vlog = verbose_log or (lambda s: None)
    try:
        child = root.child_window(auto_id=auto_id)
        if child.exists(timeout=2):
            wrapper = child.wrapper_object()
            try:
                text = wrapper.window_text()[:80]
            except Exception:
                text = "<no text>"
            vlog(f"  Found auto_id={auto_id!r}: text={text!r}")
            return wrapper
    except Exception as e:
        vlog(f"  Search for auto_id={auto_id!r} failed: {e}")
    return None


def inspect_connection_tab(
    window,
    verbose_log: Callable[[str], None] | None = None,
) -> ConnectionControls:
    """Identify key Connection tab controls by exact auto_id.

    Uses child_window(auto_id=...) directly instead of gathering all controls
    and filtering by control_type.  WindowsForms controls report control_type
    as <unknown>, making type-based filtering useless.

    Search order:
    1. frmAR1Main (RadarAPI child window) — primary search root
    2. Top window — fallback if RadarAPI not found

    Does NOT click anything.
    """
    vlog = verbose_log or (lambda s: None)
    result = ConnectionControls()

    # --- Find the RadarAPI child window ---
    radarapi_root = None
    try:
        radarapi_win = window.child_window(auto_id="frmAR1Main")
        if radarapi_win.exists(timeout=3):
            radarapi_root = radarapi_win.wrapper_object()
            result.radarapi_window = radarapi_root
            vlog(f"Found RadarAPI window (frmAR1Main): {radarapi_root.window_text()!r}")
        else:
            vlog("frmAR1Main not found by auto_id, falling back to title search")
            try:
                radarapi_win = window.child_window(title="RadarAPI")
                if radarapi_win.exists(timeout=2):
                    radarapi_root = radarapi_win.wrapper_object()
                    result.radarapi_window = radarapi_root
                    vlog("Found RadarAPI window by title")
            except Exception:
                pass
    except Exception as e:
        vlog(f"RadarAPI window search error: {e}")

    # --- Find the Output document ---
    try:
        output_win = window.child_window(auto_id="frmOutput")
        if output_win.exists(timeout=2):
            try:
                doc = output_win.child_window(auto_id="m_ConsoleText")
                if doc.exists(timeout=2):
                    result.output_document = doc.wrapper_object()
                    vlog("Found Output document (m_ConsoleText)")
            except Exception:
                pass
    except Exception:
        pass

    # --- Search root: RadarAPI preferred, fallback to top window ---
    search_root = radarapi_root if radarapi_root is not None else window
    vlog(f"Control search root: {'frmAR1Main' if radarapi_root else 'top_window'}")

    # --- Direct auto_id lookups for known controls ---
    for auto_id, (attr_name, label) in _KNOWN_CONTROLS.items():
        vlog(f"Searching for {label} (auto_id={auto_id!r})")
        ctrl = _find_by_auto_id(search_root, auto_id, vlog)
        if ctrl is not None:
            setattr(result, attr_name, ctrl)
        else:
            # Fallback: search from top window if we were searching RadarAPI
            if search_root is not window:
                vlog(f"  Retrying from top window...")
                ctrl = _find_by_auto_id(window, auto_id, vlog)
                if ctrl is not None:
                    setattr(result, attr_name, ctrl)

    # --- Device Variant group discovery ---
    vlog("Searching for Device Variant group (m_grpDeviceVariantTypes)")
    dv_group = _find_by_auto_id(search_root, "m_grpDeviceVariantTypes", vlog)
    if dv_group is None and search_root is not window:
        dv_group = _find_by_auto_id(window, "m_grpDeviceVariantTypes", vlog)
    if dv_group is not None:
        result.device_variant_group = dv_group
        vlog("Scanning Device Variant group children for AWR29xx/XWR2944...")
        _AWR29_PATTERNS = ["awr29", "xwr29", "2944", "29xx"]
        try:
            for child in dv_group.descendants():
                try:
                    child_auto_id = child.automation_id() if hasattr(child, 'automation_id') else ""
                    child_text = child.window_text()[:120] if child.window_text() else ""
                except Exception:
                    continue
                combined = (child_auto_id + " " + child_text).lower()
                result.device_variant_candidates.append((child_auto_id, child_text))
                vlog(f"  Device Variant child: auto_id={child_auto_id!r} text={child_text!r}")
                # Match AWR29xx / XWR2944 candidate
                if result.device_variant_radio is None:
                    if any(pat in combined for pat in _AWR29_PATTERNS):
                        result.device_variant_radio = child
                        vlog(f"  >>> MATCHED device variant: auto_id={child_auto_id!r} text={child_text!r}")
        except Exception as e:
            vlog(f"  Error scanning Device Variant group: {e}")
    else:
        vlog("  Device Variant group (m_grpDeviceVariantTypes) NOT FOUND")

    # --- Device Status label (exclude m_lblStatus which is just a header) ---
    # m_lblStatus contains 'FTDI Connectivity Status:' — NOT the device identity.
    for device_status_id in [
        "m_lblDeviceStatus", "lblDeviceStatus",
        "m_txtDeviceStatus", "DeviceStatus",
    ]:
        if result.device_status_label is not None:
            break
        vlog(f"Searching for Device Status label (auto_id={device_status_id!r})")
        ctrl = _find_by_auto_id(search_root, device_status_id, vlog)
        if ctrl is None and search_root is not window:
            ctrl = _find_by_auto_id(window, device_status_id, vlog)
        if ctrl is not None:
            result.device_status_label = ctrl

    # --- Build missing list ---
    if result.set_button is None:
        result.missing.append("Set(1) button (m_btnSetSop)")
    if result.rs232_connect_button is None:
        result.missing.append("RS232 Connect button (m_btnConnect)")
    if result.frequency_radio is None:
        result.missing.append("77 GHz radio button (m_RadioBtn77GHzRadarDev)")
    if result.device_variant_radio is None:
        result.missing.append("Device variant AWR29xx/XWR2944 (in m_grpDeviceVariantTypes)")
    if result.com_combo is None:
        result.missing.append("COM port selector (m_cboComPort) (optional)")
    if result.baud_combo is None:
        result.missing.append("Baud rate selector (m_cboBaudRate) (optional)")
    if result.device_status_label is None:
        result.missing.append("Device Status label (optional)")
    if result.rs232_status_label is None:
        result.missing.append("RS232 status label (m_lblRS232UARTConnectivityStatus) (optional)")

    return result


# ---------------------------------------------------------------------------
# Screenshot helper
# ---------------------------------------------------------------------------

def _take_screenshot(window, output_path: Path, verbose_log: Callable[[str], None] | None = None):
    """Capture a screenshot of the mmWave Studio window."""
    vlog = verbose_log or (lambda s: None)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        img = window.capture_as_image()
        img.save(str(output_path))
        vlog(f"Screenshot saved: {output_path}")
    except Exception as e:
        vlog(f"Screenshot failed: {e}")


# ---------------------------------------------------------------------------
# Device status reader
# ---------------------------------------------------------------------------

def read_device_status(
    window,
    controls: ConnectionControls | None = None,
    verbose_log: Callable[[str], None] | None = None,
    after_monotonic: float | None = None,
) -> dict[str, Any]:
    """Read the Device Status from Output document text.

    Primary source: Output document (m_ConsoleText) — search for
    'Device Status : AWR2944/GP/...' lines.

    The GUI label m_lblStatus contains 'FTDI Connectivity Status:' which
    is NOT the device identity.  Therefore we rely on Output text.

    Returns a dict with keys:
      raw_text, valid, device, type, sop, es, rs232_status
    """
    vlog = verbose_log or (lambda s: None)

    if controls is None:
        controls = inspect_connection_tab(window, verbose_log=vlog)

    raw = ""

    # Primary: Output document (m_ConsoleText)
    if controls.output_document is not None:
        vlog("Reading Output document (m_ConsoleText) for Device Status")
        try:
            doc_text = controls.output_document.window_text()
            # Search from bottom for most recent Device Status line
            for line in reversed(doc_text.splitlines()):
                if "Device Status" in line and "/" in line:
                    raw = line.strip()
                    vlog(f"Found Device Status in Output: {raw!r}")
                    break
        except Exception as e:
            vlog(f"Output document read failed: {e}")

    # Fallback: Device Status label (if it actually has device identity)
    if not raw and controls.device_status_label is not None:
        try:
            label_text = controls.device_status_label.window_text()
            # Only use if it actually looks like a device status, not a header
            if label_text and ("AWR" in label_text or "XWR" in label_text) and "/" in label_text:
                raw = label_text
                vlog(f"Found Device Status via label: {raw!r}")
            else:
                vlog(f"Device Status label text is not device identity: {label_text!r}")
        except Exception:
            pass

    # Read RS232 status separately
    rs232_status = ""
    if controls.rs232_status_label is not None:
        try:
            rs232_status = controls.rs232_status_label.window_text()
        except Exception:
            pass

    vlog(f"Device Status raw text: {raw!r}")
    vlog(f"RS232 status: {rs232_status!r}")

    result: dict[str, Any] = {
        "raw_text": raw,
        "valid": False,
        "device": None,
        "type": None,
        "sop": None,
        "es": None,
        "rs232_status": rs232_status,
    }

    if not raw:
        return result

    # Parse: "AWR2944/GP/ASIL-B/SOP:2/ES:2.0" or "Device Status : AWR2944/..."
    text = raw
    if ":" in text and "Device Status" in text:
        text = text.split(":", 1)[1].strip()

    parts = [p.strip() for p in text.split("/")]
    for p in parts:
        if p.startswith("AWR") or p.startswith("XWR"):
            result["device"] = p
        elif p in ("GP", "QM"):
            result["type"] = p
        elif p.startswith("SOP:"):
            result["sop"] = p.replace("SOP:", "")
        elif p.startswith("ES:"):
            result["es"] = p.replace("ES:", "")

    # Valid = AWR2944 + GP + SOP:2
    result["valid"] = (
        result["device"] is not None
        and "2944" in (result["device"] or "")
        and result["type"] == "GP"
        and result["sop"] == "2"
    )

    return result


# ---------------------------------------------------------------------------
# JSONL progress helper
# ---------------------------------------------------------------------------

class ProgressLogger:
    """Write JSONL progress entries."""

    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        # Truncate/create
        with open(path, "w", encoding="utf-8") as f:
            pass

    def log(self, step: str, detail: str | None = None, **extra: Any):
        entry: dict[str, Any] = {
            "step": step,
            "timestamp": time.strftime("%H:%M:%S"),
            "monotonic": round(time.monotonic(), 3),
        }
        if detail is not None:
            entry["detail"] = detail
        entry.update(extra)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------------------
# Click flow
# ---------------------------------------------------------------------------

def click_flow(
    window,
    com_port: str = "COM6",
    baud: int = 115200,
    probe_dir: Path | None = None,
    dry_run: bool = False,
    verbose_log: Callable[[str], None] | None = None,
) -> ClickFlowResult:
    """Execute the full GUI click sequence for Connection tab.

    Steps:
    1. Discover controls (same logic as inspect)
    2. Select 77 GHz frequency band
    3. Select xWR2944/AWR29xx device variant
    4. Click Set(1) button
    5. Wait 5 seconds for SOP
    6. Set COM port
    7. Set baud rate
    8. Click RS232 Connect button
    9. Poll Device Status for valid identity (up to 15s)

    If dry_run=True, identifies controls and prints what WOULD happen but
    does NOT click anything.
    """
    vlog = verbose_log or (lambda s: None)

    if probe_dir is None:
        probe_dir = Path("ti") / "probe_logs"
    probe_dir.mkdir(parents=True, exist_ok=True)

    progress = ProgressLogger(probe_dir / "gui_connect_click_flow_progress.jsonl")
    controls_path = probe_dir / "gui_connect_controls.txt"

    flow_start = time.monotonic()
    progress.log("click_flow_started", f"com={com_port} baud={baud} dry_run={dry_run}")

    # --- Step 0: Screenshot before ---
    _take_screenshot(window, probe_dir / "gui_connect_before_click_flow.png", vlog)

    # --- Step 1: Discover controls ---
    progress.log("discovering_controls")
    dump_control_tree(window, controls_path, verbose_log=vlog)
    controls = inspect_connection_tab(window, verbose_log=vlog)

    # Report findings
    for attr in ["frequency_radio", "device_variant_group", "device_variant_radio",
                 "set_button", "refresh_ports_button",
                 "com_combo", "baud_combo", "rs232_connect_button",
                 "rs232_status_label", "spi_status_label",
                 "device_status_label", "output_document", "radarapi_window"]:
        ctrl = getattr(controls, attr)
        if ctrl is not None:
            try:
                text = ctrl.window_text()[:80]
                auto_id = ctrl.automation_id() if hasattr(ctrl, "automation_id") else ""
                progress.log(f"found_{attr}", f"text={text!r} auto_id={auto_id!r}")
            except Exception:
                progress.log(f"found_{attr}", "present")
        else:
            progress.log(f"missing_{attr}")

    # Check required controls
    if controls.set_button is None:
        progress.log("CONTROL_NOT_FOUND", "Set(1) button not found")
        return ClickFlowResult(
            status="CONTROL_NOT_FOUND",
            error="Set(1) button not found in control tree. "
                  "Check ti/probe_logs/gui_connect_controls.txt for the full dump.",
        )

    if controls.rs232_connect_button is None:
        progress.log("CONTROL_NOT_FOUND", "RS232 Connect button not found")
        return ClickFlowResult(
            status="CONTROL_NOT_FOUND",
            error="RS232 Connect button not found in control tree. "
                  "Check ti/probe_logs/gui_connect_controls.txt for the full dump.",
        )

    # --- Check device variant is found (required for AWR2944) ---
    if controls.device_variant_radio is None:
        progress.log("CONTROL_NOT_FOUND", "Device variant AWR29xx/XWR2944 not found")
        if controls.device_variant_candidates:
            for aid, txt in controls.device_variant_candidates:
                progress.log("device_variant_candidate", f"auto_id={aid!r} text={txt!r}")
        return ClickFlowResult(
            status="CONTROL_NOT_FOUND",
            error="Device variant AWR29xx/XWR2944 not found in m_grpDeviceVariantTypes. "
                  "Check ti/probe_logs/gui_connect_controls.txt and progress JSONL for candidates.",
        )

    # --- DRY RUN ---
    if dry_run:
        actions = []
        if controls.frequency_radio is not None:
            actions.append("WOULD click 77 GHz radio button (m_RadioBtn77GHzRadarDev)")
        else:
            actions.append("WOULD SKIP 77 GHz selection (control not found)")

        try:
            dv_text = controls.device_variant_radio.window_text()[:80]
            dv_aid = controls.device_variant_radio.automation_id() if hasattr(controls.device_variant_radio, 'automation_id') else ''
        except Exception:
            dv_text = "?"
            dv_aid = "?"
        actions.append(f"WOULD click device variant AWR29xx/XWR2944 (auto_id={dv_aid!r} text={dv_text!r})")

        actions.append("WOULD click Set(1) button (m_btnSetSop)")
        actions.append("WOULD wait 5 seconds for SOP")

        if controls.refresh_ports_button is not None:
            actions.append("WOULD click Refresh Ports (m_btnRefreshPorts)")
        if controls.com_combo is not None:
            actions.append(f"WOULD set COM port to {com_port} (m_cboComPort)")
        else:
            actions.append(f"WOULD SKIP COM port selection (control not found, assume pre-set)")

        if controls.baud_combo is not None:
            actions.append(f"WOULD set baud rate to {baud} (m_cboBaudRate)")
        else:
            actions.append(f"WOULD SKIP baud rate selection (control not found, assume pre-set)")

        actions.append("WOULD click RS232 Connect button (m_btnConnect)")
        actions.append("WOULD poll Output document for AWR2944/GP/SOP:2 (up to 15s)")

        for a in actions:
            progress.log("dry_run_action", a)

        return ClickFlowResult(
            status="DRY_RUN_COMPLETE",
            details={"planned_actions": actions},
        )

    # --- LIVE CLICK FLOW ---

    # Step 2: Click 77 GHz radio button
    if controls.frequency_radio is not None:
        progress.log("before_click_77ghz_radio")
        try:
            controls.frequency_radio.click_input()
            progress.log("after_click_77ghz_radio", "clicked")
        except Exception as e:
            progress.log("after_click_77ghz_radio", f"error: {e}")
            vlog(f"77 GHz radio click failed: {e}")
    else:
        progress.log("skip_77ghz_radio", "control not found")

    time.sleep(0.5)

    # Step 3: Click device variant AWR29xx/XWR2944
    progress.log("before_click_device_variant")
    try:
        dv_text = controls.device_variant_radio.window_text()[:80]
        dv_aid = ""
        try:
            dv_aid = controls.device_variant_radio.automation_id()
        except Exception:
            pass
        controls.device_variant_radio.click_input()
        progress.log("after_click_device_variant", f"clicked auto_id={dv_aid!r} text={dv_text!r}")
    except Exception as e:
        progress.log("after_click_device_variant", f"error: {e}")
        return ClickFlowResult(
            status="DEVICE_VARIANT_CLICK_FAILED",
            error=f"Failed to click device variant: {e}",
        )

    time.sleep(0.5)

    # Step 4: Click Set(1)
    progress.log("before_click_set1")
    try:
        controls.set_button.click_input()
        progress.log("after_click_set1", "clicked")
    except Exception as e:
        progress.log("after_click_set1", f"error: {e}")
        _take_screenshot(window, probe_dir / "gui_connect_after_set1.png", vlog)
        return ClickFlowResult(
            status="SET1_CLICK_FAILED",
            error=f"Failed to click Set(1): {e}",
        )

    # Step 5: Wait for SOP
    progress.log("waiting_after_set1", "5000 ms")
    time.sleep(5.0)
    _take_screenshot(window, probe_dir / "gui_connect_after_set1.png", vlog)

    # Step 6: Set COM port
    if controls.com_combo is not None:
        # Click Refresh Ports first if available
        if controls.refresh_ports_button is not None:
            progress.log("before_click_refresh_ports")
            try:
                controls.refresh_ports_button.click_input()
                progress.log("after_click_refresh_ports", "clicked")
                time.sleep(1.0)  # wait for port list to populate
            except Exception as e:
                progress.log("after_click_refresh_ports", f"error: {e}")
                vlog(f"Refresh Ports click failed: {e}")

        progress.log("before_set_com", com_port)
        method_used = _select_combo_item_robust(
            controls.com_combo, com_port, vlog, progress
        )
        progress.log("after_set_com", f"done via {method_used}")
    else:
        progress.log("skip_set_com", f"control not found, assume {com_port} pre-set")

    time.sleep(0.3)

    # Step 7: Set baud rate
    if controls.baud_combo is not None:
        progress.log("before_set_baud", str(baud))
        method_used = _select_combo_item_robust(
            controls.baud_combo, str(baud), vlog, progress
        )
        progress.log("after_set_baud", f"done via {method_used}")
    else:
        progress.log("skip_set_baud", f"control not found, assume {baud} pre-set")

    time.sleep(0.3)

    # Step 8: Click RS232 Connect
    progress.log("before_click_rs232_connect")
    connect_click_time = time.monotonic()
    try:
        controls.rs232_connect_button.click_input()
        progress.log("after_click_rs232_connect", "clicked")
    except Exception as e:
        progress.log("after_click_rs232_connect", f"error: {e}")
        _take_screenshot(window, probe_dir / "gui_connect_after_rs232_connect.png", vlog)
        return ClickFlowResult(
            status="RS232_CONNECT_CLICK_FAILED",
            error=f"Failed to click RS232 Connect: {e}",
        )

    # Step 9: Poll Device Status (up to 15 seconds)
    progress.log("polling_device_status", "max 15 seconds")
    device_status: dict[str, Any] = {}

    for i in range(15):
        time.sleep(1.0)
        device_status = read_device_status(window, controls, verbose_log=vlog)
        progress.log(
            f"poll_device_status_{i+1}",
            device_status.get("raw_text", ""),
        )
        if device_status.get("valid"):
            break

    _take_screenshot(window, probe_dir / "gui_connect_after_rs232_connect.png", vlog)

    # Evaluate result
    if device_status.get("valid"):
        progress.log("connection_success", device_status.get("raw_text", ""))
        return ClickFlowResult(
            status="CONNECTION_GUI_BUTTON_SUCCESS",
            device_status_text=device_status.get("raw_text", ""),
            details=device_status,
        )

    raw_text = device_status.get("raw_text", "")
    if not raw_text or "UnDet" in raw_text or "Inv" in raw_text or "TEST" in raw_text:
        progress.log("need_power_cycle", raw_text)
        return ClickFlowResult(
            status="NEED_POWER_CYCLE",
            device_status_text=raw_text,
            details=device_status,
            error=(
                "Device Status does not show valid AWR2944/GP/SOP:2. "
                "Power-cycle AWR using power-before-USB order and retry."
            ),
        )

    progress.log("device_status_not_valid", raw_text)
    return ClickFlowResult(
        status="DEVICE_STATUS_NOT_VALID",
        device_status_text=raw_text,
        details=device_status,
        error=f"Device Status does not contain expected AWR2944/GP/SOP:2: {raw_text!r}",
    )


# ---------------------------------------------------------------------------
# Combo box selection helper
# ---------------------------------------------------------------------------

def _select_combo_item(
    ctrl,
    value: str,
    verbose_log: Callable[[str], None] | None = None,
    partial: bool = False,
):
    """Try to select an item in a combo box / dropdown.

    Priority:
    1. Use select() / select_by_text() if available
    2. Expand dropdown and click matching item
    3. Clear and type the value (Edit control fallback, logged loudly)
    """
    vlog = verbose_log or (lambda s: None)

    # Try native selection methods
    try:
        # pywinauto ComboBox has select() method
        if hasattr(ctrl, "select"):
            ctrl.select(value)
            vlog(f"Selected {value!r} via select()")
            return
    except Exception:
        pass

    # Try to find items in the combo and click
    try:
        items = ctrl.texts()
        for item_text in items:
            if partial:
                if value.lower() in item_text.lower():
                    ctrl.select(item_text)
                    vlog(f"Selected {item_text!r} (partial match for {value!r})")
                    return
            else:
                if item_text.strip().lower() == value.strip().lower():
                    ctrl.select(item_text)
                    vlog(f"Selected {item_text!r} (exact match)")
                    return
    except Exception:
        pass

    # Fallback: type the value (loudly logged)
    vlog(f"[FALLBACK] Typing {value!r} into control (select methods unavailable)")
    try:
        ctrl.set_focus()
        time.sleep(0.1)
        ctrl.set_edit_text(value)
        vlog(f"Typed {value!r} via set_edit_text()")
    except Exception:
        try:
            from pywinauto import keyboard  # type: ignore[import-untyped]
            ctrl.set_focus()
            time.sleep(0.1)
            keyboard.send_keys("^a")
            time.sleep(0.05)
            keyboard.send_keys(value, with_spaces=True)
            vlog(f"Typed {value!r} via keyboard.send_keys()")
        except Exception as e:
            raise RuntimeError(
                f"Cannot select/type {value!r} in control: {e}"
            )


def _select_combo_item_robust(
    ctrl,
    value: str,
    verbose_log: Callable[[str], None] | None = None,
    progress: ProgressLogger | None = None,
) -> str:
    """Robust combo box selection with logged fallback chain.

    Returns a string describing which method was used.

    Fallback order:
    1. select(value) — native pywinauto ComboBox method
    2. texts() scan + select(matched_text) — list items and match
    3. Edit child: find edit child and set_edit_text(value)
    4. Keyboard: focus + Ctrl+A + type — logged loudly as KEYBOARD_FALLBACK
    """
    vlog = verbose_log or (lambda s: None)

    # Method 1: Native select()
    try:
        if hasattr(ctrl, "select"):
            ctrl.select(value)
            vlog(f"Selected {value!r} via select()")
            return "select()"
    except Exception as e:
        vlog(f"  select({value!r}) failed: {e}")

    # Method 2: List items and match
    try:
        items = ctrl.texts()
        vlog(f"  Combo items: {items!r}")
        for item_text in items:
            if item_text.strip().upper() == value.strip().upper():
                ctrl.select(item_text)
                vlog(f"  Selected {item_text!r} via texts() exact match")
                return "texts_exact_match"
        # Partial match
        for item_text in items:
            if value.upper() in item_text.upper():
                ctrl.select(item_text)
                vlog(f"  Selected {item_text!r} via texts() partial match")
                return "texts_partial_match"
    except Exception as e:
        vlog(f"  texts() scan failed: {e}")

    # Method 3: Edit child
    try:
        edit_child = ctrl.child_window(control_type="Edit")
        if edit_child.exists(timeout=1):
            edit_wrapper = edit_child.wrapper_object()
            edit_wrapper.set_edit_text(value)
            vlog(f"  Set {value!r} via edit child set_edit_text()")
            return "edit_child_set_text"
    except Exception as e:
        vlog(f"  Edit child method failed: {e}")

    # Method 3b: set_edit_text directly on control
    try:
        ctrl.set_edit_text(value)
        vlog(f"  Set {value!r} via direct set_edit_text()")
        return "direct_set_edit_text"
    except Exception as e:
        vlog(f"  Direct set_edit_text failed: {e}")

    # Method 4: Keyboard fallback (logged loudly)
    vlog(f"  [KEYBOARD_FALLBACK] Typing {value!r} into control via keyboard")
    if progress is not None:
        progress.log("KEYBOARD_FALLBACK", f"typing {value!r}")
    try:
        from pywinauto import keyboard as kb  # type: ignore[import-untyped]
        ctrl.set_focus()
        time.sleep(0.1)
        kb.send_keys("^a")
        time.sleep(0.05)
        kb.send_keys(value, with_spaces=True)
        vlog(f"  Typed {value!r} via keyboard.send_keys()")
        return "keyboard_fallback"
    except Exception as e:
        vlog(f"  [KEYBOARD_FALLBACK FAILED] {e}")
        return f"FAILED: {e}"

