import pytest
import subprocess
import tempfile
from pathlib import Path
import json
import uuid

def test_check_run_firmware_success(tmp_path):
    run_id = "testfwok"
    manifest = {
        "run_id": run_id,
        "stage": "firmware_power",
        "lua_path": str(tmp_path / f"{run_id}_fw.lua"),
        "result_path": str(tmp_path / f"{run_id}_fw_result.json"),
        "progress_path": str(tmp_path / f"{run_id}_fw_progress.jsonl")
    }
    (tmp_path / f"{run_id}_manifest.json").write_text(json.dumps(manifest))
    
    (tmp_path / f"{run_id}_fw_result.json").write_text(json.dumps({"success": True}))
    
    prog_lines = [
        {"ts": "0.0", "cmd": "DownloadBSSFw", "ret": 0, "ok": True},
        {"ts": "0.1", "cmd": "GetBSSFwVersion", "ret": "02.04.05.03 (20/04/22", "ok": True},
        {"ts": "0.2", "cmd": "RfEnable", "ret": 0, "ok": True}
    ]
    with open(tmp_path / f"{run_id}_fw_progress.jsonl", "w") as f:
        for p in prog_lines:
            f.write(json.dumps(p) + "\n")
            
    # Mock _lua_launch_probe_dir to return tmp_path by monkeypatching or setting an env var?
    # Actually, we can run awr cli with a monkeypatch on the probe dir, or just use the python entrypoint.
    # For a subprocess test, we'll just run it against the real script but we need the CLI to look at tmp_path.
    # Let's use monkeypatch in a direct function call instead of subprocess.
    from awr2944_dca.cli import mmws_post_check_run, _lua_launch_probe_dir
    import awr2944_dca.cli
    
    original_probe = awr2944_dca.cli._lua_launch_probe_dir
    awr2944_dca.cli._lua_launch_probe_dir = lambda: tmp_path
    try:
        # Should not raise any Exit(1)
        mmws_post_check_run(run_id=run_id)
    finally:
        awr2944_dca.cli._lua_launch_probe_dir = original_probe


def test_check_run_firmware_failure(tmp_path):
    run_id = "testfwfail"
    manifest = {
        "run_id": run_id,
        "stage": "firmware_power",
        "result_path": str(tmp_path / f"{run_id}_fw_result.json"),
        "progress_path": str(tmp_path / f"{run_id}_fw_progress.jsonl")
    }
    (tmp_path / f"{run_id}_manifest.json").write_text(json.dumps(manifest))
    
    (tmp_path / f"{run_id}_fw_result.json").write_text(json.dumps({"success": False, "error": "RfEnable failed: -1"}))
    
    prog_lines = [
        {"ts": "0.0", "cmd": "DownloadBSSFw", "ret": 0, "ok": True},
        {"ts": "0.2", "cmd": "RfEnable", "ret": -1, "ok": True} # -1 numeric return for critical command
    ]
    with open(tmp_path / f"{run_id}_fw_progress.jsonl", "w") as f:
        for p in prog_lines:
            f.write(json.dumps(p) + "\n")
            
    from awr2944_dca.cli import mmws_post_check_run
    import awr2944_dca.cli
    
    original_probe = awr2944_dca.cli._lua_launch_probe_dir
    awr2944_dca.cli._lua_launch_probe_dir = lambda: tmp_path
    try:
        mmws_post_check_run(run_id=run_id)
    finally:
        awr2944_dca.cli._lua_launch_probe_dir = original_probe


def test_check_run_smoke_success(tmp_path):
    run_id = "testsmk"
    manifest = {
        "run_id": run_id,
        "stage": "smoke_known_awr2944",
        "result_path": str(tmp_path / f"{run_id}_smk_result.json"),
        "progress_path": str(tmp_path / f"{run_id}_smk_progress.jsonl")
    }
    (tmp_path / f"{run_id}_manifest.json").write_text(json.dumps(manifest))
    
    (tmp_path / f"{run_id}_smk_result.json").write_text(json.dumps({"success": True}))
    
    prog_lines = [
        {"ts": "0.0", "cmd": "ChanNAdcConfig", "ret": 0, "ok": True},
        {"ts": "0.1", "cmd": "ProfileConfig", "ret": 0, "ok": True},
    ]
    with open(tmp_path / f"{run_id}_smk_progress.jsonl", "w") as f:
        for p in prog_lines:
            f.write(json.dumps(p) + "\n")
            
    from awr2944_dca.cli import mmws_post_check_run
    import awr2944_dca.cli
    
    original_probe = awr2944_dca.cli._lua_launch_probe_dir
    awr2944_dca.cli._lua_launch_probe_dir = lambda: tmp_path
    try:
        mmws_post_check_run(run_id=run_id)
    finally:
        awr2944_dca.cli._lua_launch_probe_dir = original_probe


def test_watch_run_timeout(tmp_path):
    run_id = "testwait"
    manifest = {
        "run_id": run_id,
        "stage": "smoke_known_awr2944",
        "result_path": str(tmp_path / f"{run_id}_wait_result.json"),
        "progress_path": str(tmp_path / f"{run_id}_wait_progress.jsonl")
    }
    (tmp_path / f"{run_id}_manifest.json").write_text(json.dumps(manifest))
    
    # Do NOT write result JSON, so it times out.
    
    from awr2944_dca.cli import mmws_post_watch_run
    import awr2944_dca.cli
    import typer
    
    original_probe = awr2944_dca.cli._lua_launch_probe_dir
    awr2944_dca.cli._lua_launch_probe_dir = lambda: tmp_path
    try:
        with pytest.raises(typer.Exit) as e:
            # Short timeout to make test fast
            mmws_post_watch_run(run_id=run_id, timeout=1)
        assert e.value.exit_code == 1
    finally:
        awr2944_dca.cli._lua_launch_probe_dir = original_probe

def test_watch_run_success(tmp_path):
    run_id = "testwaitok"
    manifest = {
        "run_id": run_id,
        "stage": "smoke_known_awr2944",
        "result_path": str(tmp_path / f"{run_id}_wait_result.json"),
        "progress_path": str(tmp_path / f"{run_id}_wait_progress.jsonl")
    }
    (tmp_path / f"{run_id}_manifest.json").write_text(json.dumps(manifest))
    
    (tmp_path / f"{run_id}_wait_result.json").write_text(json.dumps({"success": True}))
    
    from awr2944_dca.cli import mmws_post_watch_run
    import awr2944_dca.cli
    import typer
    
    original_probe = awr2944_dca.cli._lua_launch_probe_dir
    awr2944_dca.cli._lua_launch_probe_dir = lambda: tmp_path
    try:
        with pytest.raises(SystemExit) as e:
            mmws_post_watch_run(run_id=run_id, timeout=2)
        assert e.value.code == 0
    finally:
        awr2944_dca.cli._lua_launch_probe_dir = original_probe
