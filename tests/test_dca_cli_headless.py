"""Tests for dca_cli.py — DCA1000 CLI subprocess wrapper."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from awr2944_dca.dca_cli import DcaCli, DcaCmdResult, DcaConfigIssue, StartRecordResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_cf_json(tmp_path):
    """Create a minimal cf.json for testing."""
    cfg = {
        "DCA1000Config": {
            "dataLoggingMode": "raw",
            "dataTransferMode": "LVDSCapture",
            "dataCaptureMode": "ethernetStream",
            "lvdsMode": 1,
            "dataFormatMode": 3,
            "packetDelay_us": 25,
            "ethernetConfig": {
                "DCA1000IPAddress": "192.168.33.180",
                "DCA1000ConfigPort": 4096,
                "DCA1000DataPort": 4098,
            },
            "ethernetConfigUpdate": {
                "systemIPAddress": "192.168.33.30",
                "DCA1000IPAddress": "192.168.33.180",
                "DCA1000MACAddress": "12.34.56.78.90.12",
                "DCA1000ConfigPort": 4096,
                "DCA1000DataPort": 4098,
            },
            "captureConfig": {
                "fileBasePath": str(tmp_path).replace("\\", "\\\\"),
                "filePrefix": "adc_data",
                "maxRecFileSize_MB": 1024,
                "sequenceNumberEnable": 1,
                "captureStopMode": "infinite",
                "bytesToCapture": 4000,
                "durationToCapture_ms": 4000,
                "framesToCapture": 40,
            },
        }
    }
    cf_path = tmp_path / "cf.json"
    cf_path.write_text(json.dumps(cfg, indent=2))
    return cf_path


@pytest.fixture
def dca_cli(tmp_path, sample_cf_json):
    """Create a DcaCli in dry-run mode."""
    control = tmp_path / "DCA1000EVM_CLI_Control.exe"
    record = tmp_path / "DCA1000EVM_CLI_Record.exe"
    rf_api = tmp_path / "RF_API.dll"
    control.touch()
    record.touch()
    rf_api.touch()
    cli = DcaCli(
        control_exe=control,
        record_exe=record,
        rf_api_dll=rf_api,
        cf_json_path=sample_cf_json,
        working_dir=tmp_path,
    )
    cli.dry_run = True
    return cli


# ---------------------------------------------------------------------------
# Status tests
# ---------------------------------------------------------------------------

class TestDcaStatus:
    def test_status_reports_paths(self, dca_cli):
        s = dca_cli.status()
        assert s["control_exe_exists"]
        assert s["record_exe_exists"]
        assert s["cf_json_exists"]
        assert s["dry_run"]

    def test_status_missing_exe(self, tmp_path, sample_cf_json):
        cli = DcaCli(
            control_exe=tmp_path / "missing.exe",
            record_exe=tmp_path / "missing2.exe",
            rf_api_dll=tmp_path / "missing3.dll",
            cf_json_path=sample_cf_json,
        )
        s = cli.status()
        assert not s["control_exe_exists"]
        assert not s["record_exe_exists"]


# ---------------------------------------------------------------------------
# Config validation tests
# ---------------------------------------------------------------------------

class TestConfigValidation:
    def test_valid_config_no_errors(self, dca_cli):
        issues = dca_cli.validate_config()
        errors = [i for i in issues if i.level == "error"]
        assert len(errors) == 0

    def test_wrong_ip_detected(self, dca_cli, sample_cf_json):
        # Modify IP in cf.json
        cfg = json.loads(sample_cf_json.read_text())
        cfg["DCA1000Config"]["ethernetConfig"]["DCA1000IPAddress"] = "10.0.0.1"
        sample_cf_json.write_text(json.dumps(cfg))

        issues = dca_cli.validate_config()
        ip_errors = [i for i in issues if "DCA1000IPAddress" in i.field]
        assert len(ip_errors) == 1

    def test_missing_config_file(self, tmp_path):
        cli = DcaCli(
            control_exe=tmp_path / "ctrl.exe",
            record_exe=tmp_path / "rec.exe",
            rf_api_dll=tmp_path / "rf.dll",
            cf_json_path=tmp_path / "nonexistent.json",
        )
        issues = cli.validate_config()
        assert any(i.level == "error" for i in issues)


# ---------------------------------------------------------------------------
# Dry-run command tests
# ---------------------------------------------------------------------------

class TestDryRunCommands:
    def test_dry_run_fpga_config(self, dca_cli):
        result = dca_cli.configure_fpga()
        assert result.success
        assert "DRY RUN" in result.stdout

    def test_dry_run_start_record(self, dca_cli):
        result = dca_cli.start_record()
        assert isinstance(result, StartRecordResult)
        assert result.recording_active
        assert "DRY RUN" in result.query_status_text

    def test_dry_run_stop_record(self, dca_cli):
        result = dca_cli.stop_record()
        assert result.success

    def test_dry_run_query_status(self, dca_cli):
        result = dca_cli.query_status()
        assert result.success

    def test_dry_run_query_sys_status(self, dca_cli):
        result = dca_cli.query_sys_status()
        assert result.success

    def test_dry_run_cli_version(self, dca_cli):
        result = dca_cli.cli_version()
        assert result.success

    def test_dry_run_dll_version(self, dca_cli):
        result = dca_cli.dll_version()
        assert result.success


# ---------------------------------------------------------------------------
# Transcript tests
# ---------------------------------------------------------------------------

class TestDcaTranscript:
    def test_transcript_records_commands(self, dca_cli):
        dca_cli.configure_fpga()
        dca_cli.start_record()  # dry-run start_record returns StartRecordResult, no transcript entry
        dca_cli.stop_record()
        # start_record in dry_run returns early without appending to transcript
        assert len(dca_cli.transcript) == 2

    def test_save_transcript(self, dca_cli, tmp_path):
        dca_cli.configure_fpga()
        out = dca_cli.save_transcript(tmp_path / "dca_transcript.json")
        assert out.exists()
        data = json.loads(out.read_text())
        assert len(data) == 1
        assert data[0]["command"] == "fpga"


# ---------------------------------------------------------------------------
# Config copy and customize
# ---------------------------------------------------------------------------

class TestCopyConfig:
    def test_copy_and_customize(self, sample_cf_json, tmp_path):
        dest = tmp_path / "capture_001" / "cf.json"
        report = DcaCli.copy_and_customize_config(
            sample_cf_json, dest,
            file_base_path=str(tmp_path / "capture_001"),
            file_prefix="test_capture",
            capture_stop_mode="frames",
            frames_to_capture=8,
        )
        assert dest.exists()
        assert report["source_sha256"]
        assert report["dest_sha256"]
        assert len(report["changes"]) == 4

        # Verify the changes in the output file
        cfg = json.loads(dest.read_text())
        cap = cfg["DCA1000Config"]["captureConfig"]
        assert cap["filePrefix"] == "test_capture"
        assert cap["captureStopMode"] == "frames"
        assert cap["framesToCapture"] == 8

    def test_no_overwrite_of_source(self, sample_cf_json, tmp_path):
        original_content = sample_cf_json.read_text()
        dest = tmp_path / "modified.json"
        DcaCli.copy_and_customize_config(
            sample_cf_json, dest,
            file_prefix="changed",
        )
        assert sample_cf_json.read_text() == original_content


# ---------------------------------------------------------------------------
# Subprocess execution (mocked)
# ---------------------------------------------------------------------------

class TestSubprocessExecution:
    @patch("awr2944_dca.dca_cli.subprocess.run")
    def test_live_execution(self, mock_run, tmp_path, sample_cf_json):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="FPGA Configuration command : Success",
            stderr="",
        )
        control = tmp_path / "DCA1000EVM_CLI_Control.exe"
        control.touch()
        cli = DcaCli(
            control_exe=control,
            record_exe=tmp_path / "rec.exe",
            rf_api_dll=tmp_path / "rf.dll",
            cf_json_path=sample_cf_json,
            working_dir=tmp_path,
        )
        cli.dry_run = False
        result = cli.configure_fpga()
        assert result.success
        assert "Success" in result.stdout

    @patch("awr2944_dca.dca_cli.subprocess.run")
    def test_execution_failure_detected(self, mock_run, tmp_path, sample_cf_json):
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="Error: Unable to connect",
            stderr="",
        )
        control = tmp_path / "DCA1000EVM_CLI_Control.exe"
        control.touch()
        cli = DcaCli(
            control_exe=control,
            record_exe=tmp_path / "rec.exe",
            rf_api_dll=tmp_path / "rf.dll",
            cf_json_path=sample_cf_json,
            working_dir=tmp_path,
        )
        cli.dry_run = False
        result = cli.configure_fpga()
        assert not result.success

    @patch("awr2944_dca.dca_cli.subprocess.run",
           side_effect=FileNotFoundError("exe not found"))
    def test_missing_exe_handled(self, mock_run, tmp_path, sample_cf_json):
        cli = DcaCli(
            control_exe=tmp_path / "missing.exe",
            record_exe=tmp_path / "rec.exe",
            rf_api_dll=tmp_path / "rf.dll",
            cf_json_path=sample_cf_json,
            working_dir=tmp_path,
        )
        cli.dry_run = False
        result = cli.configure_fpga()
        assert not result.success
        assert "not found" in result.stderr.lower()


# ---------------------------------------------------------------------------
# Repr test
# ---------------------------------------------------------------------------

class TestRepr:
    def test_repr_dry_run(self, dca_cli):
        r = repr(dca_cli)
        assert "DRY_RUN" in r

    def test_repr_live(self, dca_cli):
        dca_cli.dry_run = False
        r = repr(dca_cli)
        assert "LIVE" in r


# ---------------------------------------------------------------------------
# start_record pipe-blocking regression tests
# ---------------------------------------------------------------------------

class TestStartRecordProcessManagement:
    """Regression tests for the start_record pipe-blocking bug.

    Root cause: subprocess.run(capture_output=True) blocks on stdout
    PIPE when CLI_Control spawns a long-lived CLI_Record child that
    inherits the pipe handles.
    """

    @patch("awr2944_dca.dca_cli.subprocess.Popen")
    @patch("awr2944_dca.dca_cli.subprocess.run")
    def test_start_record_uses_popen_not_run(
        self, mock_run, mock_popen, tmp_path, sample_cf_json
    ):
        """start_record must use Popen, not subprocess.run, to avoid pipe blocking."""
        mock_proc = MagicMock()
        mock_proc.pid = 12345
        mock_proc.returncode = 0
        mock_proc.wait = MagicMock(return_value=0)
        mock_popen.return_value = mock_proc

        # query_status response
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Record process in progress",
            stderr="",
        )

        control = tmp_path / "DCA1000EVM_CLI_Control.exe"
        control.touch()
        cli = DcaCli(
            control_exe=control,
            record_exe=tmp_path / "DCA1000EVM_CLI_Record.exe",
            rf_api_dll=tmp_path / "RF_API.dll",
            cf_json_path=sample_cf_json,
            working_dir=tmp_path,
        )
        cli.dry_run = False

        result = cli.start_record(
            stdout_log_path=tmp_path / "stdout.log",
            stderr_log_path=tmp_path / "stderr.log",
        )

        # Popen must have been used (not subprocess.run for the launch)
        mock_popen.assert_called_once()
        # Verify no capture_output=True in Popen call
        call_kwargs = mock_popen.call_args[1]
        assert call_kwargs.get("stdout") is not subprocess.PIPE

    @patch("awr2944_dca.dca_cli.subprocess.Popen")
    @patch("awr2944_dca.dca_cli.subprocess.run")
    def test_start_record_cwd_is_postproc_dir(
        self, mock_run, mock_popen, tmp_path, sample_cf_json
    ):
        """start_record cwd must be the directory containing Control/Record/RF_API."""
        mock_proc = MagicMock()
        mock_proc.pid = 12345
        mock_proc.returncode = 0
        mock_proc.wait = MagicMock(return_value=0)
        mock_popen.return_value = mock_proc

        mock_run.return_value = MagicMock(
            returncode=0, stdout="Record process in progress", stderr="",
        )

        postproc = tmp_path / "PostProc"
        postproc.mkdir()
        control = postproc / "DCA1000EVM_CLI_Control.exe"
        record = postproc / "DCA1000EVM_CLI_Record.exe"
        rf_api = postproc / "RF_API.dll"
        control.touch()
        record.touch()
        rf_api.touch()

        cli = DcaCli(
            control_exe=control,
            record_exe=record,
            rf_api_dll=rf_api,
            cf_json_path=sample_cf_json,
            working_dir=postproc,
        )
        cli.dry_run = False

        cli.start_record(
            stdout_log_path=tmp_path / "stdout.log",
            stderr_log_path=tmp_path / "stderr.log",
        )

        call_kwargs = mock_popen.call_args[1]
        assert call_kwargs["cwd"] == str(postproc)

    @patch("awr2944_dca.dca_cli.subprocess.Popen")
    @patch("awr2944_dca.dca_cli.subprocess.run")
    def test_start_record_requires_active_query_status(
        self, mock_run, mock_popen, tmp_path, sample_cf_json
    ):
        """start_record success requires query_status to report active."""
        mock_proc = MagicMock()
        mock_proc.pid = 12345
        mock_proc.returncode = 0
        mock_proc.wait = MagicMock(return_value=0)
        mock_popen.return_value = mock_proc

        # query_status says NOT active
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="No record process is running. [error -4002]",
            stderr="",
        )

        control = tmp_path / "DCA1000EVM_CLI_Control.exe"
        control.touch()
        cli = DcaCli(
            control_exe=control,
            record_exe=tmp_path / "DCA1000EVM_CLI_Record.exe",
            rf_api_dll=tmp_path / "RF_API.dll",
            cf_json_path=sample_cf_json,
            working_dir=tmp_path,
        )
        cli.dry_run = False

        result = cli.start_record(
            stdout_log_path=tmp_path / "stdout.log",
            stderr_log_path=tmp_path / "stderr.log",
        )

        assert not result.recording_active

    @patch("awr2944_dca.dca_cli.subprocess.Popen")
    @patch("awr2944_dca.dca_cli.subprocess.run")
    def test_start_record_no_auto_retry(
        self, mock_run, mock_popen, tmp_path, sample_cf_json
    ):
        """start_record must not automatically retry on failure."""
        mock_proc = MagicMock()
        mock_proc.pid = 12345
        mock_proc.returncode = 1  # failure
        mock_proc.wait = MagicMock(return_value=1)
        mock_popen.return_value = mock_proc

        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="No record process is running. [error -4002]",
            stderr="",
        )

        control = tmp_path / "DCA1000EVM_CLI_Control.exe"
        control.touch()
        cli = DcaCli(
            control_exe=control,
            record_exe=tmp_path / "DCA1000EVM_CLI_Record.exe",
            rf_api_dll=tmp_path / "RF_API.dll",
            cf_json_path=sample_cf_json,
            working_dir=tmp_path,
        )
        cli.dry_run = False

        cli.start_record(
            stdout_log_path=tmp_path / "stdout.log",
            stderr_log_path=tmp_path / "stderr.log",
        )

        # Popen should be called exactly once (no retry)
        assert mock_popen.call_count == 1

    def test_start_record_result_fields(self):
        """StartRecordResult must have all required fields."""
        result = StartRecordResult(
            control_pid=1234,
            control_return_code=0,
            control_exited=True,
            record_pid=5678,
            query_status_text="Record process in progress",
            recording_active=True,
            stdout_log="/path/stdout.log",
            stderr_log="/path/stderr.log",
        )
        assert result.control_pid == 1234
        assert result.control_return_code == 0
        assert result.control_exited
        assert result.record_pid == 5678
        assert result.recording_active
        assert result.error == ""  # default
        assert result.ti_cli_log_paths == []  # default
        assert result.timestamp  # auto-populated

    def test_dry_run_start_record_returns_start_record_result(self, dca_cli):
        """Dry-run start_record must return StartRecordResult, not DcaCmdResult."""
        result = dca_cli.start_record()
        assert isinstance(result, StartRecordResult)
        assert result.recording_active

