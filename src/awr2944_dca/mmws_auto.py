"""mmWave Studio dofile automation layer.

Provides safety classification and safe execution of generated Lua dofiles.
Wraps the existing executor.py transport backends with a notebook-friendly
safety gate around StartFrame/StartRecord.

Priority of truth for execution results:
1. Result JSON / progress JSONL written by the dofile (source of truth)
2. Executor return code (submission/transport status)
3. Lua Shell / Output text (diagnostic evidence)
4. Screenshots (last resort)
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class DofileSafety(str, Enum):
    """Safety classification for a Lua dofile."""
    SAFE = "safe"           # config, DCA setup — no RF
    DANGEROUS = "dangerous" # StartFrame, StartRecord — RF transmission
    UNKNOWN = "unknown"     # unclassified Lua


# Patterns that make a dofile dangerous
_DANGEROUS_PATTERNS = [
    re.compile(r"\bar1\.StartFrame\b", re.IGNORECASE),
    re.compile(r"\bStartFrame\s*\(", re.IGNORECASE),
    re.compile(r"\bCaptureCardConfig_StartRecord\b", re.IGNORECASE),
]

# Patterns for known-safe DCA setup calls
_SAFE_DCA_PATTERNS = [
    "SelectCaptureDevice",
    "CaptureCardConfig_EthInit",
    "CaptureCardConfig_Mode",
    "CaptureCardConfig_PacketDelay",
]

# Patterns for known-safe radar config calls
_SAFE_CONFIG_PATTERNS = [
    "ProfileConfig",
    "ChirpConfig",
    "FrameConfig",
    "RfInit",
    "DataPathConfig",
    "LVDSLaneConfig",
    "ChanNAdcConfig",
    "LPModConfig",
    "RfLdoBypassConfig",
    "SetCalMonFreqLimitConfig",
    "SetRFDeviceConfig",
    "RfSetCalMonFreqTxPowLimitConfig",
    "SetApllSynthBWCtlConfig",
]


@dataclass
class DofileClassification:
    """Result of classifying a Lua dofile for safety."""
    safety: DofileSafety
    reasons: list[str] = field(default_factory=list)
    contains_startframe: bool = False
    contains_startrecord: bool = False
    file_path: str = ""


def classify_dofile(path: Path) -> DofileClassification:
    """Classify a Lua dofile as safe, dangerous, or unknown.

    Reads the file content and scans for dangerous patterns.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dofile not found: {path}")

    content = path.read_text(encoding="utf-8")
    result = DofileClassification(
        safety=DofileSafety.UNKNOWN,
        file_path=str(path),
    )

    # Check for dangerous patterns
    for pattern in _DANGEROUS_PATTERNS:
        match = pattern.search(content)
        if match:
            matched_text = match.group()
            if "StartFrame" in matched_text:
                result.contains_startframe = True
                result.reasons.append(f"Contains StartFrame call: {matched_text}")
            if "StartRecord" in matched_text:
                result.contains_startrecord = True
                result.reasons.append(f"Contains StartRecord call: {matched_text}")

    if result.contains_startframe or result.contains_startrecord:
        result.safety = DofileSafety.DANGEROUS
        return result

    # Check if it matches known-safe patterns
    has_safe_pattern = False
    for pat in _SAFE_CONFIG_PATTERNS + _SAFE_DCA_PATTERNS:
        if pat in content:
            has_safe_pattern = True
            break

    if has_safe_pattern:
        result.safety = DofileSafety.SAFE
        result.reasons.append("Contains only known-safe ar1/DCA commands")
    else:
        result.safety = DofileSafety.UNKNOWN
        result.reasons.append("No recognized safe or dangerous patterns found")

    return result


def safe_execute_dofile(
    path: Path,
    *,
    allow_startframe: bool = False,
    timeout_s: float = 60,
    verbose: bool = False,
    mode: str = "auto",
) -> dict[str, Any]:
    """Safely execute a Lua dofile through the mmWave Studio executor.

    1. Classifies the dofile for safety
    2. Refuses dangerous files unless allow_startframe=True
    3. Delegates to executor.execute_script()
    4. Returns a dict with classification, execution result, and status

    Args:
        path: Path to .lua dofile
        allow_startframe: If True, allows execution of dangerous scripts
        timeout_s: Execution timeout in seconds
        verbose: Enable verbose logging
        mode: Executor mode ("auto", "csharp-rstd", "pywinauto", "manual")

    Returns:
        Dict with keys: classification, executed, exec_result, error

    Raises:
        FileNotFoundError: If dofile does not exist
        ValueError: If dofile is dangerous and allow_startframe=False
    """
    path = Path(path).resolve()
    classification = classify_dofile(path)

    result: dict[str, Any] = {
        "classification": {
            "safety": classification.safety.value,
            "reasons": classification.reasons,
            "contains_startframe": classification.contains_startframe,
            "contains_startrecord": classification.contains_startrecord,
        },
        "executed": False,
        "exec_result": None,
        "error": None,
    }

    # Safety gate
    if classification.safety == DofileSafety.DANGEROUS and not allow_startframe:
        msg = (
            f"Dofile is classified as DANGEROUS: {', '.join(classification.reasons)}. "
            "Pass allow_startframe=True to execute, or use "
            "run_next_step(confirm_startframe=True)."
        )
        raise ValueError(msg)

    # Execute through the existing executor
    from awr2944_dca.mmws.executor import execute_script, ExecutionResult

    exec_result = execute_script(
        path,
        mode=mode,
        timeout=timeout_s,
        verbose=verbose,
    )

    result["executed"] = True
    result["exec_result"] = {
        "mode": exec_result.mode.value,
        "success": exec_result.success,
        "return_code": exec_result.return_code,
        "error": exec_result.error,
        "elapsed_seconds": exec_result.elapsed_seconds,
        "lua_command_sent": exec_result.lua_command_sent,
    }

    if not exec_result.success:
        result["error"] = f"Executor submission failed: {exec_result.error}"

    return result


# ---------------------------------------------------------------------------
# Smoke test helpers (result-file-only, no WriteToLog)
# ---------------------------------------------------------------------------

def make_smoke_lua(result_path: str | Path) -> str:
    """Generate a minimal smoke-test Lua script.

    Writes a result JSON/text file via io.open — the source of truth.
    Does NOT call WriteToLog (proven nil in many contexts).
    If WriteToLog exists it is called optionally via pcall.

    Args:
        result_path: Absolute path where the result file should be written.

    Returns:
        Lua source string.
    """
    p = str(Path(result_path)).replace("\\", "/")
    return f"""\
-- mmWave Studio smoke test — result-file-only, no required WriteToLog
-- Source of truth: result file at {p}
local result_path = [[{p}]]
local ok, err = pcall(function()
    local f, ferr = io.open(result_path, "w")
    if f == nil then
        error("io.open failed: " .. (ferr or "unknown"))
    end
    f:write("{{\\"executed\\": true, \\"test\\": \\"smoke_test_ok\\"}}\\n")
    f:close()
end)

-- Optional: WriteToLog is nil in some contexts; guard it
if WriteToLog ~= nil then
    pcall(function()
        if ok then
            WriteToLog("SMOKE_TEST_OK\\n", "green")
        else
            WriteToLog("SMOKE_TEST_FAILED: " .. tostring(err) .. "\\n", "red")
        end
    end)
end

if not ok then
    error("Smoke test failed: " .. tostring(err))
end
"""


def bridge_health_check(
    timeout_s: float = 15.0,
    verbose: bool = False,
) -> dict:
    """Run a real health check for the C# RSTD bridge.

    Creates a temp result file, sends a smoke Lua via the C# bridge,
    and verifies the result file appears.

    Returns:
        Dict with keys: healthy (bool), mode, elapsed_seconds, error, result_file_found
    """
    import tempfile
    from awr2944_dca.mmws.executor import execute_script

    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = Path(tmpdir) / "bridge_health_result.json"
        lua_src = make_smoke_lua(result_path)
        lua_path = Path(tmpdir) / "bridge_health.lua"
        lua_path.write_text(lua_src, encoding="utf-8")

        exec_result = execute_script(
            lua_path,
            mode="csharp-rstd",
            timeout=timeout_s,
            verbose=verbose,
        )

        result_file_found = result_path.exists()

        return {
            "healthy": exec_result.success and result_file_found,
            "mode": exec_result.mode.value,
            "elapsed_seconds": exec_result.elapsed_seconds,
            "error": exec_result.error,
            "result_file_found": result_file_found,
            "return_code": exec_result.return_code,
        }


def cli_lua_health_check(
    timeout_s: float = 20.0,
    verbose: bool = False,
) -> dict:
    """Run a health check using the official mmWaveStudio.exe /lua backend.

    Proven to write result files. Does NOT guarantee current-session state.
    Do not use for capture-session commands without verifying session continuity.

    Returns:
        Dict with keys: healthy (bool), mode, elapsed_seconds, error, result_file_found.
        Also includes warning about session isolation.
    """
    import tempfile
    from awr2944_dca.mmws.executor import execute_script, _find_mmws_exe, ExecutionMode

    exe = _find_mmws_exe()
    if exe is None:
        return {
            "healthy": False,
            "mode": ExecutionMode.LUA_LAUNCH.value,
            "elapsed_seconds": 0.0,
            "error": "mmWaveStudio.exe not found in C:\\ti",
            "result_file_found": False,
            "warning": "cli_lua_launch may open a new Studio instance — does not preserve current session",
        }

    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = Path(tmpdir) / "cli_lua_health_result.json"
        lua_src = make_smoke_lua(result_path)
        lua_path = Path(tmpdir) / "cli_lua_health.lua"
        lua_path.write_text(lua_src, encoding="utf-8")

        exec_result = execute_script(
            lua_path,
            mode="lua-launch",
            timeout=timeout_s,
            verbose=verbose,
        )

        result_file_found = result_path.exists()

        return {
            "healthy": result_file_found,  # for /lua: result file is the proof
            "mode": exec_result.mode.value,
            "elapsed_seconds": exec_result.elapsed_seconds,
            "error": exec_result.error,
            "result_file_found": result_file_found,
            "warning": (
                "cli_lua_launch launches via mmWaveStudio.exe /lua. "
                "May open new instance. Does not guarantee current GUI session state. "
                "Safe for smoke tests and standalone scripts."
            ),
        }


def restart_bridge(verbose: bool = False) -> dict:
    """Kill any stale MmwsRstdBridge.exe processes and verify bridge is ready.

    Returns:
        Dict with: killed_count, bridge_found, port_open, ready.
    """
    import subprocess
    from awr2944_dca.mmws.executor import _find_csharp_bridge, _is_rstd_port_open

    # Kill stale bridge processes
    killed = 0
    try:
        result = subprocess.run(
            ["taskkill", "/F", "/IM", "MmwsRstdBridge.exe"],
            capture_output=True, text=True, timeout=5,
        )
        if "SUCCESS" in result.stdout or "success" in result.stdout.lower():
            # Count from output
            import re
            killed = len(re.findall(r"SUCCESS", result.stdout, re.IGNORECASE))
        if verbose:
            print(f"[restart_bridge] taskkill: {result.stdout.strip()}")
    except Exception as e:
        if verbose:
            print(f"[restart_bridge] taskkill error: {e}")

    import time
    time.sleep(0.5)  # brief pause for cleanup

    bridge = _find_csharp_bridge()
    port_open = _is_rstd_port_open()

    return {
        "killed_count": killed,
        "bridge_found": bridge is not None,
        "bridge_path": str(bridge) if bridge else None,
        "port_open": port_open,
        "ready": bridge is not None and port_open,
    }


def ui_lua_health_check(timeout_s: float = 30.0, verbose: bool = False) -> dict:
    """Check if pywinauto ui_lua_shell can execute a script and write a result.
    
    This actually waits for the result JSON to prove mmWave Studio processed it.
    """
    import tempfile
    from awr2944_dca.mmws.executor import execute_script, wait_for_result_json, _is_mmws_running
    
    if not _is_mmws_running():
        return {
            "healthy": False,
            "error": "mmWave Studio not running",
            "result_file_found": False
        }

    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = Path(tmpdir) / "ui_lua_smoke_result.json"
        lua_src = make_smoke_lua(result_path)
        lua_path = Path(tmpdir) / "ui_lua_smoke.lua"
        lua_path.write_text(lua_src, encoding="utf-8")

        exec_res = execute_script(
            lua_path, mode="pywinauto", timeout=timeout_s, verbose=verbose
        )

        if not exec_res.success:
            return {
                "healthy": False,
                "error": exec_res.error,
                "result_file_found": False
            }

        # ui_lua_shell submits asynchronously, so we MUST wait
        res_data = wait_for_result_json(result_path, timeout=timeout_s)
        
        return {
            "healthy": bool(res_data),
            "result_file_found": bool(res_data),
            "error": None if res_data else "Result file not written within timeout",
            "elapsed_seconds": exec_res.elapsed_seconds,
        }


def smoke_matrix(
    timeout_csharp: float = 15.0,
    timeout_cli: float = 25.0,
    verbose: bool = False,
) -> dict:
    """Test all available execution backends and report results.

    Tests:
    - csharp_rstd: C# RSTD bridge → result file
    - cli_lua_launch: mmWaveStudio.exe /lua → result file (proven to work)
    - ui_lua_shell: pywinauto paste (transport-only, no result file verification)
    - manual: always-available fallback (reports instruction only)

    Returns:
        Dict keyed by backend name, each with health dict.
        Also includes 'recommended' key with the best working backend.
    """
    results: dict = {}

    # 1. C# RSTD bridge
    try:
        results["csharp_rstd"] = bridge_health_check(
            timeout_s=timeout_csharp, verbose=verbose
        )
    except Exception as e:
        results["csharp_rstd"] = {
            "healthy": False, "error": str(e), "result_file_found": False
        }

    # 2. cli_lua_launch — officially documented, proven to write result files
    try:
        results["cli_lua_launch"] = cli_lua_health_check(
            timeout_s=timeout_cli, verbose=verbose
        )
    except Exception as e:
        results["cli_lua_launch"] = {
            "healthy": False, "error": str(e), "result_file_found": False,
            "warning": "cli_lua_launch may open new instance; does not preserve session",
        }

    # 3. ui_lua_shell — verified by result file
    try:
        results["ui_lua_shell"] = ui_lua_health_check(
            timeout_s=timeout_cli, verbose=verbose
        )
    except Exception as e:
        results["ui_lua_shell"] = {"healthy": False, "error": str(e), "result_file_found": False}

    # 4. manual (always available)
    results["manual"] = {
        "healthy": True,
        "available": True,
        "note": "Always available. Use run.dofile() to copy command, paste manually.",
        "error": None,
    }

    # Recommend the best result-file-verified backend
    recommended = None
    # Prioritize ui_lua_shell tonight, then fallback to csharp_rstd or cli_lua_launch
    for backend in ("ui_lua_shell", "csharp_rstd", "cli_lua_launch", "manual"):
        if results.get(backend, {}).get("healthy"):
            recommended = backend
            break

    results["recommended"] = recommended
    return results

# ---------------------------------------------------------------------------
# mmWave Studio Output Reading (pywinauto multi-strategy)
# ---------------------------------------------------------------------------

@dataclass
class OutputReadResult:
    """Result of reading mmWave Studio Output panel."""
    text: str | None
    available: bool
    backend: str = ""  # "uia", "win32", or ""
    strategy: str = ""  # which search strategy matched
    error: str = ""
    control_info: str = ""


# Search strategies for the output control
_OUTPUT_SEARCH_STRATEGIES = [
    {"name": "auto_id_m_ConsoleText", "kwargs": {"auto_id": "m_ConsoleText"}},
    {"name": "name_RichEdit_Control", "kwargs": {"title": "RichEdit Control"}},
    {"name": "control_type_Edit", "kwargs": {"control_type": "Edit", "auto_id": "m_ConsoleText"}},
    {"name": "class_name_RichEdit", "kwargs": {"class_name_re": ".*RichEdit.*"}},
    {"name": "class_name_WindowsForms_RichEdit", "kwargs": {"class_name_re": ".*WindowsForms10\\.RichEdit.*"}},
]


def _try_find_output_control(backend: str = "uia") -> OutputReadResult:
    """Try to find the mmWave Studio Output control using a specific backend.

    Args:
        backend: "uia" or "win32"

    Returns:
        OutputReadResult with text or structured error.
    """
    try:
        import pywinauto  # type: ignore[import-untyped]
    except ImportError:
        return OutputReadResult(
            text=None, available=False,
            error="pywinauto not installed. Install: pip install pywinauto",
        )

    try:
        app = pywinauto.Application(backend=backend).connect(
            title_re="mmWave Studio.*", timeout=3
        )
    except Exception as e:
        return OutputReadResult(
            text=None, available=False, backend=backend,
            error=f"Cannot connect to mmWave Studio ({backend}): {e}",
        )

    main_window = app.top_window()

    # Try each search strategy
    for strat in _OUTPUT_SEARCH_STRATEGIES:
        try:
            control = main_window.child_window(**strat["kwargs"])
            if control.exists(timeout=1):
                try:
                    text = control.window_text()
                    ctrl_info = ""
                    try:
                        ctrl_info = repr(control.element_info)
                    except Exception:
                        ctrl_info = str(strat["kwargs"])
                    return OutputReadResult(
                        text=text,
                        available=True,
                        backend=backend,
                        strategy=strat["name"],
                        control_info=ctrl_info,
                    )
                except Exception as e:
                    return OutputReadResult(
                        text=None, available=True, backend=backend,
                        strategy=strat["name"],
                        error=f"Control found but text read failed: {e}",
                        control_info=str(strat["kwargs"]),
                    )
        except Exception:
            continue

    return OutputReadResult(
        text=None, available=False, backend=backend,
        error=f"No matching output control found via {backend} backend "
              f"(tried {len(_OUTPUT_SEARCH_STRATEGIES)} strategies)",
    )


def find_mmws_output() -> OutputReadResult:
    """Find and read the mmWave Studio Output panel.

    Tries both pywinauto backends (uia, win32) and multiple search strategies.
    Returns structured result, never silent None.
    """
    # Try uia first (richer API), then win32 fallback
    for backend in ("uia", "win32"):
        result = _try_find_output_control(backend)
        if result.available and result.text is not None:
            return result

    # If uia found the window but not the control, try win32
    # Return the last result which has the most info
    return result


def read_mmws_output(max_chars: int = 20000) -> str | None:
    """Read the mmWave Studio Output/Lua Shell panel text.

    Returns the text content, or None if unavailable.
    For structured diagnostics, use find_mmws_output() instead.
    """
    result = find_mmws_output()
    if result.text is None:
        return None
    text = result.text
    if len(text) > max_chars:
        text = text[-max_chars:]
    return text


def tail_mmws_output(lines: int = 100) -> str | None:
    """Return the last N lines of mmWave Studio Output panel.

    Returns a string of the last N lines, or None if unavailable.
    """
    text = read_mmws_output()
    if text is None:
        return None
    all_lines = text.splitlines()
    return "\n".join(all_lines[-lines:])


def save_output_snapshot(
    output_dir: Path,
    label: str | None = None,
) -> Path | None:
    """Save current mmWave Studio Output text to a file.

    Args:
        output_dir: Directory to save the snapshot in
        label: Optional label for the filename

    Returns:
        Path to the saved file, or None if output unavailable
    """
    text = read_mmws_output(max_chars=100000)
    if text is None:
        return None

    import datetime
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"mmws_output_{ts}"
    if label:
        name += f"_{label}"
    name += ".txt"

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / name
    out_path.write_text(text, encoding="utf-8")
    return out_path


def wait_for_output(
    pattern: str,
    timeout_s: float = 60,
    poll_interval: float = 1.0,
) -> bool:
    """Wait for a regex pattern to appear in mmWave Studio Output.

    Returns True if found within timeout, False otherwise.
    """
    compiled = re.compile(pattern)
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        text = read_mmws_output()
        if text and compiled.search(text):
            return True
        time.sleep(poll_interval)
    return False


def list_output_controls() -> list[dict]:
    """List all candidate controls in the mmWave Studio window.

    Returns a list of dicts with control info for diagnostics.
    Useful when the standard search strategies don't find the output panel.
    """
    try:
        import pywinauto  # type: ignore[import-untyped]
    except ImportError:
        return [{"error": "pywinauto not installed"}]

    results = []
    for backend in ("uia", "win32"):
        try:
            app = pywinauto.Application(backend=backend).connect(
                title_re="mmWave Studio.*", timeout=3
            )
            main_window = app.top_window()

            # Find Edit / RichEdit controls
            try:
                children = main_window.descendants()
                for child in children:
                    try:
                        info = child.element_info
                        class_name = getattr(info, "class_name", "")
                        ctrl_type = getattr(info, "control_type", "")
                        auto_id = getattr(info, "automation_id", "")
                        name = getattr(info, "name", "")

                        # Only report Edit/RichEdit/Document controls
                        if any(k in str(class_name).lower() for k in ("edit", "richedit", "scintilla")) or \
                           ctrl_type in ("Edit", "Document"):
                            text_preview = ""
                            try:
                                t = child.window_text()
                                text_preview = t[:200] if t else "(empty)"
                            except Exception:
                                text_preview = "(unreadable)"

                            results.append({
                                "backend": backend,
                                "class_name": class_name,
                                "control_type": ctrl_type,
                                "auto_id": auto_id,
                                "name": name,
                                "text_preview": text_preview,
                            })
                    except Exception:
                        continue
            except Exception as e:
                results.append({"backend": backend, "error": f"Cannot enumerate children: {e}"})

        except Exception as e:
            results.append({"backend": backend, "error": f"Cannot connect: {e}"})

    return results

