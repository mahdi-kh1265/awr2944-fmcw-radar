"""Tests for mmw_demo_config.py — .cfg parser/model."""

from __future__ import annotations

from pathlib import Path

import pytest

from awr2944_dca.mmw_demo_config import MmwDemoConfig, KNOWN_COMMANDS, ValidationIssue


# ---------------------------------------------------------------------------
# Official TI profile_LVDS.cfg content (embedded for offline testing)
# ---------------------------------------------------------------------------

TI_PROFILE_LVDS = """\
% ***************************************************************
% Created for SDK ver:04.01
% Created using Visualizer ver:4.1.0.0
% Frequency:77
% Platform:AWR294X
% CFG TYPE: LVDS streaming enabled
% ***************************************************************
sensorStop
flushCfg
dfeDataOutputMode 1
channelCfg 15 7 0
adcCfg 2 0
adcbufCfg -1 1 1 1 1
lowPower 0 0
profileCfg 0 77 267 7 57.14 0 0 70 1 560 11396 0 0 158
chirpCfg 0 0 0 0 0 0 0 1
chirpCfg 1 1 0 0 0 0 0 4
chirpCfg 2 2 0 0 0 0 0 2
frameCfg 0 2 16 20 560 100 1 0
lowPower 0 0
guiMonitor -1 1 1 0 0 0 1
cfarCfg -1 0 2 8 4 3 0 15 1
cfarCfg -1 1 0 4 2 3 1 15 1
multiObjBeamForming -1 1 0.5
calibDcRangeSig -1 0 -5 8 256
clutterRemoval -1 0
antGeometryCfg 1 0 1 1 1 2 1 3 0 2 0 3 0 4 0 5 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1 11 0.5 0.8
compRangeBiasAndRxChanPhase 0.0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0
measureRangeBiasAndRxChanPhase 0 1.5 0.2
aoaFovCfg -1 -90 90 -90 90
cfarFovCfg -1 0 0 19.53
cfarFovCfg -1 1 -1 1.00
extendedMaxVelocity -1 0
calibData 0 0 0x1f0000
CQRxSatMonitor 0 3 11 121 0
CQSigImgMonitor 0 127 8
analogMonitor 0 0
lvdsStreamCfg -1 0 1 0
sensorStart
"""


# ---------------------------------------------------------------------------
# Parsing tests
# ---------------------------------------------------------------------------

class TestCfgParsing:
    """Test .cfg file parsing."""

    def test_parse_ti_sample(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        assert cfg.source_path == ""
        assert len(cfg.lines) > 0

    def test_preserves_comments(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        comments = [l for l in cfg.lines if l.is_comment]
        assert len(comments) == 7  # 7 header comment lines

    def test_preserves_blank_lines(self):
        text = "sensorStop\n\nflushCfg\n"
        cfg = MmwDemoConfig.from_cfg_text(text)
        blanks = [l for l in cfg.lines if l.is_blank]
        assert len(blanks) == 1

    def test_parses_commands(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        cmds = [l for l in cfg.lines if l.is_command]
        assert len(cmds) > 20

    def test_sensor_start_detected(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        starts = [l for l in cfg.lines if l.is_sensor_start]
        assert len(starts) == 1
        assert starts[0].command == "sensorStart"

    def test_chirp_cfg_multiple(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        chirps = cfg.get_commands("chirpCfg")
        assert len(chirps) == 3
        assert chirps[0].args[0] == "0"
        assert chirps[1].args[0] == "1"
        assert chirps[2].args[0] == "2"

    def test_profilecfg_14_args(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        profile = cfg.get_command("profileCfg")
        assert profile is not None
        assert len(profile.args) == 14

    def test_framecfg_8_args(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        frame = cfg.get_command("frameCfg")
        assert frame is not None
        assert len(frame.args) == 8

    def test_lvds_stream_cfg_4_args(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        lvds = cfg.get_command("lvdsStreamCfg")
        assert lvds is not None
        assert len(lvds.args) == 4
        assert lvds.args[2] == "1"  # dataFmt = ADC data


# ---------------------------------------------------------------------------
# Roundtrip tests
# ---------------------------------------------------------------------------

class TestCfgRoundtrip:
    """Test that parsing and rendering preserve content."""

    def test_roundtrip_with_sensor_start(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        rendered = cfg.to_cfg_text(include_sensor_start=True)
        # Re-parse
        cfg2 = MmwDemoConfig.from_cfg_text(rendered)
        cmds1 = cfg.command_list(include_sensor_start=True)
        cmds2 = cfg2.command_list(include_sensor_start=True)
        assert cmds1 == cmds2

    def test_sensor_start_blocked_by_default(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        rendered = cfg.to_cfg_text(include_sensor_start=False)
        assert "% [BLOCKED] sensorStart" in rendered
        assert "\nsensorStart\n" not in rendered

    def test_command_list_excludes_sensor_start(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        cmds = cfg.command_list(include_sensor_start=False)
        assert all("sensorStart" not in c for c in cmds)

    def test_command_list_includes_sensor_start_when_asked(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        cmds = cfg.command_list(include_sensor_start=True)
        assert any("sensorStart" in c for c in cmds)


# ---------------------------------------------------------------------------
# Split start command
# ---------------------------------------------------------------------------

class TestSplitStartCommand:
    def test_split(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        config_cmds, start_cmd = cfg.split_start_command()
        assert start_cmd == "sensorStart"
        assert all("sensorStart" not in c for c in config_cmds)
        assert "sensorStop" in config_cmds[0]


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------

class TestValidation:
    def test_ti_sample_validates_clean(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        issues = cfg.validate()
        errors = [i for i in issues if i.level == "error"]
        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_missing_required_commands(self):
        cfg = MmwDemoConfig.from_cfg_text("sensorStop\nflushCfg\n")
        issues = cfg.validate()
        warnings = [i for i in issues if i.level == "warning"]
        missing_cmds = [i.command for i in warnings]
        assert "profileCfg" in missing_cmds
        assert "channelCfg" in missing_cmds
        assert "frameCfg" in missing_cmds

    def test_unknown_command_warns(self):
        cfg = MmwDemoConfig.from_cfg_text("sensorStop\nflushCfg\nmadeUpCommand 1 2 3\n")
        issues = cfg.validate()
        unknown = [i for i in issues if "Unknown" in i.message]
        assert len(unknown) == 1
        assert unknown[0].command == "madeUpCommand"

    def test_wrong_arg_count_errors(self):
        cfg = MmwDemoConfig.from_cfg_text("channelCfg 15 7\n")  # Missing 3rd arg
        issues = cfg.validate()
        errors = [i for i in issues if i.level == "error"]
        assert any(i.command == "channelCfg" for i in errors)


# ---------------------------------------------------------------------------
# Summary and derived tests
# ---------------------------------------------------------------------------

class TestSummaryAndDerived:
    def test_summary_extracts_profile(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        s = cfg.summary()
        assert "profile" in s
        assert s["profile"]["start_freq_ghz"] == 77.0
        assert s["profile"]["num_adc_samples"] == 560

    def test_summary_extracts_frame(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        s = cfg.summary()
        assert s["frame"]["num_loops"] == 16
        assert s["frame"]["num_frames"] == 20

    def test_summary_extracts_channel(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        s = cfg.summary()
        assert s["channel"]["num_rx"] == 4
        assert s["channel"]["num_tx"] == 3

    def test_summary_extracts_lvds(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        s = cfg.summary()
        assert s["lvds"]["data_fmt"] == 1
        assert s["lvds"]["enable_header"] == 0

    def test_derived_lvds_bandwidth_ok(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        d = cfg.derived()
        assert d["lvds_bandwidth_ok"]

    def test_derived_expected_bytes(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        d = cfg.derived()
        # 20 frames × 16 loops × 3 chirps/loop × 560 samples × 4 RX × 4 bytes
        expected = 20 * 16 * 3 * 560 * 4 * 4
        assert d["expected_adc_payload_bytes"] == expected

    def test_derived_transport_bytes_unknown(self):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        d = cfg.derived()
        assert "UNKNOWN" in str(d["expected_transport_bytes"])


# ---------------------------------------------------------------------------
# Compare tests
# ---------------------------------------------------------------------------

class TestCompare:
    def test_identical_configs_no_diffs(self):
        cfg1 = MmwDemoConfig.from_cfg_text("sensorStop\nflushCfg\n")
        cfg2 = MmwDemoConfig.from_cfg_text("sensorStop\nflushCfg\n")
        diffs = cfg1.compare(cfg2)
        assert len(diffs) == 0

    def test_modified_command_detected(self):
        cfg1 = MmwDemoConfig.from_cfg_text("channelCfg 15 7 0\n")
        cfg2 = MmwDemoConfig.from_cfg_text("channelCfg 15 3 0\n")
        diffs = cfg1.compare(cfg2)
        assert len(diffs) == 1
        assert diffs[0]["change"] == "modified"

    def test_added_command_detected(self):
        cfg1 = MmwDemoConfig.from_cfg_text("sensorStop\n")
        cfg2 = MmwDemoConfig.from_cfg_text("sensorStop\nlvdsStreamCfg -1 0 1 0\n")
        diffs = cfg1.compare(cfg2)
        added = [d for d in diffs if d["change"] == "added"]
        assert len(added) == 1
        assert added[0]["command"] == "lvdsStreamCfg"


# ---------------------------------------------------------------------------
# File I/O tests
# ---------------------------------------------------------------------------

class TestFileIO:
    def test_save_and_reload(self, tmp_path):
        cfg = MmwDemoConfig.from_cfg_text(TI_PROFILE_LVDS)
        out = cfg.save(tmp_path / "test.cfg", include_sensor_start=False)
        assert out.exists()

        cfg2 = MmwDemoConfig.from_cfg_file(out)
        assert cfg2.source_sha256  # SHA256 computed
        cmds1 = cfg.command_list(include_sensor_start=False)
        cmds2 = cfg2.command_list(include_sensor_start=False)
        assert cmds1 == cmds2

    def test_from_cfg_file_computes_sha256(self, tmp_path):
        p = tmp_path / "test.cfg"
        p.write_text("sensorStop\nflushCfg\n", encoding="utf-8")
        cfg = MmwDemoConfig.from_cfg_file(p)
        assert len(cfg.source_sha256) == 64


# ---------------------------------------------------------------------------
# Repr test
# ---------------------------------------------------------------------------

class TestRepr:
    def test_repr(self):
        cfg = MmwDemoConfig.from_cfg_text("sensorStop\n")
        r = repr(cfg)
        assert "MmwDemoConfig" in r
        assert "commands=1" in r
