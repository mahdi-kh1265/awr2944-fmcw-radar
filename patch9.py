import re

with open('tests/test_failure_report.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace test_failure_report_old_mismatch
old_oldmismatch = '''    # Write state JSON (failed at timeout)
    state_path = tmp_path / f"guided_oldmismatch_state.json"
    state = {
        "workflow_id": "oldmismatch",
        "label": "test",
        "pid": None,
        "state_path": str(state_path),
        "current_stage": "failed",
        "firmware_run_id": run_id,
        "errors": ["firmware_validated failed: Firmware run failed or timed out."]
    }
    state_path.write_text(json.dumps(state), encoding="utf-8")'''

new_oldmismatch = '''    # Write state JSON (failed at timeout)
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
    state.save()'''
content = content.replace(old_oldmismatch, new_oldmismatch)

# Replace test_failure_report_new_summary_bug
old_newsummary = '''    # Write state JSON (failed at summarize_session with OptionInfo error)
    state_path = tmp_path / f"guided_newsummary_state.json"
    state = {
        "workflow_id": "newsummary",
        "label": "test",
        "pid": None,
        "state_path": str(state_path),
        "current_stage": "failed",
        "firmware_run_id": fw_id,
        "config_run_id": cfg_id,
        "errors": ["session_summarized failed: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'OptionInfo'"]
    }
    state_path.write_text(json.dumps(state), encoding="utf-8")'''

new_newsummary = '''    # Write state JSON (failed at summarize_session with OptionInfo error)
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
    state.save()'''
content = content.replace(old_newsummary, new_newsummary)

with open('tests/test_failure_report.py', 'w', encoding='utf-8') as f:
    f.write(content)