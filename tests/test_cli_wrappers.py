import json
from pathlib import Path
from typer.testing import CliRunner
from awr2944_dca.cli import app
from awr2944_dca.api.experiment import Experiment

runner = CliRunner()

def test_cli_probe_status_missing(tmp_path, monkeypatch):
    # Setup experiment
    exp = Experiment.init(name="test_probe", preset="first-capture", root=tmp_path)
    monkeypatch.chdir(exp.root_dir)
    
    result = runner.invoke(app, ["ti", "probe-status"])
    assert result.exit_code == 0
    assert "NOT RUN" in result.stdout

def test_cli_probe_status_success(tmp_path, monkeypatch):
    exp = Experiment.init(name="test_probe_success", preset="first-capture", root=tmp_path)
    monkeypatch.chdir(exp.root_dir)
    
    log_dir = exp.root_dir / "ti" / "probe_logs"
    log_dir.mkdir(parents=True)
    json_path = log_dir / "probe_result.json"
    
    mock_data = {
        "probe_executed": True,
        "ar1_available": True,
        "write_to_log_available": True
    }
    json_path.write_text(json.dumps(mock_data))
    
    result = runner.invoke(app, ["ti", "probe-status"])
    assert result.exit_code == 0
    assert "SUCCESS" in result.stdout

def test_cli_probe_status_stale(tmp_path, monkeypatch):
    exp = Experiment.init(name="test_probe_stale", preset="first-capture", root=tmp_path)
    monkeypatch.chdir(exp.root_dir)
    
    log_dir = exp.root_dir / "ti" / "probe_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    json_path = log_dir / "probe_result.json"
    manifest_path = log_dir / "probe_manifest.json"
    
    manifest_path.write_text(json.dumps({"probe_id": "new_id"}))
    json_path.write_text(json.dumps({
        "probe_id": "old_id",
        "probe_executed": True,
        "ar1_available": True,
        "write_to_log_available": True
    }))
    
    result = runner.invoke(app, ["ti", "probe-status"])
    assert result.exit_code == 0
    assert "STALE RESULT" in result.stdout

def test_cli_inventory_status(tmp_path, monkeypatch):
    exp = Experiment.init(name="test_inventory", preset="first-capture", root=tmp_path)
    monkeypatch.chdir(exp.root_dir)
    
    log_dir = exp.root_dir / "ti" / "probe_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    json_path = log_dir / "inventory_result.json"
    manifest_path = log_dir / "inventory_manifest.json"
    
    manifest_path.write_text(json.dumps({"probe_id": "inv_123"}))
    json_path.write_text(json.dumps({
        "probe_id": "inv_123",
        "inventory_executed": True,
        "ar1_exists": True,
        "ar1_type": "table",
        "ar1_iterable": True,
        "ar1_keys": ["Connect", "PowerOn"],
        "_G_keys": ["os", "io"]
    }))
    
    result = runner.invoke(app, ["ti", "inventory-status"])
    assert result.exit_code == 0
    assert "SUCCESS" in result.stdout
    assert "ar1 exists: True" in result.stdout

def test_cli_lua_command(tmp_path):
    script_path = tmp_path / "test.lua"
    script_path.touch()
    result = runner.invoke(app, ["ti", "lua-command", str(script_path)])
    assert result.exit_code == 0
    assert "dofile([[" in result.stdout
    assert str(script_path.resolve()) in result.stdout.replace("\n", "")

def test_cli_summary_formatting(tmp_path, monkeypatch):
    exp = Experiment.init(name="test_summary", preset="first-capture", root=tmp_path)
    monkeypatch.chdir(exp.root_dir)
    
    result = runner.invoke(app, ["summary"])
    assert result.exit_code == 0
    assert "MiB" in result.stdout  # Ensure size format is MiB
    assert "Parser layout:" in result.stdout # Ensure layout string is printed below table
def test_cli_check_warning(tmp_path, monkeypatch):
    exp = Experiment.init(name="test_check_warn", preset="first-capture", root=tmp_path)
    monkeypatch.chdir(exp.root_dir)
    
    # Intentionally trigger a warning (candidate layout)
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0
    assert "No errors; 1 warning(s)." in result.stdout
