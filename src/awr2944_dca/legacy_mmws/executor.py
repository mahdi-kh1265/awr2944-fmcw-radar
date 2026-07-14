"""Executor: automatic Lua script execution in mmWave Studio.

Supports multiple transport modes, in priority order:

1. RSTD .NET Remoting (TCP:2777) via RtttNetClientAPI.dll + pythonnet
2. pywinauto UI Lua Shell paste (focus window + paste dofile only)
3. manual_one_shot (debug fallback — only when explicitly requested)

The executor is transport only.  It does not bypass stage safety.
Generated Lua must still pass static forbidden-call validation.

RSTD API sequence (from TI MATLAB example Init_RSTD_Connection.m):
  1. RtttNetClient.Init()
  2. RtttNetClient.Connect('127.0.0.1', 2777)
  3. RtttNetClient.SendCommand(lua_string)

SendCommand return code 30000 means the command was submitted.
It is NOT proof the stage succeeded — the result JSON is the source of truth.
"""

from __future__ import annotations

import io
import socket
import subprocess
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ExecutionMode(str, Enum):
    """Supported transport modes for reaching mmWave Studio."""

    CSHARP_RSTD = "csharp_rstd"
    MATLAB_RSTD = "matlab_rstd"
    RSTD_NET_REMOTING = "rstd_net_remoting"
    CLI_LAUNCH = "cli_launch"
    UI_LUA_SHELL = "ui_lua_shell"
    LUA_LAUNCH = "lua_launch"
    MANUAL_ONE_SHOT = "manual_one_shot"


class ExecutionStatus(str, Enum):
    """Detailed execution status labels."""

    SUCCESS = "SUCCESS"
    SUBMISSION_FAILED = "SUBMISSION_FAILED"
    SUBMITTED_BUT_NO_RESULT = "SUBMITTED_BUT_NO_RESULT"
    LUA_REPORTED_ERROR = "LUA_REPORTED_ERROR"
    TIMEOUT = "TIMEOUT"
    TRANSPORT_UNAVAILABLE = "TRANSPORT_UNAVAILABLE"


@dataclass
class ExecutionResult:
    """Result of a script execution attempt."""

    mode: ExecutionMode
    success: bool
    return_code: int | None = None
    error: str | None = None
    elapsed_seconds: float = 0.0
    verbose_log: list[str] = field(default_factory=list)
    lua_command_sent: str = ""


@dataclass
class TransportInfo:
    """Describes a discovered execution transport."""

    mode: ExecutionMode
    available: bool
    confidence: str  # high, medium, low
    detail: str = ""


# ---------------------------------------------------------------------------
# Verbose logger
# ---------------------------------------------------------------------------

class _VerboseLog:
    """Collects verbose log lines for diagnostic output."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.lines: list[str] = []

    def log(self, msg: str) -> None:
        self.lines.append(msg)

    def print_if_enabled(self) -> None:
        if self.enabled:
            for line in self.lines:
                print(f"  [verbose] {line}")


# ---------------------------------------------------------------------------
# RSTD .NET Remoting transport
# ---------------------------------------------------------------------------

_RSTD_PORT = 2777
_RSTD_HOST = "127.0.0.1"
_RSTD_SUCCESS_CODE = 30000

# Optional imports — deferred to avoid hard dependency
_HAVE_PYTHONNET = False
_pythonnet_error = ""
try:
    import clr  # type: ignore[import-untyped]
    _HAVE_PYTHONNET = True
except ImportError as e:
    _pythonnet_error = str(e)

_HAVE_PYWINAUTO = False
_pywinauto_error = ""
try:
    import pywinauto  # type: ignore[import-untyped]
    _HAVE_PYWINAUTO = True
except ImportError as e:
    _pywinauto_error = str(e)


def _is_rstd_port_open(host: str = _RSTD_HOST, port: int = _RSTD_PORT, timeout: float = 1.0) -> bool:
    """Check if RSTD .NET Remoting port is listening."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (ConnectionRefusedError, TimeoutError, OSError):
        return False


def _find_rtttnet_dll() -> Path | None:
    """Find RtttNetClientAPI.dll in TI installation."""
    candidates = [
        Path("C:/ti"),
    ]
    for base in candidates:
        if not base.exists():
            continue
        for child in sorted(base.iterdir(), reverse=True):  # prefer newest
            if child.is_dir() and "mmwave_studio" in child.name.lower():
                dll = child / "mmWaveStudio" / "Clients" / "RtttNetClientController" / "RtttNetClientAPI.dll"
                if dll.exists():
                    return dll
    return None


def _extract_version_from_path(path: Path | str) -> str | None:
    """Extract mmwave_studio version string from a path like C:/ti/mmwave_studio_03_01_04_04/..."""
    import re
    match = re.search(r"mmwave_studio_(\d+_\d+_\d+_\d+)", str(path))
    return match.group(1) if match else None


def _get_mmws_process_path() -> Path | None:
    """Get the full path of the running mmWaveStudio.exe process.

    May fail if mmWaveStudio runs elevated but the current shell is not elevated.
    Tries Get-Process first, then Get-CimInstance Win32_Process.
    """
    # Method 1: Get-Process -ExpandProperty Path
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "Get-Process mmWaveStudio -ErrorAction SilentlyContinue | "
             "Select-Object -ExpandProperty Path"],
            capture_output=True, text=True, timeout=5,
        )
        path_str = result.stdout.strip()
        if path_str:
            return Path(path_str)
    except Exception:
        pass

    # Method 2: CimInstance Win32_Process
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "(Get-CimInstance Win32_Process -Filter \"Name = 'mmWaveStudio.exe'\" "
             "| Select-Object -First 1).ExecutablePath"],
            capture_output=True, text=True, timeout=5,
        )
        path_str = result.stdout.strip()
        if path_str:
            return Path(path_str)
    except Exception:
        pass

    return None


def _find_mmws_dir() -> Path | None:
    """Find the mmWave Studio installation directory."""
    candidates = sorted(Path("C:/ti").glob("mmwave_studio_*/mmWaveStudio"), reverse=True)
    return candidates[0] if candidates else None


def _read_last_worker_step(progress_file: Path) -> str | None:
    """Read the JSONL progress log and return the last step name."""
    import json
    if not progress_file.exists():
        return None
    last_step = None
    for line in progress_file.read_text(encoding="utf-8").strip().splitlines():
        try:
            entry = json.loads(line)
            last_step = entry.get("step", last_step)
        except Exception:
            continue
    return last_step


def _run_rstd_worker_subprocess(
    lua_cmd: str,
    timeout: float,
    vlog: _VerboseLog,
    *,
    step: str | None = None,
    method: str = "SendCommand",
    cwd_mode: str = "default",
) -> tuple[int, str | None]:
    """Execute RSTD commands via an isolated worker subprocess to enforce strict timeouts.

    Returns (return_code, error_string).
    30000 = command accepted.
    """
    import json
    import tempfile

    dll_path = _find_rtttnet_dll()
    if not dll_path:
        return -1, "RtttNetClientAPI.dll not found in TI installation"

    vlog.log(f"DLL path: {dll_path}")

    # Determine CWD
    cwd: str | None = None
    if cwd_mode == "mmwave-studio":
        mmws_dir = _find_mmws_dir()
        if mmws_dir:
            cwd = str(mmws_dir)
            vlog.log(f"Worker CWD: {cwd} (mmwave-studio mode)")
        else:
            vlog.log("mmWave Studio directory not found, using default CWD")

    # Create temporary files for command and worker result
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        cmd_file = temp_path / "cmd.txt"
        worker_result_file = temp_path / "worker_result.json"
        progress_file = temp_path / "progress.jsonl"

        cmd_file.write_text(lua_cmd, encoding="utf-8")
        vlog.log(f"Worker command path: {cmd_file}")
        vlog.log(f"Lua command string: {lua_cmd!r}")

        cmd = [
            sys.executable, "-m", "awr2944_dca.mmws.rstd_worker",
            "--dll", str(dll_path),
            "--host", _RSTD_HOST,
            "--port", str(_RSTD_PORT),
            "--command-file", str(cmd_file),
            "--result-file", str(worker_result_file),
            "--progress-file", str(progress_file),
            "--method", method,
        ]
        if step:
            cmd.extend(["--step", step])

        vlog.log(f"Subprocess started: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd
            )
            vlog.log(f"Subprocess returned: {result.returncode}")
            if result.stdout:
                vlog.log(f"Subprocess stdout: {result.stdout.strip()}")
            if result.stderr:
                vlog.log(f"Subprocess stderr: {result.stderr.strip()}")

        except subprocess.TimeoutExpired:
            last_step = _read_last_worker_step(progress_file)
            step_info = f" last_worker_step={last_step}" if last_step else ""
            vlog.log(f"Subprocess timed out after {timeout}s{step_info}")
            # Log progress contents
            if progress_file.exists():
                vlog.log(f"Progress log:\n{progress_file.read_text(encoding='utf-8')}")
            return -1, f"SENDCOMMAND_TIMEOUT: exceeded {timeout}s{step_info}"
        except Exception as e:
            vlog.log(f"Subprocess exception: {e}")
            return -1, f"Worker subprocess exception: {e}"

        # Log progress contents on success too
        if progress_file.exists():
            vlog.log(f"Progress log:\n{progress_file.read_text(encoding='utf-8')}")

        if not worker_result_file.exists():
            return -1, "Worker subprocess failed to produce result JSON."

        try:
            worker_data = json.loads(worker_result_file.read_text(encoding="utf-8"))
            vlog.log(f"worker_result.json contents: {json.dumps(worker_data)}")
        except Exception as e:
            vlog.log(f"worker_result.json parse error: {e}")
            return -1, f"Failed to parse worker_result.json: {e}"

        if worker_data.get("exception"):
            return -1, f"Worker exception: {worker_data['exception']}"

        send_ret = worker_data.get("send_return")
        if send_ret == _RSTD_SUCCESS_CODE:
            return send_ret, None
        if send_ret is not None:
            return send_ret, f"Worker SendCommand returned {send_ret} (expected {_RSTD_SUCCESS_CODE})"
        # For step-limited runs where send was not reached, that's OK
        if step:
            return 0, None
        return -1, "Worker did not produce send_return"


def run_rstd_worker_test(
    step: str,
    timeout: float = 10.0,
    verbose: bool = False,
    cwd_mode: str = "default",
    method: str = "SendCommand",
    lua_result_dir: Path | None = None,
) -> dict:
    """Run the RSTD worker subprocess up to a specific step for diagnostics.

    Returns a dict with step results, last_step, exception, etc.
    For runscript-file and sendcommand-dofile steps, generates a real Lua file
    that writes a result JSON, and checks for that result file after execution.
    """
    import json
    import tempfile

    vlog = _VerboseLog(verbose)
    dll_path = _find_rtttnet_dll()
    if not dll_path:
        return {"success": False, "error": "RtttNetClientAPI.dll not found"}

    cwd: str | None = None
    if cwd_mode == "mmwave-studio":
        mmws_dir = _find_mmws_dir()
        if mmws_dir:
            cwd = str(mmws_dir)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        worker_result_file = temp_path / "worker_result.json"
        progress_file = temp_path / "progress.jsonl"
        cmd_file = temp_path / "cmd.txt"
        cmd_file.write_text('WriteToLog("RSTD_WORKER_TEST\\n", "green")', encoding="utf-8")

        # For runscript-file and sendcommand-dofile, generate a real Lua file
        lua_file_path: str | None = None
        lua_result_file: Path | None = None
        if step in ("runscript-file", "sendcommand-dofile"):
            if lua_result_dir is None:
                lua_result_dir = Path.cwd() / "ti" / "probe_logs"
            lua_result_dir.mkdir(parents=True, exist_ok=True)

            lua_result_file = lua_result_dir / f"rstd_{step.replace('-', '_')}_result.json"
            lua_script_file = lua_result_dir / f"rstd_{step.replace('-', '_')}_test.lua"

            # Clean up stale result
            if lua_result_file.exists():
                lua_result_file.unlink()

            # Write the Lua script
            result_path_fwd = str(lua_result_file.resolve()).replace("\\", "/")
            lua_content = (
                f'local f = io.open([[{result_path_fwd}]], "w")\n'
                f'if f then\n'
                f'    f:write([[{{"executed":true,"method":"{step}"}}]])\n'
                f'    f:close()\n'
                f'end\n'
            )
            lua_script_file.write_text(lua_content, encoding="utf-8")
            lua_file_path = str(lua_script_file.resolve())
            vlog.log(f"Generated Lua file: {lua_file_path}")
            vlog.log(f"Expected result: {lua_result_file}")

        cmd = [
            sys.executable, "-m", "awr2944_dca.mmws.rstd_worker",
            "--dll", str(dll_path),
            "--host", _RSTD_HOST,
            "--port", str(_RSTD_PORT),
            "--command-file", str(cmd_file),
            "--result-file", str(worker_result_file),
            "--progress-file", str(progress_file),
            "--step", step,
            "--method", method,
        ]
        if lua_file_path:
            cmd.extend(["--lua-file", lua_file_path])

        vlog.log(f"Worker test: step={step}, cwd_mode={cwd_mode}, method={method}")
        vlog.log(f"Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd,
            )
        except subprocess.TimeoutExpired:
            last_step = _read_last_worker_step(progress_file)
            progress_text = ""
            if progress_file.exists():
                progress_text = progress_file.read_text(encoding="utf-8")
            vlog.print_if_enabled()
            return {
                "success": False,
                "error": f"TIMEOUT after {timeout}s",
                "last_worker_step": last_step,
                "progress": progress_text,
                "verbose_log": vlog.lines,
            }
        except Exception as e:
            vlog.print_if_enabled()
            return {"success": False, "error": str(e), "verbose_log": vlog.lines}

        progress_text = ""
        if progress_file.exists():
            progress_text = progress_file.read_text(encoding="utf-8")

        worker_data = {}
        if worker_result_file.exists():
            try:
                worker_data = json.loads(worker_result_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        vlog.log(f"stdout: {result.stdout.strip()}" if result.stdout else "stdout: (empty)")
        vlog.log(f"stderr: {result.stderr.strip()}" if result.stderr else "stderr: (empty)")
        vlog.log(f"worker_result: {json.dumps(worker_data)}")

        # Check Lua-side result file for runscript-file/sendcommand-dofile
        lua_result_data = None
        if lua_result_file and lua_result_file.exists():
            try:
                lua_result_data = json.loads(lua_result_file.read_text(encoding="utf-8"))
                vlog.log(f"Lua result JSON: {json.dumps(lua_result_data)}")
            except Exception as e:
                vlog.log(f"Lua result parse error: {e}")

        vlog.print_if_enabled()

        return {
            "success": worker_data.get("exception") is None,
            "worker_result": worker_data,
            "progress": progress_text,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "verbose_log": vlog.lines,
            "lua_result": lua_result_data,
        }


def run_rstd_get_last_error(timeout: float = 10.0, verbose: bool = False) -> dict:
    """Run Init + Connect, then call GetLastError/GetErrMsg via isolated subprocess."""
    import json
    import tempfile

    vlog = _VerboseLog(verbose)
    dll_path = _find_rtttnet_dll()
    if not dll_path:
        return {"success": False, "error": "RtttNetClientAPI.dll not found"}

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        worker_result_file = temp_path / "worker_result.json"
        progress_file = temp_path / "progress.jsonl"

        cmd = [
            sys.executable, "-m", "awr2944_dca.mmws.rstd_worker",
            "--dll", str(dll_path),
            "--host", _RSTD_HOST,
            "--port", str(_RSTD_PORT),
            "--mode", "get-last-error",
            "--result-file", str(worker_result_file),
            "--progress-file", str(progress_file),
        ]

        vlog.log(f"Get-last-error command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            last_step = _read_last_worker_step(progress_file)
            vlog.print_if_enabled()
            return {
                "success": False,
                "error": f"TIMEOUT after {timeout}s",
                "last_worker_step": last_step,
            }
        except Exception as e:
            vlog.print_if_enabled()
            return {"success": False, "error": str(e)}

        if not worker_result_file.exists():
            vlog.print_if_enabled()
            return {"success": False, "error": "Worker failed to produce result", "stderr": result.stderr}

        try:
            worker_data = json.loads(worker_result_file.read_text(encoding="utf-8"))
        except Exception as e:
            vlog.print_if_enabled()
            return {"success": False, "error": f"Parse error: {e}"}

        vlog.log(f"Get-last-error result: {json.dumps(worker_data)}")
        vlog.print_if_enabled()

        return {
            "success": worker_data.get("exception") is None,
            "last_error": worker_data.get("last_error"),
            "error_msg": worker_data.get("error_msg"),
            "exception": worker_data.get("exception"),
            "elapsed_seconds": worker_data.get("elapsed_seconds"),
        }


def run_rstd_introspect(timeout: float = 10.0, verbose: bool = False) -> dict:
    """Load RtttNetClientAPI.dll via a subprocess and list public methods.

    Runs introspection in an isolated subprocess so hangs are safely killed.
    """
    import json
    import tempfile

    vlog = _VerboseLog(verbose)
    dll_path = _find_rtttnet_dll()
    if not dll_path:
        return {"success": False, "error": "RtttNetClientAPI.dll not found"}

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        worker_result_file = temp_path / "worker_result.json"
        progress_file = temp_path / "progress.jsonl"

        cmd = [
            sys.executable, "-m", "awr2944_dca.mmws.rstd_worker",
            "--dll", str(dll_path),
            "--mode", "introspect",
            "--result-file", str(worker_result_file),
            "--progress-file", str(progress_file),
        ]

        vlog.log(f"Introspect command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            last_step = _read_last_worker_step(progress_file)
            vlog.print_if_enabled()
            return {
                "success": False,
                "error": f"TIMEOUT after {timeout}s",
                "last_worker_step": last_step,
            }
        except Exception as e:
            vlog.print_if_enabled()
            return {"success": False, "error": str(e)}

        if not worker_result_file.exists():
            vlog.print_if_enabled()
            return {
                "success": False,
                "error": "Worker failed to produce result",
                "stderr": result.stderr,
            }

        try:
            worker_data = json.loads(worker_result_file.read_text(encoding="utf-8"))
        except Exception as e:
            vlog.print_if_enabled()
            return {"success": False, "error": f"Parse error: {e}"}

        vlog.log(f"Introspect result: {json.dumps(worker_data)}")
        vlog.print_if_enabled()

        return {
            "success": worker_data.get("exception") is None,
            "methods": worker_data.get("methods", []),
            "properties": worker_data.get("properties", []),
            "exception": worker_data.get("exception"),
            "elapsed_seconds": worker_data.get("elapsed_seconds"),
        }


def _execute_via_rstd(script_path: Path, verbose: bool = False, timeout: float = 30.0) -> ExecutionResult:
    """Execute a Lua script via RSTD .NET Remoting using dofile in a worker subprocess."""
    vlog = _VerboseLog(verbose)
    vlog.log(f"Script path: {script_path}")
    vlog.log(f"TCP {_RSTD_HOST}:{_RSTD_PORT} open: {_is_rstd_port_open()}")

    start = time.monotonic()
    lua_cmd = f'dofile([[{str(script_path.resolve())}]])'
    ret, err = _run_rstd_worker_subprocess(lua_cmd, timeout=timeout, vlog=vlog)

    elapsed = time.monotonic() - start
    vlog.print_if_enabled()
    return ExecutionResult(
        mode=ExecutionMode.RSTD_NET_REMOTING,
        success=(ret == _RSTD_SUCCESS_CODE),
        return_code=ret,
        elapsed_seconds=elapsed,
        error=err,
        verbose_log=vlog.lines,
        lua_command_sent=lua_cmd,
    )


def send_inline_lua(lua_cmd: str, verbose: bool = False, timeout: float = 5.0) -> ExecutionResult:
    """Send inline Lua directly via RSTD SendCommand (no dofile) in a worker subprocess."""
    vlog = _VerboseLog(verbose)
    vlog.log(f"Inline Lua: {lua_cmd!r}")
    vlog.log(f"TCP {_RSTD_HOST}:{_RSTD_PORT} open: {_is_rstd_port_open()}")

    start = time.monotonic()
    ret, err = _run_rstd_worker_subprocess(lua_cmd, timeout=timeout, vlog=vlog)
    elapsed = time.monotonic() - start
    vlog.print_if_enabled()
    return ExecutionResult(
        mode=ExecutionMode.RSTD_NET_REMOTING,
        success=(ret == _RSTD_SUCCESS_CODE),
        return_code=ret,
        elapsed_seconds=elapsed,
        error=err,
        verbose_log=vlog.lines,
        lua_command_sent=lua_cmd,
    )


def rstd_ping_diagnostic(
    result_dir: Path,
    verbose: bool = False,
    per_variant_timeout: float = 5.0,
    print_fn: Any = None,
) -> dict[str, Any]:
    """Run RSTD ping diagnostic: try multiple command formats.

    Tries inline Lua and dofile variants, reporting which one worked.
    Only used in diagnostic commands, not in normal execution.
    """
    import json

    result_dir.mkdir(parents=True, exist_ok=True)
    if not print_fn:
        print_fn = print

    results: dict[str, Any] = {
        "variants_tried": [],
        "working_variant": None,
        "all_failed": True,
    }

    variants = [
        "raw_inline",
        "raw_inline_semicolons",
        "write_to_log_only"
    ]

    try:
        for name in variants:
            print_fn(f"\n[bold cyan]Starting variant:[/bold cyan] {name}")
            result_file = result_dir / f"rstd_ping_{name}_result.json"
            abs_result = str(result_file.resolve()).replace("\\", "/")

            # Remove old result
            if result_file.exists():
                try:
                    result_file.unlink()
                except Exception as e:
                    print_fn(f"[yellow]Warning: could not delete stale file {result_file.name}: {e}[/yellow]")

            if name == "raw_inline":
                lua_cmd = (
                    f'local f = io.open([[{abs_result}]], "w") '
                    f'if f then '
                    f'f:write(\'{{\"executed\":true,\"source\":\"inline_rstd\",\"variant\":\"raw_inline\"}}\') '
                    f'f:close() '
                    f'end'
                )
            elif name == "raw_inline_semicolons":
                lua_cmd = (
                    f'local f = io.open([[{abs_result}]], "w"); '
                    f'if f then '
                    f'f:write(\'{{\"executed\":true,\"source\":\"inline_rstd\",\"variant\":\"raw_inline_semicolons\"}}\'); '
                    f'f:close(); '
                    f'end'
                )
            elif name == "write_to_log_only":
                lua_cmd = 'WriteToLog("RSTD_PING_OK\\n", "green")'

            entry: dict[str, Any] = {"name": name, "lua": lua_cmd}
            
            start_time = time.monotonic()
            exec_result = send_inline_lua(lua_cmd, verbose=verbose, timeout=per_variant_timeout)
            elapsed = time.monotonic() - start_time
            
            entry["return_code"] = exec_result.return_code
            entry["success_submit"] = exec_result.success
            entry["error"] = exec_result.error
            entry["verbose_log"] = exec_result.verbose_log
            entry["elapsed"] = elapsed

            print_fn(f"  SendCommand return code: {exec_result.return_code}")
            
            if "io.open" in lua_cmd:
                print_fn(f"  Expected result file: {result_file.name}")
            else:
                print_fn("  Expected result file: N/A (WriteToLog only)")

            if exec_result.success:
                # Wait briefly for file to appear (for file-writing variants)
                if "io.open" in lua_cmd:
                    poll_start = time.monotonic()
                    file_appeared = False
                    # Wait up to 2 seconds for the file to appear
                    while time.monotonic() - poll_start < 2.0:
                        if result_file.exists():
                            file_appeared = True
                            break
                        time.sleep(0.5)

                    if file_appeared:
                        try:
                            data = json.loads(result_file.read_text(encoding="utf-8"))
                            entry["result_json"] = data
                            entry["file_appeared"] = True
                            results["working_variant"] = name
                            results["all_failed"] = False
                            print_fn("  Result appeared: [green]yes[/green]")
                        except Exception as e:
                            entry["file_appeared"] = True
                            entry["parse_error"] = str(e)
                            print_fn(f"  Result appeared: [yellow]yes (parse failed: {e})[/yellow]")
                    else:
                        entry["file_appeared"] = False
                        print_fn("  Result appeared: [red]no[/red]")
                else:
                    # Non-file variant (e.g. WriteToLog) — success = submitted OK
                    entry["file_appeared"] = None
                    if results["working_variant"] is None:
                        results["working_variant"] = name
                        results["all_failed"] = False
                    print_fn("  Result appeared: [green]N/A (WriteToLog submitted OK)[/green]")
            else:
                entry["file_appeared"] = False
                if "TIMEOUT" in str(exec_result.error):
                    print_fn("  Error: [red]SENDCOMMAND_TIMEOUT[/red]")
                else:
                    print_fn(f"  Error: [red]{exec_result.error}[/red]")

            print_fn(f"  Elapsed time: {elapsed:.2f}s")
            results["variants_tried"].append(entry)

            if results["working_variant"] is not None:
                print_fn(f"\n[green]Stopping early because variant '{name}' succeeded.[/green]")
                break
                
    except KeyboardInterrupt:
        print_fn("\n[yellow]Diagnostic interrupted by user.[/yellow]")

    return results


# ---------------------------------------------------------------------------
# C# RSTD Bridge transport
# ---------------------------------------------------------------------------


def _find_csharp_bridge() -> Path | None:
    """Find the compiled MmwsRstdBridge.exe.

    Searches relative to the package installation (tools/MmwsRstdBridge/)
    and also common project-root locations.
    """
    # Try relative to this source file's project root
    src_root = Path(__file__).resolve().parent.parent.parent.parent  # src/awr2944_dca/mmws -> project root
    candidates = [
        src_root / "tools" / "MmwsRstdBridge" / "MmwsRstdBridge.exe",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def build_csharp_bridge(
    dll_path: Path | None = None,
    verbose: bool = False,
) -> tuple[bool, str]:
    """Build the C# RSTD bridge.

    Returns (success, message).
    """
    csc = Path(r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe")
    if not csc.exists():
        return False, f"csc.exe not found at {csc}"

    # Find the DLL
    if dll_path is None:
        dll_path = _find_rtttnet_dll()
    if dll_path is None:
        return False, "RtttNetClientAPI.dll not found in C:\\ti"
    dll_path = Path(dll_path)

    # Find source
    src_root = Path(__file__).resolve().parent.parent.parent.parent
    src_file = src_root / "tools" / "MmwsRstdBridge" / "MmwsRstdBridge.cs"
    out_file = src_root / "tools" / "MmwsRstdBridge" / "MmwsRstdBridge.exe"

    if not src_file.exists():
        return False, f"Source not found: {src_file}"

    lines = [
        f"csc.exe: {csc}",
        f"RtttNetClientAPI.dll: {dll_path}",
        f"Platform: x86",
        f"Source: {src_file}",
        f"Output: {out_file}",
    ]

    # DLL architecture check
    try:
        with open(dll_path, "rb") as f:
            data = f.read(1024)
        import struct
        pe_off = struct.unpack_from("<I", data, 0x3C)[0]
        machine = struct.unpack_from("<H", data, pe_off + 4)[0]
        arch_map = {0x14C: "x86 (32-bit)", 0x8664: "x64 (64-bit)"}
        arch_str = arch_map.get(machine, f"unknown (0x{machine:X})")
        lines.append(f"DLL architecture: {arch_str}")
        if machine != 0x14C:
            lines.append("WARNING: DLL is not x86. Build may fail with BadImageFormatException.")
    except Exception as e:
        lines.append(f"DLL architecture check failed: {e}")

    # Compile
    cmd = [
        str(csc),
        "/target:exe",
        "/platform:x86",
        "/optimize+",
        f"/reference:{dll_path}",
        f"/out:{out_file}",
        str(src_file),
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            size = out_file.stat().st_size if out_file.exists() else 0
            lines.append(f"BUILD SUCCESS ({size} bytes)")
            return True, "\n".join(lines)
        else:
            lines.append(f"BUILD FAILED (exit code {result.returncode})")
            lines.append(result.stdout.strip())
            lines.append(result.stderr.strip())
            return False, "\n".join(lines)
    except subprocess.TimeoutExpired:
        return False, "\n".join(lines) + "\nBuild timed out after 30s"
    except Exception as e:
        return False, "\n".join(lines) + f"\nBuild error: {e}"


def _execute_via_csharp_bridge(
    script_path: Path,
    verbose: bool = False,
    timeout: float = 10.0,
    bridge_mode: str = "send-command",
    apartment: str = "mta",
) -> ExecutionResult:
    """Execute a Lua script via the C# RSTD bridge subprocess.

    The bridge does: Init + Connect + SendCommand('dofile([[script]])').
    Python waits for the subprocess, then checks the worker result JSON.
    The Lua-side result file is checked separately by the caller.
    """
    vlog = _VerboseLog(verbose)
    start = time.monotonic()

    bridge_exe = _find_csharp_bridge()
    if bridge_exe is None:
        elapsed = time.monotonic() - start
        vlog.log("MmwsRstdBridge.exe not found. Run: awr mmws csharp-bridge build")
        vlog.print_if_enabled()
        return ExecutionResult(
            mode=ExecutionMode.CSHARP_RSTD,
            success=False,
            error="MmwsRstdBridge.exe not found. Run: awr mmws csharp-bridge build",
            elapsed_seconds=elapsed,
            verbose_log=vlog.lines,
        )

    script_path = Path(script_path).resolve()
    vlog.log(f"Bridge exe: {bridge_exe}")
    vlog.log(f"Script: {script_path}")
    vlog.log(f"Bridge mode: {bridge_mode}")

    # Create temp dir for worker result
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        worker_result_path = Path(tmpdir) / "worker_result.json"

        # Find the DLL directory for AssemblyResolve
        dll_path = _find_rtttnet_dll()
        dll_dir = str(Path(dll_path).parent) if dll_path else None

        cmd = [
            str(bridge_exe),
            "--mode", bridge_mode,
            "--script", str(script_path),
            "--result", str(worker_result_path),
            "--host", _RSTD_HOST,
            "--port", str(_RSTD_PORT),
            "--apartment", apartment,
        ]
        if dll_dir:
            cmd.extend(["--dll-dir", dll_dir])
        if verbose:
            cmd.append("--verbose")

        vlog.log(f"Command: {' '.join(cmd)}")

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                # Set cwd to DLL directory so .NET can find dependent assemblies
                cwd=dll_dir if dll_dir else None,
            )

            if verbose and proc.stderr:
                for line in proc.stderr.strip().splitlines():
                    vlog.log(f"[bridge] {line}")

            # Parse worker result
            import json
            worker_data = {}
            if worker_result_path.exists():
                try:
                    worker_data = json.loads(worker_result_path.read_text())
                except Exception:
                    pass

            vlog.log(f"Worker exit code: {proc.returncode}")
            vlog.log(f"Worker result file exists: {worker_result_path.exists()}")

            send_ret = worker_data.get("send_return") or worker_data.get("runscript_return")
            exception = worker_data.get("exception")
            lua_cmd = worker_data.get("lua_command", "")

            if send_ret is not None:
                vlog.log(f"Send/RunScript return: {send_ret}")

            elapsed = time.monotonic() - start
            vlog.print_if_enabled()

            # Check for bridge-level errors
            if exception is not None:
                return ExecutionResult(
                    mode=ExecutionMode.CSHARP_RSTD,
                    success=False,
                    return_code=send_ret,
                    error=f"Bridge exception: {exception}",
                    elapsed_seconds=elapsed,
                    verbose_log=vlog.lines,
                    lua_command_sent=lua_cmd,
                )

            # SendCommand 30000 = submission accepted (per TI docs)
            success = send_ret == 30000 if bridge_mode == "send-command" else send_ret is not None

            return ExecutionResult(
                mode=ExecutionMode.CSHARP_RSTD,
                success=success,
                return_code=send_ret,
                elapsed_seconds=elapsed,
                verbose_log=vlog.lines,
                lua_command_sent=lua_cmd,
            )

        except subprocess.TimeoutExpired as e:
            elapsed = time.monotonic() - start
            last_step = "unknown"
            if e.stdout:
                # Parse stdout for STEP_START / STEP_DONE
                lines = e.stdout.splitlines()
                for line in lines:
                    if line.startswith("STEP_START:"):
                        last_step = "before_" + line.split(":", 1)[1].strip()
                    elif line.startswith("STEP_DONE:"):
                        last_step = "after_" + line.split(":", 1)[1].strip()

            vlog.log(f"Bridge subprocess timed out after {timeout}s")
            vlog.log(f"CSHARP_RSTD_HUNG_AT_{last_step.upper()}")
            vlog.print_if_enabled()
            return ExecutionResult(
                mode=ExecutionMode.CSHARP_RSTD,
                success=False,
                error=f"HARDWARE_SCRIPT_TIMEOUT (CSHARP_RSTD_HUNG_AT_{last_step.upper()})",
                elapsed_seconds=elapsed,
                verbose_log=vlog.lines,
            )
        except Exception as e:
            elapsed = time.monotonic() - start
            vlog.log(f"Bridge subprocess error: {e}")
            vlog.print_if_enabled()
            return ExecutionResult(
                mode=ExecutionMode.CSHARP_RSTD,
                success=False,
                error=str(e),
                elapsed_seconds=elapsed,
                verbose_log=vlog.lines,
            )


# ---------------------------------------------------------------------------
# pywinauto UI Lua Shell transport
# ---------------------------------------------------------------------------


def _execute_via_pywinauto(
    script_path: Path,
    verbose: bool = False,
    focused_only: bool = False,
) -> ExecutionResult:
    """Execute a Lua script using pywinauto to paste into the Lua Shell.

    This is a TRANSPORT ONLY — it submits Lua to the existing Lua Shell.

    If focused_only=True, it skips searching for the window and control,
    assuming the user has manually focused the Lua Shell input. It just
    pastes the command and presses Enter.
    """
    vlog = _VerboseLog(verbose)
    start = time.monotonic()
    try:
        from pywinauto import Application  # type: ignore[import-untyped]
        from pywinauto import keyboard  # type: ignore[import-untyped]
        import pyperclip  # type: ignore[import-untyped]

        lua_shell = None
        for ctrl in main_window.descendants():
            try:
                class_name = ctrl.class_name()
            except Exception:
                continue
            if "scintilla" in class_name.lower():
                lua_shell = ctrl
                vlog.log(f"Found Scintilla control: class={class_name}")
                break

        # Strategy 2: Look for a control with "Lua" in the text
        if lua_shell is None:
            for ctrl in main_window.descendants():
                try:
                    ctrl_text = ctrl.window_text()
                    class_name = ctrl.class_name()
                except Exception:
                    continue
                if "lua" in ctrl_text.lower() and ("edit" in class_name.lower()
                        or "scintilla" in class_name.lower()
                        or "textbox" in class_name.lower()):
                    lua_shell = ctrl
                    vlog.log(f"Found Lua control: class={class_name}, text={ctrl_text[:50]}")
                    break

        if not focused_only and lua_shell is None:
            elapsed = time.monotonic() - start
            vlog.print_if_enabled()
            return ExecutionResult(
                mode=ExecutionMode.UI_LUA_SHELL,
                success=False,
                error="Could not find Lua Shell input in mmWave Studio. "
                      "Open/show Lua Shell in mmWave Studio or use RSTD if available.",
                elapsed_seconds=elapsed,
                verbose_log=vlog.lines,
            )

        # Use clipboard paste for reliability (type_keys can lose characters)
        try:
            old_clipboard = pyperclip.paste()
        except Exception:
            old_clipboard = ""

        try:
            if lua_shell:
                lua_shell.set_focus()
                time.sleep(0.2)
            elif focused_only:
                # Give user a tiny window if they just alt-tabbed back
                time.sleep(0.5)
            pyperclip.copy(dofile_cmd)
            keyboard.send_keys("^v")  # Ctrl+V
            time.sleep(0.1)
            keyboard.send_keys("{ENTER}")
            vlog.log(f"Pasted and sent: {dofile_cmd}")
        finally:
            # Restore clipboard
            try:
                pyperclip.copy(old_clipboard)
            except Exception:
                pass

        elapsed = time.monotonic() - start
        vlog.print_if_enabled()
        return ExecutionResult(
            mode=ExecutionMode.UI_LUA_SHELL,
            success=True,
            elapsed_seconds=elapsed,
            verbose_log=vlog.lines,
            lua_command_sent=dofile_cmd,
        )
    except ImportError as e:
        elapsed = time.monotonic() - start
        vlog.print_if_enabled()
        missing = "pyperclip" if "pyperclip" in str(e) else "pywinauto"
        return ExecutionResult(
            mode=ExecutionMode.UI_LUA_SHELL,
            success=False,
            error=f"{missing} not installed. "
                  f"Install: python -m pip install -e \".[automation]\"",
            elapsed_seconds=elapsed,
            verbose_log=vlog.lines,
        )
    except Exception as e:
        elapsed = time.monotonic() - start
        vlog.print_if_enabled()
        error_msg = str(e)
        # Detect elevation mismatch: pywinauto can't access elevated process
        if "not found" in error_msg.lower() and _is_mmws_running():
            error_msg = (
                "mmWave Studio is running but inaccessible to pywinauto. "
                "This usually means mmWave Studio runs as administrator but "
                "Python does not. Either:\n"
                "  1. Run Python/terminal as administrator, OR\n"
                "  2. Run mmWave Studio without 'Run as administrator'"
            )
        return ExecutionResult(
            mode=ExecutionMode.UI_LUA_SHELL,
            success=False,
            error=error_msg,
            elapsed_seconds=elapsed,
            verbose_log=vlog.lines,
        )


# ---------------------------------------------------------------------------
# CLI Launch transport
# ---------------------------------------------------------------------------


def _find_mmws_exe() -> Path | None:
    """Find mmWaveStudio.exe."""
    base = Path("C:/ti")
    if not base.exists():
        return None
    for child in sorted(base.iterdir(), reverse=True):  # prefer newest
        if child.is_dir() and "mmwave_studio" in child.name.lower():
            exe = child / "mmWaveStudio" / "RunTime" / "mmWaveStudio.exe"
            if exe.exists():
                return exe
    return None


def _is_mmws_running() -> bool:
    """Check if mmWaveStudio.exe is currently running."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq mmWaveStudio.exe", "/NH"],
            capture_output=True, text=True, timeout=5,
        )
        return "mmWaveStudio.exe" in result.stdout
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def detect_available_modes() -> list[TransportInfo]:
    """Discover which execution transports are available right now."""
    modes: list[TransportInfo] = []

    # C# RSTD Bridge (primary transport)
    bridge = _find_csharp_bridge()
    port_open = _is_rstd_port_open()
    if bridge and _is_rstd_port_open():
        running = _is_mmws_running()
        if not running:
            modes.append(TransportInfo(
                mode=ExecutionMode.CSHARP_RSTD,
                available=False,
                confidence="low",
                detail=f"MmwsRstdBridge.exe alive (TCP:{_RSTD_PORT} open) but mmWaveStudio.exe is NOT running. Stale bridge.",
            ))
        else:
            modes.append(TransportInfo(
                mode=ExecutionMode.CSHARP_RSTD,
                available=True,
                confidence="high",
                detail=f"MmwsRstdBridge.exe found, TCP:{_RSTD_PORT} open, mmWaveStudio running",
            ))
    elif bridge:
        modes.append(TransportInfo(
            mode=ExecutionMode.CSHARP_RSTD,
            available=False,
            confidence="medium",
            detail=f"Bridge built but TCP:{_RSTD_PORT} not open. "
                   f"Is mmWave Studio running?",
        ))
    else:
        modes.append(TransportInfo(
            mode=ExecutionMode.CSHARP_RSTD,
            available=False,
            confidence="low",
            detail="MmwsRstdBridge.exe not found. Run: awr mmws csharp-bridge build",
        ))

    # pywinauto (fallback)
    if _HAVE_PYWINAUTO:
        running = _is_mmws_running()
        modes.append(TransportInfo(
            mode=ExecutionMode.UI_LUA_SHELL,
            available=running,
            confidence="medium" if running else "low",
            detail="mmWave Studio running" if running else "mmWave Studio not running",
        ))
    else:
        modes.append(TransportInfo(
            mode=ExecutionMode.UI_LUA_SHELL,
            available=False,
            confidence="low",
            detail=f"pywinauto not installed: {_pywinauto_error}. "
                   f"Install: python -m pip install -e \".[automation]\"",
        ))

    # RSTD .NET Remoting (legacy/diagnostic only)
    if _HAVE_PYTHONNET:
        dll = _find_rtttnet_dll()
        if dll and port_open:
            modes.append(TransportInfo(
                mode=ExecutionMode.RSTD_NET_REMOTING,
                available=True,
                confidence="low",
                detail=f"Pythonnet RSTD (legacy, known unreliable). "
                       f"Use csharp-rstd instead.",
            ))
        else:
            modes.append(TransportInfo(
                mode=ExecutionMode.RSTD_NET_REMOTING,
                available=False,
                confidence="low",
                detail="Legacy Pythonnet RSTD not recommended",
            ))

    # CLI launch via mmWaveStudio.exe /lua
    # Proven to execute Lua and write result files (manual test confirmed).
    # WARNING: may launch a new instance; does not guarantee current GUI session state.
    # Safe for smoke tests and standalone scripts.
    exe = _find_mmws_exe()
    if exe:
        modes.append(TransportInfo(
            mode=ExecutionMode.CLI_LAUNCH,
            available=True,
            confidence="medium",  # proven for standalone scripts; session-isolation caveat
            detail=(
                f"mmWaveStudio.exe found: {exe}. "
                "Proven to execute Lua + write result files. "
                "WARNING: may open new instance, does not preserve current session."
            ),
        ))
    else:
        modes.append(TransportInfo(
            mode=ExecutionMode.CLI_LAUNCH,
            available=False,
            confidence="low",
            detail="mmWaveStudio.exe not found in C:\\ti",
        ))

    # Manual (always available but only when explicitly requested)
    modes.append(TransportInfo(
        mode=ExecutionMode.MANUAL_ONE_SHOT,
        available=True,
        confidence="high",
        detail="Always available (debug/fallback, must be explicitly requested)",
    ))

    return modes



def _execute_matlab_bridge(
    script_path: Path,
    verbose: bool = False,
    timeout: float = 10.0,
    bridge_mode: str = "send-command",
) -> ExecutionResult:
    """Execute via MATLAB -batch."""
    vlog = _VerboseLog(verbose)
    start = time.monotonic()

    from .matlab_bridge import find_matlab, build_matlab_script
    matlab_exe = find_matlab()
    if not matlab_exe:
        vlog.log("MATLAB not found. Ensure matlab is on PATH or installed in C:\\Program Files\\MATLAB")
        return ExecutionResult(
            mode=ExecutionMode.MATLAB_RSTD,
            success=False,
            error="MATLAB not found",
            elapsed_seconds=time.monotonic() - start,
        )

    vlog.log(f"MATLAB exe: {matlab_exe}")

    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        m_script_path = Path(tmpdir) / "run_bridge.m"
        result_path = Path(tmpdir) / "worker_result.json"

        dll_path = _find_rtttnet_dll()
        
        m_content = build_matlab_script(
            dll_path=str(dll_path),
            mode=bridge_mode,
            script_path=str(script_path),
            result_path=str(result_path),
            host=_RSTD_HOST,
            port=_RSTD_PORT,
        )
        m_script_path.write_text(m_content, encoding="utf-8")
        
        if verbose:
            vlog.log("MATLAB Script:")
            for line in m_content.splitlines():
                vlog.log(f"  {line}")

        cmd = [matlab_exe, "-wait", "-batch", "run_bridge"]
        vlog.log(f"Command: {' '.join(cmd)}")

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(tmpdir),
            )

            if verbose and proc.stdout:
                for line in proc.stdout.strip().splitlines():
                    vlog.log(f"[matlab] {line}")
            if verbose and proc.stderr:
                for line in proc.stderr.strip().splitlines():
                    vlog.log(f"[matlab err] {line}")

            import json
            worker_data = {}
            if result_path.exists():
                try:
                    worker_data = json.loads(result_path.read_text())
                except Exception:
                    pass

            vlog.log(f"MATLAB exit code: {proc.returncode}")
            
            exception = worker_data.get("exception")
            success = worker_data.get("success", False)
            
            elapsed = time.monotonic() - start
            if proc.returncode != 0:
                return ExecutionResult(
                    mode=ExecutionMode.MATLAB_RSTD,
                    success=False,
                    error=f"MATLAB process exited with code {proc.returncode}",
                    elapsed_seconds=elapsed,
                    verbose_log=vlog.lines,
                )
            
            if not result_path.exists():
                return ExecutionResult(
                    mode=ExecutionMode.MATLAB_RSTD,
                    success=False,
                    error="MATLAB did not produce worker_result.json",
                    elapsed_seconds=elapsed,
                    verbose_log=vlog.lines,
                )
            
            if exception:
                return ExecutionResult(
                    mode=ExecutionMode.MATLAB_RSTD,
                    success=False,
                    error=f"MATLAB bridge exception: {exception}",
                    elapsed_seconds=elapsed,
                    verbose_log=vlog.lines,
                )
                
            return ExecutionResult(
                mode=ExecutionMode.MATLAB_RSTD,
                success=success,
                elapsed_seconds=elapsed,
                verbose_log=vlog.lines,
            )

        except subprocess.TimeoutExpired as e:
            elapsed = time.monotonic() - start
            last_step = "unknown"
            if e.stdout:
                lines = e.stdout.decode('utf-8', errors='replace').splitlines()
                for line in lines:
                    if line.startswith("STEP_START:"):
                        last_step = "before_" + line.split(":", 1)[1].strip()
                    elif line.startswith("STEP_DONE:"):
                        last_step = "after_" + line.split(":", 1)[1].strip()

            vlog.log(f"MATLAB timed out after {timeout}s")
            vlog.log(f"MATLAB_RSTD_HUNG_AT_{last_step.upper()}")
            return ExecutionResult(
                mode=ExecutionMode.MATLAB_RSTD,
                success=False,
                error=f"HARDWARE_SCRIPT_TIMEOUT (MATLAB_RSTD_HUNG_AT_{last_step.upper()})",
                elapsed_seconds=elapsed,
                verbose_log=vlog.lines,
            )

def _execute_lua_launch(
    script_path: Path,
    verbose: bool = False,
    timeout: float = 30.0,
    result_path: Path | None = None,
) -> ExecutionResult:
    """Execute via mmWaveStudio.exe /lua <script_path>.

    lua-launch scripts run before Startup.lua finishes, so they must be
    fully self-contained: no WriteToLog, no ar1, no Startup helpers.

    Success criteria (when result_path is given):
      1. Result JSON file exists
      2. JSON is valid and contains "executed": true
    Process exit is NOT required — mmWaveStudio.exe typically stays open.
    The Startup.lua warning is expected and harmless for standalone scripts.
    """
    vlog = _VerboseLog(verbose)
    start = time.monotonic()

    exe = _find_mmws_exe()
    if not exe:
        return ExecutionResult(
            mode=ExecutionMode.LUA_LAUNCH,
            success=False,
            error="mmWaveStudio.exe not found",
            elapsed_seconds=time.monotonic() - start,
        )

    cmd = [str(exe), "/lua", str(script_path)]
    vlog.log(f"Command: {' '.join(cmd)}")
    vlog.log(f"Script: {script_path}")
    if result_path:
        vlog.log(f"Expected result: {result_path}")

    # Use Popen so we can poll for the result file while the process runs.
    # mmWaveStudio.exe typically does NOT exit after /lua — it stays open.
        # Prepend required DLL paths to PATH to avoid EntryPointNotFoundExceptions
    import os
    env = os.environ.copy()
    ar1x_path = "C:\\ti\\mmwave_studio_03_01_04_04\\mmWaveStudio\\Clients\\AR1xController"
    runtime_path = "C:\\ti\\mmwave_studio_03_01_04_04\\mmWaveStudio\\RunTime"
    current_path = env.get("PATH", "")
    env["PATH"] = f"{ar1x_path};{runtime_path};{current_path}"
    
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env,
        cwd=runtime_path,
    )

    # Poll for result file (primary success signal) or process exit
    poll_interval = 0.5
    deadline = time.monotonic() + timeout
    result_found = False

    while time.monotonic() < deadline:
        # Check if result file appeared
        if result_path and result_path.exists():
            # Give a tiny extra delay for file to finish writing
            time.sleep(0.3)
            result_found = True
            break
        # Check if process exited
        retcode = proc.poll()
        if retcode is not None:
            vlog.log(f"Process exited with code {retcode}")
            break
        time.sleep(poll_interval)

    elapsed = time.monotonic() - start

    # Collect any stdout/stderr without blocking
    try:
        stdout, stderr = proc.communicate(timeout=2)
    except subprocess.TimeoutExpired:
        stdout, stderr = "", ""
    if verbose and stdout:
        for line in stdout.strip().splitlines():
            vlog.log(f"[studio] {line}")
    if verbose and stderr:
        for line in stderr.strip().splitlines():
            vlog.log(f"[studio err] {line}")

    still_alive = proc.poll() is None
    vlog.log(f"Process still running: {still_alive}")

    # --- Validate result file ---
    if result_path:
        if not result_path.exists():
            vlog.log(f"Result file not found: {result_path}")
            vlog.log(f"Generated script: {script_path}")
            vlog.log("Check the mmWave Studio Output tab for errors.")
            return ExecutionResult(
                mode=ExecutionMode.LUA_LAUNCH,
                success=False,
                error=f"Result file not created after {elapsed:.1f}s: {result_path}",
                elapsed_seconds=elapsed,
                verbose_log=vlog.lines,
            )

        raw_content = result_path.read_text(encoding="utf-8")
        import json
        try:
            data = json.loads(raw_content)
            vlog.log(f"Result JSON: {data}")
            if not data.get("executed"):
                return ExecutionResult(
                    mode=ExecutionMode.LUA_LAUNCH,
                    success=False,
                    error=f"Result JSON executed=false: {data.get('error', 'unknown')}",
                    elapsed_seconds=elapsed,
                    verbose_log=vlog.lines,
                )
        except (json.JSONDecodeError, OSError) as e:
            vlog.log(f"Result JSON unreadable: {e}")
            vlog.log(f"Raw file contents:\n{raw_content}")
            return ExecutionResult(
                mode=ExecutionMode.LUA_LAUNCH,
                success=False,
                error=f"Result JSON unreadable: {e}",
                elapsed_seconds=elapsed,
                verbose_log=vlog.lines,
            )

    return ExecutionResult(
        mode=ExecutionMode.LUA_LAUNCH,
        success=True,
        elapsed_seconds=elapsed,
        verbose_log=vlog.lines,
    )

def execute_script(
    script_path: Path,
    mode: str = "auto",
    timeout: float = 30.0,
    verbose: bool = False,
    allow_fallback: bool = True,
    apartment: str = "mta",
) -> ExecutionResult:
    """Execute a Lua script in mmWave Studio.

    Args:
        script_path: Path to the .lua script
        mode: "auto", "rstd", "pywinauto", or "manual"
        timeout: Seconds to wait for result JSON (used by caller, not here)
        verbose: If True, print detailed diagnostic info

    Returns:
        ExecutionResult with success/error info.

    Raises:
        RuntimeError if mode="auto" and no automatic transport is available.
        The caller must handle this — --execute must NOT silently fall back to manual.
    """
    script_path = Path(script_path).resolve()
    if not script_path.exists():
        return ExecutionResult(
            mode=ExecutionMode.MANUAL_ONE_SHOT,
            success=False,
            error=f"Script not found: {script_path}",
        )

    # Normalize aliases
    mode = mode.lower().replace("_", "-")
    if mode in ("cli-lua-launch", "lua-launch", "cli-launch"):
        mode = "lua-launch"
    if mode in ("ui-lua-shell", "ui-lua-shell-focused"):
        # We handle focused as a special flag
        focused_only = (mode == "ui-lua-shell-focused")
        mode = "pywinauto"
    else:
        focused_only = False

    if mode == "manual":
        return ExecutionResult(
            mode=ExecutionMode.MANUAL_ONE_SHOT,
            success=True,
            error=None,
        )

    # --- Priority 1: pywinauto Lua Shell (Primary transport for tonight) ---
    if mode in ("pywinauto", "auto"):
        if _HAVE_PYWINAUTO and (focused_only or _is_mmws_running()):
            return _execute_via_pywinauto(script_path, verbose=verbose, focused_only=focused_only)
        elif mode == "pywinauto":
            if not _HAVE_PYWINAUTO:
                return ExecutionResult(
                    mode=ExecutionMode.UI_LUA_SHELL,
                    success=False,
                    error="pywinauto not installed. "
                          "Install: python -m pip install -e \".[automation]\"",
                )
            return ExecutionResult(
                mode=ExecutionMode.UI_LUA_SHELL,
                success=False,
                error="mmWave Studio is not running",
            )

    # --- Priority 2: C# RSTD Bridge (fallback/legacy) ---
    if mode in ("csharp-rstd", "auto"):
        bridge = _find_csharp_bridge()
        if bridge and _is_rstd_port_open():
            result = _execute_via_csharp_bridge(
                script_path, verbose=verbose, timeout=timeout, apartment=apartment,
            )
            return result
        elif mode == "csharp-rstd":
            if bridge is None:
                return ExecutionResult(
                    mode=ExecutionMode.CSHARP_RSTD,
                    success=False,
                    error="MmwsRstdBridge.exe not found. "
                          "Run: awr mmws csharp-bridge build",
                )
            return ExecutionResult(
                mode=ExecutionMode.CSHARP_RSTD,
                success=False,
                error=f"RSTD port {_RSTD_PORT} not open. "
                      f"Is mmWave Studio running?",
            )

    # --- MATLAB RSTD Bridge ---
    if mode == "matlab-rstd":
        return _execute_matlab_bridge(script_path, verbose=verbose, timeout=timeout, bridge_mode="send-command")

    # --- LUA LAUNCH (Official Transport) ---
    if mode == "lua-launch":
        return _execute_lua_launch(script_path, verbose=verbose, timeout=timeout)

    # --- Legacy: Pythonnet RSTD (only when explicitly requested) ---
    if mode == "rstd":
        if _HAVE_PYTHONNET and _is_rstd_port_open():
            return _execute_via_rstd(script_path, verbose=verbose, timeout=timeout)
        if not _HAVE_PYTHONNET:
            return ExecutionResult(
                mode=ExecutionMode.RSTD_NET_REMOTING,
                success=False,
                error="pythonnet not installed. "
                      "Install: python -m pip install -e \".[automation]\"",
            )
        return ExecutionResult(
            mode=ExecutionMode.RSTD_NET_REMOTING,
            success=False,
            error=f"RSTD port {_RSTD_PORT} not open. "
                  f"Is mmWave Studio running?",
        )

    if mode == "auto":
        # No automatic transport worked — ERROR, never silent manual fallback
        help_parts = []
        bridge = _find_csharp_bridge()
        if bridge is None:
            help_parts.append(
                "C# RSTD bridge not built. Run: awr mmws csharp-bridge build"
            )
        elif not _is_rstd_port_open():
            help_parts.append(
                f"RSTD port {_RSTD_PORT} not open (is mmWave Studio running?)"
            )
        if not _HAVE_PYWINAUTO:
            help_parts.append(
                "pywinauto not installed (needed for UI fallback)"
            )
        elif not _is_mmws_running():
            help_parts.append("mmWave Studio not running")

        raise RuntimeError(
            "No automatic execution transport available.\n"
            + "\n".join(f"  - {p}" for p in help_parts)
            + "\n\nBuild C# bridge: awr mmws csharp-bridge build\n"
            "Then start mmWave Studio and try again.\n"
            "Or use --manual to print the dofile command instead."
        )

    return ExecutionResult(
        mode=ExecutionMode.MANUAL_ONE_SHOT,
        success=False,
        error=f"Unknown mode: {mode}",
    )


def wait_for_result_json(
    result_path: Path,
    timeout: float = 30.0,
    poll_interval: float = 0.5,
) -> dict[str, Any] | None:
    """Poll for a result JSON file to appear, then read it.

    Returns the parsed JSON dict, or None if timeout.
    """
    import json

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if result_path.exists():
            try:
                data = json.loads(result_path.read_text(encoding="utf-8"))
                return data
            except (json.JSONDecodeError, PermissionError):
                pass  # file may still be written
        time.sleep(poll_interval)
    return None


def build_dofile_command(script_path: Path) -> str:
    """Build the dofile([[...]]) command string for manual use."""
    return f"dofile([[{script_path.resolve()}]])"


def classify_execution_status(
    exec_result: ExecutionResult,
    stage_result: dict[str, Any] | None,
) -> ExecutionStatus:
    """Classify the detailed execution status.

    Returns one of:
    - SUCCESS: submitted and result JSON reports no error
    - SUBMISSION_FAILED: transport could not submit the command
    - SUBMITTED_BUT_NO_RESULT: command was submitted but no result JSON appeared
    - LUA_REPORTED_ERROR: result JSON appeared but contains an error
    - TIMEOUT: timed out waiting for result
    """
    if not exec_result.success:
        return ExecutionStatus.SUBMISSION_FAILED

    if stage_result is None:
        return ExecutionStatus.SUBMITTED_BUT_NO_RESULT

    err = stage_result.get("error")
    if err is not None and err != "nil" and err != "null":
        return ExecutionStatus.LUA_REPORTED_ERROR

    return ExecutionStatus.SUCCESS
