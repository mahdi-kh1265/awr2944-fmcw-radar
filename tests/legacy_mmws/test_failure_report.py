import pytest
pytestmark = pytest.mark.legacy_mmws
import json
from pathlib import Path
import pytest

from awr2944_dca.mmws.failure_report import generate_failure_report
from awr2944_dca.cli import mmws_post_app
from typer.testing import CliRunner

runner = CliRunner()

def test_failure_report_no_artifacts(tmp_path):
    report = generate_failure_report(latest=True, probe_dir_str=str(tmp_path))
    assert report.detected_failure_type == "unknown"

def test_failure_report_guided_state_failed(tmp_path):
    sf = tmp_path / "guided_1234_state.json"
    state_data = {
        "workflow_id": "1234",
        "label": "test",
        "pid": 123,
        "state_path": str(sf),
        "current_stage": "failed",
        "firmware_run_id": "fw1",
        "config_run_id": "cfg1",
        "errors": ["_atomic_write_manifest() got an unexpected keyword argument 'manifest_path'"]
    }
    sf.write_text(json.dumps(state_data))
    
    report = generate_failure_report(latest=True, probe_dir_str=str(tmp_path))
    assert report.detected_failure_type == "guided_workflow_failed"
    assert report.resume_safe == "false"
    assert "guided_runner called a private manifest helper" in report.likely_root_cause
    assert "Do not resume this workflow" in report.recommended_next_action

def test_failure_report_direct_state_arg(tmp_path):
    sf = tmp_path / "guided_1234_state.json"
    sf.write_text(json.dumps({
        "workflow_id": "1234",
        "label": "test",
        "pid": 123,
        "state_path": str(sf),
        "current_stage": "failed"
    }))
    
    report = generate_failure_report(state_path=str(sf), probe_dir_str=str(tmp_path))
    assert report.detected_failure_type == "guided_workflow_failed"
    assert report.primary_artifact == str(sf)

def test_failure_report_run_failed(tmp_path):
    rf = tmp_path / "fw1_firmware_power_result.json"
    rf.write_text(json.dumps({"success": False, "run_id": "fw1"}))
    
    report = generate_failure_report(latest=True, probe_dir_str=str(tmp_path))
    assert report.detected_failure_type == "run_failed"
    assert report.resume_safe == "false"

def test_failure_report_dirty_session(tmp_path):
    af = tmp_path / "123_session_audit.json"
    af.write_text(json.dumps({"requires_power_cycle": True}))
    
    report = generate_failure_report(latest=True, probe_dir_str=str(tmp_path))
    assert report.detected_failure_type == "dirty_session"
    assert report.power_cycle_required is True
    assert report.resume_safe == "false"

def test_failure_report_orphan_manifest(tmp_path):
    mf = tmp_path / "1111_manifest.json"
    mf.write_text(json.dumps({"run_id": "1111"}))
    
    report = generate_failure_report(latest=True, probe_dir_str=str(tmp_path))
    assert report.detected_failure_type == "orphan_manifest"
    assert report.primary_artifact == "1111_manifest.json"
    assert "1111_manifest.json" in report.orphan_artifacts

def test_cli_json_output(tmp_path, monkeypatch):
    import awr2944_dca.cli
    import awr2944_dca.mmws.failure_report
    monkeypatch.setattr(awr2944_dca.mmws.failure_report, "_lua_launch_probe_dir", lambda: tmp_path)
    
    sf = tmp_path / "guided_1234_state.json"
    sf.write_text(json.dumps({
        "workflow_id": "1234",
        "label": "test",
        "pid": 123,
        "state_path": str(sf),
        "current_stage": "failed",
        "errors": ["test"]
    }))
    
    res = runner.invoke(mmws_post_app, ["failure-report", "--latest", "--format", "json", "--probe-dir", str(tmp_path)])
    assert res.exit_code == 0
    data = json.loads(res.stdout)
    assert data["detected_failure_type"] == "guided_workflow_failed"
    assert data["workflow_id"] == "1234"
    assert "test" in data["errors"]

def test_cli_text_output(tmp_path, monkeypatch):
    import awr2944_dca.cli
    import awr2944_dca.mmws.failure_report
    monkeypatch.setattr(awr2944_dca.mmws.failure_report, "_lua_launch_probe_dir", lambda: tmp_path)
    
    sf = tmp_path / "guided_1234_state.json"
    sf.write_text(json.dumps({
        "workflow_id": "1234",
        "label": "test",
        "pid": 123,
        "state_path": str(sf),
        "current_stage": "failed",
        "errors": ["_atomic_write_manifest() got an unexpected keyword argument 'manifest_path'"]
    }))
    
    res = runner.invoke(mmws_post_app, ["failure-report", "--latest", "--probe-dir", str(tmp_path)])
    assert res.exit_code == 0
    assert "guided_workflow_failed" in res.stdout
    assert "Do not resume this workflow" in res.stdout

def test_semantic_dry_run_bug(tmp_path):
    sf = tmp_path / "guided_1234_state.json"
    sf.write_text(json.dumps({
        "workflow_id": "1234",
        "label": "test",
        "pid": 123,
        "state_path": str(sf),
        "current_stage": "validation_recorded",
        "dry_run": True
    }))
    
    report = generate_failure_report(state_path=str(sf), probe_dir_str=str(tmp_path))
    assert report.detected_failure_type == "semantic_dry_run_bug"
    assert any("validation_recorded reached during dry_run" in e for e in report.errors)

def test_hardware_likely_touched(tmp_path):
    from awr2944_dca.mmws.failure_report import _check_hardware_touched
    
    # 1. No run_id
    assert _check_hardware_touched(tmp_path, "") is False
    
    # 2. run_id but no progress file
    assert _check_hardware_touched(tmp_path, "norun") == "unknown"
    
    # 3. progress file exists but no hardware commands
    (tmp_path / "safefw_1_progress.jsonl").write_text(json.dumps({"cmd": "WriteToLog"}))
    assert _check_hardware_touched(tmp_path, "safefw") is False
    
    # 4. progress file exists and has hardware commands
    lines = [
        json.dumps({"cmd": "WriteToLog"}),
        json.dumps({"cmd": "PowerOn"})
    ]
    (tmp_path / "hwfw_1_progress.jsonl").write_text("\n".join(lines))
    assert _check_hardware_touched(tmp_path, "hwfw") is True

def test_failure_report_old_mismatch(tmp_path):
    from awr2944_dca.mmws.failure_report import generate_failure_report
    import json
    
    run_id = "testoldmismatch"
    
    # Write result JSON (success)
    res_path = tmp_path / f"{run_id}_firmware_power_result.json"
    res_path.write_text(json.dumps({"success": True}), encoding="utf-8")
    
    # Write progress JSONL (touched hardware)
    prog_path = tmp_path / f"{run_id}_firmware_power_progress.jsonl"
    lines = [
        json.dumps({"cmd": "PowerOn", "ret": 0, "ok": True}),
        json.dumps({"cmd": "RfEnable", "ret": 0, "ok": True})
    ]
    prog_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    
    # Write state JSON (failed at timeout)
    state_path = tmp_path / f"guided_oldmismatch_state.json"
    from awr2944_dca.mmws.guided_runner import GuidedWorkflowState
    state = GuidedWorkflowState(
        workflow_id="oldmismatch",
        label="test",
        pid=None,
        state_path=str(state_path),
        current_stage="failed",
        firmware_run_id=run_id
    )
    state.errors.append("firmware_validated failed: Firmware run failed or timed out.")
    state.save()
    
    report = generate_failure_report(state_path=str(state_path), probe_dir_override=str(tmp_path))
    
    assert report.detected_failure_type == "guided_watch_result_mismatch"
    assert report.hardware_likely_touched is True

def test_failure_report_new_summary_bug(tmp_path):
    from awr2944_dca.mmws.failure_report import generate_failure_report
    import json
    
    fw_id = "fwsym"
    cfg_id = "cfgsym"
    
    # Write progress JSONL (touched hardware)
    prog_path = tmp_path / f"{fw_id}_firmware_power_progress.jsonl"
    prog_path.write_text(json.dumps({"cmd": "PowerOn", "ret": 0, "ok": True}) + "\n", encoding="utf-8")
    prog_path2 = tmp_path / f"{cfg_id}_config_progress.jsonl"
    prog_path2.write_text(json.dumps({"cmd": "ProfileConfig", "ret": 0, "ok": True}) + "\n", encoding="utf-8")
    
    # Write state JSON (failed at summarize_session with OptionInfo error)
    state_path = tmp_path / f"guided_newsummary_state.json"
    from awr2944_dca.mmws.guided_runner import GuidedWorkflowState
    state = GuidedWorkflowState(
        workflow_id="newsummary",
        label="test",
        pid=None,
        state_path=str(state_path),
        current_stage="failed",
        firmware_run_id=fw_id,
        config_run_id=cfg_id
    )
    state.errors.append("session_summarized failed: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'OptionInfo'")
    state.save()
    
    report = generate_failure_report(state_path=str(state_path), probe_dir_override=str(tmp_path))
    
    assert report.detected_failure_type == "guided_summary_failed"
    assert report.hardware_likely_touched is True
    assert report.recommended_next_action == "run summarize-session/record-validation after fixing CLI OptionInfo leak; do not rerun firmware/config blindly."
