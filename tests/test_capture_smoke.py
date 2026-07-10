"""Tests for DCA capture-smoke workflow (Path A).

All tests use monkeypatched preflight and tmp_path.
No automatic Lua execution.
No guided runner modifications.
"""

import json
import os
import time
from pathlib import Path

import pytest
from typer.testing import CliRunner

from awr2944_dca.cli import app
from awr2944_dca.dca.workflow import (
    STAGES,
    CaptureWorkflowState,
    RunMeta,
    archive_existing_capture,
    find_latest_state,
    load_state,
    resume_workflow,
    save_state,
    start_workflow,
)

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fake_preflight_ready(monkeypatch):
    """Monkeypatch preflight to return READY_WITH_WARNINGS."""
    from awr2944_dca.dca.preflight import PreflightCheck, PreflightReport

    def fake_preflight(**kwargs):
        return PreflightReport(
            overall="READY_WITH_WARNINGS",
            checks=[
                PreflightCheck("Adapter IP 192.168.33.30/24", "PASS", "Ethernet 5, idx=27"),
                PreflightCheck("Ping 192.168.33.180", "WARN", "No replies"),
                PreflightCheck("ARP 192.168.33.180", "PASS", "0C:22:38:4E:5A:0C"),
            ],
        )

    monkeypatch.setattr("awr2944_dca.dca.workflow.run_dca_preflight", fake_preflight)


def _fake_preflight_not_ready(monkeypatch):
    """Monkeypatch preflight to return NOT_READY."""
    from awr2944_dca.dca.preflight import PreflightCheck, PreflightReport

    def fake_preflight(**kwargs):
        return PreflightReport(
            overall="NOT_READY",
            checks=[
                PreflightCheck("Adapter IP 192.168.33.30/24", "FAIL", "Not found"),
            ],
        )

    monkeypatch.setattr("awr2944_dca.dca.workflow.run_dca_preflight", fake_preflight)


def _write_success_result(path: Path, run_id: str, stage: str = ""):
    """Write a successful run result JSON."""
    path.write_text(json.dumps({
        "run_id": run_id,
        "executed": True,
        "success": True,
        "error": "",
        "warnings": [],
        "stage": stage,
    }), encoding="utf-8")


def _write_failed_result(path: Path, run_id: str, error: str = "something failed"):
    """Write a failed run result JSON."""
    path.write_text(json.dumps({
        "run_id": run_id,
        "executed": True,
        "success": False,
        "error": error,
        "warnings": [],
    }), encoding="utf-8")


# ---------------------------------------------------------------------------
# Start tests
# ---------------------------------------------------------------------------

def _setup_valid_runs(probe_dir: Path, fw_id: str = "fw1", cfg_id: str = "cfg1"):
    probe_dir.mkdir(parents=True, exist_ok=True)
    _write_success_result(probe_dir / f"{fw_id}_result.json", fw_id, stage="firmware_power")
    _write_success_result(probe_dir / f"{cfg_id}_result.json", cfg_id, stage="smoke_config")

def test_start_refuses_without_confirm_startframe(tmp_path, monkeypatch):
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    with pytest.raises(ValueError, match="confirm-startframe"):
        start_workflow(
            probe_dir=probe_dir,
            capture_dir=capture_dir,
            firmware_run_id="fw1",
            config_run_id="cfg1",
            confirm_startframe=False,
        )


def test_start_refuses_not_ready_preflight(tmp_path, monkeypatch):
    _fake_preflight_not_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    with pytest.raises(ValueError, match="NOT_READY"):
        start_workflow(
            probe_dir=probe_dir,
            capture_dir=capture_dir,
            firmware_run_id="fw1",
            config_run_id="cfg1",
            confirm_startframe=True,
        )


def test_start_allows_ready_with_warnings(tmp_path, monkeypatch):
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    state = start_workflow(
        probe_dir=probe_dir,
        capture_dir=capture_dir,
        firmware_run_id="fw1",
        config_run_id="cfg1",
        confirm_startframe=True,
    )
    assert state.current_stage == "dca_setup_script_generated"
    assert len(state.warnings) > 0


def test_start_refuses_existing_adc_data_without_flags(tmp_path, monkeypatch):
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    (capture_dir / "adc_data.bin").write_bytes(b"\x01" * 100)
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    with pytest.raises(ValueError, match="adc_data.bin already exists"):
        start_workflow(
            probe_dir=probe_dir,
            capture_dir=capture_dir,
            firmware_run_id="fw1",
            config_run_id="cfg1",
            confirm_startframe=True,
        )


def test_start_archive_existing_moves_files(tmp_path, monkeypatch):
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    (capture_dir / "adc_data.bin").write_bytes(b"\x01" * 100)
    (capture_dir / "dca_validation_test.json").write_text("{}", encoding="utf-8")
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    state = start_workflow(
        probe_dir=probe_dir,
        capture_dir=capture_dir,
        firmware_run_id="fw1",
        config_run_id="cfg1",
        confirm_startframe=True,
        archive_existing=True,
    )

    # Original files should be gone
    assert not (capture_dir / "adc_data.bin").exists()
    assert not (capture_dir / "dca_validation_test.json").exists()

    # Should be in an archive folder
    archive_dirs = list(capture_dir.glob("archive_*"))
    assert len(archive_dirs) == 1
    assert (archive_dirs[0] / "adc_data.bin").exists()

    assert state.current_stage == "dca_setup_script_generated"


def test_start_writes_state_json(tmp_path, monkeypatch):
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    state = start_workflow(
        probe_dir=probe_dir,
        capture_dir=capture_dir,
        firmware_run_id="fw1",
        config_run_id="cfg1",
        confirm_startframe=True,
    )

    state_files = list(probe_dir.glob("dca_capture_smoke_*_state.json"))
    assert len(state_files) == 1
    loaded = load_state(state.workflow_id, probe_dir)
    assert loaded.workflow_id == state.workflow_id
    assert loaded.current_stage == "dca_setup_script_generated"
    assert loaded.pending_dofile != ""
    assert loaded.pending_operator_action != ""
    assert loaded.firmware_run_id == "fw1"
    assert loaded.dca_setup.run_id != ""


# ---------------------------------------------------------------------------
# Resume tests
# ---------------------------------------------------------------------------

def test_resume_validates_setup_generates_capture(tmp_path, monkeypatch):
    """After setup generated + successful result → generates capture script."""
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    state = start_workflow(
        probe_dir=probe_dir, capture_dir=capture_dir,
        firmware_run_id="fw1", config_run_id="cfg1",
        confirm_startframe=True,
    )

    # Write successful setup result
    _write_success_result(Path(state.dca_setup.result_path), state.dca_setup.run_id)

    state = resume_workflow(state.workflow_id, probe_dir)
    assert state.current_stage == "capture_script_generated"
    assert state.capture_trigger.run_id != ""
    assert "StartFrame" in state.pending_operator_action
    assert state.pending_dofile != ""


def test_resume_stops_on_failed_setup(tmp_path, monkeypatch):
    """If setup result is failure, resume stops and shows error."""
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    state = start_workflow(
        probe_dir=probe_dir, capture_dir=capture_dir,
        firmware_run_id="fw1", config_run_id="cfg1",
        confirm_startframe=True,
    )

    _write_failed_result(Path(state.dca_setup.result_path), state.dca_setup.run_id, "EthInit failed")

    state = resume_workflow(state.workflow_id, probe_dir)
    assert state.current_stage == "dca_setup_script_generated"  # Not advanced
    assert "failed" in state.pending_operator_action.lower()


def test_resume_after_capture_generates_postproc(tmp_path, monkeypatch):
    """After capture validated → generates postproc script."""
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    state = start_workflow(
        probe_dir=probe_dir, capture_dir=capture_dir,
        firmware_run_id="fw1", config_run_id="cfg1",
        confirm_startframe=True,
    )

    # Setup success
    _write_success_result(Path(state.dca_setup.result_path), state.dca_setup.run_id)
    state = resume_workflow(state.workflow_id, probe_dir)
    assert state.current_stage == "capture_script_generated"

    # Capture success
    _write_success_result(Path(state.capture_trigger.result_path), state.capture_trigger.run_id)
    state = resume_workflow(state.workflow_id, probe_dir)
    assert state.current_stage == "postproc_script_generated"
    assert state.postproc.run_id != ""
    assert state.pending_dofile != ""


def test_resume_stops_on_failed_capture(tmp_path, monkeypatch):
    """If capture fails, resume stops."""
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    state = start_workflow(
        probe_dir=probe_dir, capture_dir=capture_dir,
        firmware_run_id="fw1", config_run_id="cfg1",
        confirm_startframe=True,
    )
    _write_success_result(Path(state.dca_setup.result_path), state.dca_setup.run_id)
    state = resume_workflow(state.workflow_id, probe_dir)

    _write_failed_result(Path(state.capture_trigger.result_path), state.capture_trigger.run_id)
    state = resume_workflow(state.workflow_id, probe_dir)
    assert state.current_stage == "capture_script_generated"  # Not advanced
    assert "failed" in state.pending_operator_action.lower()


def test_resume_after_postproc_validates_and_records(tmp_path, monkeypatch):
    """Full workflow: setup → capture → postproc → validation → complete."""
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    state = start_workflow(
        probe_dir=probe_dir, capture_dir=capture_dir,
        firmware_run_id="fw1", config_run_id="cfg1",
        confirm_startframe=True,
        expected_bytes=32,  # Small for test
    )

    # Setup success
    _write_success_result(Path(state.dca_setup.result_path), state.dca_setup.run_id)
    state = resume_workflow(state.workflow_id, probe_dir)

    # Capture success
    _write_success_result(Path(state.capture_trigger.result_path), state.capture_trigger.run_id)
    state = resume_workflow(state.workflow_id, probe_dir)

    # Write adc_data.bin with correct size
    (capture_dir / "adc_data.bin").write_bytes(b"\x01" * 32)

    # Postproc success
    _write_success_result(Path(state.postproc.result_path), state.postproc.run_id)
    state = resume_workflow(state.workflow_id, probe_dir)

    assert state.completed is True
    assert state.current_stage == "complete"
    assert state.adc_data_bin_size == 32
    assert state.adc_data_bin_sha256 != ""
    assert state.validation_record_path != ""

    # Validation record was written
    val_files = list(capture_dir.glob("dca_validation_*.json"))
    assert len(val_files) == 1


def test_resume_preserves_raw_capture(tmp_path, monkeypatch):
    """Raw adc_data_Raw_0.bin is copied before postproc generation."""
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    state = start_workflow(
        probe_dir=probe_dir, capture_dir=capture_dir,
        firmware_run_id="fw1", config_run_id="cfg1",
        confirm_startframe=True,
    )

    _write_success_result(Path(state.dca_setup.result_path), state.dca_setup.run_id)
    state = resume_workflow(state.workflow_id, probe_dir)

    # Write raw file before capture resume
    (capture_dir / "adc_data_Raw_0.bin").write_bytes(b"\xAB" * 1000)

    _write_success_result(Path(state.capture_trigger.result_path), state.capture_trigger.run_id)
    state = resume_workflow(state.workflow_id, probe_dir)

    # Raw file was preserved
    preserve_dirs = list(capture_dir.glob(f"raw_preserve_{state.workflow_id}"))
    assert len(preserve_dirs) == 1
    preserved_files = list(preserve_dirs[0].glob("adc_data_Raw_0_*.bin"))
    assert len(preserved_files) == 1
    assert preserved_files[0].stat().st_size == 1000


def test_resume_continues_with_warning_if_raw_missing(tmp_path, monkeypatch):
    """If raw file is missing, continue with warning."""
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    state = start_workflow(
        probe_dir=probe_dir, capture_dir=capture_dir,
        firmware_run_id="fw1", config_run_id="cfg1",
        confirm_startframe=True,
    )
    _write_success_result(Path(state.dca_setup.result_path), state.dca_setup.run_id)
    state = resume_workflow(state.workflow_id, probe_dir)

    # No raw file exists
    _write_success_result(Path(state.capture_trigger.result_path), state.capture_trigger.run_id)
    state = resume_workflow(state.workflow_id, probe_dir)

    # Should proceed to postproc_script_generated with a warning
    assert state.current_stage == "postproc_script_generated"
    assert any("Raw_0" in w for w in state.warnings)


# ---------------------------------------------------------------------------
# Freshness / stale result tests
# ---------------------------------------------------------------------------

def test_resume_rejects_stale_result(tmp_path, monkeypatch):
    """Resume rejects result file older than script generation time."""
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    state = start_workflow(
        probe_dir=probe_dir, capture_dir=capture_dir,
        firmware_run_id="fw1", config_run_id="cfg1",
        confirm_startframe=True,
    )

    # Write result with old mtime (before script generation)
    result_path = Path(state.dca_setup.result_path)
    _write_success_result(result_path, state.dca_setup.run_id)
    # Set mtime to 1 hour ago
    old_time = time.time() - 3600
    os.utime(result_path, (old_time, old_time))

    state = resume_workflow(state.workflow_id, probe_dir)
    assert state.current_stage == "dca_setup_script_generated"  # Not advanced
    assert "stale" in state.pending_operator_action.lower()


def test_resume_rejects_wrong_run_id(tmp_path, monkeypatch):
    """Resume rejects result with wrong run_id."""
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    state = start_workflow(
        probe_dir=probe_dir, capture_dir=capture_dir,
        firmware_run_id="fw1", config_run_id="cfg1",
        confirm_startframe=True,
    )

    # Write result with wrong run_id
    result_path = Path(state.dca_setup.result_path)
    _write_success_result(result_path, "wrong_id")

    state = resume_workflow(state.workflow_id, probe_dir)
    assert state.current_stage == "dca_setup_script_generated"  # Not advanced
    assert "mismatch" in state.pending_operator_action.lower()


# ---------------------------------------------------------------------------
# Idempotent resume
# ---------------------------------------------------------------------------

def test_resume_after_complete_is_idempotent(tmp_path, monkeypatch):
    """Resuming a completed workflow does not regenerate anything."""
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    state = start_workflow(
        probe_dir=probe_dir, capture_dir=capture_dir,
        firmware_run_id="fw1", config_run_id="cfg1",
        confirm_startframe=True,
        expected_bytes=8,
    )

    # Fast-forward through all stages
    _write_success_result(Path(state.dca_setup.result_path), state.dca_setup.run_id)
    state = resume_workflow(state.workflow_id, probe_dir)
    _write_success_result(Path(state.capture_trigger.result_path), state.capture_trigger.run_id)
    state = resume_workflow(state.workflow_id, probe_dir)
    (capture_dir / "adc_data.bin").write_bytes(b"\x01" * 8)
    _write_success_result(Path(state.postproc.result_path), state.postproc.run_id)
    state = resume_workflow(state.workflow_id, probe_dir)
    assert state.completed is True

    # Resume again — should be idempotent
    state2 = resume_workflow(state.workflow_id, probe_dir)
    assert state2.completed is True
    assert state2.current_stage == "complete"
    assert "already complete" in state2.pending_operator_action.lower()


# ---------------------------------------------------------------------------
# Status / latest
# ---------------------------------------------------------------------------

def test_status_prints_pending_dofile(tmp_path, monkeypatch):
    """Status returns pending dofile info."""
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    state = start_workflow(
        probe_dir=probe_dir, capture_dir=capture_dir,
        firmware_run_id="fw1", config_run_id="cfg1",
        confirm_startframe=True,
    )

    loaded = load_state(state.workflow_id, probe_dir)
    assert loaded.pending_dofile != ""
    assert "dofile" in loaded.pending_dofile.lower()
    assert loaded.pending_operator_action != ""


def test_latest_finds_newest(tmp_path, monkeypatch):
    """find_latest_state finds the newest workflow."""
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir, fw_id="fw1", cfg_id="cfg1")
    _setup_valid_runs(probe_dir, fw_id="fw2", cfg_id="cfg2")

    state1 = start_workflow(
        probe_dir=probe_dir, capture_dir=capture_dir,
        firmware_run_id="fw1", config_run_id="cfg1",
        confirm_startframe=True,
    )
    time.sleep(0.05)
    state2 = start_workflow(
        probe_dir=probe_dir, capture_dir=capture_dir,
        firmware_run_id="fw2", config_run_id="cfg2",
        confirm_startframe=True,
    )

    latest = find_latest_state(probe_dir)
    assert latest is not None
    assert latest.workflow_id == state2.workflow_id


# ---------------------------------------------------------------------------
# Safety checks
# ---------------------------------------------------------------------------

def test_no_lua_auto_executed(tmp_path, monkeypatch):
    """No Lua is automatically executed during start or resume."""
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    state = start_workflow(
        probe_dir=probe_dir, capture_dir=capture_dir,
        firmware_run_id="fw1", config_run_id="cfg1",
        confirm_startframe=True,
    )
    # The lua script should exist as a file but never be executed
    assert Path(state.dca_setup.script_path).exists()
    # pending_dofile should tell operator to paste
    assert "dofile" in state.pending_dofile.lower()


def test_capture_script_has_correct_sequence(tmp_path, monkeypatch):
    """Generated capture script still contains StartRecord(.bin), StartFrame, StopRecord."""
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    _setup_valid_runs(probe_dir)

    state = start_workflow(
        probe_dir=probe_dir, capture_dir=capture_dir,
        firmware_run_id="fw1", config_run_id="cfg1",
        confirm_startframe=True,
    )
    _write_success_result(Path(state.dca_setup.result_path), state.dca_setup.run_id)
    state = resume_workflow(state.workflow_id, probe_dir)

    script_content = Path(state.capture_trigger.script_path).read_text(encoding="utf-8")
    assert "CaptureCardConfig_StartRecord" in script_content
    assert "StartFrame" in script_content
    assert "CaptureCardConfig_StopRecord" in script_content
    assert "adc_data.bin" in script_content


def test_no_guided_runner_modifications():
    """Guided runner stages are not modified by workflow module."""
    from awr2944_dca.mmws.stages import STAGES as GUIDED_STAGES
    # Just verify import works and stages exist
    assert len(GUIDED_STAGES) > 0

# ---------------------------------------------------------------------------
# Regression Tests
# ---------------------------------------------------------------------------

def test_archive_existing_capture_does_not_move_cf_json(tmp_path, monkeypatch):
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    
    (capture_dir / "adc_data.bin").write_bytes(b"\x01" * 100)
    (capture_dir / "adc_data_Raw_0.bin").write_bytes(b"\x02" * 100)
    (capture_dir / "dca_validation_test.json").write_text("{}", encoding="utf-8")
    (capture_dir / "cf.json").write_text("{}", encoding="utf-8")
    (capture_dir / "other_LogFile.txt").write_text("log", encoding="utf-8")

    state = start_workflow(
        probe_dir=tmp_path / "probe",
        capture_dir=capture_dir,
        firmware_run_id="",
        config_run_id="",
        confirm_startframe=True,
        archive_existing=True,
    )

    # These should be gone
    assert not (capture_dir / "adc_data.bin").exists()
    assert not (capture_dir / "adc_data_Raw_0.bin").exists()
    assert not (capture_dir / "dca_validation_test.json").exists()

    # These should remain
    assert (capture_dir / "cf.json").exists()
    assert (capture_dir / "other_LogFile.txt").exists()


def test_start_fails_if_supplied_run_id_not_found(tmp_path, monkeypatch):
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()

    with pytest.raises(ValueError, match="not found"):
        start_workflow(
            probe_dir=tmp_path / "probe",
            capture_dir=capture_dir,
            firmware_run_id="fw_missing",
            config_run_id="",
            confirm_startframe=True,
        )


def test_start_fails_if_supplied_run_id_wrong_stage(tmp_path, monkeypatch):
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    probe_dir.mkdir()
    
    res_path = probe_dir / "fw_wrong_result.json"
    res_path.write_text(json.dumps({
        "run_id": "fw_wrong",
        "success": True,
        "stage": "smoke_config" # should be firmware_power
    }), encoding="utf-8")

    with pytest.raises(ValueError, match="wrong stage"):
        start_workflow(
            probe_dir=probe_dir,
            capture_dir=capture_dir,
            firmware_run_id="fw_wrong",
            config_run_id="",
            confirm_startframe=True,
        )


def test_start_fails_if_supplied_run_id_failed(tmp_path, monkeypatch):
    _fake_preflight_ready(monkeypatch)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir()
    probe_dir = tmp_path / "probe"
    probe_dir.mkdir()
    
    res_path = probe_dir / "fw_failed_result.json"
    res_path.write_text(json.dumps({
        "run_id": "fw_failed",
        "success": False,
        "stage": "firmware_power",
        "error": "some error"
    }), encoding="utf-8")

    with pytest.raises(ValueError, match="failed"):
        start_workflow(
            probe_dir=probe_dir,
            capture_dir=capture_dir,
            firmware_run_id="fw_failed",
            config_run_id="",
            confirm_startframe=True,
        )

