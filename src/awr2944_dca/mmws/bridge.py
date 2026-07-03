"""Bridge between Python controller and mmWave Studio execution backend.

Supports multiple bridge modes.  Currently only ``manual_one_shot`` is
implemented: Python generates a Lua script, the user runs it inside the
mmWave Studio Lua Shell, and Lua writes a result JSON that Python reads.

The API is designed so that a future live bridge (FILE_QUEUE, NAMED_PIPE,
MMWS_LIVE_LUA) can be added without changing the caller's interface.
Python must never directly open the AWR radar RS232 port.
"""

from __future__ import annotations

import json
import uuid
from enum import Enum
from pathlib import Path
from typing import Any

from awr2944_dca.mmws.lua_builder import write_connection_script
from awr2944_dca.mmws.stages import StageName


class BridgeMode(str, Enum):
    """Supported bridge transport modes."""

    MANUAL_ONE_SHOT = "manual_one_shot"
    # Future (not implemented):
    # FILE_QUEUE = "file_queue"
    # NAMED_PIPE = "named_pipe"
    # MMWS_LIVE_LUA = "mmws_live_lua"


class StageStatus(str, Enum):
    """Result of checking a stage's execution status."""

    NOT_RUN = "NOT_RUN"
    STALE_RESULT = "STALE_RESULT"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class ManualOneShotBridge:
    """Bridge that generates Lua scripts for manual execution in mmWave Studio.

    Workflow:
        1. Python calls ``generate_script(stage, ...)``
        2. A manifest JSON (with ``run_id``) and Lua script are written
        3. User copies ``dofile([[path]])`` into mmWave Studio Lua Shell
        4. Lua writes a result JSON with the matching ``run_id``
        5. Python calls ``check_status(stage)`` to read the result
    """

    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Manifest / result helpers
    # ------------------------------------------------------------------

    def _manifest_path(self, stage: StageName) -> Path:
        return self.log_dir / f"{stage.value}_manifest.json"

    def _result_path(self, stage: StageName) -> Path:
        return self.log_dir / f"{stage.value}_result.json"

    def _script_path(self, stage: StageName) -> Path:
        return self.log_dir / f"{stage.value}.lua"

    def _write_manifest(self, stage: StageName, run_id: str) -> Path:
        path = self._manifest_path(stage)
        path.write_text(json.dumps({"run_id": run_id}, indent=2), encoding="utf-8")
        return path

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

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
        self._write_manifest(StageName.CONNECTION_ONLY, run_id)

        script_path = self._script_path(StageName.CONNECTION_ONLY)
        write_connection_script(script_path, run_id, com_num, baud, timeout_ms)
        return script_path

    # ------------------------------------------------------------------
    # Status checking
    # ------------------------------------------------------------------

    def check_status(self, stage: StageName) -> tuple[StageStatus, dict[str, Any]]:
        """Check the result of a stage execution.

        Returns (status, result_dict).
        """
        manifest = self._read_json(self._manifest_path(stage))
        result = self._read_json(self._result_path(stage))

        if not manifest or not result:
            return StageStatus.NOT_RUN, {}

        if manifest.get("run_id") != result.get("run_id"):
            return StageStatus.STALE_RESULT, result

        # Stage-specific success check
        if stage == StageName.CONNECTION_ONLY:
            err = result.get("error")
            connect_ret = result.get("connect_return")
            if connect_ret == 0 and (err is None or err == "nil"):
                return StageStatus.SUCCESS, result
            return StageStatus.ERROR, result

        # Generic: if no error field, treat as success
        if result.get("error") in (None, "nil", ""):
            return StageStatus.SUCCESS, result
        return StageStatus.ERROR, result
