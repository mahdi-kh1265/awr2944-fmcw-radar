import pytest
pytestmark = pytest.mark.legacy_mmws
import pytest
from pathlib import Path
from typer.testing import CliRunner
from awr2944_dca.cli import app
from awr2944_dca.project import init_project

runner = CliRunner()

def test_capture_smoke_cli_status_and_resume_output(tmp_path, monkeypatch):
    # Mock preflight and hardware to allow workflow to proceed
    from awr2944_dca.dca.preflight import PreflightCheck, PreflightReport
    def fake_preflight(*args, **kwargs):
        return PreflightReport("READY_WITH_WARNINGS", [])
    monkeypatch.setattr("awr2944_dca.dca.workflow.run_dca_preflight", fake_preflight)
    
    # Setup directories
    probe_dir = tmp_path / "probe"
    probe_dir.mkdir(parents=True)
    capture_dir = tmp_path / "PostProc"
    capture_dir.mkdir(parents=True)
    
    # Fake valid firmware and config runs
    fw_run = probe_dir / "fw1_result.json"
    fw_run.write_text('{"success": true}')
    cfg_run = probe_dir / "cfg1_result.json"
    cfg_run.write_text('{"success": true}')
    
    # Initialize project
    init_project("test_proj", root=tmp_path, postproc_dir=capture_dir)
    
    # Start workflow
    result = runner.invoke(app, [
        "dca", "capture-smoke", "start",
        "--probe-dir", str(probe_dir),
        "--capture-dir", str(capture_dir),
        "--firmware-run-id", "fw1",
        "--config-run-id", "cfg1",
        "--confirm-startframe",
        "--project-root", str(tmp_path),
        "--capture-name", "auto_cap",
        "--auto-create-capture"
    ])
    if result.exit_code != 0:
        print(result.stdout)
        if result.exception:
            raise result.exception
    assert result.exit_code == 0
    
    # Extract workflow ID from stdout
    workflow_id = None
    import re
    # Remove rich formatting
    stdout_clean = re.sub(r'\[.*?\]', '', result.stdout)
    for line in stdout_clean.splitlines():
        if "Workflow started:" in line:
            workflow_id = line.split("Workflow started:")[-1].strip()
            break
    if workflow_id is None:
        print("STDOUT WAS:", result.stdout)
    assert workflow_id is not None
    
    # Status output includes project binding fields after start with auto-created capture
    result_status = runner.invoke(app, [
        "dca", "capture-smoke", "status",
        "--workflow-id", workflow_id,
        "--probe-dir", str(probe_dir)
    ])
    assert result_status.exit_code == 0
    assert "Project Binding" in result_status.stdout
    assert "Project Capture ID:" in result_status.stdout
    assert "auto_cap" in result_status.stdout
    assert "Bind requested:     True" in result_status.stdout
    
    # Latest output includes project binding fields
    result_latest = runner.invoke(app, [
        "dca", "capture-smoke", "latest",
        "--probe-dir", str(probe_dir)
    ])
    assert result_latest.exit_code == 0
    assert "Project Binding" in result_latest.stdout
    assert "Project Capture ID:" in result_latest.stdout
    assert "auto_cap" in result_latest.stdout
    assert "Bind requested:     True" in result_latest.stdout
    
    # Fast forward the workflow manually by mocking results
    # 1. DCA setup
    import json
    state_file = probe_dir / f"dca_capture_smoke_{workflow_id}_state.json"
    state_data = json.loads(state_file.read_text())
    setup_run_id = state_data["dca_setup"]["run_id"]
    (Path(state_data["dca_setup"]["result_path"])).write_text(f'{{"success": true, "run_id": "{setup_run_id}"}}')

    result_resume_1 = runner.invoke(app, [
        "dca", "capture-smoke", "resume",
        "--workflow-id", workflow_id,
        "--probe-dir", str(probe_dir)
    ])
    if result_resume_1.exit_code != 0:
        print("RESUME 1 STDOUT:", result_resume_1.stdout)
        if result_resume_1.exception:
            raise result_resume_1.exception
    assert result_resume_1.exit_code == 0
    
    # 2. Capture trigger
    state_data = json.loads(state_file.read_text())
    trigger_run_id = state_data["capture_trigger"]["run_id"]
    (Path(state_data["capture_trigger"]["result_path"])).write_text(f'{{"success": true, "run_id": "{trigger_run_id}"}}')
    
    result_resume_2 = runner.invoke(app, [
        "dca", "capture-smoke", "resume",
        "--workflow-id", workflow_id,
        "--probe-dir", str(probe_dir)
    ])
    if result_resume_2.exit_code != 0:
        print("RESUME 2 STDOUT:", result_resume_2.stdout)
        if result_resume_2.exception:
            raise result_resume_2.exception
    assert result_resume_2.exit_code == 0
    
    # 3. Postproc (needs actual mock bin file for expected size 4M)
    (capture_dir / "adc_data.bin").write_bytes(b"A" * 4194304)
    state_data = json.loads(state_file.read_text())
    postproc_run_id = state_data["postproc"]["run_id"]
    (Path(state_data["postproc"]["result_path"])).write_text(f'{{"success": true, "run_id": "{postproc_run_id}"}}')
    
    # Final resume output includes project capture bound + verify PASS
    result_final = runner.invoke(app, [
        "dca", "capture-smoke", "resume",
        "--workflow-id", workflow_id,
        "--probe-dir", str(probe_dir)
    ])
    assert result_final.exit_code == 0
    assert "Workflow COMPLETE" in result_final.stdout
    assert "Project Binding" in result_final.stdout
    assert "Capture verify:     PASS" in result_final.stdout
    assert "Capture manifest:" in result_final.stdout
    assert "Bound raw SHA256:" in result_final.stdout
    
    # Status output includes project binding fields after completed workflow
    result_status_final = runner.invoke(app, [
        "dca", "capture-smoke", "status",
        "--workflow-id", workflow_id,
        "--probe-dir", str(probe_dir)
    ])
    assert result_status_final.exit_code == 0
    assert "Project Binding" in result_status_final.stdout
    assert "Capture verify:     PASS" in result_status_final.stdout
    
    # State JSON persists expected fields
    final_state_data = json.loads(state_file.read_text())
    assert final_state_data["bind_requested"] is True
    assert final_state_data["bind_completed"] is True
    assert final_state_data["capture_verify_passed"] is True
    assert "auto_cap" in final_state_data["capture_id"]
    assert final_state_data["capture_manifest_path_rel"] != ""
    assert final_state_data["bound_raw_file_sha256"] != ""
