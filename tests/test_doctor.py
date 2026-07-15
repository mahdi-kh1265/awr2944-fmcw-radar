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
    project = RadarProject.create(name="test_proj", parent=tmp_path)
    
    # Let's write dummy exe and cf.json so offline checks pass
    project.config.local.dca_control_exe = str(project.root / "dca_control.exe")
    project.config.local.dca_record_exe = str(project.root / "dca_record.exe")
    project.config.local.cf_json_path = str(project.root / "cf.json")
    
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
bad_modules = ["awr2944_dca.legacy_mmws", "pywinauto", "pythonnet"]
found = [m for m in bad_modules if m in sys.modules]
if found:
    print("FAILED:", found)
    sys.exit(1)
print("OK")
"""
    res = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert res.returncode == 0, f"Import boundary failed: {res.stdout} {res.stderr}"
    assert "OK" in res.stdout
