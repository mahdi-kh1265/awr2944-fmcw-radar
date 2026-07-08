import json
import pytest
from awr2944_dca.mmws.guided_runner import GuidedWorkflowState
from awr2944_dca.mmws.failure_report import generate_failure_report
from pathlib import Path

def run():
    p = Path("tmp_test_dir")
    p.mkdir(exist_ok=True)
    fw_id = "fwsym"
    cfg_id = "cfgsym"

    prog_path = p / f"{fw_id}_firmware_power_progress.jsonl"
    prog_path.write_text(json.dumps({"cmd": "PowerOn", "ret": 0, "ok": True}) + "\n", encoding="utf-8")

    state_path = p / f"guided_newsummary_state.json"
    state = GuidedWorkflowState(
        workflow_id="newsummary",
        label="test",
        pid=None,
        state_path=str(state_path),
        current_stage="failed",
        firmware_run_id=fw_id,
        config_run_id=cfg_id,
    )
    state.errors.append("session_summarized failed: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'OptionInfo'")
    state.save()

    report = generate_failure_report(state_path=str(state_path), probe_dir_override=str(p))
    print("Detected:", report.detected_failure_type)

run()