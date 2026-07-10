"""DCA capture-smoke staged workflow.

Orchestrates the validated DCA setup → capture → postproc → validation
sequence using manual dofile paste.  No automatic Lua execution.

State machine persists to ``dca_capture_smoke_<workflow_id>_state.json``
in the probe directory and advances one stage per ``resume()`` call.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import shutil
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from awr2944_dca.dca.preflight import run_dca_preflight
from awr2944_dca.dca.scripts import (
    generate_capture_trigger_script,
    generate_dca_setup_script,
    generate_postproc_script,
)
from awr2944_dca.dca.validate import check_capture_files
from awr2944_dca.mmws.post_connect import load_run_result


# ---------------------------------------------------------------------------
# Stage definitions
# ---------------------------------------------------------------------------

STAGES = [
    "preflight_checked",
    "capture_dir_checked",
    "existing_capture_archived_or_refused",
    "dca_setup_script_generated",
    "dca_setup_validated",
    "capture_script_generated",
    "capture_validated",
    "raw_capture_preserved",
    "postproc_script_generated",
    "postproc_validated",
    "capture_file_validated",
    "validation_recorded",
    "complete",
]


# ---------------------------------------------------------------------------
# Run metadata (for freshness enforcement)
# ---------------------------------------------------------------------------

@dataclass
class RunMeta:
    run_id: str = ""
    generated_at: str = ""
    script_path: str = ""
    result_path: str = ""
    progress_path: str = ""


# ---------------------------------------------------------------------------
# Workflow state
# ---------------------------------------------------------------------------

@dataclass
class CaptureWorkflowState:
    schema_version: int = 1
    workflow_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    current_stage: str = ""
    probe_dir: str = ""
    capture_dir: str = ""
    expected_bytes: int = 4_194_304

    firmware_run_id: str = ""
    config_run_id: str = ""

    dca_setup: RunMeta = field(default_factory=RunMeta)
    capture_trigger: RunMeta = field(default_factory=RunMeta)
    postproc: RunMeta = field(default_factory=RunMeta)

    validation_record_path: str = ""
    adc_data_bin_path: str = ""
    adc_data_bin_size: int = 0
    adc_data_bin_sha256: str = ""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    completed: bool = False

    # Operator-facing fields
    pending_dofile: str = ""
    pending_operator_action: str = ""

    # Convenience run_id accessors
    @property
    def dca_setup_run_id(self) -> str:
        return self.dca_setup.run_id

    @property
    def capture_trigger_run_id(self) -> str:
        return self.capture_trigger.run_id

    @property
    def postproc_run_id(self) -> str:
        return self.postproc.run_id


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def _state_path(workflow_id: str, probe_dir: Path) -> Path:
    return probe_dir / f"dca_capture_smoke_{workflow_id}_state.json"


def save_state(state: CaptureWorkflowState, probe_dir: Path) -> Path:
    state.updated_at = datetime.datetime.now().isoformat()
    path = _state_path(state.workflow_id, probe_dir)
    path.write_text(json.dumps(asdict(state), indent=2), encoding="utf-8")
    return path


def load_state(workflow_id: str, probe_dir: Path) -> CaptureWorkflowState:
    path = _state_path(workflow_id, probe_dir)
    if not path.exists():
        raise FileNotFoundError(f"Workflow state not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))

    # Reconstruct RunMeta from dicts
    for key in ("dca_setup", "capture_trigger", "postproc"):
        if key in raw and isinstance(raw[key], dict):
            raw[key] = RunMeta(**raw[key])
        elif key not in raw:
            raw[key] = RunMeta()

    return CaptureWorkflowState(**raw)


def find_latest_state(probe_dir: Path) -> CaptureWorkflowState | None:
    files = sorted(probe_dir.glob("dca_capture_smoke_*_state.json"))
    if not files:
        return None
    # Newest by mtime
    newest = max(files, key=lambda p: p.stat().st_mtime)
    wid = newest.stem.replace("dca_capture_smoke_", "").replace("_state", "")
    return load_state(wid, probe_dir)


# ---------------------------------------------------------------------------
# Archive helper
# ---------------------------------------------------------------------------

def archive_existing_capture(capture_dir: Path) -> Path:
    """Move adc_data*.bin and dca_validation*.json into a timestamped archive."""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive = capture_dir / f"archive_{ts}"
    archive.mkdir(parents=True, exist_ok=True)

    patterns = ["adc_data*.bin", "dca_validation_*.json"]
    moved = []
    for pat in patterns:
        for f in capture_dir.glob(pat):
            if f.is_file():
                dest = archive / f.name
                shutil.move(str(f), str(dest))
                moved.append(f.name)

    return archive


def _preserve_raw_file(capture_dir: Path, workflow_id: str) -> tuple[str, str | None]:
    """Copy adc_data_Raw_0.bin if present. Returns (status, path_or_warning)."""
    raw = capture_dir / "adc_data_Raw_0.bin"
    if not raw.exists():
        return "missing", "adc_data_Raw_0.bin not found (may have been consumed by postproc)"

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_dir = capture_dir / f"raw_preserve_{workflow_id}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"adc_data_Raw_0_{ts}.bin"
    shutil.copy2(str(raw), str(dest))
    return "preserved", str(dest)


# ---------------------------------------------------------------------------
# Run validation helpers
# ---------------------------------------------------------------------------

def _validate_run(
    run_meta: RunMeta,
    expected_stage: str,
    probe_dir: Path,
) -> tuple[bool, str]:
    """Validate a run result with freshness checks.

    Returns (success, error_message).
    """
    if not run_meta.run_id:
        return False, f"No run_id recorded for {expected_stage}"

    result_path = Path(run_meta.result_path)
    if not result_path.exists():
        return False, (
            f"Result file not found: {result_path}\n"
            f"Paste the dofile into mmWave Studio Lua Shell, then resume."
        )

    # Freshness: result mtime must be >= script generation time
    if run_meta.generated_at:
        gen_dt = datetime.datetime.fromisoformat(run_meta.generated_at)
        result_mtime = datetime.datetime.fromtimestamp(result_path.stat().st_mtime)
        if result_mtime < gen_dt:
            return False, (
                f"Result file {result_path.name} is stale "
                f"(mtime {result_mtime.isoformat()} < generated_at {run_meta.generated_at}). "
                f"Re-paste the dofile and run it again."
            )

    # Parse result
    try:
        res_data = json.loads(result_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        return False, f"Cannot parse result: {e}"

    # run_id match
    if res_data.get("run_id") != run_meta.run_id:
        return False, (
            f"run_id mismatch: result has '{res_data.get('run_id')}', "
            f"expected '{run_meta.run_id}'"
        )

    if not res_data.get("success"):
        error = res_data.get("error", "unknown error")
        return False, f"{expected_stage} failed: {error}"

    return True, ""


# ---------------------------------------------------------------------------
# Start workflow
# ---------------------------------------------------------------------------

def start_workflow(
    probe_dir: Path,
    capture_dir: Path,
    firmware_run_id: str,
    config_run_id: str,
    confirm_startframe: bool,
    expected_bytes: int = 4_194_304,
    archive_existing: bool = False,
    allow_overwrite: bool = False,
) -> CaptureWorkflowState:
    """Create and initialize a new capture-smoke workflow.

    Raises ValueError on preflight failure or safety violations.
    """
    if not confirm_startframe:
        raise ValueError(
            "ERROR: --confirm-startframe is required. "
            "This workflow will generate a script that calls ar1.StartFrame() "
            "(RF transmission)."
        )

    # 1. Preflight
    preflight = run_dca_preflight()
    if preflight.overall == "NOT_READY":
        details = "\n".join(
            f"  {c.name}: {c.status} ({c.detail})" for c in preflight.checks
        )
        raise ValueError(
            f"DCA preflight is NOT_READY. Fix issues before starting:\n{details}"
        )

    # 1.5 Validate provided run IDs
    def _check_run_id(rid: str, label: str, expected_stage: str) -> None:
        if not rid:
            return
        result_path = probe_dir / f"{rid}_result.json"
        if not result_path.exists():
            result_files = sorted(probe_dir.glob(f"{rid}_*result.json"))
            if result_files:
                result_path = result_files[0]
        if not result_path.exists():
            raise ValueError(
                f"Run ID {rid} ({label}) not found in {probe_dir}. "
                "Are you in the correct experiment directory?"
            )
        try:
            res = json.loads(result_path.read_text(encoding="utf-8"))
            if not res.get("success"):
                raise ValueError(
                    f"Run ID {rid} ({label}) failed: {res.get('error', 'unknown error')}"
                )
            if "stage" in res and res["stage"] != expected_stage:
                raise ValueError(f"Run ID {rid} ({label}) has wrong stage '{res['stage']}', expected '{expected_stage}'")
        except json.JSONDecodeError:
            raise ValueError(f"Run ID {rid} ({label}) result is invalid JSON")

    _check_run_id(firmware_run_id, "firmware", "firmware_power")
    _check_run_id(config_run_id, "config", "smoke_config")

    wid = str(uuid.uuid4())[:8]
    now = datetime.datetime.now().isoformat()
    probe_dir.mkdir(parents=True, exist_ok=True)

    state = CaptureWorkflowState(
        workflow_id=wid,
        created_at=now,
        updated_at=now,
        current_stage="preflight_checked",
        probe_dir=str(probe_dir.resolve()),
        capture_dir=str(capture_dir.resolve()),
        expected_bytes=expected_bytes,
        firmware_run_id=firmware_run_id,
        config_run_id=config_run_id,
    )

    if preflight.overall == "READY_WITH_WARNINGS":
        state.warnings.append(f"Preflight READY_WITH_WARNINGS: {preflight.overall}")

    # 2. Capture dir
    if not capture_dir.exists():
        raise ValueError(f"Capture directory does not exist: {capture_dir}")
    state.current_stage = "capture_dir_checked"

    # 3. Existing capture check
    adc_bin = capture_dir / "adc_data.bin"
    if adc_bin.exists():
        if archive_existing:
            archive_path = archive_existing_capture(capture_dir)
            state.warnings.append(f"Archived existing capture to {archive_path}")
        elif allow_overwrite:
            state.warnings.append("allow_overwrite: existing adc_data.bin will be overwritten")
        else:
            raise ValueError(
                f"adc_data.bin already exists in {capture_dir}. "
                f"Use --archive-existing or --allow-overwrite."
            )
    state.current_stage = "existing_capture_archived_or_refused"

    # 4. Generate DCA setup script
    run_id = str(uuid.uuid4())[:8]
    out_path = probe_dir / f"{run_id}_dca_setup.lua"
    script = generate_dca_setup_script(run_id=run_id, out_path=out_path)
    script.lua_path.write_text(script.script, encoding="utf-8")

    state.dca_setup = RunMeta(
        run_id=run_id,
        generated_at=datetime.datetime.now().isoformat(),
        script_path=str(script.lua_path.resolve()),
        result_path=str(script.result_path.resolve()),
        progress_path=str(script.progress_path.resolve()),
    )
    state.current_stage = "dca_setup_script_generated"
    state.pending_dofile = script.dofile
    state.pending_operator_action = (
        "Paste the DCA setup dofile into mmWave Studio Lua Shell, "
        "then run: awr dca capture-smoke resume --workflow-id " + wid
    )

    save_state(state, probe_dir)
    return state


# ---------------------------------------------------------------------------
# Resume workflow
# ---------------------------------------------------------------------------

def resume_workflow(
    workflow_id: str,
    probe_dir: Path,
) -> CaptureWorkflowState:
    """Advance the workflow by one step.

    Returns the updated state. The caller should inspect
    ``state.pending_operator_action`` to know what to do next.
    """
    state = load_state(workflow_id, probe_dir)
    probe = Path(state.probe_dir)
    capture = Path(state.capture_dir)

    if state.completed:
        state.pending_operator_action = "Workflow already complete."
        state.pending_dofile = ""
        return state

    if state.errors:
        last_error = state.errors[-1]
        state.pending_operator_action = f"Workflow has errors. Last: {last_error}"
        state.pending_dofile = ""
        save_state(state, probe)
        return state

    stage = state.current_stage

    # -----------------------------------------------------------------------
    # After setup generated → validate setup result
    # -----------------------------------------------------------------------
    if stage == "dca_setup_script_generated":
        ok, err = _validate_run(state.dca_setup, "dca_setup", probe)
        if not ok:
            state.pending_operator_action = err
            save_state(state, probe)
            return state

        state.current_stage = "dca_setup_validated"

        # Generate capture trigger script
        run_id = str(uuid.uuid4())[:8]
        out_path = probe / f"{run_id}_capture_trigger.lua"
        script = generate_capture_trigger_script(
            run_id=run_id,
            out_path=out_path,
            output_dir=capture,
            confirm_startframe=True,
        )
        script.lua_path.write_text(script.script, encoding="utf-8")

        state.capture_trigger = RunMeta(
            run_id=run_id,
            generated_at=datetime.datetime.now().isoformat(),
            script_path=str(script.lua_path.resolve()),
            result_path=str(script.result_path.resolve()),
            progress_path=str(script.progress_path.resolve()),
        )
        state.current_stage = "capture_script_generated"
        state.pending_dofile = script.dofile
        state.pending_operator_action = (
            "WARNING: This script calls ar1.StartFrame() (RF transmission).\n"
            "Paste the capture dofile into mmWave Studio Lua Shell ONLY when ready.\n"
            "Then run: awr dca capture-smoke resume --workflow-id " + workflow_id
        )
        save_state(state, probe)
        return state

    # -----------------------------------------------------------------------
    # After capture generated → validate capture result
    # -----------------------------------------------------------------------
    if stage == "capture_script_generated":
        ok, err = _validate_run(state.capture_trigger, "capture_trigger", probe)
        if not ok:
            state.pending_operator_action = err
            save_state(state, probe)
            return state

        state.current_stage = "capture_validated"

        # Preserve raw file
        raw_status, raw_detail = _preserve_raw_file(capture, workflow_id)
        if raw_status == "missing":
            state.warnings.append(raw_detail)
        state.current_stage = "raw_capture_preserved"

        # Generate postproc script
        run_id = str(uuid.uuid4())[:8]
        out_path = probe / f"{run_id}_postproc.lua"
        script = generate_postproc_script(
            run_id=run_id,
            out_path=out_path,
            output_dir=capture,
        )
        script.lua_path.write_text(script.script, encoding="utf-8")

        state.postproc = RunMeta(
            run_id=run_id,
            generated_at=datetime.datetime.now().isoformat(),
            script_path=str(script.lua_path.resolve()),
            result_path=str(script.result_path.resolve()),
            progress_path=str(script.progress_path.resolve()),
        )
        state.current_stage = "postproc_script_generated"
        state.pending_dofile = script.dofile
        state.pending_operator_action = (
            "Paste the postproc dofile into mmWave Studio Lua Shell.\n"
            "Then run: awr dca capture-smoke resume --workflow-id " + workflow_id
        )
        save_state(state, probe)
        return state

    # -----------------------------------------------------------------------
    # After postproc generated → validate postproc + capture files
    # -----------------------------------------------------------------------
    if stage == "postproc_script_generated":
        ok, err = _validate_run(state.postproc, "postproc", probe)
        if not ok:
            state.pending_operator_action = err
            save_state(state, probe)
            return state

        state.current_stage = "postproc_validated"

        # Validate capture files
        validation = check_capture_files(capture, expected_bytes=state.expected_bytes)
        if validation.overall == "FAIL":
            state.errors.append(f"Capture validation FAIL: {validation.postproc_file.detail}")
            state.pending_operator_action = (
                f"Capture validation FAIL: {validation.postproc_file.detail}"
            )
            save_state(state, probe)
            return state

        state.current_stage = "capture_file_validated"

        adc_bin = capture / "adc_data.bin"
        state.adc_data_bin_path = str(adc_bin.resolve())
        state.adc_data_bin_size = adc_bin.stat().st_size

        # SHA256
        sha = hashlib.sha256()
        with open(adc_bin, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha.update(chunk)
        state.adc_data_bin_sha256 = sha.hexdigest()

        # Record validation
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        val_path = capture / f"dca_validation_{ts}.json"
        record = {
            "schema_version": 1,
            "timestamp": datetime.datetime.now().isoformat(),
            "overall": validation.overall,
            "workflow_id": workflow_id,
            "capture_dir": str(capture.resolve()),
            "expected_bytes": state.expected_bytes,
            "size_model": "256 samples × 4 bytes × 4 RX × 128 chirps × 8 frames",
            "adc_data_bin": {
                "exists": validation.postproc_file.exists,
                "size_bytes": validation.postproc_file.size_bytes,
                "status": validation.postproc_file.status,
                "detail": validation.postproc_file.detail,
                "sha256": state.adc_data_bin_sha256,
            },
            "run_ids": {
                "firmware": state.firmware_run_id,
                "config": state.config_run_id,
                "dca_setup": state.dca_setup_run_id,
                "capture_trigger": state.capture_trigger_run_id,
                "postproc": state.postproc_run_id,
            },
            "post_processing_status": validation.post_processing_status,
        }
        val_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        state.validation_record_path = str(val_path.resolve())
        state.current_stage = "validation_recorded"

        # Complete
        state.completed = True
        state.current_stage = "complete"
        state.pending_dofile = ""
        state.pending_operator_action = "Workflow complete. Capture validated."
        save_state(state, probe)
        return state

    # Fallback — unknown stage
    state.errors.append(f"Unknown stage: {stage}")
    save_state(state, probe)
    return state
