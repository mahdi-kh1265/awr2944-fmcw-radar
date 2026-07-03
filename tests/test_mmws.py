"""Tests for the mmws backend package."""

from pathlib import Path
import json
import pytest

from awr2944_dca.mmws.stages import (
    StageName, get_stage, get_all_allowed_calls, get_all_forbidden_calls,
    STAGES, ALL_KNOWN_CALLS, STATIC_CONFIG_FIELD_MAP,
)
from awr2944_dca.mmws.lua_builder import (
    build_connection_script, validate_script_safety, write_connection_script,
)
from awr2944_dca.mmws.bridge import ManualOneShotBridge, StageStatus
from awr2944_dca.mmws.models import ConnectionTabConfig, StaticConfig
from awr2944_dca.mmws.catalog import scan_scripts, CatalogEntry


# ---------------------------------------------------------------------------
# Stages
# ---------------------------------------------------------------------------


def test_connection_only_is_enabled():
    stage = get_stage(StageName.CONNECTION_ONLY)
    assert stage.allowed_yet is True


def test_all_dangerous_stages_disabled():
    for s in STAGES:
        if s.name != StageName.CONNECTION_ONLY:
            assert s.allowed_yet is False, f"Stage {s.name} should be disabled"


def test_poweron_not_in_connection():
    conn = get_stage(StageName.CONNECTION_ONLY)
    assert "PowerOn" not in conn.allowed_ar1_calls


def test_poweron_in_device_boot():
    boot = get_stage(StageName.DEVICE_BOOT)
    assert "PowerOn" in boot.allowed_ar1_calls


def test_forbidden_calls_excludes_own_stage():
    for s in STAGES:
        forbidden = get_all_forbidden_calls(s.name)
        for call in s.allowed_ar1_calls:
            assert call not in forbidden


# ---------------------------------------------------------------------------
# Lua Builder
# ---------------------------------------------------------------------------


def test_connection_script_contains_allowed_calls():
    script = build_connection_script("test-run-id", 6, 921600, 1000)
    assert "ar1.SOPControl(2)" in script
    assert "ar1.Connect(6, 921600, 1000)" in script
    assert "ar1.IsConnected()" in script


def test_connection_script_forbidden_calls_absent():
    """Static safety test: generated Lua must not contain any forbidden ar1 calls."""
    script = build_connection_script("test-run-id", 8, 921600, 1000)
    forbidden = [
        "DownloadBSSFw", "DownloadMSSFw", "PowerOn", "RfEnable", "RfInit",
        "ChanNAdcConfig", "LPModConfig", "DataPathConfig", "LvdsClkConfig",
        "LVDSLaneConfig", "ProfileConfig", "ChirpConfig", "FrameConfig",
        "AdvanceFrameConfig", "SelectCaptureDevice", "CaptureCardConfig",
        "StartFrame", "StartMatlabPostProc", "SensorStart", "FrameStart",
    ]
    for fn in forbidden:
        assert fn not in script, f"Forbidden call {fn} found in connection script!"


def test_validate_script_safety_clean():
    script = build_connection_script("test", 6, 921600, 1000)
    violations = validate_script_safety(script, StageName.CONNECTION_ONLY)
    assert violations == []


def test_validate_script_safety_catches_violation():
    bad_script = "ar1.SOPControl(2)\nar1.PowerOn(1, 1000, 0)\nar1.Connect(6, 921600, 1000)"
    violations = validate_script_safety(bad_script, StageName.CONNECTION_ONLY)
    assert len(violations) > 0
    assert any("PowerOn" in v for v in violations)


def test_write_connection_script_creates_file(tmp_path):
    out = tmp_path / "connection_only.lua"
    write_connection_script(out, "run-123", 6, 921600, 1000)
    assert out.exists()
    content = out.read_text()
    assert "ar1.Connect(6, 921600, 1000)" in content


# ---------------------------------------------------------------------------
# COM normalization
# ---------------------------------------------------------------------------


def test_com_normalization():
    cfg = ConnectionTabConfig(rs232_com="COM6")
    assert cfg.com_number == 6

    cfg2 = ConnectionTabConfig(rs232_com="COM12")
    assert cfg2.com_number == 12


def test_com_normalization_invalid():
    cfg = ConnectionTabConfig(rs232_com="INVALID")
    with pytest.raises(ValueError):
        _ = cfg.com_number


# ---------------------------------------------------------------------------
# Bridge
# ---------------------------------------------------------------------------


def test_bridge_not_run(tmp_path):
    bridge = ManualOneShotBridge(tmp_path)
    status, result = bridge.check_status(StageName.CONNECTION_ONLY)
    assert status == StageStatus.NOT_RUN


def test_bridge_stale_detection(tmp_path):
    bridge = ManualOneShotBridge(tmp_path)
    # Write manifest with one run_id
    manifest = tmp_path / "connection_only_manifest.json"
    manifest.write_text(json.dumps({"run_id": "aaa"}))
    # Write result with different run_id
    result = tmp_path / "connection_only_result.json"
    result.write_text(json.dumps({"run_id": "bbb", "connect_return": 0}))

    status, _ = bridge.check_status(StageName.CONNECTION_ONLY)
    assert status == StageStatus.STALE_RESULT


def test_bridge_success(tmp_path):
    bridge = ManualOneShotBridge(tmp_path)
    manifest = tmp_path / "connection_only_manifest.json"
    manifest.write_text(json.dumps({"run_id": "xyz"}))
    result = tmp_path / "connection_only_result.json"
    result.write_text(json.dumps({
        "run_id": "xyz",
        "connect_return": 0,
        "error": None,
    }))

    status, data = bridge.check_status(StageName.CONNECTION_ONLY)
    assert status == StageStatus.SUCCESS


def test_bridge_error(tmp_path):
    bridge = ManualOneShotBridge(tmp_path)
    manifest = tmp_path / "connection_only_manifest.json"
    manifest.write_text(json.dumps({"run_id": "xyz"}))
    result = tmp_path / "connection_only_result.json"
    result.write_text(json.dumps({
        "run_id": "xyz",
        "connect_return": -1,
        "error": "Connect failed",
    }))

    status, data = bridge.check_status(StageName.CONNECTION_ONLY)
    assert status == StageStatus.ERROR


def test_bridge_generate_creates_files(tmp_path):
    bridge = ManualOneShotBridge(tmp_path)
    script = bridge.generate_connection_script(6, 921600, 1000)
    assert script.exists()
    assert (tmp_path / "connection_only_manifest.json").exists()


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------


def test_scan_scripts_extracts_ar1_calls(tmp_path):
    lua = tmp_path / "test.lua"
    lua.write_text("ar1.SOPControl(2)\nar1.Connect(6, 921600, 1000)\nar1.MysteryFunction()\n")

    catalog = scan_scripts([tmp_path])
    assert "SOPControl" in catalog
    assert "Connect" in catalog
    assert "MysteryFunction" in catalog


def test_catalog_marks_unknowns(tmp_path):
    lua = tmp_path / "test.lua"
    lua.write_text("ar1.TotallyFakeAPI()\n")

    catalog = scan_scripts([tmp_path])
    entry = catalog["TotallyFakeAPI"]
    assert entry.known_stage is False
    assert "Unknown" in entry.notes or "unknown" in entry.notes.lower()


def test_catalog_known_functions_marked(tmp_path):
    lua = tmp_path / "test.lua"
    lua.write_text("ar1.SOPControl(2)\n")

    catalog = scan_scripts([tmp_path])
    entry = catalog["SOPControl"]
    assert entry.known_stage is True


# ---------------------------------------------------------------------------
# Static plan field mapping
# ---------------------------------------------------------------------------


def test_static_plan_maps_fields():
    """Verify all static config calls are mapped to capture.yaml fields."""
    static_calls = get_all_allowed_calls(StageName.STATIC_CONFIG)
    for call in static_calls:
        assert call in STATIC_CONFIG_FIELD_MAP, f"{call} missing from STATIC_CONFIG_FIELD_MAP"
        assert len(STATIC_CONFIG_FIELD_MAP[call]) > 0, f"{call} has no mapped fields"


def test_static_config_not_yet_allowed():
    stage = get_stage(StageName.STATIC_CONFIG)
    assert stage.allowed_yet is False


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


def test_static_config_masks():
    cfg = StaticConfig(tx_enable=[0, 2], rx_enable=[0, 1, 2, 3])
    assert cfg.tx_mask == 0b0101  # TX0 and TX2
    assert cfg.rx_mask == 0b1111  # all 4 RX


# ---------------------------------------------------------------------------
# Gitignore
# ---------------------------------------------------------------------------


def test_local_hardware_gitignored():
    gitignore_path = Path(__file__).parent.parent / ".gitignore"
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        assert "local_hardware.yaml" in content
