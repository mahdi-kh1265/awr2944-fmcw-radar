"""Tests for experiment init command."""

from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from awr2944_dca.cli import app
from awr2944_dca.config.schema import RadarConfig

runner = CliRunner()


class TestExperimentInit:
    """Test awr experiment init command."""

    def test_init_creates_directory_structure(self, tmp_path: Path) -> None:
        result = runner.invoke(app, [
            "experiment", "init", "test_exp",
            "--preset", "first-capture",
            "--root", str(tmp_path),
        ])
        assert result.exit_code == 0

        exp_dir = tmp_path / "test_exp"
        assert exp_dir.exists()
        assert (exp_dir / "raw").is_dir()
        assert (exp_dir / "ti_config").is_dir()
        assert (exp_dir / "screenshots").is_dir()
        assert (exp_dir / "compare_layouts").is_dir()
        assert (exp_dir / "capture.yaml").is_file()
        assert (exp_dir / "manifest.yaml").is_file()
        assert (exp_dir / "notes.md").is_file()

    def test_init_capture_yaml_is_valid(self, tmp_path: Path) -> None:
        runner.invoke(app, [
            "experiment", "init", "test_exp",
            "--preset", "first-capture",
            "--root", str(tmp_path),
        ])
        cfg = RadarConfig.from_yaml(tmp_path / "test_exp" / "capture.yaml")
        assert cfg.experiment.name == "test_exp"

    def test_init_manifest_has_metadata(self, tmp_path: Path) -> None:
        runner.invoke(app, [
            "experiment", "init", "test_exp",
            "--preset", "first-capture",
            "--root", str(tmp_path),
        ])
        manifest_path = tmp_path / "test_exp" / "manifest.yaml"
        manifest = yaml.safe_load(manifest_path.read_text())
        assert manifest["experiment"] == "test_exp"
        assert manifest["preset"] == "first-capture"
        assert "created" in manifest
        assert "tool_version" in manifest

    def test_init_notes_template(self, tmp_path: Path) -> None:
        runner.invoke(app, [
            "experiment", "init", "test_exp",
            "--preset", "first-capture",
            "--root", str(tmp_path),
        ])
        notes = (tmp_path / "test_exp" / "notes.md").read_text()
        assert "test_exp" in notes
        assert "Setup Notes" in notes

    def test_init_duplicate_fails(self, tmp_path: Path) -> None:
        runner.invoke(app, [
            "experiment", "init", "test_exp",
            "--preset", "first-capture",
            "--root", str(tmp_path),
        ])
        result = runner.invoke(app, [
            "experiment", "init", "test_exp",
            "--preset", "first-capture",
            "--root", str(tmp_path),
        ])
        assert result.exit_code != 0

    def test_init_unknown_preset_fails(self, tmp_path: Path) -> None:
        result = runner.invoke(app, [
            "experiment", "init", "test_exp",
            "--preset", "nonexistent",
            "--root", str(tmp_path),
        ])
        assert result.exit_code != 0

    def test_init_with_different_presets(self, tmp_path: Path) -> None:
        for preset in ("first-capture", "parser-validation", "corner-reflector", "walking-person"):
            result = runner.invoke(app, [
                "experiment", "init", f"exp_{preset}",
                "--preset", preset,
                "--root", str(tmp_path),
            ])
            assert result.exit_code == 0
            cfg = RadarConfig.from_yaml(tmp_path / f"exp_{preset}" / "capture.yaml")
            assert cfg.experiment.name == f"exp_{preset}"
