import json
import pytest
from awr2944_dca.mmws.guided_runner import GuidedWorkflowState
from awr2944_dca.mmws.failure_report import generate_failure_report, _check_hardware_touched, _lua_launch_probe_dir
from pathlib import Path

def run():
    p = Path("tmp_test_dir").resolve()
    fw_id = "fwsym"
    cfg_id = "cfgsym"

    print("Checking glob:", list(p.glob(f"{fw_id}_*_progress.jsonl")))
    probe_dir = _lua_launch_probe_dir(str(p))
    print("Probe dir:", probe_dir)
    print("Direct _check_hardware_touched:", _check_hardware_touched(probe_dir, fw_id))

run()