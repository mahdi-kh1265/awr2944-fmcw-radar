import pytest
from pathlib import Path

from awr2944_dca.api.profile import (
    RadarProfile,
    ProfileCompilationNotSupported,
)
from awr2944_dca.api.profile_collection import ProfileCollection

# The checked-in literal GOLDEN_SMOKE_V1_COMMANDS
GOLDEN_SMOKE_V1_COMMANDS = [
    "flushCfg",
    "dfeDataOutputMode 1",
    "channelCfg 15 7 0",
    "adcCfg 2 0",
    "adcbufCfg -1 1 1 1 1",
    "lowPower 0 0",
    "profileCfg 0 77 100 6 60 0 0 29.982 0 256 10000 0 0 30",
    "chirpCfg 0 0 0 0 0 0 0 3",
    "frameCfg 0 0 128 8 256 40 1 0",
    "lowPower 0 0",
    "guiMonitor -1 1 1 0 0 0 1",
    "cfarCfg -1 0 2 8 4 3 0 15 1",
    "cfarCfg -1 1 0 4 2 3 1 15 1",
    "multiObjBeamForming -1 1 0.5",
    "calibDcRangeSig -1 0 -5 8 256",
    "clutterRemoval -1 0",
    "antGeometryCfg 1 0 1 1 1 2 1 3 0 2 0 3 0 4 0 5 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1 11 0.5 0.8",
    "compRangeBiasAndRxChanPhase 0.0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0",
    "measureRangeBiasAndRxChanPhase 0 1.5 0.2",
    "aoaFovCfg -1 -90 90 -90 90",
    "cfarFovCfg -1 0 0 19.53",
    "cfarFovCfg -1 1 -1 1.00",
    "extendedMaxVelocity -1 0",
    "calibData 0 0 0x1f0000",
    "CQRxSatMonitor 0 3 11 121 0",
    "CQSigImgMonitor 0 127 8",
    "analogMonitor 0 0",
    "lvdsStreamCfg -1 0 1 0",
]

def test_golden_parity_and_sensor_absence():
    smoke = RadarProfile.smoke_v1()
    cmds = smoke.to_sdk_cli()
    
    # Exact golden parity
    assert cmds == GOLDEN_SMOKE_V1_COMMANDS
    
    # Verify sensorStart and sensorStop are absent
    cmd_text = " ".join(cmds)
    assert "sensorStart" not in cmd_text
    assert "sensorStop" not in cmd_text

def test_to_dsp_profile_exact_mapping():
    smoke = RadarProfile.smoke_v1()
    dsp = smoke.to_dsp_profile()
    
    assert dsp.start_frequency_hz == 77.0 * 1e9
    assert dsp.slope_hz_per_s == 29.982 * 1e12
    assert dsp.adc_sample_rate_hz == 10.0 * 1e6
    assert dsp.adc_samples == 256
    assert dsp.idle_time_s == 100.0 * 1e-6
    assert dsp.ramp_end_time_s == 60.0 * 1e-6
    assert dsp.chirps_per_frame == 128
    assert dsp.frame_count == 8
    assert dsp.frame_period_s == 40.0 * 1e-3
    assert dsp.rx_count == 4  # bit count of 15
    assert dsp.tx_mask == 3   # chirp tx_enable_mask
    assert dsp.sample_format == "real_int16"
    assert dsp.cube_layout == "frame_chirp_rx_sample"

def test_adc_start_time_s_mapping():
    smoke = RadarProfile.smoke_v1()
    assert smoke.adc_start_time_s == 6e-6
    # DspRadarProfile does not carry adc_start_time_s,
    # so verify it is not a field on the internal profile
    dsp = smoke.to_dsp_profile()
    assert not hasattr(dsp, 'adc_start_time_s') or 'adc_start_time_s' not in dsp.__dataclass_fields__

def test_toml_round_trip():
    smoke = RadarProfile.smoke_v1()
    toml_str = smoke.to_toml()
    
    recovered = RadarProfile.from_toml(toml_str)
    assert smoke == recovered

def test_minimal_profile_compatibility():
    # Phase A created a minimal smoke_v1 schema
    minimal_toml = """
    schema_version = "1.0"
    name = "minimal"
    """
    recovered = RadarProfile.from_toml(minimal_toml)
    
    # Should fall back to smoke defaults for omitted fields
    assert recovered.rf.start_frequency_ghz == 77.0
    assert recovered.sampling.samples == 256

def test_supported_frame_only_variant():
    smoke = RadarProfile.smoke_v1()
    variant = smoke.with_frame(frame_count=16, chirps_per_frame=64)
    
    cmds = variant.to_sdk_cli()
    # It should succeed compilation and just pass the overrides
    assert any("frameCfg 0 0 64 16 256 40 1 0" in c for c in cmds)

def test_unsupported_frame_period_variant_rejection():
    smoke = RadarProfile.smoke_v1()
    variant = smoke.with_frame(frame_period_ms=20.0)
    
    with pytest.raises(ProfileCompilationNotSupported) as exc:
        variant.to_sdk_cli()
        
    assert "frame.frame_period_ms" in str(exc.value.unsupported_fields)

def test_unsupported_rf_variant_rejection():
    smoke = RadarProfile.smoke_v1()
    variant = smoke.with_rf(slope_mhz_per_us=35.0)
    
    with pytest.raises(ProfileCompilationNotSupported) as exc:
        variant.to_sdk_cli()
        
    assert "rf" in str(exc.value.unsupported_fields)

def test_profile_collection_rules(tmp_path: Path):
    coll = ProfileCollection(tmp_path)
    
    # 1. Has built in smoke_v1
    entries = coll.list()
    assert len(entries) == 1
    assert entries[0].name == "smoke_v1"
    assert entries[0].origin == "built_in"
    
    # 2. Get builtin
    smoke = coll.get("smoke_v1")
    assert smoke.name == "smoke_v1"
    
    # 3. Save a new profile
    fast = smoke.rename("fast_scan")
    coll.save(fast)
    
    entries = coll.list()
    assert len(entries) == 2
    fast_entry = next(e for e in entries if e.name == "fast_scan")
    assert fast_entry.origin == "project"
    
    # 4. Refuse overwrite
    with pytest.raises(FileExistsError):
        coll.save(fast)
        
    coll.save(fast, overwrite=True)
    
    # 5. Cannot delete builtin
    with pytest.raises(ValueError, match="Cannot delete built-in profile: smoke_v1"):
        coll.delete("smoke_v1")
        
    # 6. Delete project profile
    coll.delete("fast_scan")
    assert len(coll.list()) == 1

def test_validation_derived_bytes():
    smoke = RadarProfile.smoke_v1()
    plan = smoke.byte_plan(guard_frames=2)
    # Total frames = 8 + 2 = 10
    # Logical = 256 * 4 * 128 * 10 * 2 = 2,621,440
    assert plan["logical_bytes"] == 2621440
    assert plan["canonical_bytes"] == 2621440
    # Native includes 10-byte overhead every packet.
    # We let expected_native_bytes handle that.
    assert plan["native_bytes"] > plan["canonical_bytes"]

def test_validation_warnings():
    smoke = RadarProfile.smoke_v1()
    # TX0 and TX1 simultaneous = tx_enable_mask = 3 -> multiple bits
    report = smoke.validate()
    assert any("Simultaneous multiple-TX operation" in w for w in report.warnings)
    
    # Unsupported variant
    variant = smoke.with_rf(slope_mhz_per_us=35.0)
    report_v = variant.validate()
    assert any("smoke-compatible" in w for w in report_v.warnings)
    assert report_v.success  # It is physically valid, just not C1 compatible

def test_validation_errors():
    smoke = RadarProfile.smoke_v1()
    bad = smoke.with_sampling(samples=0)
    report = bad.validate()
    assert not report.success
    assert any("adc.samples must be positive" in e for e in report.errors)
