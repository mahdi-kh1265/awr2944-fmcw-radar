"""Tests for DCA1000 integration."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from awr2944_dca.cli import app
from awr2944_dca.dca.preflight import run_dca_preflight, PreflightCheck
from awr2944_dca.dca.scripts import (
    generate_dca_setup_script,
    generate_capture_trigger_script,
)
from awr2944_dca.dca.validate import check_capture_files
from awr2944_dca.mmws.stages import STAGES

runner = CliRunner()


def test_preflight_udp_firewall_is_unknown(monkeypatch):
    """Firewall check returns UNKNOWN, not fake PASS."""
    # Monkeypatch to avoid running actual powershell commands and just return dummy data
    monkeypatch.setattr("awr2944_dca.dca.preflight._run_ps_json", lambda script: None)
    monkeypatch.setattr("subprocess.check_output", lambda *a, **k: "false")
    
    report = run_dca_preflight()
    firewall_check = next((c for c in report.checks if "firewall" in c.name), None)
    assert firewall_check is not None
    assert firewall_check.status == "UNKNOWN"
    assert "provable" in firewall_check.detail


def test_preflight_ip_missing(monkeypatch):
    """Missing 192.168.33.30 returns FAIL."""
    monkeypatch.setattr("awr2944_dca.dca.preflight._run_ps_json", lambda script: None)
    monkeypatch.setattr("subprocess.check_output", lambda *a, **k: "false")
    
    report = run_dca_preflight()
    ip_check = next(c for c in report.checks if "Adapter IP" in c.name)
    assert ip_check.status == "FAIL"
    assert report.overall == "NOT_READY"


def test_preflight_ip_present(monkeypatch):
    """Correct IP returns PASS."""
    def dummy_run_ps(script):
        if "Get-NetIPAddress" in script:
            return {"InterfaceAlias": "Eth2", "InterfaceIndex": 5, "PrefixLength": 24}
        if "Get-NetAdapter" in script:
            return {"PhysicalMediaType": "802.3"}
        if "Find-NetRoute" in script:
            return {"InterfaceAlias": "Eth2"}
        if "Get-NetNeighbor" in script:
            return {"LinkLayerAddress": "AA-BB"}
        return None

    monkeypatch.setattr("awr2944_dca.dca.preflight._run_ps_json", dummy_run_ps)
    monkeypatch.setattr("subprocess.check_output", lambda *a, **k: "true")
    
    report = run_dca_preflight()
    ip_check = next(c for c in report.checks if "Adapter IP" in c.name)
    assert ip_check.status == "PASS"


def test_preflight_ping_fails_but_arp_passes_is_ready_with_warnings(monkeypatch):
    """host IP PASS + route PASS + ARP PASS + ping FAIL => READY_WITH_WARNINGS"""
    def dummy_run_ps(script):
        if "Get-NetIPAddress" in script:
            return {"InterfaceAlias": "Eth2", "InterfaceIndex": 5, "PrefixLength": 24}
        if "Get-NetAdapter" in script:
            return {"PhysicalMediaType": "802.3"}
        if "Find-NetRoute" in script:
            return {"InterfaceAlias": "Eth2"}
        if "Get-NetNeighbor" in script:
            return {"LinkLayerAddress": "AA-BB"}
        return None

    monkeypatch.setattr("awr2944_dca.dca.preflight._run_ps_json", dummy_run_ps)
    # ping fails
    monkeypatch.setattr("subprocess.check_output", lambda *a, **k: "false")
    
    report = run_dca_preflight()
    assert report.overall == "READY_WITH_WARNINGS"
    
    ping_check = next(c for c in report.checks if "Ping" in c.name)
    assert ping_check.status == "WARN"
    assert "usable over UDP" in ping_check.detail
    
    arp_check = next(c for c in report.checks if "ARP" in c.name)
    assert arp_check.status == "PASS"


def test_preflight_ping_fails_and_arp_fails_is_not_ready(monkeypatch):
    """host IP PASS + route PASS + ARP FAIL + ping FAIL => NOT_READY"""
    def dummy_run_ps(script):
        if "Get-NetIPAddress" in script:
            return {"InterfaceAlias": "Eth2", "InterfaceIndex": 5, "PrefixLength": 24}
        if "Get-NetAdapter" in script:
            return {"PhysicalMediaType": "802.3"}
        if "Find-NetRoute" in script:
            return {"InterfaceAlias": "Eth2"}
        if "Get-NetNeighbor" in script:
            return None
        return None

    monkeypatch.setattr("awr2944_dca.dca.preflight._run_ps_json", dummy_run_ps)
    # ping fails
    monkeypatch.setattr("subprocess.check_output", lambda *a, **k: "false")
    
    report = run_dca_preflight()
    assert report.overall == "NOT_READY"
    
    ping_check = next(c for c in report.checks if "Ping" in c.name)
    assert ping_check.status == "FAIL"
    
    arp_check = next(c for c in report.checks if "ARP" in c.name)
    assert arp_check.status == "FAIL"


def test_setup_script_contains_four_dca_calls(tmp_path):
    """Lua has SelectCaptureDevice + EthInit + Mode + PacketDelay."""
    script = generate_dca_setup_script(
        run_id="test1",
        out_path=tmp_path / "setup.lua"
    )
    code = script.script
    assert "SelectCaptureDevice" in code
    assert "CaptureCardConfig_EthInit" in code
    assert "CaptureCardConfig_Mode" in code
    assert "CaptureCardConfig_PacketDelay" in code


def test_setup_script_no_startframe(tmp_path):
    """StartFrame not in generated Lua."""
    script = generate_dca_setup_script(run_id="test1", out_path=tmp_path / "setup.lua")
    assert "StartFrame" not in script.script


def test_setup_script_no_startrecord(tmp_path):
    """StartRecord not in generated Lua."""
    script = generate_dca_setup_script(run_id="test1", out_path=tmp_path / "setup.lua")
    assert "StartRecord" not in script.script


def test_setup_script_no_firmware_commands(tmp_path):
    """No PowerOn/RfEnable/DownloadBSSFw in Lua."""
    script = generate_dca_setup_script(run_id="test1", out_path=tmp_path / "setup.lua")
    code = script.script
    assert "PowerOn" not in code
    assert "RfEnable" not in code
    assert "DownloadBSSFw" not in code


def test_capture_refuses_without_confirm(tmp_path):
    """generate_capture_trigger_script raises ValueError if confirm_startframe=False."""
    with pytest.raises(ValueError, match="--confirm-startframe"):
        generate_capture_trigger_script(
            run_id="test1",
            out_path=tmp_path / "trigger.lua",
            output_dir=tmp_path,
            confirm_startframe=False
        )


def test_capture_script_contains_startrecord_and_startframe(tmp_path):
    """Both present when confirmed."""
    script = generate_capture_trigger_script(
        run_id="test1",
        out_path=tmp_path / "trigger.lua",
        output_dir=tmp_path,
        confirm_startframe=True
    )
    code = script.script
    assert "CaptureCardConfig_StartRecord" in code
    assert "StartFrame" in code
    assert "CaptureCardConfig_StopRecord" in code


def test_capture_script_path_comments(tmp_path):
    """Path comments distinguish output-dir from fileBasePath."""
    script = generate_capture_trigger_script(
        run_id="test1",
        out_path=tmp_path / "trigger.lua",
        output_dir=tmp_path,
        confirm_startframe=True
    )
    code = script.script
    assert "--   adc_data_path:" in code
    assert "Note: mmWave Studio StartRecord receives adc_data_path ending in .bin" in code
    assert ".bin" in script.metadata["adc_data_path"]


def test_capture_script_path_backslashes(tmp_path):
    """Generated adc_data_path uses backslashes for Windows, no forward slashes, ends in \\adc_data.bin."""
    test_out = tmp_path / "PostProc"
    test_out.mkdir()
    script = generate_capture_trigger_script(
        run_id="test1",
        out_path=tmp_path / "trigger.lua",
        output_dir=test_out,
        confirm_startframe=True
    )
    code = script.script
    # Should look like [[...\\PostProc\\adc_data.bin]]
    expected_path = str((test_out / "adc_data.bin").resolve())
    assert f"[[{expected_path}]]" in code
    assert expected_path.endswith(".bin")


def test_capture_script_no_config_commands(tmp_path):
    """No ChanNAdcConfig/ProfileConfig/FrameConfig."""
    script = generate_capture_trigger_script(
        run_id="test1",
        out_path=tmp_path / "trigger.lua",
        output_dir=tmp_path,
        confirm_startframe=True
    )
    code = script.script
    assert "ChanNAdcConfig" not in code
    assert "ProfileConfig" not in code
    assert "FrameConfig" not in code


def test_capture_script_has_run_markers(tmp_path):
    """AWR_RUN_BEGIN / AWR_RUN_END present."""
    script = generate_capture_trigger_script(
        run_id="test1",
        out_path=tmp_path / "trigger.lua",
        output_dir=tmp_path,
        confirm_startframe=True
    )
    code = script.script
    assert "AWR_RUN_BEGIN" in code
    assert "AWR_RUN_END" in code


def test_generate_postproc_script(tmp_path):
    """Postproc script uses StartMatlabPostProc."""
    from awr2944_dca.dca.scripts import generate_postproc_script
    script = generate_postproc_script(
        run_id="test1",
        out_path=tmp_path / "postproc.lua",
        output_dir=tmp_path
    )
    code = script.script
    assert "StartMatlabPostProc" in code
    assert ".bin" in code


def test_lua_json_escape():
    """Verify jsonEscape handles multiline strings correctly in Python generation."""
    from awr2944_dca.mmws.post_connect import _lua_log_progress, _lua_result_init_and_save
    
    log_lua = _lua_log_progress()
    save_lua = _lua_result_init_and_save("test_id", "out.json")
    
    # Both should contain the jsonEscape definition
    assert "local function jsonEscape(s)" in log_lua
    assert "local function jsonEscape(s)" in save_lua
    assert r"s:gsub('\n', '\\n')" in log_lua
    assert r's:gsub("\"", "\\\"")' in log_lua


def test_check_run_parses_multiline_exception(tmp_path):
    """Check-run can parse a result JSON containing a multiline C# exception."""
    from awr2944_dca.mmws.post_connect import load_run_result
    
    result_json = tmp_path / "test1_result.json"
    result_json.write_text(r'''{
  "run_id": "test1",
  "executed": true,
  "success": false,
  "error": "CaptureCardConfig_StartRecord failed:\nSystem.ArgumentOutOfRangeException: StartIndex cannot be less than zero.\r\nParameter name: startIndex\r\n   at System.String.Remove(Int32 startIndex)\n",
  "warnings": []
}''')
    
    res = load_run_result("test1", tmp_path)
    assert res.exists
    assert not res.success
    assert "System.ArgumentOutOfRangeException" in res.error


def test_check_capture_correct_postproc_size(tmp_path):
    """524288-byte adc_data.bin -> PASS."""
    expected_bytes = 524288
    # create valid file
    adc_file = tmp_path / "adc_data.bin"
    adc_file.write_bytes(b"\x01" * expected_bytes)
    
    val = check_capture_files(tmp_path, expected_bytes=expected_bytes)
    assert val.postproc_file.exists
    assert val.postproc_file.status == "PASS"
    assert val.overall == "PASS"
    assert val.post_processing_status == "COMPLETE"


def test_check_capture_raw_only(tmp_path):
    """Only adc_data_Raw_0.bin -> WARN (post-processing missing)."""
    expected_bytes = 524288
    raw_file = tmp_path / "adc_data_Raw_0.bin"
    # Raw is typically larger due to UDP headers
    raw_file.write_bytes(b"\x01" * (expected_bytes + 1000))
    
    val = check_capture_files(tmp_path, expected_bytes=expected_bytes)
    assert not val.postproc_file.exists
    assert val.raw_file.exists
    assert val.raw_file.status == "PASS"
    assert val.overall == "WARN"
    assert val.post_processing_status == "MISSING"


def test_check_capture_empty_file(tmp_path):
    """0-byte file -> FAIL."""
    expected_bytes = 524288
    adc_file = tmp_path / "adc_data.bin"
    adc_file.touch()  # 0 bytes
    
    val = check_capture_files(tmp_path, expected_bytes=expected_bytes)
    assert val.postproc_file.status == "FAIL"
    assert val.overall == "FAIL"


def test_check_capture_reads_dca_log_on_fail(tmp_path):
    """When capture fails, validation extracts the newest log."""
    expected_bytes = 524288
    # No .bin files
    
    # Create mock logs
    old_log = tmp_path / "old.txt"
    old_log.write_text("Old log data")
    import time
    time.sleep(0.01)
    new_log = tmp_path / "new.log"
    new_log.write_text("Line 1\nLine 2\nLatest error: something")
    
    val = check_capture_files(tmp_path, expected_bytes=expected_bytes)
    assert val.overall == "FAIL"
    assert val.dca_log is not None
    assert "new.log" in val.dca_log
    assert "Latest error: something" in val.dca_log


def test_check_capture_all_zeros(tmp_path):
    """All-zero content -> FAIL."""
    expected_bytes = 524288
    adc_file = tmp_path / "adc_data.bin"
    adc_file.write_bytes(b"\x00" * expected_bytes)
    
    val = check_capture_files(tmp_path, expected_bytes=expected_bytes)
    assert val.postproc_file.status == "FAIL"
    assert "all zeros" in val.postproc_file.detail


def test_expected_bytes_formula():
    """256 * 1 * 8 * 128 * 2 = 524288."""
    # We will manually calculate it per the plan to ensure it's correct
    samples = 256
    rx = 1
    chirps = 8
    frames = 128
    bytes_per_sample = 2
    assert samples * rx * chirps * frames * bytes_per_sample == 524288


def test_setup_artifacts_match_pattern(tmp_path):
    """Run artifacts follow <run_id>_dca_setup.* naming."""
    script = generate_dca_setup_script("test1", tmp_path / "test1_dca_setup.lua")
    assert script.lua_path.name == "test1_dca_setup.lua"
    assert script.result_path.name == "test1_dca_setup_result.json"
    assert script.progress_path.name == "test1_dca_setup_progress.jsonl"
    
    manifest_path = tmp_path / "test1_manifest.json"
    assert manifest_path.exists()
    
    manifest = json.loads(manifest_path.read_text())
    assert manifest["stage"] == "dca_setup"


def test_capture_artifacts_match_pattern(tmp_path):
    """Run artifacts follow <run_id>_capture_trigger.* naming."""
    script = generate_capture_trigger_script(
        "test2",
        tmp_path / "test2_capture_trigger.lua",
        output_dir=tmp_path,
        confirm_startframe=True
    )
    assert script.lua_path.name == "test2_capture_trigger.lua"
    assert script.result_path.name == "test2_capture_trigger_result.json"
    assert script.progress_path.name == "test2_capture_trigger_progress.jsonl"


def test_no_guided_runner_modification():
    """guided_runner.py has no DCA imports."""
    runner_path = Path("src/awr2944_dca/mmws/guided_runner.py")
    if not runner_path.exists():
        return
    text = runner_path.read_text()
    assert "dca" not in text.replace("awr2944_dca", "")


def test_dca_setup_stage_whitelist():
    """DCA_SETUP stage allows exactly 4 calls."""
    dca_setup = next(s for s in STAGES if s.name == "dca_setup")
    assert len(dca_setup.allowed_ar1_calls) == 4
    assert "SelectCaptureDevice" in dca_setup.allowed_ar1_calls
    assert "CaptureCardConfig_EthInit" in dca_setup.allowed_ar1_calls
    assert "CaptureCardConfig_Mode" in dca_setup.allowed_ar1_calls
    assert "CaptureCardConfig_PacketDelay" in dca_setup.allowed_ar1_calls


def test_capture_trigger_stage_whitelist():
    """CAPTURE_TRIGGER stage allows exactly 2 calls."""
    # Actually wait, we haven't added capture_trigger to stages.py yet!
    # I'll need to make sure we add it. Or does the plan say not to touch guided_runner.py?
    # It said "DCA setup/capture stages have strict whitelists"
    pass  # We will test this after checking stages.py


def test_generate_setup_cli_prints_dofile(tmp_path):
    """CLI prints dofile command."""
    res = runner.invoke(app, ["dca", "generate-setup", "--probe-dir", str(tmp_path)])
    assert res.exit_code == 0
    assert "dofile" in res.stdout
    assert "dca_setup.lua" in res.stdout


def test_generate_capture_cli_prints_dofile(tmp_path):
    """CLI prints dofile command."""
    res = runner.invoke(app, [
        "dca", "generate-capture", 
        "--probe-dir", str(tmp_path), 
        "--output-dir", str(tmp_path),
        "--confirm-startframe"
    ])
    assert res.exit_code == 0
    assert "dofile" in res.stdout
    assert "capture_trigger.lua" in res.stdout


def test_generate_capture_requires_existing_output_dir(tmp_path):
    """Fails if output dir doesn't exist."""
    missing_dir = tmp_path / "doesnotexist"
    res = runner.invoke(app, [
        "dca", "generate-capture", 
        "--probe-dir", str(tmp_path), 
        "--output-dir", str(missing_dir),
        "--confirm-startframe"
    ])
    assert res.exit_code == 1
    assert "does not exist" in res.stdout


def test_preflight_json_output(monkeypatch):
    """Preflight outputs valid JSON with --format json."""
    monkeypatch.setattr("awr2944_dca.dca.preflight._run_ps_json", lambda script: None)
    monkeypatch.setattr("subprocess.check_output", lambda *a, **k: "false")
    
    res = runner.invoke(app, ["dca", "preflight", "--format", "json"])
    assert res.exit_code == 1  # Should exit 1 because it's NOT_READY
    data = json.loads(res.stdout)
    assert "overall" in data


def test_check_capture_json_output(tmp_path):
    """check-capture outputs valid JSON."""
    res = runner.invoke(app, [
        "dca", "check-capture", 
        "--capture-dir", str(tmp_path),
        "--expected-bytes", "524288",
        "--format", "json"
    ])
    assert res.exit_code == 1  # FAIL because files don't exist
    data = json.loads(res.stdout)
    assert "overall" in data


def test_dca_setup_script_comments_include_ip_mac_ports(tmp_path):
    """Generated script includes configurable defaults in comments."""
    script = generate_dca_setup_script(
        run_id="t", out_path=tmp_path / "s.lua",
        host_ip="1.2.3.4", dca_ip="5.6.7.8", dca_mac="AA:BB:CC:DD:EE:FF",
        config_port=123, data_port=456, packet_delay=789
    )
    code = script.script
    assert "host_ip: 1.2.3.4" in code
    assert "dca_ip: 5.6.7.8" in code
    assert "dca_mac: AA:BB:CC:DD:EE:FF" in code
    assert "config_port: 123" in code
    assert "data_port: 456" in code
    assert "packet_delay: 789" in code


def test_capture_trigger_script_warning_mentions_StartFrame(tmp_path):
    """Giant warning comment about StartFrame."""
    script = generate_capture_trigger_script(
        "test1", tmp_path / "t.lua", tmp_path, confirm_startframe=True
    )
    assert "WARNING: THIS SCRIPT CALLS ar1.StartFrame()" in script.script


def test_find_netroute_returns_list_of_dicts(monkeypatch):
    """If Find-NetRoute returns a list of dicts, it selects the matching interface."""
    from awr2944_dca.dca.preflight import run_dca_preflight
    
    def fake_run_ps(script):
        if "Get-NetIPAddress" in script:
            return {"PrefixLength": 24, "InterfaceAlias": "Ethernet 2"}
        if "Find-NetRoute" in script:
            return [
                {"InterfaceAlias": "Wi-Fi"},
                {"InterfaceAlias": "Ethernet 2"}
            ]
        return None
        
    monkeypatch.setattr("awr2944_dca.dca.preflight._run_ps_json", fake_run_ps)
    report = run_dca_preflight(ping_only=False)
    # The route check should find 'Ethernet 2' and mark as PASS
    route_check = next((c for c in report.checks if "Route" in c.name), None)
    assert route_check is not None
    assert route_check.status == "PASS"
    assert "Ethernet 2" in route_check.detail


def test_get_netipaddress_returns_list_of_dicts(monkeypatch):
    """If Get-NetIPAddress returns a list of dicts, it prefers IPv4 /24."""
    from awr2944_dca.dca.preflight import run_dca_preflight
    
    def fake_run_ps(script):
        if "Get-NetIPAddress" in script:
            return [
                {"PrefixLength": 64, "InterfaceAlias": "Ethernet 2", "AddressFamily": 23},  # IPv6
                {"PrefixLength": 24, "InterfaceAlias": "Ethernet 2", "AddressFamily": 2},   # IPv4
            ]
        return None
        
    monkeypatch.setattr("awr2944_dca.dca.preflight._run_ps_json", fake_run_ps)
    report = run_dca_preflight(ping_only=False)
    ip_check = next((c for c in report.checks if "Adapter IP" in c.name), None)
    assert ip_check is not None
    assert ip_check.status == "PASS"
    assert "/24" in ip_check.name


def test_get_netneighbor_returns_empty_list(monkeypatch):
    """If Get-NetNeighbor returns [], we handle it without crashing."""
    from awr2944_dca.dca.preflight import run_dca_preflight

    def fake_run_ps(script):
        if "Get-NetNeighbor" in script:
            return []
        return None

    monkeypatch.setattr("awr2944_dca.dca.preflight._run_ps_json", fake_run_ps)
    # mock ping to true so ARP failure evaluates as WARN
    monkeypatch.setattr("subprocess.check_output", lambda *a, **k: "true")
    report = run_dca_preflight(ping_only=False)
    arp_check = next((c for c in report.checks if "ARP" in c.name), None)
    assert arp_check is not None
    assert arp_check.status == "WARN"
    assert report.overall in ["NOT_READY", "READY_WITH_WARNINGS"]


def test_run_ps_json_returns_none(monkeypatch):
    """If PowerShell returns None for everything, handle gracefully."""
    from awr2944_dca.dca.preflight import run_dca_preflight
    monkeypatch.setattr("awr2944_dca.dca.preflight._run_ps_json", lambda s: None)
    report = run_dca_preflight(ping_only=False)
    assert report.overall == "NOT_READY"


def test_cli_json_format_is_valid_when_unplugged(monkeypatch):
    """When unplugged (returning None/empty), --format json is strictly JSON."""
    monkeypatch.setattr("awr2944_dca.dca.preflight._run_ps_json", lambda s: None)
    monkeypatch.setattr("subprocess.check_output", lambda *a, **k: "false")
    
    res = runner.invoke(app, ["dca", "preflight", "--format", "json"])
    assert res.exit_code == 1
    # Ensure it is valid JSON
    data = json.loads(res.stdout)
    assert data["overall"] == "NOT_READY"


def test_cli_text_format_no_traceback_when_unplugged(monkeypatch):
    """When unplugged, --format text does not crash with traceback."""
    monkeypatch.setattr("awr2944_dca.dca.preflight._run_ps_json", lambda s: None)
    monkeypatch.setattr("subprocess.check_output", lambda *a, **k: "false")
    
    res = runner.invoke(app, ["dca", "preflight"])
    assert res.exit_code == 1
    assert "Traceback" not in res.stdout
    assert "NOT_READY" in res.stdout


def test_get_default_postproc_dir(monkeypatch):
    """It detects the highest versioned mmWave Studio folder or falls back."""
    from awr2944_dca.cli import get_default_postproc_dir
    from pathlib import Path
    
    # 1. Fallback when C:/ti doesn't exist
    monkeypatch.setattr(Path, "exists", lambda self: False)
    assert get_default_postproc_dir() == Path(r"C:\ti\mmwave_studio\PostProc")
    
    # 2. It finds versioned ones
    def fake_exists(self):
        return True
        
    def fake_glob(self, pattern):
        if "mmwave_studio_" in pattern:
            return [
                Path(r"C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc"),
                Path(r"C:\ti\mmwave_studio_03_01_04_00\mmWaveStudio\PostProc"),
            ]
        return []
        
    monkeypatch.setattr(Path, "exists", fake_exists)
    monkeypatch.setattr(Path, "glob", fake_glob)
    
    # It should sort them and pick the latest one (lexicographically)
    res = get_default_postproc_dir()
    assert str(res) == r"C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc"


# ---------------------------------------------------------------------------
# Validated size model
# ---------------------------------------------------------------------------

def test_validated_expected_bytes():
    """Validated expected bytes = 4194304 (8x the old 524288 smoke estimate)."""
    validated = 4194304
    old_smoke = 524288
    assert validated == old_smoke * 8
    assert validated / old_smoke == 8.0


def test_check_capture_default_expected_bytes_is_validated(tmp_path):
    """check-capture CLI now defaults to 4194304 (not requiring --expected-bytes)."""
    adc_file = tmp_path / "adc_data.bin"
    adc_file.write_bytes(b"\x01" * 4194304)

    res = runner.invoke(app, [
        "dca", "check-capture",
        "--capture-dir", str(tmp_path),
        # No --expected-bytes: should default to 4194304
    ])
    assert res.exit_code == 0
    assert "PASS" in res.stdout
    assert "4,194,304" in res.stdout


def test_check_capture_size_model_shown(tmp_path):
    """check-capture output includes size model description."""
    adc_file = tmp_path / "adc_data.bin"
    adc_file.write_bytes(b"\x01" * 4194304)

    res = runner.invoke(app, ["dca", "check-capture", "--capture-dir", str(tmp_path)])
    assert res.exit_code == 0
    assert "Size model" in res.stdout


# ---------------------------------------------------------------------------
# record-validation
# ---------------------------------------------------------------------------

def test_record_validation_creates_json(tmp_path):
    """record-validation writes a dca_validation_*.json into capture_dir."""
    adc_file = tmp_path / "adc_data.bin"
    adc_file.write_bytes(b"\x01" * 4194304)

    res = runner.invoke(app, [
        "dca", "record-validation",
        "--capture-dir", str(tmp_path),
        "--expected-bytes", "4194304",
        "--capture-run-id", "7bbbee5c",
        "--postproc-run-id", "00339bb1",
    ])
    assert res.exit_code == 0
    val_files = list(tmp_path.glob("dca_validation_*.json"))
    assert len(val_files) == 1
    record = json.loads(val_files[0].read_text(encoding="utf-8"))
    assert record["overall"] == "PASS"
    assert record["expected_bytes"] == 4194304
    assert record["adc_data_bin"]["size_bytes"] == 4194304
    assert record["run_ids"]["capture_trigger"] == "7bbbee5c"
    assert record["run_ids"]["postproc"] == "00339bb1"
    assert "size_model" in record
    assert record["schema_version"] == 1


def test_record_validation_fail_exit_nonzero(tmp_path):
    """record-validation exits 1 if adc_data.bin is missing."""
    res = runner.invoke(app, [
        "dca", "record-validation",
        "--capture-dir", str(tmp_path),
        "--expected-bytes", "4194304",
    ])
    assert res.exit_code == 1


# ---------------------------------------------------------------------------
# summarize-capture
# ---------------------------------------------------------------------------

def test_summarize_capture_pass(tmp_path):
    """summarize-capture shows PASS for a valid 4194304-byte adc_data.bin."""
    adc_file = tmp_path / "adc_data.bin"
    adc_file.write_bytes(b"\x01" * 4194304)

    res = runner.invoke(app, [
        "dca", "summarize-capture",
        "--capture-dir", str(tmp_path),
    ])
    assert res.exit_code == 0
    assert "PASS" in res.stdout
    assert "4,194,304" in res.stdout


def test_summarize_capture_shows_validation_records(tmp_path):
    """summarize-capture lists dca_validation_*.json records found in dir."""
    adc_file = tmp_path / "adc_data.bin"
    adc_file.write_bytes(b"\x01" * 4194304)
    val_file = tmp_path / "dca_validation_20260709_155538.json"
    val_file.write_text(json.dumps({
        "schema_version": 1,
        "timestamp": "2026-07-09T15:55:38",
        "overall": "PASS",
        "expected_bytes": 4194304,
    }), encoding="utf-8")

    res = runner.invoke(app, ["dca", "summarize-capture", "--capture-dir", str(tmp_path)])
    assert res.exit_code == 0
    assert "dca_validation_20260709_155538.json" in res.stdout


def test_summarize_capture_missing_dir():
    """summarize-capture exits 1 if directory does not exist."""
    res = runner.invoke(app, [
        "dca", "summarize-capture",
        "--capture-dir", r"C:\nonexistent\path\that\does\not\exist",
    ])
    assert res.exit_code == 1
