"""Bridge between Python controller and mmWave Studio execution backend.

Python/Jupyter is the control layer.  mmWave Studio is the execution backend.
The bridge generates Lua scripts, optionally executes them automatically via
the executor, and reads structured result JSON.

Python must never directly open the AWR radar RS232 port.
"""

from __future__ import annotations

import json
import uuid
from enum import Enum
from pathlib import Path
from typing import Any

from awr2944_dca.legacy_mmws.lua_builder import write_connection_diag_script, write_smoke_script
from awr2944_dca.legacy_mmws.stages import StageName


class StageStatus(str, Enum):
    """Result of checking a stage's execution status."""

    NOT_RUN = "NOT_RUN"
    STALE_RESULT = "STALE_RESULT"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"


# Pseudo-stage name for smoke test
_SMOKE_STAGE = "smoke"


class StudioBridge:
    """Bridge that generates and optionally executes Lua scripts.

    Workflow:
        1. Python calls ``generate_*`` to create a Lua script + manifest
        2. Optionally calls ``execute()`` to auto-run via RSTD/pywinauto
        3. Calls ``check_status()`` to read result JSON

    The executor is transport only — it does not bypass stage whitelists.
    RSTD SendCommand return code only means the command was submitted;
    the result JSON is the source of truth for stage success.
    """

    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------

    def _manifest_path(self, stage: str) -> Path:
        return self.log_dir / f"{stage}_manifest.json"

    def _result_path(self, stage: str) -> Path:
        return self.log_dir / f"{stage}_result.json"

    def _script_path(self, stage: str) -> Path:
        return self.log_dir / f"{stage}.lua"

    def _write_manifest(self, stage: str, run_id: str) -> Path:
        path = self._manifest_path(stage)
        path.write_text(json.dumps({"run_id": run_id}, indent=2), encoding="utf-8")
        return path

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, PermissionError):
            return {}

    # ------------------------------------------------------------------
    # Script generation
    # ------------------------------------------------------------------

    def generate_connection_script(
        self,
        com_num: int,
        baud: int = 921600,
        timeout_ms: int = 1000,
    ) -> Path:
        """Generate a connection-only Lua script with manifest."""
        run_id = str(uuid.uuid4())
        self._write_manifest(StageName.CONNECTION_ONLY.value, run_id)
        script_path = self._script_path(StageName.CONNECTION_ONLY.value)
        write_connection_diag_script(script_path, run_id, com_num, baud, timeout_ms)
        return script_path

    def generate_smoke_script(self) -> Path:
        """Generate a harmless smoke test script with manifest."""
        run_id = str(uuid.uuid4())
        self._write_manifest(_SMOKE_STAGE, run_id)
        script_path = self._script_path(_SMOKE_STAGE)
        write_smoke_script(script_path, run_id)
        return script_path

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(self, script_path: Path, mode: str = "auto", timeout: float = 30.0, verbose: bool = False, apartment: str = "mta") -> dict:
        """Execute a script and wait for its result JSON.

        Returns a dict with keys: exec_result, stage_result, status, execution_status.

        Raises RuntimeError if mode="auto" and no transport is available
        (never silently falls back to manual).
        """
        from awr2944_dca.legacy_mmws.executor import (
            execute_script, wait_for_result_json, classify_execution_status,
        )

        exec_result = execute_script(script_path, mode=mode, verbose=verbose, apartment=apartment)

        if not exec_result.success:
            execution_status = classify_execution_status(exec_result, None)
            return {
                "exec_result": exec_result,
                "stage_result": {},
                "status": StageStatus.ERROR,
                "execution_status": execution_status,
            }

        # Determine result path from the script path
        # Convention: script is {stage}.lua, result is {stage}_result.json
        stage_name = script_path.stem  # e.g. "connection_only" or "smoke"
        result_path = self._result_path(stage_name)

        stage_result = wait_for_result_json(result_path, timeout=timeout)

        execution_status = classify_execution_status(exec_result, stage_result)

        if stage_result is None:
            return {
                "exec_result": exec_result,
                "stage_result": {},
                "status": StageStatus.TIMEOUT,
                "execution_status": execution_status,
            }

        stage_status = StageStatus.SUCCESS if stage_result.get("error") in (None, "nil") else StageStatus.ERROR
        return {
            "exec_result": exec_result,
            "stage_result": stage_result,
            "status": stage_status,
            "execution_status": execution_status,
        }

    # ------------------------------------------------------------------
    # Status checking (reads existing result files)
    # ------------------------------------------------------------------

    def check_status(self, stage: StageName | str) -> tuple[StageStatus, dict[str, Any]]:
        """Check the result of a stage execution.

        Returns (status, result_dict).
        """
        stage_str = stage.value if isinstance(stage, StageName) else stage
        manifest = self._read_json(self._manifest_path(stage_str))
        result = self._read_json(self._result_path(stage_str))

        if not manifest or not result:
            return StageStatus.NOT_RUN, {}

        if manifest.get("run_id") != result.get("run_id"):
            return StageStatus.STALE_RESULT, result

        # Stage-specific success check
        if stage_str == StageName.CONNECTION_ONLY.value:
            err = result.get("error")
            connect_ret = result.get("connect_return")
            if connect_ret == 0 and (err is None or err == "nil"):
                return StageStatus.SUCCESS, result
            return StageStatus.ERROR, result

        # Generic: if no error field, treat as success
        if result.get("error") in (None, "nil", ""):
            return StageStatus.SUCCESS, result
        return StageStatus.ERROR, result


# Keep old name as alias for backward compatibility
ManualOneShotBridge = StudioBridge

