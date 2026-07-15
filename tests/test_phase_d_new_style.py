import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from awr2944_dca.lab import RadarProject
from awr2944_dca.api._session import SessionState


@pytest.fixture
def new_style_project(tmp_path):
    # Do NOT create project.json
    
    (tmp_path / "awr2944.toml").write_text("""
[project]
name = "test_new_style"
id = "test1234"
schema_version = 2

[defaults]
frames = 10
guard_frames = 2
profile = "smoke_v1"

[network]
dca_ip = "192.168.33.180"
config_port = 4096
data_port = 4098
""")

    local_dir = tmp_path / ".awr2944"
    local_dir.mkdir()
    (local_dir / "local.toml").write_text("""
[serial]
com_port = "COM99"
aux_com_port = "COM100"
baud_rate = 115200

[network]
host_ip = "192.168.33.30"

[dca_tools]
control_exe = "fake_control.exe"
record_exe = "fake_record.exe"
rf_api_dll = "fake_rf_api.dll"
cf_json = "fake_cf.json"
""")

    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    (profiles_dir / "smoke_v1.toml").write_text("""
[profile]
name = "smoke_v1"

[frame]
frame_count = 10
""")
    return tmp_path


def test_new_style_project_open_and_connect(new_style_project):
    """RadarProject.open() works and project.connect() succeeds without project.json."""
    # Ensure no attempt to read project.json
    pj = new_style_project / "project.json"
    assert not pj.exists()

    project = RadarProject.open(new_style_project)
    
    # 2. project.connect() succeeds
    with project.connect() as session:
        assert session.state == SessionState.OPEN
        assert session.connection.rf_api_dll == "fake_rf_api.dll"


@patch("awr2944_dca.capture_session.run_capture")
def test_new_style_capture_run_resolves_dca_cli(mock_run_capture, new_style_project):
    """session.capture.run() resolves complete DcaCli arguments."""
    project = RadarProject.open(new_style_project)
    
    # Create fake cf.json so it exists
    tools_dir = new_style_project / "tools" / "dca1000"
    tools_dir.mkdir(parents=True)
    (tools_dir / "cf.json").write_text("{}")
    
    # Mock return value
    mock_run_capture.return_value = MagicMock(success=True)

    with project.connect() as session:
        result = session.capture.run(profile="smoke_v1", name="test_cap")

    assert result.session_result.success is True

    # Check DcaCli was passed
    dca_cli = mock_run_capture.call_args.kwargs["dca_cli"]
    assert dca_cli is not None
    assert dca_cli._control_exe.name == "fake_control.exe"
    assert dca_cli._record_exe.name == "fake_record.exe"
    assert dca_cli._rf_api_dll.name == "fake_rf_api.dll"
    assert dca_cli._cf_json.name == "cf.json"

    # 8. capture_manifest.json is placed inside the capture directory
    cap_dir = new_style_project / "captures" / result.capture.capture_id
    assert (cap_dir / "capture_manifest.json").exists()
    
    # 9. manifest.json remains untouched (does not exist yet because run_capture is mocked)
    assert not (cap_dir / "manifest.json").exists()


@patch("awr2944_dca.api._capture_run._create_capture_manifest_facade")
def test_dca_cli_construction_failure(mock_create_manifest, new_style_project):
    """If DcaCli construction fails, no hardware/directory, session enters ERROR."""
    project = RadarProject.open(new_style_project)
    
    # Create tools/dca1000 directory and cf.json so it exists
    tools_dir = new_style_project / "tools" / "dca1000"
    tools_dir.mkdir(parents=True, exist_ok=True)
    (tools_dir / "cf.json").write_text("{}")
    
    # We patch DcaCli in the module where it is imported/used, but it is imported locally:
    # `from awr2944_dca.dca_cli import DcaCli`
    with patch("awr2944_dca.dca_cli.DcaCli") as MockDcaCli:
        MockDcaCli.side_effect = TypeError("missing 2 required positional arguments")
        
        with project.connect() as session:
            try:
                session.capture.run(profile="smoke_v1")
                pytest.fail("Should have raised TypeError")
            except TypeError as e:
                assert "missing 2 required positional arguments" in str(e)
                # 12. Explicit session enters ERROR (checked BEFORE session.close is called by __exit__)
                assert session.state == SessionState.ERROR
            
    # 10. DcaCli failure occurs before capture directory creation
    mock_create_manifest.assert_not_called()
    
    # 13. Context-manager exit releases the global hardware lock
    # 14. A new session can acquire that lock afterward
    with project.connect() as session2:
        assert session2.state == SessionState.OPEN
