"""Tests for TI bridge: inspect, import, compare, export."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from awr2944_dca.cli import app
from awr2944_dca.config.schema import RadarConfig
from awr2944_dca.ti.compare import CompSeverity, compare_configs
from awr2944_dca.ti.export_dca import DcaConfigError, export_dca_config
from awr2944_dca.ti.export_lua import export_lua_template
from awr2944_dca.ti.import_config import import_ti_config
from awr2944_dca.ti.inspect import UNKNOWN, inspect_ti_file

runner = CliRunner()
EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "configs"

# ---------------------------------------------------------------------------
# Fake TI files for testing
# ---------------------------------------------------------------------------

FAKE_LUA = """\
-- Test Lua script
if (ar1.ChanNAdcConfig(1, 15, 0, 2, 0, 0, 1, 2, 1, 0) == 0) then
    WriteToLog("ChanNAdcConfig Success")
end

ar1.DataPathConfig(1, 1, 0)

ar1.LVDSLaneConfig(0, 1, 1, 1, 1, 1, 0, 0)

ar1.ProfileConfig(0, 77, 10, 6, 60, 0, 0, 0, 0, 0, 0, 60.0, 0, 256, 10000, 0, 0, 94)

ar1.ChirpConfig(0, 0, 0, 0, 0, 0, 0, 1, 1, 0)

ar1.FrameConfig(0, 0, 128, 10, 50, 0, 1)
"""

FAKE_JSON = json.dumps({
    "mmWaveDevices": [{
        "rfConfig": {
            "rlChanCfg_t": {
                "rxChannelEn": 15,
                "txChannelEn": 1,
            },
            "rlAdcOutCfg_t": {
                "adcFmt": 0,
                "adcBits": 2,
            },
            "rlDevDataFmtCfg_t": {
                "chInterleave": 1,
                "iqSwapSel": 0,
            },
        },
        "profileConfig": {
            "numAdcSamples": 256,
            "startFreqConst": 77,
            "freqSlopeConst": 60,
            "digOutSampleRate": 10000,
            "idleTimeConst": 10,
            "rampEndTime": 60,
        },
        "frameConfig": {
            "chirpsPerFrame": 128,
            "numFrames": 10,
        },
    }]
})


class TestTiInspectLua:
    """Test TI Lua file inspection."""

    def test_inspect_lua_extracts_fields(self, tmp_path: Path) -> None:
        lua_file = tmp_path / "test.lua"
        lua_file.write_text(FAKE_LUA)

        result = inspect_ti_file(lua_file)
        assert result.source_format == "lua"
        assert result.tx_channel_en == "1"
        assert result.rx_channel_en == "15"
        assert result.adc_bits == "2"
        assert result.adc_fmt == "0"
        assert result.ch_interleave == "1"
        assert result.num_adc_samples == "256"
        assert result.sample_rate_ksps == "10000"
        assert result.start_freq_ghz == "77"
        assert result.num_frames == "10"

    def test_inspect_lua_preserves_raw_calls(self, tmp_path: Path) -> None:
        lua_file = tmp_path / "test.lua"
        lua_file.write_text(FAKE_LUA)

        result = inspect_ti_file(lua_file)
        assert len(result.raw_api_calls) > 0
        assert any("ChanNAdcConfig" in c for c in result.raw_api_calls)
        assert any("ProfileConfig" in c for c in result.raw_api_calls)
        assert any("FrameConfig" in c for c in result.raw_api_calls)

    def test_inspect_lua_chirps_computed(self, tmp_path: Path) -> None:
        lua_file = tmp_path / "test.lua"
        lua_file.write_text(FAKE_LUA)
        result = inspect_ti_file(lua_file)
        # FrameConfig(0, 0, 128, 10, ...) → chirps = (0-0+1)*128 = 128
        assert result.chirps_per_frame == "128"


class TestTiInspectJson:
    """Test TI JSON file inspection."""

    def test_inspect_json_extracts_fields(self, tmp_path: Path) -> None:
        json_file = tmp_path / "test.json"
        json_file.write_text(FAKE_JSON)

        result = inspect_ti_file(json_file)
        assert result.source_format == "json"
        assert result.rx_channel_en == "15"
        assert result.adc_fmt == "0"
        assert result.adc_bits == "2"
        assert result.ch_interleave == "1"
        assert result.num_adc_samples == "256"
        assert result.num_frames == "10"


class TestTiInspectUnknown:
    """Test inspection of unknown format."""

    def test_inspect_unknown_format(self, tmp_path: Path) -> None:
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("some random text")

        result = inspect_ti_file(txt_file)
        assert result.source_format == "unknown"
        assert result.adc_fmt == UNKNOWN

    def test_inspect_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            inspect_ti_file("/nonexistent/file.lua")


class TestTiImport:
    """Test TI config import."""

    def test_import_lua(self, tmp_path: Path) -> None:
        lua_file = tmp_path / "test.lua"
        lua_file.write_text(FAKE_LUA)
        out_yaml = tmp_path / "imported.yaml"

        config_dict, assumptions, unknown_fields = import_ti_config(
            lua_file, output_path=out_yaml
        )
        assert out_yaml.exists()

        # Should be loadable as RadarConfig
        cfg = RadarConfig.from_yaml(out_yaml)
        assert cfg.adc.samples_per_chirp == 256
        assert cfg.adc.is_complex is False  # adc_fmt=0 → real

    def test_import_records_assumptions(self, tmp_path: Path) -> None:
        # Use a minimal Lua with missing fields
        lua_file = tmp_path / "minimal.lua"
        lua_file.write_text("-- empty lua\n")
        out_yaml = tmp_path / "imported.yaml"

        _, assumptions, unknown_fields = import_ti_config(
            lua_file, output_path=out_yaml
        )
        assert len(assumptions) > 0
        assert len(unknown_fields) > 0


class TestTiCompare:
    """Test TI config comparison."""

    def test_compare_matching_config(self, tmp_path: Path) -> None:
        """Our config and TI file should match for known fields."""
        lua_file = tmp_path / "test.lua"
        lua_file.write_text(FAKE_LUA)

        # Build a config that matches the fake Lua
        cfg = RadarConfig.model_validate({
            "experiment": {"name": "test"},
            "hardware": {
                "tx_enabled": [0],
                "rx_enabled": [0, 1, 2, 3],
                "antenna_mode": "single_tx",
            },
            "adc": {
                "samples_per_chirp": 256,
                "bits": 16,
                "is_complex": False,
                "channel_interleave": 1,
                "layout": "awr2944_real_2lane_noninterleaved_candidate",
            },
            "frame": {
                "chirps_per_frame": 128,
                "num_frames": 10,
            },
        })

        results = compare_configs(cfg, lua_file)
        errors = [r for r in results if r.severity == CompSeverity.ERROR]
        assert len(errors) == 0

    def test_compare_detects_adc_mode_mismatch(self, tmp_path: Path) -> None:
        lua_file = tmp_path / "test.lua"
        lua_file.write_text(FAKE_LUA)  # adc_fmt=0 → real

        cfg = RadarConfig.model_validate({
            "experiment": {"name": "test"},
            "adc": {"is_complex": True},  # mismatch!
        })

        results = compare_configs(cfg, lua_file)
        errors = [r for r in results if r.severity == CompSeverity.ERROR]
        assert any("ADC mode" in e.field for e in errors)

    def test_compare_detects_interleave_mismatch(self, tmp_path: Path) -> None:
        lua_file = tmp_path / "test.lua"
        lua_file.write_text(FAKE_LUA)  # ch_interleave=1

        cfg = RadarConfig.model_validate({
            "experiment": {"name": "test"},
            "adc": {"channel_interleave": 0},  # mismatch!
        })

        results = compare_configs(cfg, lua_file)
        errors = [r for r in results if r.severity == CompSeverity.ERROR]
        assert any("channel_interleave" in e.field for e in errors)

    def test_compare_detects_samples_mismatch(self, tmp_path: Path) -> None:
        lua_file = tmp_path / "test.lua"
        lua_file.write_text(FAKE_LUA)  # samples=256

        cfg = RadarConfig.model_validate({
            "experiment": {"name": "test"},
            "adc": {"samples_per_chirp": 512},  # mismatch
        })

        results = compare_configs(cfg, lua_file)
        warnings = [r for r in results if r.severity == CompSeverity.WARNING]
        assert any("samples_per_chirp" in w.field for w in warnings)


class TestExportLua:
    """Test Lua template export."""

    def test_export_lua_creates_file(self, tmp_path: Path) -> None:
        cfg = RadarConfig.model_validate({
            "experiment": {"name": "test"},
        })
        out = tmp_path / "test.lua"
        result = export_lua_template(cfg, out)
        assert result.exists()

    def test_export_lua_has_warning_banner(self, tmp_path: Path) -> None:
        cfg = RadarConfig.model_validate({
            "experiment": {"name": "test"},
        })
        out = tmp_path / "test.lua"
        export_lua_template(cfg, out)
        content = out.read_text()
        assert "WARNING" in content
        assert "Not hardware validated" in content
        assert "TEMPLATE" in content

    def test_export_lua_contains_api_calls(self, tmp_path: Path) -> None:
        cfg = RadarConfig.model_validate({
            "experiment": {"name": "test"},
        })
        out = tmp_path / "test.lua"
        export_lua_template(cfg, out)
        content = out.read_text()
        assert "ar1.ChanNAdcConfig" in content
        assert "ar1.ProfileConfig" in content
        assert "ar1.FrameConfig" in content


class TestExportDca:
    """Test DCA1000 JSON config export."""

    def test_export_dca_creates_valid_json(self, tmp_path: Path) -> None:
        cfg = RadarConfig.model_validate({
            "experiment": {"name": "test"},
        })
        out = tmp_path / "dca.json"
        result = export_dca_config(cfg, out)
        assert result.exists()

        data = json.loads(out.read_text())
        assert "DCA1000Config" in data
        assert "EthernetConfig" in data

    def test_export_dca_invalid_lanes_fails(self, tmp_path: Path) -> None:
        cfg = RadarConfig.model_validate({
            "experiment": {"name": "test"},
            "adc": {"num_lvds_lanes": 3},  # invalid
        })
        out = tmp_path / "dca.json"
        with pytest.raises(DcaConfigError):
            export_dca_config(cfg, out)


class TestTiInspectCLI:
    """Test awr ti inspect CLI command."""

    def test_inspect_cli_lua(self, tmp_path: Path) -> None:
        lua_file = tmp_path / "test.lua"
        lua_file.write_text(FAKE_LUA)
        result = runner.invoke(app, ["ti", "inspect", str(lua_file)])
        assert result.exit_code == 0
        assert "ChanNAdcConfig" in result.output

    def test_inspect_cli_nonexistent(self) -> None:
        result = runner.invoke(app, ["ti", "inspect", "/nonexistent.lua"])
        assert result.exit_code != 0


class TestTiCompareCLI:
    """Test awr ti compare CLI command."""

    def test_compare_cli(self, tmp_path: Path) -> None:
        lua_file = tmp_path / "test.lua"
        lua_file.write_text(FAKE_LUA)
        result = runner.invoke(app, [
            "ti", "compare",
            str(EXAMPLES_DIR / "first_capture.yaml"),
            str(lua_file),
        ])
        assert result.exit_code == 0


class TestTiExportLuaCLI:
    """Test awr ti export-lua-template CLI command."""

    def test_export_lua_cli(self, tmp_path: Path) -> None:
        out = tmp_path / "test.lua"
        result = runner.invoke(app, [
            "ti", "export-lua-template",
            str(EXAMPLES_DIR / "first_capture.yaml"),
            "--out", str(out),
        ])
        assert result.exit_code == 0
        assert out.exists()
        assert "WARNING" in result.output


class TestTiExportDcaCLI:
    """Test awr ti export-dca-config CLI command."""

    def test_export_dca_cli(self, tmp_path: Path) -> None:
        out = tmp_path / "dca.json"
        result = runner.invoke(app, [
            "ti", "export-dca-config",
            str(EXAMPLES_DIR / "first_capture.yaml"),
            "--out", str(out),
        ])
        assert result.exit_code == 0
        assert out.exists()
