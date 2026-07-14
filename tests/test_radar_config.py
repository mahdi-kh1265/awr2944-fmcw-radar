from pathlib import Path
import pytest
from awr2944_dca.radar_config import RadarConfig, smoke_config_preset

def test_smoke_preset_has_exactly_13_commands():
    cfg = smoke_config_preset()
    assert len(cfg.commands) == 13
    
    # Must contain FrameConfig, ProfileConfig, ChirpConfig
    funcs = [cmd["func"] for cmd in cfg.commands]
    assert "ar1.FrameConfig" in funcs
    assert "ar1.ProfileConfig" in funcs
    assert "ar1.ChirpConfig" in funcs
    
    # Verify strict ordering or at least presence of the exact 13
    assert funcs == [
        "ar1.ChanNAdcConfig",
        "ar1.LPModConfig",
        "ar1.RfLdoBypassConfig",
        "ar1.SetCalMonFreqLimitConfig",
        "ar1.SetRFDeviceConfig",
        "ar1.RfSetCalMonFreqTxPowLimitConfig",
        "ar1.SetApllSynthBWCtlConfig",
        "ar1.RfInit",
        "ar1.DataPathConfig",
        "ar1.LVDSLaneConfig",
        "ar1.ProfileConfig",
        "ar1.ChirpConfig",
        "ar1.FrameConfig"
    ]

def test_smoke_preset_derived_values():
    cfg = smoke_config_preset()
    d = cfg.derived()
    assert d["expected_bytes"] == 4_194_304
    assert d["sampled_bandwidth_mhz"] > 0
    assert d["ramp_bandwidth_mhz"] > 0
    assert d["approximate_range_resolution_m"] > 0

def test_validate_catches_invalid_commands():
    cfg = smoke_config_preset()
    assert cfg.validate()["passed"] is True
    
    cfg.add_command("ar1.StartFrame")
    res = cfg.validate()
    assert res["passed"] is False
    assert "ar1.StartFrame is not allowed" in str(res["errors"])
    
    cfg = smoke_config_preset()
    cfg.add_command("ar1.CaptureCardConfig_StartRecord")
    res = cfg.validate()
    assert res["passed"] is False

def test_to_lua_has_no_startframe():
    cfg = smoke_config_preset()
    lua = cfg.to_lua()
    assert "StartFrame" not in lua
    assert "StartRecord" not in lua
    assert "ar1.FrameConfig(0, 0, 8, 128, 40, 0, 1)" in lua
    assert "ar1.ProfileConfig(0, 77, 100, 6, 60, 0, 0, 0, 0, 0, 0, 0, 0, 29.982, 0, 256, 10000, 2216755200, 0, 30, 0, 0, 0)" in lua

def test_clone_and_override():
    cfg = smoke_config_preset()
    cfg2 = cfg.clone(name="custom", num_frames=16)
    assert cfg2.name == "custom"
    
    # Original should be 8 frames
    d1 = cfg.derived()
    assert d1["expected_bytes"] == 4_194_304
    
    # Custom should be 16 frames
    d2 = cfg2.derived()
    assert d2["expected_bytes"] == 4_194_304 * 2

def test_save_and_load_roundtrip(tmp_path):
    cfg = smoke_config_preset()
    cfg.name = "test_config"
    path = cfg.save(project_root=tmp_path)
    
    # Load it back
    import json
    data = json.loads(path.read_text(encoding="utf-8"))
    cfg2 = RadarConfig.from_dict(data)
    
    assert cfg2.name == "test_config"
    assert len(cfg2.commands) == 13
    assert cfg2.to_lua() == cfg.to_lua()

def test_export_lua(tmp_path):
    cfg = smoke_config_preset()
    cfg.name = "test_export"
    p = cfg.export_lua(project_root=tmp_path)
    assert p.name == "test_export.lua"
    assert p.parent.name == "lua"
    assert p.parent.parent.name == "mmws"
    
    txt = p.read_text(encoding="utf-8")
    assert "ar1.FrameConfig" in txt
