import pytest
import json
import subprocess
import sys
import os
from pathlib import Path
from unittest.mock import patch
from awr2944_dca.project import init_project

def _run_cli(*args):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent.parent / "src")
    return subprocess.run(
        [sys.executable, "-m", "awr2944_dca.capture_cli", *args],
        capture_output=True, text=True, env=env
    )

def test_cli_help(tmp_path):
    result = _run_cli("--help")
    assert result.returncode == 0
    assert "--project-root" in result.stdout
    assert "--dry-run" in result.stdout

def test_cli_dry_run(tmp_path):
    init_project("test_proj", tmp_path)
    result = _run_cli(
        "smoke_v1",
        "--project-root", str(tmp_path),
        "--frames", "8",
        "--guard-frames", "1",
        "--dry-run"
    )
    assert result.returncode == 0
    
    plan = json.loads(result.stdout)
    assert plan["hardware_touched"] is False
    assert plan["total_frames"] == 9
    assert plan["canonical_frames"] == 8
    assert plan["expected_native_dca_bytes"] == 4718592
    assert plan["expected_canonical_dca_bytes"] == 4194304
    assert plan["logical_depacked_bytes"] == 2359296
    assert plan["canonical_logical_bytes"] == 2097152
    assert plan["canonical_cube"] == [8, 128, 4, 256]
    assert plan["dca_storage_expansion_factor"] == 2

def test_cli_missing_project_fails(tmp_path):
    # No project initialized in tmp_path
    result = _run_cli(
        "smoke_v1",
        "--project-root", str(tmp_path),
        "--dry-run"
    )
    assert result.returncode == 1
    assert "Error: Explicit --project-root" in result.stdout

@pytest.mark.skip(reason="Fails when real hardware is connected")
def test_cli_zero_byte_capture_returns_nonzero(tmp_path):
    init_project("test_proj", tmp_path)
    
    # The CLI runs in a subprocess, so mocks won't work.
    # Without real hardware, it will genuinely time out.
    result = _run_cli(
        "smoke_v1",
        "--project-root", str(tmp_path),
        "--frames", "9",
        "--guard-frames", "1"
    )
    
    assert result.returncode == 1
    assert "CAPTURE_FAILED" not in result.stdout
    assert "[FATAL] Capture failed at stage: " in result.stdout
    assert "Reason:" in result.stdout
    assert "Success." not in result.stdout
    assert "Capture Complete" not in result.stdout

@pytest.mark.skip(reason="Fails when real hardware is connected")
def test_cli_viewer_not_launched_on_failure(tmp_path):
    init_project("test_proj", tmp_path)
    
    # Subprocess execution, genuine failure
    result = _run_cli(
        "smoke_v1",
        "--project-root", str(tmp_path),
        "--frames", "9",
        "--guard-frames", "1",
        "--launch-viewer" # Request viewer
    )
    
    assert result.returncode == 1
    assert "Opening standalone viewer" not in result.stdout
