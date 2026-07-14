"""Worker subprocess for executing RSTD .NET Remoting commands.

This runs as a separate process so the parent can enforce a strict timeout
and kill it if RtttNetClientAPI blocks indefinitely.

Modes:
  execute  - Full Init -> Connect -> SendCommand flow (default)
  introspect - Load DLL and list public methods of RtttNetClient

Step-level progress is written to --progress-file (JSONL) so the parent
can determine exactly which API call hung if the worker is killed.

Usage:
  python -m awr2944_dca.mmws.rstd_worker \\
    --dll <path> --host 127.0.0.1 --port 2777 \\
    --command-file <in.txt> --result-file <out.json> \\
    --progress-file <progress.jsonl>

  python -m awr2944_dca.mmws.rstd_worker \\
    --dll <path> --mode introspect --result-file <out.json> \\
    --progress-file <progress.jsonl>
"""

import argparse
import json
import sys
import time
from pathlib import Path


def _log_step(progress_path: Path | None, step: str, **extra: object) -> None:
    """Append a step entry to the JSONL progress log."""
    entry = {"step": step, "time": time.monotonic(), **extra}
    if progress_path:
        with open(progress_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    # Also print to stderr for subprocess capture
    print(f"[worker] {step}" + (f" {extra}" if extra else ""), file=sys.stderr, flush=True)


# Step names that --step can target.  Execution stops AFTER the named step.
_STEP_ORDER = [
    "import-clr",
    "add-reference",
    "import-api",
    "init",
    "connect",
    "send-log",           # send a WriteToLog via SendCommand
    "runscript-file",     # RunScript with a real Lua file path
    "sendcommand-dofile", # SendCommand('dofile([[path]])')
]


def _should_stop(current_step: str, stop_after: str | None) -> bool:
    if stop_after is None:
        return False
    try:
        return _STEP_ORDER.index(current_step) >= _STEP_ORDER.index(stop_after)
    except ValueError:
        return False


def _run_execute(args: argparse.Namespace, progress: Path | None) -> dict:
    """Execute the Init -> Connect -> SendCommand flow with step logging."""
    result: dict = {
        "init_return": None,
        "connect_return": None,
        "send_return": None,
        "exception": None,
        "elapsed_seconds": 0.0,
        "last_step": "worker_started",
    }
    start = time.monotonic()

    try:
        # Read command
        lua_cmd: str | None = None
        if args.command_file:
            lua_cmd = Path(args.command_file).read_text(encoding="utf-8")

        # --- import clr ---
        _log_step(progress, "importing_clr_start")
        import clr  # type: ignore
        _log_step(progress, "importing_clr_done")
        result["last_step"] = "importing_clr_done"

        if _should_stop("import-clr", args.step):
            return result

        # --- AddReference ---
        dll_path = Path(args.dll).resolve()
        dll_dir = str(dll_path.parent)
        if dll_dir not in sys.path:
            sys.path.insert(0, dll_dir)

        _log_step(progress, "add_reference_start", dll=str(dll_path))
        clr.AddReference(str(dll_path))
        _log_step(progress, "add_reference_done")
        result["last_step"] = "add_reference_done"

        if _should_stop("add-reference", args.step):
            return result

        # --- import API class ---
        _log_step(progress, "import_api_start")
        from RtttNetClientAPI import RtttNetClient  # type: ignore
        _log_step(progress, "import_api_done")
        result["last_step"] = "import_api_done"

        if _should_stop("import-api", args.step):
            return result

        # --- Init ---
        _log_step(progress, "init_start")
        init_ret = RtttNetClient.Init()
        _log_step(progress, "init_done", return_code=init_ret)
        result["init_return"] = init_ret
        result["last_step"] = "init_done"

        if init_ret != 0:
            raise RuntimeError(f"Init() returned {init_ret}")

        if _should_stop("init", args.step):
            return result

        # --- IsConnected (before) ---
        _log_step(progress, "is_connected_before_start")
        already_connected = False
        try:
            already_connected = bool(RtttNetClient.IsConnected())
            _log_step(progress, "is_connected_before_done", connected=already_connected)
        except Exception as e:
            _log_step(progress, "is_connected_before_done", error=str(e))

        # --- Connect ---
        if already_connected:
            connect_ret = 0
            _log_step(progress, "connect_start", skipped=True, reason="already_connected")
            _log_step(progress, "connect_done", return_code=0, skipped=True)
        else:
            _log_step(progress, "connect_start")
            connect_ret = RtttNetClient.Connect(args.host, args.port)
            _log_step(progress, "connect_done", return_code=connect_ret)

        result["connect_return"] = connect_ret
        result["last_step"] = "connect_done"

        if connect_ret != 0:
            raise RuntimeError(f"Connect() returned {connect_ret}")

        # Small pause after connect (TI example does pause(1))
        time.sleep(0.5)

        if _should_stop("connect", args.step):
            # --- IsConnected (after) ---
            _log_step(progress, "is_connected_after_start")
            try:
                is_conn = bool(RtttNetClient.IsConnected())
                _log_step(progress, "is_connected_after_done", connected=is_conn)
            except Exception as e:
                _log_step(progress, "is_connected_after_done", error=str(e))
            return result

        # --- IsConnected (after) ---
        _log_step(progress, "is_connected_after_start")
        try:
            is_conn = bool(RtttNetClient.IsConnected())
            _log_step(progress, "is_connected_after_done", connected=is_conn)
        except Exception as e:
            _log_step(progress, "is_connected_after_done", error=str(e))

        # --- Determine which send variant to use ---
        lua_file = getattr(args, "lua_file", None)

        # runscript-file: SKIP send-log, go directly to RunScript with file path
        if args.step == "runscript-file" and lua_file:
            if not hasattr(RtttNetClient, "RunScript"):
                raise RuntimeError("RtttNetClient does not have RunScript method")
            _log_step(progress, "runscript_file_start", file=lua_file)
            send_ret = RtttNetClient.RunScript(lua_file)
            _log_step(progress, "runscript_file_done", return_code=send_ret)
            result["send_return"] = send_ret
            result["last_step"] = "runscript_file_done"
            return result

        # sendcommand-dofile: SKIP send-log, go directly to SendCommand('dofile([[path]])')
        if args.step == "sendcommand-dofile" and lua_file:
            dofile_cmd = f'dofile([[{lua_file}]])'
            _log_step(progress, "sendcommand_dofile_start", command=dofile_cmd)
            send_ret = RtttNetClient.SendCommand(dofile_cmd)
            _log_step(progress, "sendcommand_dofile_done", return_code=send_ret)
            result["send_return"] = send_ret
            result["last_step"] = "sendcommand_dofile_done"
            return result

        # --- send-log: SendCommand with inline Lua (default) ---
        if lua_cmd is None:
            lua_cmd = 'WriteToLog("RSTD_WORKER_PING\\n", "green")'

        method = getattr(args, "method", "SendCommand") or "SendCommand"

        _log_step(progress, "send_start", method=method, command=lua_cmd[:200])

        if method == "RunScript":
            if not hasattr(RtttNetClient, "RunScript"):
                raise RuntimeError("RtttNetClient does not have RunScript method")
            send_ret = RtttNetClient.RunScript(lua_cmd)
        else:
            send_ret = RtttNetClient.SendCommand(lua_cmd)

        _log_step(progress, "send_done", return_code=send_ret)
        result["send_return"] = send_ret
        result["last_step"] = "send_done"

    except Exception as e:
        result["exception"] = str(e)
    finally:
        result["elapsed_seconds"] = time.monotonic() - start
        _log_step(progress, "worker_done",
                  elapsed=result["elapsed_seconds"],
                  exception=result.get("exception"))

    return result


def _run_introspect(args: argparse.Namespace, progress: Path | None) -> dict:
    """Load DLL and list public methods/properties of RtttNetClient."""
    result: dict = {
        "methods": [],
        "properties": [],
        "exception": None,
        "elapsed_seconds": 0.0,
        "last_step": "worker_started",
    }
    start = time.monotonic()

    try:
        _log_step(progress, "importing_clr_start")
        import clr  # type: ignore
        _log_step(progress, "importing_clr_done")
        result["last_step"] = "importing_clr_done"

        dll_path = Path(args.dll).resolve()
        dll_dir = str(dll_path.parent)
        if dll_dir not in sys.path:
            sys.path.insert(0, dll_dir)

        _log_step(progress, "add_reference_start", dll=str(dll_path))
        clr.AddReference(str(dll_path))
        _log_step(progress, "add_reference_done")
        result["last_step"] = "add_reference_done"

        _log_step(progress, "import_api_start")
        from RtttNetClientAPI import RtttNetClient  # type: ignore
        _log_step(progress, "import_api_done")
        result["last_step"] = "import_api_done"

        # Introspect
        _log_step(progress, "introspect_start")
        methods = []
        properties = []
        for name in dir(RtttNetClient):
            if name.startswith("_"):
                continue
            obj = getattr(RtttNetClient, name, None)
            if callable(obj):
                methods.append(name)
            else:
                properties.append(name)

        result["methods"] = sorted(methods)
        result["properties"] = sorted(properties)
        result["last_step"] = "introspect_done"
        _log_step(progress, "introspect_done",
                  method_count=len(methods),
                  property_count=len(properties))

    except Exception as e:
        result["exception"] = str(e)
    finally:
        result["elapsed_seconds"] = time.monotonic() - start
        _log_step(progress, "worker_done", elapsed=result["elapsed_seconds"])

    return result


def _run_get_last_error(args: argparse.Namespace, progress: Path | None) -> dict:
    """Init + Connect, then call GetLastError() and GetErrMsg()."""
    result: dict = {
        "last_error": None,
        "error_msg": None,
        "exception": None,
        "elapsed_seconds": 0.0,
        "last_step": "worker_started",
    }
    start = time.monotonic()

    try:
        _log_step(progress, "importing_clr_start")
        import clr  # type: ignore
        _log_step(progress, "importing_clr_done")

        dll_path = Path(args.dll).resolve()
        dll_dir = str(dll_path.parent)
        if dll_dir not in sys.path:
            sys.path.insert(0, dll_dir)

        _log_step(progress, "add_reference_start", dll=str(dll_path))
        clr.AddReference(str(dll_path))
        _log_step(progress, "add_reference_done")

        _log_step(progress, "import_api_start")
        from RtttNetClientAPI import RtttNetClient  # type: ignore
        _log_step(progress, "import_api_done")

        _log_step(progress, "init_start")
        init_ret = RtttNetClient.Init()
        _log_step(progress, "init_done", return_code=init_ret)
        result["last_step"] = "init_done"

        if init_ret != 0:
            raise RuntimeError(f"Init() returned {init_ret}")

        # Connect
        _log_step(progress, "connect_start")
        try:
            already = bool(RtttNetClient.IsConnected())
            if not already:
                connect_ret = RtttNetClient.Connect(args.host, args.port)
            else:
                connect_ret = 0
        except Exception:
            connect_ret = RtttNetClient.Connect(args.host, args.port)
        _log_step(progress, "connect_done", return_code=connect_ret)
        result["last_step"] = "connect_done"

        time.sleep(0.5)

        # GetLastError
        _log_step(progress, "get_last_error_start")
        try:
            last_err = RtttNetClient.GetLastError()
            result["last_error"] = last_err
            _log_step(progress, "get_last_error_done", value=last_err)
        except Exception as e:
            _log_step(progress, "get_last_error_done", error=str(e))

        # GetErrMsg
        _log_step(progress, "get_err_msg_start")
        try:
            err_msg = RtttNetClient.GetErrMsg()
            result["error_msg"] = str(err_msg) if err_msg else None
            _log_step(progress, "get_err_msg_done", value=str(err_msg) if err_msg else None)
        except Exception as e:
            _log_step(progress, "get_err_msg_done", error=str(e))

        result["last_step"] = "get_err_msg_done"

    except Exception as e:
        result["exception"] = str(e)
    finally:
        result["elapsed_seconds"] = time.monotonic() - start
        _log_step(progress, "worker_done", elapsed=result["elapsed_seconds"])

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RSTD worker subprocess for isolated .NET API execution."
    )
    parser.add_argument("--dll", required=True, help="Path to RtttNetClientAPI.dll")
    parser.add_argument("--host", default="127.0.0.1", help="RSTD TCP host")
    parser.add_argument("--port", type=int, default=2777, help="RSTD TCP port")
    parser.add_argument("--command-file", default=None, help="File containing Lua command string")
    parser.add_argument("--result-file", required=True, help="File to write JSON result")
    parser.add_argument("--progress-file", default=None, help="File to write JSONL progress log")
    parser.add_argument("--step", default=None, choices=_STEP_ORDER,
                        help="Stop after this step (for targeted diagnostics)")
    parser.add_argument("--method", default="SendCommand", choices=["SendCommand", "RunScript"],
                        help="Which RtttNetClient method to use for sending")
    parser.add_argument("--lua-file", default=None,
                        help="Path to Lua file for runscript-file/sendcommand-dofile steps")
    parser.add_argument("--mode", default="execute",
                        choices=["execute", "introspect", "get-last-error"],
                        help="Worker mode: execute commands, introspect DLL, or get last error")

    args = parser.parse_args()

    progress = Path(args.progress_file) if args.progress_file else None
    if progress:
        progress.parent.mkdir(parents=True, exist_ok=True)
        # Truncate existing progress file
        progress.write_text("", encoding="utf-8")

    _log_step(progress, "worker_started",
              mode=args.mode,
              dll=args.dll,
              stop_at=args.step,
              method=args.method if args.mode == "execute" else None)

    if args.mode == "introspect":
        result = _run_introspect(args, progress)
    elif args.mode == "get-last-error":
        result = _run_get_last_error(args, progress)
    else:
        result = _run_execute(args, progress)

    # Write result
    out_path = Path(args.result_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
