import pytest
pytestmark = pytest.mark.legacy_mmws
import json
import uuid
import os
from pathlib import Path
import pytest

from awr2944_dca.legacy_mmws.guided_runner import GuidedWorkflowState, run_guided_workflow, resume_guided_workflow
from awr2944_dca.cli import mmws_post_app
from typer.testing import CliRunner

runner = CliRunner()

def test_dry_run_does_not_write_lua(tmp_path, monkeypatch):
    import awr2944_dca.legacy_mmws.guided_runner
    import awr2944_dca.cli
    
    monkeypatch.setattr(awr2944_dca.cli, "_lua_launch_probe_dir", lambda override=None: tmp_path)
    monkeypatch.setattr(awr2944_dca.legacy_mmws.guided_runner, "_lua_launch_probe_dir", lambda override=None: tmp_path)
    
    res = runner.invoke(mmws_post_app, ["guided-validate", "--label", "test-dry", "--dry-run", "--probe-dir", str(tmp_path)])
    assert res.exit_code == 0, res.output
    assert "DRY-RUN completed. No hardware was touched. No validation was recorded." in res.stdout
    
    # Check that no Lua or manifest files were created
    luas = list(tmp_path.glob("*.lua"))
    manifests = list(tmp_path.glob("*_manifest.json"))
    assert len(luas) == 0
    assert len(manifests) == 0
    
    # Check state JSON flags
    state_files = list(tmp_path.glob("guided_*_state.json"))
    assert len(state_files) == 1
    state = GuidedWorkflowState.load(str(state_files[0]))
    assert state.current_stage == "dry_run_completed"
    assert state.dry_run is True
    assert state.hardware_touched is False
    assert state.lua_generated is False
    assert state.validation_recorded is False
    assert state.dry_run_preview.get("firmware_run_id") == "dryrunfw"
    assert state.dry_run_preview.get("config_run_id") == "dryruncfg"
    # Ensure real run IDs weren't set to fake values
    assert state.firmware_run_id == ""
    assert state.config_run_id == ""

def test_atomic_state_write(tmp_path):
    state_path = str(tmp_path / "guided_123_state.json")
    state = GuidedWorkflowState(
        workflow_id="123",
        label="test",
        pid=None,
        state_path=state_path,
        current_stage="created"
    )
    # The save() method writes to .json.tmp then os.replace
    state.save()
    assert Path(state_path).exists()
    assert not Path(state_path + ".tmp").exists()

def test_manual_check_failure_stops_workflow(tmp_path, monkeypatch):
    import awr2944_dca.legacy_mmws.guided_runner as gr
    monkeypatch.setattr(gr, "_lua_launch_probe_dir", lambda override=None: tmp_path)
    
    def fake_manual_check(*args, **kwargs):
        from awr2944_dca.legacy_mmws.gui_connect import ClickFlowResult
        return ClickFlowResult("FAILED", "Simulated failure", None)
        
    monkeypatch.setattr(gr, "manual_check", fake_manual_check)
    monkeypatch.setattr(gr, "attach_mmwave_studio", lambda *a, **kw: (None, None))
    
    with pytest.raises(SystemExit) as exc:
        gr.run_guided_workflow(
            label="failtest",
            pid=None,
            dry_run=False,
            timeout_firmware=10,
            timeout_config=10
        )
    assert exc.value.code == 1
    
    # Verify state was marked failed
    state_files = list(tmp_path.glob("guided_*_state.json"))
    assert len(state_files) == 1
    state = GuidedWorkflowState.load(str(state_files[0]))
    assert state.current_stage == "failed"
    assert "manual_check_passed failed" in state.errors[0]

def test_firmware_preflight_failure_stops_workflow(tmp_path, monkeypatch):
    import awr2944_dca.legacy_mmws.guided_runner as gr
    monkeypatch.setattr(gr, "_lua_launch_probe_dir", lambda override=None: tmp_path)
    monkeypatch.setattr(gr, "attach_mmwave_studio", lambda *a, **kw: (None, None))
    
    def fake_manual_check(*args, **kwargs):
        from awr2944_dca.legacy_mmws.gui_connect import ClickFlowResult
        return ClickFlowResult("MANUAL_CONNECTION_VALID", "", None)
        
    monkeypatch.setattr(gr, "manual_check", fake_manual_check)
    
    def fake_audit(*args, **kwargs):
        from awr2944_dca.legacy_mmws.post_connect import SessionAudit
        return SessionAudit(requires_power_cycle=False, rs232_valid=True)
        
    monkeypatch.setattr(gr, "audit_session", fake_audit)
    monkeypatch.setattr(gr, "connection_gate", lambda *a, **kw: {"gate_passed": True})
    monkeypatch.setattr(gr, "dump_output_snapshot", lambda *a, **kw: None)
    
    def fake_preflight(*args, **kwargs):
        return False, ["Preflight fail"]
        
    monkeypatch.setattr(gr, "preflight_firmware", fake_preflight)
    
    with pytest.raises(SystemExit) as exc:
        gr.run_guided_workflow(
            label="failtest",
            pid=None,
            dry_run=False,
            timeout_firmware=10,
            timeout_config=10
        )
    assert exc.value.code == 1
    
    state_files = list(tmp_path.glob("guided_*_state.json"))
    state = GuidedWorkflowState.load(str(state_files[0]))
    assert state.current_stage == "failed"
    assert "firmware_preflight_passed failed" in state.errors[0]

def test_resume_from_firmware_script_generated(tmp_path, monkeypatch):
    import awr2944_dca.legacy_mmws.guided_runner as gr
    
    state_path = tmp_path / "guided_123_state.json"
    state = GuidedWorkflowState(
        workflow_id="123",
        label="test",
        pid=None,
        state_path=str(state_path),
        current_stage="firmware_script_generated",
        firmware_run_id="fw_id_123",
        firmware_dofile="dofile([[test.lua]])"
    )
    state.save()
    
    monkeypatch.setattr(gr, "_lua_launch_probe_dir", lambda override=None: tmp_path)
    
    stages_hit = []
    def fake_watch_run_sync(run_id, timeout, probe_dir=None):
        stages_hit.append("watch_run_" + run_id)
        return True
        
    monkeypatch.setattr(gr, "watch_run_sync", fake_watch_run_sync)
    monkeypatch.setattr(gr, "attach_mmwave_studio", lambda *a, **kw: (None, None))
    monkeypatch.setattr(gr, "connection_gate", lambda *a, **kw: {"gate_passed": True})
    monkeypatch.setattr(gr, "dump_output_snapshot", lambda *a, **kw: None)
    
    def fake_audit(*args, **kwargs):
        from awr2944_dca.legacy_mmws.post_connect import SessionAudit
        return SessionAudit(requires_power_cycle=False, rs232_valid=True)
    monkeypatch.setattr(gr, "audit_session", fake_audit)
    
    monkeypatch.setattr(gr, "preflight_config", lambda *a, **kw: (True, []))
    
    def fake_generate_cfg(state_obj, dry_run):
        stages_hit.append("generate_config")
        state_obj.config_run_id = "cfg_id_123"
        
    monkeypatch.setattr(gr, "step_generate_config", fake_generate_cfg)
    monkeypatch.setattr(gr, "summarize_session_sync", lambda *a, **kw: True)
    monkeypatch.setattr(gr, "record_validation_sync", lambda *a, **kw: True)
    
    gr.resume_guided_workflow(str(state_path))
    
    assert "watch_run_fw_id_123" in stages_hit
    assert "generate_config" in stages_hit
    assert "watch_run_cfg_id_123" in stages_hit
    
    final_state = GuidedWorkflowState.load(str(state_path))
    assert final_state.current_stage == "validation_recorded"

def test_resume_records_validation(tmp_path, monkeypatch):
    import awr2944_dca.legacy_mmws.guided_runner as gr
    
    state_path = tmp_path / "guided_123_state.json"
    state = GuidedWorkflowState(
        workflow_id="123",
        label="test",
        pid=None,
        state_path=str(state_path),
        current_stage="config_validated",
        firmware_run_id="fw",
        config_run_id="cfg"
    )
    state.save()
    
    monkeypatch.setattr(gr, "_lua_launch_probe_dir", lambda override=None: tmp_path)
    monkeypatch.setattr(gr, "summarize_session_sync", lambda *a, **kw: True)
    
    recorded = []
    def fake_record(fw, cfg, label, probe_dir=None):
        recorded.append((fw, cfg, label))
        return True
        
    monkeypatch.setattr(gr, "record_validation_sync", fake_record)
    
    gr.resume_guided_workflow(str(state_path))
    
    assert len(recorded) == 1
    assert recorded[0] == ("fw", "cfg", "test")
    final_state = GuidedWorkflowState.load(str(state_path))
    assert final_state.current_stage == "validation_recorded"

def test_firmware_script_generation(tmp_path, monkeypatch):
    import awr2944_dca.legacy_mmws.guided_runner as gr
    
    state_path = tmp_path / "guided_123_state.json"
    state = GuidedWorkflowState(
        workflow_id="123",
        label="test",
        pid=None,
        state_path=str(state_path),
        current_stage="firmware_preflight_passed"
    )
    
    monkeypatch.setattr(gr, "_lua_launch_probe_dir", lambda override=None: tmp_path)
    
    def fake_generate_fw(run_id, lua_path):
        from awr2944_dca.legacy_mmws.post_connect import GeneratedScript
        return GeneratedScript(
            script="-- dummy fw",
            run_id=run_id,
            lua_path=lua_path,
            result_path=tmp_path / "res.json",
            progress_path=tmp_path / "prog.jsonl",
            dofile="dofile([[fake]])",
            metadata={}
        )
        
    monkeypatch.setattr(gr, "generate_firmware_power_script", fake_generate_fw)
    
    gr.step_generate_firmware(state, dry_run=False)
    
    assert state.firmware_run_id != ""
    assert state.firmware_run_id != "dryrunfw"
    assert state.lua_generated is True
    assert state.firmware_dofile == "dofile([[fake]])"
    assert (tmp_path / f"{state.firmware_run_id}_firmware_power.lua").read_text() == "-- dummy fw"

