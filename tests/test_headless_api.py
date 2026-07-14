"""Tests for the lab.headless API integration."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def project_root(tmp_path):
    """Create a minimal project structure for testing."""
    # Create project.json
    proj = {
        "name": "test_project",
        "project_id": "test_001",
    }
    (tmp_path / "project.json").write_text(json.dumps(proj))
    (tmp_path / "captures").mkdir()
    (tmp_path / "exp_lau_probe" / "ti" / "headless").mkdir(parents=True)

    # Create toolchain.local.json
    tc = {
        "dca_cli_control_exe": str(tmp_path / "DCA1000EVM_CLI_Control.exe"),
        "dca_cli_record_exe": str(tmp_path / "DCA1000EVM_CLI_Record.exe"),
        "rf_api_dll": str(tmp_path / "RF_API.dll"),
        "dca_cli_cf_json": str(tmp_path / "cf.json"),
        "sample_lvds_cfg": str(tmp_path / "profile_LVDS.cfg"),
        "mmw_demo_appimage": str(tmp_path / "awr2944_mmw_demoTDM.appimage"),
        "uart_uniflash_py": str(tmp_path / "uart_uniflash.py"),
        "sbl_uart_uniflash_tiimage": str(tmp_path / "sbl_uart_uniflash.release.tiimage"),
        "sbl_qspi_tiimage": str(tmp_path / "sbl_qspi.release.tiimage"),
    }
    tc_path = tmp_path / "exp_lau_probe" / "ti" / "headless" / "toolchain.local.json"
    tc_path.write_text(json.dumps(tc))

    return tmp_path


# ---------------------------------------------------------------------------
# HeadlessApi tests
# ---------------------------------------------------------------------------

class TestHeadlessApi:
    def test_import(self):
        from awr2944_dca.headless import HeadlessApi
        assert HeadlessApi is not None

    def test_create_api(self, project_root):
        from awr2944_dca.headless import HeadlessApi
        api = HeadlessApi(project_root)
        assert repr(api)

    def test_flash_plan_missing(self, project_root):
        from awr2944_dca.headless import HeadlessApi
        api = HeadlessApi(project_root)
        result = api.flash_plan()
        assert "error" in result

    def test_flash_requires_confirmation(self, project_root):
        from awr2944_dca.headless import HeadlessApi
        api = HeadlessApi(project_root)
        with pytest.raises(ValueError, match="explicit confirmation"):
            api.flash()

    def test_flash_both_confirms_raises_not_implemented(self, project_root):
        from awr2944_dca.headless import HeadlessApi
        api = HeadlessApi(project_root)
        with pytest.raises(NotImplementedError):
            api.flash(confirm_device_flash=True, confirm_sop_uart_boot=True)

    def test_toolchain_missing_paths(self, project_root):
        from awr2944_dca.headless import HeadlessApi
        api = HeadlessApi(project_root)
        tc = api.toolchain()
        # All files are missing (we didn't create them)
        for key, val in tc.items():
            assert val["status"] in ("NOT_FOUND", "MISSING")


# ---------------------------------------------------------------------------
# RadarProject.headless integration
# ---------------------------------------------------------------------------

class TestRadarProjectHeadless:
    @patch("awr2944_dca.lab.find_project_root")
    @patch("awr2944_dca.lab.load_project")
    def test_headless_property_exists(self, mock_load, mock_find, project_root):
        mock_find.return_value = project_root
        mock_load.return_value = {"name": "test", "project_id": "test_001"}

        from awr2944_dca.lab import RadarProject
        lab = RadarProject(project_root)
        hl = lab.headless
        assert hl is not None
        # Second access returns same instance
        assert lab.headless is hl


# ---------------------------------------------------------------------------
# HeadlessApi.serial_ports (mocked)
# ---------------------------------------------------------------------------

class TestSerialPortsApi:
    @patch("awr2944_dca.headless_serial.subprocess.run")
    def test_serial_ports_api(self, mock_run, project_root):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps([{
                "FriendlyName": "XDS110 Class Application/User UART (COM8)",
                "InstanceId": "USB\\VID_0451&PID_BEF3\\A",
                "Status": "OK",
            }]),
        )
        from awr2944_dca.headless import HeadlessApi
        api = HeadlessApi(project_root)
        result = api.serial_ports()
        assert result["recommended_app_port"] == "COM8"
        assert len(result["ports"]) == 1


# ---------------------------------------------------------------------------
# HeadlessApi.configs
# ---------------------------------------------------------------------------

class TestConfigsApi:
    def test_load_cfg_from_file(self, project_root):
        # Create a sample cfg
        cfg_text = "sensorStop\nflushCfg\nchannelCfg 15 7 0\n"
        cfg_path = project_root / "test.cfg"
        cfg_path.write_text(cfg_text)

        from awr2944_dca.headless import HeadlessApi
        api = HeadlessApi(project_root)
        cfg = api.configs.load_cfg(cfg_path)
        assert cfg.get_command("channelCfg") is not None

    def test_load_ti_lvds_sample_missing(self, project_root):
        from awr2944_dca.headless import HeadlessApi
        api = HeadlessApi(project_root)
        with pytest.raises(FileNotFoundError):
            api.configs.load_ti_lvds_sample()


# ---------------------------------------------------------------------------
# HeadlessApi.capture
# ---------------------------------------------------------------------------

class TestCaptureApi:
    def test_create_capture_workflow(self, project_root):
        from awr2944_dca.headless import HeadlessApi
        api = HeadlessApi(project_root)
        wf = api.capture("test_cap_001", notes="First test")
        assert wf.workflow_id.startswith("headless_test_cap_001_")
        assert wf.manifest.notes == "First test"
        assert (project_root / "captures" / "test_cap_001").exists()


# ---------------------------------------------------------------------------
# Independence checks
# ---------------------------------------------------------------------------

class TestIndependence:
    """Verify lab.headless does NOT import mmWave Studio, RSTD, etc."""

    def _check_no_forbidden_imports(self, mod, mod_name: str):
        """Check that a module has no forbidden import statements."""
        source = Path(mod.__file__).read_text()
        # Only check actual import lines, not docstrings mentioning
        # what we don't depend on
        import_lines = [
            line.strip() for line in source.splitlines()
            if line.strip().startswith(("import ", "from "))
        ]
        forbidden_imports = ["mmws", "rstd", "pywinauto", "lua_shell"]
        for line in import_lines:
            for forbidden in forbidden_imports:
                assert forbidden not in line.lower(), (
                    f"Found forbidden import '{forbidden}' in {mod_name}: {line}"
                )

    def test_no_mmws_import(self):
        import awr2944_dca.headless as mod
        self._check_no_forbidden_imports(mod, "headless.py")

    def test_no_headless_serial_mmws_import(self):
        import awr2944_dca.headless_serial as mod
        self._check_no_forbidden_imports(mod, "headless_serial.py")

    def test_no_mmw_demo_config_mmws_import(self):
        import awr2944_dca.mmw_demo_config as mod
        self._check_no_forbidden_imports(mod, "mmw_demo_config.py")

    def test_no_dca_cli_mmws_import(self):
        import awr2944_dca.dca_cli as mod
        self._check_no_forbidden_imports(mod, "dca_cli.py")

    def test_no_workflow_mmws_import(self):
        import awr2944_dca.headless_workflow as mod
        self._check_no_forbidden_imports(mod, "headless_workflow.py")
