import pytest
pytestmark = pytest.mark.legacy_mmws
import pytest
from pathlib import Path
from awr2944_dca.ti.probe import (
    find_studio,
    generate_probe_script,
    static_scan_for_hardware_actions,
    _TI_PATHS,
)

def test_find_studio(tmp_path, monkeypatch):
    # Mock _TI_PATHS to use tmp_path
    monkeypatch.setattr("awr2944_dca.ti.probe._TI_PATHS", [tmp_path])
    
    # Create fake mmwave_studio dir structure
    studio_dir = tmp_path / "mmwave_studio_03_00_00_14"
    exe = studio_dir / "mmWaveStudio" / "RunTime" / "mmWaveStudio.exe"
    exe.parent.mkdir(parents=True)
    exe.touch()
    
    installs = find_studio()
    assert len(installs) == 1
    assert installs[0].path == studio_dir
    assert installs[0].exe_path == exe

def test_generate_probe_script(tmp_path):
    out = tmp_path / "probe.lua"
    generate_probe_script(out, probe_id="test_probe_123")
    content = out.read_text(encoding="utf-8")
    assert "PROBE SUCCESS" in content
    assert "os.exit()" not in content
    assert "test_probe_123" in content

def test_generate_inventory_script(tmp_path):
    from awr2944_dca.ti.probe import generate_inventory_script
    out = tmp_path / "inventory.lua"
    generate_inventory_script(out, probe_id="test_inv_456")
    content = out.read_text(encoding="utf-8")
    assert "test_inv_456" in content
    assert "escapeJSON" in content
    assert "pcall" in content
    assert "pairs(ar1)" in content
    
    # Assert no hardware actions
    findings = static_scan_for_hardware_actions(out)
    assert len(findings) == 0

def test_connection_probe_safety(tmp_path):
    from awr2944_dca.ti.probe import generate_connection_probe_script
    out = tmp_path / "connection_probe.lua"
    generate_connection_probe_script(out, "run-123", 8, 921600, 1000)
    script = out.read_text()
    
    # Must contain allowed functions
    assert "ar1.SOPControl(2)" in script
    assert "ar1.Connect(8, 921600, 1000)" in script
    assert "ar1.IsConnected()" in script
    
    # Must NOT contain unsafe functions
    forbidden = [
        "DownloadBSSFw", "DownloadMSSFw", "PowerOn", "RfEnable", "RfInit",
        "ChanNAdcConfig", "DataPathConfig", "LVDSLaneConfig", "ProfileConfig",
        "ChirpConfig", "FrameConfig", "CaptureCardConfig", "StartFrame",
        "StartMatlabPostProc", "SensorStart", "FrameStart"
    ]
    for fn in forbidden:
        assert fn not in script, f"Forbidden function {fn} found in connection probe!"

def test_static_scan_hardware_actions(tmp_path):
    script = tmp_path / "test.lua"
    script.write_text("ar1.Connect()\nar1.PowerOn(1, 1000, 0)\nWriteToLog('hi')\n")
    
    findings = static_scan_for_hardware_actions(script)
    assert len(findings) == 2
    assert "ar1.Connect" in findings[0]
    assert "ar1.PowerOn" in findings[1]

def test_static_scan_ignores_comments(tmp_path):
    script = tmp_path / "test.lua"
    script.write_text("-- ar1.Connect()\nWriteToLog('hi')\n")
    
    findings = static_scan_for_hardware_actions(script)
    assert len(findings) == 0
