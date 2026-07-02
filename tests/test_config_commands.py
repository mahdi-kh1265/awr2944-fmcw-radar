"""Tests for config management commands: new, validate, summarize."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from awr2944_dca.cli import app
from awr2944_dca.config.presets import PRESETS, get_preset, list_presets
from awr2944_dca.config.schema import RadarConfig
from awr2944_dca.config.validation import Severity, validate_config

runner = CliRunner()
EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "configs"


class TestPresets:
    """Test config preset definitions."""

    def test_list_presets(self) -> None:
        names = list_presets()
        assert "first-capture" in names
        assert "parser-validation" in names
        assert "corner-reflector" in names
        assert "walking-person" in names

    def test_get_preset_returns_copy(self) -> None:
        p1 = get_preset("first-capture")
        p2 = get_preset("first-capture")
        assert p1 == p2
        p1["experiment"]["name"] = "modified"
        assert p2["experiment"]["name"] != "modified"

    def test_unknown_preset_raises(self) -> None:
        with pytest.raises(KeyError, match="Unknown preset"):
            get_preset("nonexistent")

    @pytest.mark.parametrize("preset_name", list_presets())
    def test_all_presets_validate(self, preset_name: str) -> None:
        """Every preset must produce a valid RadarConfig."""
        preset_dict = get_preset(preset_name)
        cfg = RadarConfig.model_validate(preset_dict)
        assert cfg.experiment.name

    @pytest.mark.parametrize("preset_name", list_presets())
    def test_all_presets_awr2944_defaults(self, preset_name: str) -> None:
        """All presets should use AWR2944 real ADC defaults."""
        preset_dict = get_preset(preset_name)
        assert preset_dict["adc"]["is_complex"] is False
        assert preset_dict["adc"]["bits"] == 16
        assert preset_dict["adc"]["channel_interleave"] == 1
        assert "noninterleaved" in preset_dict["adc"]["layout"]

    def test_tdm_mimo_presets_marked_experimental(self) -> None:
        for name in ("corner-reflector", "walking-person"):
            preset = get_preset(name)
            desc = preset["experiment"]["description"]
            assert "EXPERIMENTAL" in desc


class TestValidation:
    """Test deep validation logic."""

    def test_valid_config_no_errors(self) -> None:
        cfg = RadarConfig.model_validate(get_preset("first-capture"))
        results = validate_config(cfg)
        errors = [r for r in results if r.severity == Severity.ERROR]
        assert len(errors) == 0

    def test_candidate_layout_warning(self) -> None:
        cfg = RadarConfig.model_validate(get_preset("first-capture"))
        results = validate_config(cfg)
        warnings = [r for r in results if r.severity == Severity.WARNING]
        layout_warnings = [w for w in warnings if "candidate" in w.message.lower()]
        assert len(layout_warnings) > 0

    def test_interleave_layout_mismatch_error(self) -> None:
        preset = get_preset("first-capture")
        preset["adc"]["channel_interleave"] = 0  # interleaved
        # But layout says noninterleaved
        cfg = RadarConfig.model_validate(preset)
        results = validate_config(cfg)
        errors = [r for r in results if r.severity == Severity.ERROR]
        assert any("channel_interleave" in e.field for e in errors)

    def test_real_complex_mismatch_error(self) -> None:
        preset = get_preset("first-capture")
        preset["adc"]["is_complex"] = True  # complex
        # But layout says real
        cfg = RadarConfig.model_validate(preset)
        results = validate_config(cfg)
        errors = [r for r in results if r.severity == Severity.ERROR]
        assert any("is_complex" in e.field for e in errors)

    def test_non_power_of_two_samples_warning(self) -> None:
        preset = get_preset("first-capture")
        preset["adc"]["samples_per_chirp"] = 200  # not power of 2
        cfg = RadarConfig.model_validate(preset)
        results = validate_config(cfg)
        warnings = [r for r in results if r.severity == Severity.WARNING]
        assert any("power of 2" in w.message for w in warnings)

    def test_expected_file_size_reported(self) -> None:
        cfg = RadarConfig.model_validate(get_preset("first-capture"))
        results = validate_config(cfg)
        size_results = [r for r in results if r.field == "expected_file_size"]
        assert len(size_results) == 1
        assert "bytes" in size_results[0].message

    def test_tdm_mimo_warning(self) -> None:
        cfg = RadarConfig.model_validate(get_preset("corner-reflector"))
        results = validate_config(cfg)
        warnings = [r for r in results if r.severity == Severity.WARNING]
        assert any("TDM-MIMO" in w.message for w in warnings)


class TestConfigNewCLI:
    """Test awr config new command."""

    @pytest.mark.parametrize("preset_name", list_presets())
    def test_config_new_creates_valid_yaml(self, preset_name: str, tmp_path: Path) -> None:
        out = tmp_path / "test_config.yaml"
        result = runner.invoke(app, ["config", "new", "--preset", preset_name, "--out", str(out)])
        assert result.exit_code == 0
        assert out.exists()

        # Must be valid YAML and valid RadarConfig
        cfg = RadarConfig.from_yaml(out)
        assert cfg.experiment.name

    def test_config_new_unknown_preset(self, tmp_path: Path) -> None:
        out = tmp_path / "bad.yaml"
        result = runner.invoke(app, ["config", "new", "--preset", "nonexistent", "--out", str(out)])
        assert result.exit_code != 0


class TestConfigValidateCLI:
    """Test awr config validate command."""

    def test_validate_good_config(self) -> None:
        result = runner.invoke(app, ["config", "validate", str(EXAMPLES_DIR / "first_capture.yaml")])
        assert result.exit_code == 0
        assert "All checks passed" in result.output

    def test_validate_nonexistent(self) -> None:
        result = runner.invoke(app, ["config", "validate", "nonexistent.yaml"])
        assert result.exit_code != 0


class TestConfigSummarizeCLI:
    """Test awr config summarize command."""

    def test_summarize_first_capture(self) -> None:
        result = runner.invoke(app, ["config", "summarize", str(EXAMPLES_DIR / "first_capture.yaml")])
        assert result.exit_code == 0
        assert "first_capture" in result.output
        assert "real" in result.output
        assert "bytes" in result.output

    def test_summarize_nonexistent(self) -> None:
        result = runner.invoke(app, ["config", "summarize", "nonexistent.yaml"])
        assert result.exit_code != 0
