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

# Strong candidate patterns — only these qualify for auto-resolution.
_STRONG_PROCESS_NAMES = {"mmwavestudio", "rstd", "radarstudio", "mmwsrstdbridge"}
_STRONG_TITLE_PATTERN = re.compile(r"mmWave\s+Studio", re.IGNORECASE)


def _is_strong_candidate(cand: dict) -> bool:
    """Return True if this PowerShell candidate is a strong mmWave Studio match.

    Strong matches: process name is mmWaveStudio/RSTD/RadarStudio/MmwsRstdBridge
    or title contains the exact phrase "mmWave Studio".
    Weak matches (e.g. Chrome with "radar" in the URL bar) are not strong.
    """
    proc_name = (cand.get("ProcessName") or "").lower()
    title = cand.get("MainWindowTitle") or ""
    if proc_name in _STRONG_PROCESS_NAMES:
        return True
    if _STRONG_TITLE_PATTERN.search(title):
        return True
    return False



def _get_powershell_candidates(verbose_log: Callable[[str], None] | None = None) -> list[dict[str, Any]]:
    """Query PowerShell for candidate mmWave Studio processes using WMI/process objects."""
    import subprocess
    import json
    vlog = verbose_log or (lambda s: None)
    
    script = (
        'Get-Process | '
        'Where-Object { $_.ProcessName -match "mmwave|rstd|radarstudio" -or $_.MainWindowTitle -match "mmwave|rstd|radar|lua" } | '
        'Select-Object Id, ProcessName, MainWindowHandle, MainWindowTitle, Responding, Path | '
        'ConvertTo-Json -Depth 3'
    )
    try:
        output = subprocess.check_output(["powershell", "-NoProfile", "-Command", script], text=True)
        if not output.strip():
            return []
        data = json.loads(output)
        if isinstance(data, dict):
            return [data]
        return data
    except Exception as e:
        vlog(f"PowerShell candidate enumeration failed: {e}")
        return []


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


def _try_attach_pid(Application, target_pid: int, hwnd: int | None,
                     probe_dir: Path, vlog: Callable[[str], None]):
    """Attach to a process using the proven minimal pywinauto sequence.

    Strategy order:
    1. connect(process=pid) -> app.windows() -> pick first
    2. connect(handle=hwnd) -> app.windows() -> pick first (if hwnd given)
    3. Desktop.window(handle=hwnd).exists() -> use that spec (if hwnd given)

    IMPORTANT: app.windows() returns UIAWrapper objects which do NOT have
    child_window(). We re-wrap the result as app.window(handle=h) which
    returns a WindowSpecification that *does* support child_window().

    Returns (app, window_spec) on success.
    Raises RuntimeError with honest diagnostics on failure.
    """
    # --- Strategy 1: connect by PID, use app.windows() ---
    try:
        app = Application(backend="uia").connect(process=target_pid, timeout=5)
        wins = app.windows()
        if wins:
            win = wins[0]
            h = win.handle
            vlog(f"Attached by PID={target_pid}: {len(wins)} window(s), "
                 f"text={win.window_text()!r}, handle={h}")
            # Re-wrap as WindowSpecification for child_window() support
            spec = app.window(handle=h)
            return app, spec
        else:
            vlog(f"connect(process={target_pid}) succeeded but app.windows() "
                 f"returned empty list")
    except Exception as e:
        vlog(f"connect(process={target_pid}) failed: {e}")

    # --- Strategy 2: connect by window handle ---
    if hwnd:
        try:
            app = Application(backend="uia").connect(handle=hwnd, timeout=5)
            wins = app.windows()
            if wins:
                win = wins[0]
                h = win.handle
                vlog(f"Attached by handle={hwnd}: {len(wins)} window(s), "
                     f"text={win.window_text()!r}")
                # Re-wrap as WindowSpecification for child_window() support
                spec = app.window(handle=h)
                return app, spec
            else:
                vlog(f"connect(handle={hwnd}) succeeded but app.windows() "
                     f"returned empty list")
        except Exception as e:
            vlog(f"connect(handle={hwnd}) failed: {e}")

        # --- Strategy 3: Desktop.window(handle=hwnd) ---
        try:
            from pywinauto import Desktop  # type: ignore[import-untyped]
            dw = Desktop(backend="uia").window(handle=hwnd)
            if dw.exists(timeout=5):
                vlog(f"Desktop.window(handle={hwnd}).exists()=True, "
                     f"text={dw.window_text()!r}")
                # dw is already a WindowSpecification — supports child_window()
                app = Application(backend="uia").connect(handle=hwnd, timeout=5)
                return app, dw
        except Exception as e:
            vlog(f"Desktop.window(handle={hwnd}) failed: {e}")

    return None, None


def uia_probe(pid: int, verbose_log: Callable[[str], None] | None = None) -> dict:
    """Diagnostic probe: test UIA attach strategies for a PID.

    Returns a dict with results of each strategy. Read-only: no hardware
    interaction, no Lua, no ar1 calls.
    """
    vlog = verbose_log or (lambda s: None)
    results: dict = {"pid": pid, "strategies": {}}

    ps_cands = _get_powershell_candidates(verbose_log=vlog)
    target_cand = next((c for c in ps_cands if c.get("Id") == pid), None)
    results["ps_candidate"] = target_cand
    hwnd = target_cand.get("MainWindowHandle", 0) if target_cand else 0
    results["hwnd"] = hwnd

    try:
        from pywinauto import Application, Desktop  # type: ignore[import-untyped]
    except ImportError:
        results["error"] = "pywinauto not installed"
        return results

    # Strategy 1: connect(process=pid)
    s1: dict = {"method": "connect(process=pid)"}
    try:
        app = Application(backend="uia").connect(process=pid, timeout=5)
        wins = app.windows()
        s1["connected"] = True
        s1["window_count"] = len(wins)
        s1["windows"] = [
            {"text": w.window_text(), "handle": w.handle}
            for w in wins
        ]
    except Exception as e:
        s1["connected"] = False
        s1["error"] = str(e)
    results["strategies"]["connect_by_pid"] = s1

    # Strategy 2: connect(handle=hwnd)
    s2: dict = {"method": f"connect(handle={hwnd})"}
    if hwnd:
        try:
            app = Application(backend="uia").connect(handle=hwnd, timeout=5)
            wins = app.windows()
            s2["connected"] = True
            s2["window_count"] = len(wins)
            s2["windows"] = [
                {"text": w.window_text(), "handle": w.handle}
                for w in wins
            ]
        except Exception as e:
            s2["connected"] = False
            s2["error"] = str(e)
    else:
        s2["skipped"] = "MainWindowHandle == 0"
    results["strategies"]["connect_by_handle"] = s2

    # Strategy 3: Desktop.window(handle=hwnd).exists()
    s3: dict = {"method": f"Desktop.window(handle={hwnd}).exists()"}
    if hwnd:
        try:
            dw = Desktop(backend="uia").window(handle=hwnd)
            exists = dw.exists(timeout=5)
            s3["exists"] = exists
            if exists:
                s3["text"] = dw.window_text()
        except Exception as e:
            s3["exists"] = False
            s3["error"] = str(e)
    else:
        s3["skipped"] = "MainWindowHandle == 0"
    results["strategies"]["desktop_window"] = s3

    return results


def attach_mmwave_studio(
    pid: int | None = None,
    title_regex: str | None = None,
    probe_dir: Path | None = None,
    verbose_log: Callable[[str], None] | None = None,
):
    """Attach to a running mmWaveStudio.exe via pywinauto UIA backend.

    Attach strategies (in order of preference):
    1. connect(process=pid) -> app.windows() -> pick first window
    2. connect(handle=hwnd) -> app.windows() -> pick first window
    3. Desktop.window(handle=hwnd) -> use that wrapper

    For auto-resolve (no --pid given), only *strong* candidates are
    considered: process names mmWaveStudio/RSTD/RadarStudio or titles
    containing "mmWave Studio".  Weak matches (Chrome, IDE with "radar"
    in the title) are displayed but do not block auto-resolution.

    Returns (Application, top_window).
    Raises RuntimeError with descriptive messages on failure.
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

    ps_cands = _get_powershell_candidates(verbose_log=vlog)

    # Helper for formatting candidates
    def format_cands(cands) -> str:
        if not cands:
            return "  (No candidates found)"
        return "\n".join(
            f"  PID={c.get('Id')}  Name={c.get('ProcessName')}  "
            f"Handle={c.get('MainWindowHandle')}  Title={c.get('MainWindowTitle', '')!r}  "
            f"Strong={_is_strong_candidate(c)}"
            for c in cands
        )

    # Elevation check helper
    def check_elevation(test_pid: int) -> None:
        if _is_process_elevated(test_pid) and not _is_admin():
            raise RuntimeError(
                "If mmWave Studio was launched as Administrator, "
                "this PowerShell terminal must also be run as Administrator."
            )

    target_pid: int | None = pid

    if target_pid is not None:
        # --- Explicit PID path ---
        vlog(f"Attaching directly by PID={target_pid}")
        target_cand = next(
            (c for c in ps_cands if c.get("Id") == target_pid), None
        )
        hwnd = (target_cand.get("MainWindowHandle", 0)
                if target_cand else 0)

        if target_cand is not None and hwnd == 0:
            raise RuntimeError(
                f"UIA attach failed for PID={target_pid}:\n"
                f"No windows for that process could be found "
                f"(MainWindowHandle == 0).\n"
                f"Verify the PID is correct and mmWave Studio is running.\n\n"
                f"Candidate processes:\n{format_cands(ps_cands)}\n\n"
                f"If mmWave Studio was launched as Administrator, "
                f"this PowerShell terminal must also be run as Administrator."
            )

        check_elevation(target_pid)

        app, win = _try_attach_pid(
            Application, target_pid, hwnd, probe_dir, vlog
        )
        if app is not None and win is not None:
            return app, win

        # All strategies failed — write diagnostics and raise with honesty
        candidates = _enumerate_uia_windows(verbose_log=vlog)
        _write_window_diagnostics(candidates, probe_dir, vlog)
        raise RuntimeError(
            f"UIA attach failed for PID={target_pid}: "
            f"all attach strategies exhausted "
            f"(connect by PID, connect by handle={hwnd}, "
            f"Desktop.window).\n"
            f"If mmWave Studio was launched as Administrator, "
            f"this PowerShell terminal must also be run as Administrator."
        )

    # --- Auto-resolve: only strong visible candidates ---
    strong_visible = [
        c for c in ps_cands
        if c.get("MainWindowHandle", 0) != 0 and _is_strong_candidate(c)
    ]

    if len(strong_visible) == 1:
        cand = strong_visible[0]
        target_pid = cand.get("Id")
        hwnd = cand.get("MainWindowHandle", 0)
        vlog(f"Auto-resolved unambiguous strong PID={target_pid} "
             f"handle={hwnd}")
        check_elevation(target_pid)

        app, win = _try_attach_pid(
            Application, target_pid, hwnd, probe_dir, vlog
        )
        if app is not None and win is not None:
            return app, win

        candidates = _enumerate_uia_windows(verbose_log=vlog)
        _write_window_diagnostics(candidates, probe_dir, vlog)
        raise RuntimeError(
            f"UIA attach failed for auto-resolved PID={target_pid}: "
            f"all attach strategies exhausted.\n"
            f"If mmWave Studio was launched as Administrator, "
            f"this PowerShell terminal must also be run as Administrator."
        )
    elif len(strong_visible) == 0:
        raise RuntimeError(
            "Could not auto-resolve mmWave Studio PID: "
            "No visible strong candidate processes found.\n\n"
            f"Candidate processes:\n{format_cands(ps_cands)}\n\n"
            "Try running with explicit --pid <PID>."
        )
    else:
        raise RuntimeError(
            "Could not auto-resolve mmWave Studio PID: "
            "Multiple visible strong candidate processes found.\n\n"
            f"Candidate processes:\n{format_cands(ps_cands)}\n\n"
            "Please rerun with an explicit: --pid <PID>"
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
    """Find a control by automation_id.

    Primary: root.child_window(auto_id=...) — works on WindowSpecification.
    Fallback: search root.descendants() by automation_id — works on UIAWrapper.

    Returns the wrapper object or None.
    """
    vlog = verbose_log or (lambda s: None)

    # Primary: child_window() — available on WindowSpecification
    if hasattr(root, 'child_window'):
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

    # Fallback: descendants() — works on UIAWrapper
    if hasattr(root, 'descendants'):
        try:
            for child in root.descendants():
                try:
                    child_auto_id = child.automation_id() if hasattr(child, 'automation_id') else ""
                except Exception:
                    continue
                if child_auto_id == auto_id:
                    try:
                        text = child.window_text()[:80]
                    except Exception:
                        text = "<no text>"
                    vlog(f"  Found auto_id={auto_id!r} via descendants: text={text!r}")
                    return child
        except Exception as e:
            vlog(f"  Descendants search for auto_id={auto_id!r} failed: {e}")

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
    output_log_path: Path | None = None,
) -> dict[str, Any]:
    """Read the Device Status from Output document text.

    Extraction strategies (in order):
    A. Direct auto_id labels: m_lblDeviceStatus, lblDeviceStatus, etc.
    B. Output document (m_ConsoleText): search for 'Device Status' lines
    C. All descendants text: collect all nonempty text and search for
       'Device Status', 'AWR2944', 'SOP:2'

    Returns a dict with keys:
      raw_text, valid, device, type, sop, es, rs232_status,
      _extraction (diagnostics metadata)
    """
    vlog = verbose_log or (lambda s: None)

    if controls is None:
        controls = inspect_connection_tab(window, verbose_log=vlog)

    raw = ""
    extraction: dict[str, Any] = {
        "console_text_found": False,
        "console_text_length": 0,
        "device_status_label_found": controls.device_status_label is not None,
        "device_status_label_text": "",
        "rs232_status_found": controls.rs232_status_label is not None,
        "descendants_searched": False,
        "extraction_source": None,
    }

    # --- Strategy A: Device Status label auto_ids ---
    if controls.device_status_label is not None:
        try:
            label_text = controls.device_status_label.window_text()
            extraction["device_status_label_text"] = label_text
            if label_text and ("AWR" in label_text or "XWR" in label_text) and "/" in label_text:
                raw = label_text
                extraction["extraction_source"] = "device_status_label"
                vlog(f"Found Device Status via label: {raw!r}")
        except Exception:
            pass

    # --- Strategy B: Output document (m_ConsoleText) ---
    # Re-find fresh wrapper to avoid stale state
    output_doc = _find_by_auto_id(window, "m_ConsoleText", vlog)
    if output_doc is None:
        output_doc = controls.output_document

    doc_text = ""
    if output_doc is not None:
        extraction["console_text_found"] = True
        vlog("Reading Output document (m_ConsoleText) for Device Status")
        try:
            doc_text = output_doc.window_text() or ""
            extraction["console_text_length"] = len(doc_text)
            if output_log_path is not None:
                try:
                    with open(output_log_path, "w", encoding="utf-8", newline="") as f:
                        f.write(doc_text[-8000:])
                except Exception:
                    pass
            # Search from bottom for most recent Device Status line
            if not raw:
                for line in reversed(doc_text.splitlines()):
                    if "Device Status" in line and "/" in line:
                        raw = line.strip()
                        extraction["extraction_source"] = "console_text"
                        vlog(f"Found Device Status in Output: {raw!r}")
                        break
        except Exception as e:
            vlog(f"Output document read failed: {e}")
    else:
        vlog("m_ConsoleText NOT FOUND")

    # --- Strategy C: All descendants text search ---
    if not raw:
        vlog("Trying all-descendants text search for Device Status")
        extraction["descendants_searched"] = True
        try:
            for child in window.descendants():
                try:
                    child_text = child.window_text()
                    if not child_text:
                        continue
                    if "Device Status" in child_text and "/" in child_text:
                        # Found a Device Status string in some control
                        for line in reversed(child_text.splitlines()):
                            if "Device Status" in line and "/" in line:
                                raw = line.strip()
                                extraction["extraction_source"] = "descendants"
                                auto_id = ""
                                try:
                                    auto_id = child.automation_id()
                                except Exception:
                                    pass
                                vlog(f"Found Device Status via descendants: "
                                     f"auto_id={auto_id!r} text={raw!r}")
                                break
                        if raw:
                            break
                except Exception:
                    continue
        except Exception as e:
            vlog(f"Descendants search failed: {e}")

    # Read RS232 status separately
    rs232_status = ""
    if controls.rs232_status_label is not None:
        try:
            rs232_status = controls.rs232_status_label.window_text()
        except Exception:
            pass
    extraction["rs232_status_text"] = rs232_status

    # Read SPI status
    spi_status = ""
    if controls.spi_status_label is not None:
        try:
            spi_status = controls.spi_status_label.window_text()
        except Exception:
            pass
    extraction["spi_status_text"] = spi_status

    vlog(f"Device Status raw text: {raw!r}")
    vlog(f"RS232 status: {rs232_status!r}")

    result: dict[str, Any] = {
        "raw_text": raw,
        "valid": False,
        "device": None,
        "type": None,
        "safety": None,
        "sop": None,
        "es": None,
        "rs232_status": rs232_status,
        "_extraction": extraction,
    }

    if not raw:
        return result

    import re
    # Match strings like: "Device Status : AWR2944/GP/ASIL-B/SOP:2/ES:2.0"
    # Also handles just the string without "Device Status :"
    pattern = r"(?:Device Status\s*:\s*)?(?P<device>AWR2944|XWR2944)/(?P<type>GP|TEST|QM)/(?P<safety>[^/]+)/SOP:(?P<sop>\d+)/ES:(?P<es>[0-9.]+)"
    match = re.search(pattern, raw)

    if match:
        result["device"] = match.group("device")
        result["type"] = match.group("type")
        result["safety"] = match.group("safety")
        result["sop"] = match.group("sop")
        result["es"] = match.group("es")
    else:
        # Fallback split-based heuristic if regex fails
        text = raw
        if ":" in text and "Device Status" in text:
            text = text.split(":", 1)[1].strip()
        parts = [p.strip() for p in text.split("/")]
        for p in parts:
            if p.startswith("AWR") or p.startswith("XWR"):
                result["device"] = p
            elif p in ("GP", "QM", "TEST"):
                result["type"] = p
            elif p.startswith("SOP:"):
                result["sop"] = p.replace("SOP:", "")
            elif p.startswith("ES:"):
                result["es"] = p.replace("ES:", "")
            elif p in ("ASIL-B", "ASIL", "QM"):
                result["safety"] = p

    # Valid = AWR2944 + GP + SOP:2
    result["valid"] = (
        result["device"] is not None
        and "2944" in (result["device"] or "")
        and result["type"] == "GP"
        and result["sop"] == "2"
    )

    return result


# ---------------------------------------------------------------------------
# Manual status probe — read-only diagnostic
# ---------------------------------------------------------------------------

_PROBE_SEARCH_TERMS = [
    "Device", "Status", "RS232", "SPI", "Console", "Output",
    "Connect", "AWR", "xWR", "SOP",
]


def manual_status_probe(
    window,
    probe_dir: Path | None = None,
    verbose_log: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Diagnostic probe: exercise the same extraction path as manual_check.

    Read-only: no clicks, no Lua, no ar1, no firmware.
    Writes a diagnostic file to probe_dir.

    Returns a dict with all extraction results.
    """
    vlog = verbose_log or (lambda s: None)
    if probe_dir is None:
        probe_dir = Path("ti") / "probe_logs"
    probe_dir.mkdir(parents=True, exist_ok=True)

    results: dict[str, Any] = {}

    # Window info
    try:
        results["window_title"] = window.window_text()
        results["window_handle"] = window.handle
    except Exception as e:
        results["window_title"] = f"<error: {e}>"
        results["window_handle"] = None

    # Inspect connection tab controls
    controls = inspect_connection_tab(window, verbose_log=vlog)
    results["radarapi_found"] = controls.radarapi_window is not None
    results["console_text_found"] = controls.output_document is not None
    results["missing_controls"] = controls.missing

    # Read device status with full diagnostics
    device_status = read_device_status(
        window, controls, verbose_log=vlog,
        output_log_path=probe_dir / "manual_status_probe_output_tail.txt",
    )
    results["device_status"] = device_status
    results["extraction"] = device_status.get("_extraction", {})

    # Console text details
    if controls.output_document is not None:
        try:
            doc_text = controls.output_document.window_text() or ""
            results["console_text_length"] = len(doc_text)
            lines = doc_text.splitlines()
            results["console_text_last_30_lines"] = lines[-30:] if lines else []
        except Exception as e:
            results["console_text_length"] = 0
            results["console_text_last_30_lines"] = [f"<error: {e}>"]
    else:
        results["console_text_length"] = 0
        results["console_text_last_30_lines"] = []

    # RS232 status
    if controls.rs232_status_label is not None:
        try:
            results["rs232_status_raw"] = controls.rs232_status_label.window_text()
        except Exception:
            results["rs232_status_raw"] = "<error>"
    else:
        results["rs232_status_raw"] = "<not found>"

    # SPI status
    if controls.spi_status_label is not None:
        try:
            results["spi_status_raw"] = controls.spi_status_label.window_text()
        except Exception:
            results["spi_status_raw"] = "<error>"
    else:
        results["spi_status_raw"] = "<not found>"

    # Device Status label
    if controls.device_status_label is not None:
        try:
            results["device_status_label_raw"] = controls.device_status_label.window_text()
        except Exception:
            results["device_status_label_raw"] = "<error>"
    else:
        results["device_status_label_raw"] = "<not found>"

    # Device variant
    results["device_variant_candidates"] = controls.device_variant_candidates

    # Search all descendants for matching controls
    matching_descendants: list[dict[str, str]] = []
    try:
        for child in window.descendants():
            try:
                auto_id = child.automation_id() if hasattr(child, 'automation_id') else ""
                child_name = child.element_info.name if hasattr(child, 'element_info') else ""
                child_text = (child.window_text() or "")[:200]
            except Exception:
                continue
            combined = (auto_id + " " + child_name + " " + child_text).lower()
            if any(term.lower() in combined for term in _PROBE_SEARCH_TERMS):
                matching_descendants.append({
                    "automation_id": auto_id,
                    "name": child_name,
                    "text": child_text,
                })
    except Exception as e:
        matching_descendants.append({"error": str(e)})
    results["matching_descendants"] = matching_descendants

    # Write diagnostic file
    ts = time.strftime("%Y%m%d_%H%M%S")
    diag_path = probe_dir / f"manual_status_probe_{ts}.txt"
    try:
        with open(diag_path, "w", encoding="utf-8") as f:
            f.write(f"Manual Status Probe\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Window: title={results.get('window_title')!r} "
                    f"handle={results.get('window_handle')}\n")
            f.write(f"RadarAPI (frmAR1Main) found: {results['radarapi_found']}\n")
            f.write(f"m_ConsoleText found: {results['console_text_found']}\n")
            f.write(f"Console text length: {results['console_text_length']}\n")
            f.write(f"Device Status raw: {device_status.get('raw_text')!r}\n")
            f.write(f"Device Status valid: {device_status.get('valid')}\n")
            f.write(f"RS232 status: {results.get('rs232_status_raw')!r}\n")
            f.write(f"SPI status: {results.get('spi_status_raw')!r}\n")
            f.write(f"Device Status label: {results.get('device_status_label_raw')!r}\n")
            f.write(f"Missing controls: {controls.missing}\n\n")

            ext = results.get("extraction", {})
            f.write(f"Extraction diagnostics:\n")
            f.write(f"  extraction_source: {ext.get('extraction_source')}\n")
            f.write(f"  console_text_found: {ext.get('console_text_found')}\n")
            f.write(f"  console_text_length: {ext.get('console_text_length')}\n")
            f.write(f"  device_status_label_found: {ext.get('device_status_label_found')}\n")
            f.write(f"  descendants_searched: {ext.get('descendants_searched')}\n\n")

            f.write("Last 30 lines of m_ConsoleText:\n")
            for line in results.get("console_text_last_30_lines", []):
                f.write(f"  {line}\n")
            f.write("\n")

            f.write(f"Matching descendants ({len(matching_descendants)}):\n")
            for md in matching_descendants:
                if "error" in md:
                    f.write(f"  <error: {md['error']}>\n")
                else:
                    f.write(f"  auto_id={md['automation_id']!r}  "
                            f"name={md['name']!r}  "
                            f"text={md['text']!r}\n")
    except Exception as e:
        vlog(f"Failed to write diagnostic file: {e}")

    results["diagnostic_file"] = str(diag_path)
    vlog(f"Wrote diagnostic file: {diag_path}")
    return results


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
    slow: bool = False,
    allow_keyboard_fallback: bool = False,
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

    delay_after_click = 1.0 if slow else 0.5

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

    time.sleep(delay_after_click)
    _take_screenshot(window, probe_dir / "gui_connect_after_77ghz.png", vlog)

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

    time.sleep(delay_after_click)
    _take_screenshot(window, probe_dir / "gui_connect_after_device_variant.png", vlog)

    # Step 4: Click Set(1)
    progress.log("before_click_set1")
    try:
        controls.set_button.click_input()
        progress.log("after_click_set1", "clicked")
    except Exception as e:
        progress.log("after_click_set1", f"error: {e}")
        _take_screenshot(window, probe_dir / "gui_connect_after_set1_click.png", vlog)
        return ClickFlowResult(
            status="SET1_CLICK_FAILED",
            error=f"Failed to click Set(1): {e}",
        )

    _take_screenshot(window, probe_dir / "gui_connect_after_set1_click.png", vlog)

    # Step 5: Wait for SOP / Verification
    progress.log("waiting_after_set1", "polling up to 30s for verification")
    set1_verified = False
    for i in range(30):
        time.sleep(1.0)
        # Check COM ports
        if controls.com_combo is not None:
            try:
                items = controls.com_combo.texts()
                if any(com_port.lower() in t.lower() for t in items):
                    progress.log("set1_verified", f"COM port {com_port} populated")
                    set1_verified = True
                    break
            except Exception:
                pass
        
        # Check Output Document
        try:
            output_doc = _find_by_auto_id(window, "m_ConsoleText", vlog)
            if output_doc is not None:
                doc_text = output_doc.window_text()
                if "SOPControl" in doc_text or "FullReset" in doc_text:
                    progress.log("set1_verified", "Found SOPControl/FullReset in output")
                    set1_verified = True
                    break
        except Exception:
            pass

    _take_screenshot(window, probe_dir / "gui_connect_after_set1_wait.png", vlog)
    try:
        out_doc = _find_by_auto_id(window, "m_ConsoleText", vlog)
        if out_doc:
            (probe_dir / "gui_connect_output_after_set1.txt").write_text(out_doc.window_text()[-4000:], encoding="utf-8")
    except Exception:
        pass

    if not set1_verified:
        progress.log("set1_not_confirmed", "Failed to verify Set(1) action")
        return ClickFlowResult(
            status="SET1_NOT_CONFIRMED",
            error="Set(1) was clicked but neither SOPControl nor COM port population was detected within 30s.",
        )

    # Step 6: Refresh Ports and wait for COM
    if controls.com_combo is not None:
        if controls.refresh_ports_button is not None:
            progress.log("before_click_refresh_ports")
            try:
                controls.refresh_ports_button.click_input()
                progress.log("after_click_refresh_ports", "clicked")
            except Exception as e:
                progress.log("after_click_refresh_ports", f"error: {e}")
                vlog(f"Refresh Ports click failed: {e}")

        # Poll for COM port
        progress.log("polling_com_ports", f"Waiting for {com_port} up to 10s")
        com_found = False
        for i in range(10):
            time.sleep(1.0)
            try:
                items = controls.com_combo.texts()
                if any(com_port.lower() in t.lower() for t in items):
                    com_found = True
                    break
                else:
                    progress.log(f"poll_com_ports_{i+1}", f"items: {items}")
            except Exception:
                pass
        
        _take_screenshot(window, probe_dir / "gui_connect_after_refresh_ports.png", vlog)
        
        if not com_found:
            progress.log("com_port_not_available", f"{com_port} not found in dropdown")
            return ClickFlowResult(
                status="COM6_NOT_FOUND_IN_COMBO",
                error=f"{com_port} not found in COM dropdown after refresh.",
            )

        progress.log("before_set_com", com_port)
        try:
            method_used = _select_combo_item_robust(
                controls.com_combo, com_port, vlog, progress, allow_keyboard_fallback=allow_keyboard_fallback
            )
            progress.log("after_set_com", f"done via {method_used}")
        except RuntimeError as e:
            progress.log("after_set_com", f"failed: {e}")
            return ClickFlowResult(status="COM_PORT_NOT_AVAILABLE", error=str(e))
    else:
        progress.log("skip_set_com", f"control not found, assume {com_port} pre-set")

    time.sleep(delay_after_click)
    _take_screenshot(window, probe_dir / "gui_connect_after_com_select.png", vlog)

    # Step 7: Set baud rate
    if controls.baud_combo is not None:
        progress.log("before_set_baud", str(baud))
        try:
            method_used = _select_combo_item_robust(
                controls.baud_combo, str(baud), vlog, progress, allow_keyboard_fallback=allow_keyboard_fallback
            )
            progress.log("after_set_baud", f"done via {method_used}")
        except RuntimeError as e:
            progress.log("after_set_baud", f"failed: {e}")
            return ClickFlowResult(status="BAUD_RATE_NOT_AVAILABLE", error=str(e))
    else:
        progress.log("skip_set_baud", f"control not found, assume {baud} pre-set")

    time.sleep(delay_after_click)
    _take_screenshot(window, probe_dir / "gui_connect_after_baud_select.png", vlog)

    # Step 8: Click RS232 Connect
    progress.log("before_click_rs232_connect")
    try:
        controls.rs232_connect_button.click_input()
        progress.log("after_click_rs232_connect", "clicked")
    except Exception as e:
        progress.log("after_click_rs232_connect", f"error: {e}")
        _take_screenshot(window, probe_dir / "gui_connect_after_rs232_connect_error.png", vlog)
        return ClickFlowResult(
            status="RS232_CONNECT_CLICK_FAILED",
            error=f"Failed to click RS232 Connect: {e}",
        )
    
    time.sleep(delay_after_click)
    _take_screenshot(window, probe_dir / "gui_connect_after_rs232_connect.png", vlog)

    # Step 9: Poll Device Status (up to 15 seconds)
    progress.log("polling_device_status", "max 15 seconds")
    device_status: dict[str, Any] = {}

    for i in range(15):
        time.sleep(1.0)
        device_status = read_device_status(
            window, controls, verbose_log=vlog, 
            output_log_path=probe_dir / "gui_connect_output_after_rs232_connect.txt"
        )
        progress.log(
            f"poll_device_status_{i+1}",
            device_status.get("raw_text", ""),
        )
        if device_status.get("valid"):
            break

    _take_screenshot(window, probe_dir / "gui_connect_after_rs232_poll.png", vlog)

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
    allow_keyboard_fallback: bool = False,
) -> str:
    """Robust combo box selection with logged fallback chain.

    Returns a string describing which method was used.
    Raises RuntimeError if all methods fail or keyboard fallback is disabled.

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
    if not allow_keyboard_fallback:
        vlog(f"  [KEYBOARD_FALLBACK] Denied by allow_keyboard_fallback=False")
        raise RuntimeError(f"Combo item '{value}' not found in texts and keyboard fallback is disabled.")

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
        raise RuntimeError(f"Keyboard fallback failed: {e}")

# ---------------------------------------------------------------------------
# Manual check helper
# ---------------------------------------------------------------------------

def manual_check(
    window,
    probe_dir: Path | None = None,
    verbose_log: Callable[[str], None] | None = None,
) -> ClickFlowResult:
    """Read the Device Status after a manual GUI connection."""
    vlog = verbose_log or (lambda s: None)

    if probe_dir is None:
        probe_dir = Path("ti") / "probe_logs"
    probe_dir.mkdir(parents=True, exist_ok=True)

    progress = ProgressLogger(probe_dir / "manual_check_progress.jsonl")
    progress.log("manual_check_started")

    controls = inspect_connection_tab(window, verbose_log=vlog)

    output_log_path = probe_dir / "manual_check_output_tail.txt"
    device_status = read_device_status(
        window, controls, verbose_log=vlog,
        output_log_path=output_log_path,
    )

    result_path = probe_dir / "manual_check_result.json"

    if device_status.get("valid"):
        progress.log("manual_connection_valid", device_status.get("raw_text", ""))
        res = ClickFlowResult(
            status="MANUAL_CONNECTION_VALID",
            device_status_text=device_status.get("raw_text", ""),
            details=device_status,
        )
    else:
        raw_text = device_status.get("raw_text", "")
        ext = device_status.get("_extraction", {})
        progress.log("manual_connection_not_valid", raw_text)

        # Build honest diagnostic error message
        diag_lines = [
            "Expected Device Status containing AWR2944, GP, and SOP:2.",
            f"UIA attach succeeded (window found).",
        ]
        if raw_text:
            diag_lines.append(f"Device Status text found but did not match: {raw_text!r}")
        else:
            diag_lines.append("Device Status extraction returned empty string.")

        diag_lines.append(
            f"m_ConsoleText found: {ext.get('console_text_found', False)}"
        )
        diag_lines.append(
            f"m_ConsoleText length: {ext.get('console_text_length', 0)}"
        )
        diag_lines.append(
            f"Device Status label found: {ext.get('device_status_label_found', False)}"
        )
        if ext.get("device_status_label_text"):
            diag_lines.append(
                f"Device Status label text: {ext.get('device_status_label_text')!r}"
            )
        diag_lines.append(
            f"RS232 status found: {ext.get('rs232_status_found', False)}"
        )
        if ext.get("rs232_status_text"):
            diag_lines.append(
                f"RS232 status: {ext.get('rs232_status_text')!r}"
            )
        diag_lines.append(
            f"Descendants searched: {ext.get('descendants_searched', False)}"
        )
        diag_lines.append(
            f"Extraction source: {ext.get('extraction_source', 'none')}"
        )
        diag_lines.append(
            f"Snapshot: {output_log_path}"
        )

        error_msg = "\n".join(diag_lines)
        res = ClickFlowResult(
            status="MANUAL_CONNECTION_NOT_VALID",
            device_status_text=raw_text,
            details=device_status,
            error=error_msg,
        )

    result_data = {
        "status": res.status,
        "device_status_text": res.device_status_text,
        "details": res.details,
        "error": res.error,
    }

    import json
    result_path.write_text(json.dumps(result_data, indent=2, default=str), encoding="utf-8")

    return res

