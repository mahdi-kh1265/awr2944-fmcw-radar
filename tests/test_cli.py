"""CLI smoke tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from awr2944_dca.cli import app


runner = CliRunner()
EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "configs"


class TestCLIHelp:
    """Test that all commands have --help output."""

    def test_main_help(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "AWR2944" in result.output

    def test_doctor_help(self) -> None:
        result = runner.invoke(app, ["doctor", "--help"])
        assert result.exit_code == 0

    def test_inspect_config_help(self) -> None:
        result = runner.invoke(app, ["inspect-config", "--help"])
        assert result.exit_code == 0

    def test_parse_help(self) -> None:
        result = runner.invoke(app, ["parse", "--help"])
        assert result.exit_code == 0

    def test_process_help(self) -> None:
        result = runner.invoke(app, ["process", "--help"])
        assert result.exit_code == 0


class TestDoctor:
    """Test awr doctor command."""

    def test_doctor_runs(self) -> None:
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
        assert "Python version" in result.output
        assert "numpy" in result.output


class TestInspectConfig:
    """Test awr inspect-config command."""

    def test_inspect_first_capture(self) -> None:
        result = runner.invoke(app, ["inspect-config", str(EXAMPLES_DIR / "first_capture.yaml")])
        assert result.exit_code == 0
        assert "first_capture" in result.output
        assert "Range resolution" in result.output

    def test_inspect_walking_person(self) -> None:
        result = runner.invoke(app, ["inspect-config", str(EXAMPLES_DIR / "walking_person.yaml")])
        assert result.exit_code == 0
        assert "walking_person" in result.output
        assert "tdm_mimo" in result.output

    def test_inspect_nonexistent_config(self) -> None:
        result = runner.invoke(app, ["inspect-config", "nonexistent.yaml"])
        assert result.exit_code != 0
