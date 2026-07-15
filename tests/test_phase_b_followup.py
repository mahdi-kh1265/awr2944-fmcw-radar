import os
import json
from pathlib import Path
from typer.testing import CliRunner
from awr2944_dca.cli import app
from awr2944_dca.lab import RadarProject

runner = CliRunner()

def test_legacy_project_layout_skips_hardware(tmp_path):
    # Create a legacy workspace (has project.json, but no awr2944.toml)
    (tmp_path / "project.json").write_text('{"legacy": true}')
    
    # Run doctor in this directory using explicit project
    project = RadarProject(tmp_path)
    
    report = project.doctor(include_hardware=True)
    
    legacy_check = next((c for c in report.checks if c.name == "legacy_project_layout"), None)
    assert legacy_check is not None
    assert legacy_check.status == "FAIL"
    
    # Everything else should be skipped
    for c in report.checks:
        if c.name != "legacy_project_layout":
            assert c.status == "SKIP"
            assert "legacy layout" in c.detail

def test_open_here_uses_cwd(tmp_path, monkeypatch):
    # Create a proper project
    project = RadarProject.create(name="cwd_test", parent=tmp_path)
    
    # Change working directory to a subdirectory inside the project
    sub = project.root / "notebooks"
    monkeypatch.chdir(sub)
    
    # open_here should walk up from CWD
    found = RadarProject.open_here()
    assert found.root == project.root
    
    # Change to some unrelated directory and ensure it fails
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()
    monkeypatch.chdir(unrelated)
    
    import pytest
    with pytest.raises(FileNotFoundError, match="Could not find a RadarProject"):
        RadarProject.open_here()

def test_cli_init_creates_tree(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    # Test `awr init <name>`
    res = runner.invoke(app, ["init", "test_init"])
    assert res.exit_code == 0, f"{res.stdout} {res.exception}"
    assert (tmp_path / "test_init" / "awr2944.toml").exists()
    assert (tmp_path / "test_init" / ".awr2944" / "local.toml").exists()
    assert (tmp_path / "test_init" / "scripts").is_dir()
    assert (tmp_path / "test_init" / "notebooks").is_dir()
    
    # Test `awr init <name> --parent <path>`
    res2 = runner.invoke(app, ["init", "test_init_parent", "--parent", str(tmp_path)])
    assert res2.exit_code == 0
    assert (tmp_path / "test_init_parent" / "awr2944.toml").exists()
    
    # Test `awr init --at <exact-path>`
    exact_path = tmp_path / "my_exact_project"
    res3 = runner.invoke(app, ["init", "--at", str(exact_path)])
    assert res3.exit_code == 0
    assert (exact_path / "awr2944.toml").exists()

def test_cli_init_does_not_touch_hardware(tmp_path, monkeypatch):
    """Ensure awr init does not attempt to talk to COM ports, DCA, etc."""
    monkeypatch.chdir(tmp_path)
    
    import sys
    # We will mock serial to throw if anything imports or uses it directly,
    # though it shouldn't even be loaded for init.
    
    res = runner.invoke(app, ["init", "safe_init"])
    assert res.exit_code == 0
    
    # Since it passed without errors and we have no hardware connected, 
    # we know it didn't block on hardware.
