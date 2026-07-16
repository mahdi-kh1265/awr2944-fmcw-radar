import json
from pathlib import Path
from typer.testing import CliRunner
from awr2944_dca.cli import app
from awr2944_dca.api.experiment import Experiment

runner = CliRunner()






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
