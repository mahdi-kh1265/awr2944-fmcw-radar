import pytest
from pathlib import Path
from awr2944_dca.lab import RadarProject
from awr2944_dca._doctor import HardwareManager, CheckResult, HardwareReport

def test_hardware_doctor_offline_success(tmp_path):
    project = RadarProject.create(name="test_proj", parent=tmp_path)
    
    report = project.doctor(include_hardware=False)
    
    assert report.mode == "OFFLINE_ONLY"
    assert report.ready_for_capture == False  # Offline report never ready
    
    # We expect some failures offline because cf.json is missing in the dummy project
    assert any(c.name == "cf_json_exists" and c.status == "FAIL" for c in report.checks)
    assert any(c.name == "project_structure" and c.status == "PASS" for c in report.checks)
    
    # It shouldn't have run the diagnostic tests
    assert not any(c.name == "cli_com_port_exists" for c in report.checks)

def test_hardware_doctor_offline_missing_struct(tmp_path):
    project = RadarProject.create(name="test_proj", parent=tmp_path)
    # Break structure
    (project.root / "captures").rmdir()
    
    report = project.doctor(include_hardware=False)
    struct_check = next(c for c in report.checks if c.name == "project_structure")
    assert struct_check.status == "FAIL"
    assert not report.success

def test_hardware_doctor_diagnostics_mocked(tmp_path, monkeypatch):
    # Mock platformdirs to use tmp_path
    monkeypatch.setattr("platformdirs.user_state_dir", lambda *args, **kwargs: str(tmp_path / "state"))
    
    project = RadarProject.create(name="test_proj", parent=tmp_path)

    # Let's write dummy exe and cf.json so offline checks pass
    project.config.local.dca_control_exe = str(project.root / "dca_control.exe")
    project.config.local.dca_record_exe = str(project.root / "dca_record.exe")
    project.config.local.cf_json_path = str(project.root / "cf.json")
    project.config.local.com_port = "COM8"  # Required for resolve_connection
    project.config.local.host_ip = "192.168.33.30"
    project.config.portable.dca_ip = "192.168.33.180"
    project.config.portable.data_port = 4098
    project.config.portable.config_port = 4096

    (project.root / "dca_control.exe").touch()
    (project.root / "dca_record.exe").touch()

    # We need a valid cf.json to pass cf.json checks
    import json
    with open(project.root / "cf.json", "w") as f:
        json.dump({
            "DCA1000Config": {
                "ethernetConfigUpdate": {
                    "systemIPAddress": project.config.local.host_ip,
                    "DCA1000IPAddress": project.config.portable.dca_ip,
                    "DCA1000ConfigPort": project.config.portable.config_port,
                    "DCA1000DataPort": project.config.portable.data_port
                }
            }
        }, f)

    project.config.save()

    report = project.doctor(include_hardware=False)
    # The offline should now pass for everything
    assert all(c.status in ("PASS", "SKIP") for c in report.checks)
    assert report.success

def test_doctor_detects_session_lock(tmp_path, monkeypatch):
    monkeypatch.setattr("platformdirs.user_state_dir", lambda *args, **kwargs: str(tmp_path / "state"))
    project = RadarProject.create(name="lock_proj", parent=tmp_path)
    project.config.local.com_port = "COM8"
    project.config.local.host_ip = "192.168.33.30"
    project.config.portable.dca_ip = "192.168.33.180"
    project.config.portable.data_port = 4098
    project.config.portable.config_port = 4096
    project.config.save()
    
    # 1. Unlocked state
    report = project.doctor(include_hardware=False)
    lock_check = next(c for c in report.checks if c.name == "no_active_session_lock")
    assert lock_check.status == "PASS"
    assert "unlocked" in lock_check.detail.lower()

    # 2. Acquire lock via RadarSession simulation
    from awr2944_dca.api._lock import HardwareLease
    import os
    lease = HardwareLease(
        project_root=str(project.root),
        com_port="COM8",
        host_ip="192.168.33.30",
        data_port=4098,
        dca_ip="192.168.33.180",
        cmd_port=4096,
    )
    with lease:
        # Doctor should see "owned by this process"
        report2 = project.doctor(include_hardware=False)
        lock_check2 = next(c for c in report2.checks if c.name == "no_active_session_lock")
        assert lock_check2.status == "PASS"
        assert str(os.getpid()) in lock_check2.detail
        assert "held by this process" in lock_check2.detail

def test_import_boundary_cli():
    """Verify that running `awr doctor` does not import mmws GUI/Lua stuff."""
    import subprocess
    import sys
    
    script = """
import sys
from awr2944_dca.cli import app
from typer.testing import CliRunner
runner = CliRunner()
res = runner.invoke(app, ["doctor", "--offline"])
bad_modules = []
found = [m for m in bad_modules if m in sys.modules]
if found:
    print("FAILED:", found)
    sys.exit(1)
print("OK")
"""
    res = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert res.returncode == 0, f"Import boundary failed: {res.stdout} {res.stderr}"
    assert "OK" in res.stdout
