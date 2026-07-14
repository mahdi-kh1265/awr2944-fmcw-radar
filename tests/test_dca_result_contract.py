import pytest
from unittest.mock import MagicMock, patch
from awr2944_dca.dca_cli import DcaCmdResult, StartRecordResult
from awr2944_dca.capture_session import validate_dca_cmd_result, DcaInitializationError
from awr2944_dca.capture_cli import run_dca_preflight

def create_mock_result(returncode=0, stdout="", stderr="", success=True, elapsed_s=0.5):
    return DcaCmdResult(
        command="mock_cmd",
        args=["mock_cmd"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
        success=success,
        elapsed_s=elapsed_s,
        exe_path="/mock/path/exe",
    )

def test_validation_uses_real_fields():
    # 1. successful reset result passes validation
    res = create_mock_result(returncode=0, stdout="Done", success=True)
    validate_dca_cmd_result(res, "reset_fpga") # Should not raise

    # 4. nonzero return code fails with useful diagnostics
    res_fail = create_mock_result(returncode=1, stdout="", stderr="Some error", success=False)
    with pytest.raises(DcaInitializationError) as exc:
        validate_dca_cmd_result(res_fail, "configure_fpga")
    assert "configure_fpga failed (rc=1)" in str(exc.value)
    assert "Some error" in str(exc.value)

    # 5. timeout fails with useful diagnostics
    res_timeout = create_mock_result(returncode=-1, stderr="TIMEOUT expired", success=False)
    with pytest.raises(DcaInitializationError) as exc:
        validate_dca_cmd_result(res_timeout, "reset_fpga")
    assert "timed out after" in str(exc.value)
    
    # 6. stderr/output failure is preserved
    res_msg = create_mock_result(returncode=0, stdout="Error: bad config", success=False)
    with pytest.raises(DcaInitializationError) as exc:
        validate_dca_cmd_result(res_msg, "configure_record")
    assert "Error: bad config" in str(exc.value)
    
    # 7. no production code accesses a nonexistent .error field
    with pytest.raises(AttributeError):
        _ = res.error

def test_start_record_result_unaffected():
    # 3. StartRecordResult.error remains valid and unaffected
    res = StartRecordResult(
        control_pid=123,
        control_return_code=0,
        control_exited=True,
        record_pid=124,
        query_status_text="OK",
        recording_active=True,
        stdout_log="",
        stderr_log="",
        error="Real error field"
    )
    assert res.error == "Real error field"

@patch("awr2944_dca.capture_cli.sys.exit", side_effect=SystemExit)
def test_preflight_stops_after_first_failed_dca_operation(mock_exit):
    # Setup mocks
    lab = MagicMock()
    toolchain = {"dca_cli_control_exe": "dummy", "dca_cli_cf_json": "dummy"}
    lab.capture._load_toolchain.return_value = toolchain
    
    dca_cli = MagicMock()
    dca_cli._control_exe.resolve.return_value = "c_exe"
    dca_cli._control_exe.exists.return_value = True
    dca_cli._record_exe.resolve.return_value = "r_exe"
    dca_cli._record_exe.exists.return_value = True
    dca_cli._cf_json.resolve.return_value = "c_json"
    dca_cli._cf_json.exists.return_value = True
    dca_cli._working_dir.resolve.return_value = "wd"
    
    lab.capture._build_dca_cli.return_value = dca_cli
    
    # Preflight fails on reset
    dca_cli.reset_fpga.return_value = create_mock_result(success=False)
    
    with pytest.raises(SystemExit):
        run_dca_preflight(lab)
    
    # 4. preflight stops after the first failed DCA operation
    mock_exit.assert_called_once_with(1)
    
    # 5. configure_fpga is not called after reset failure
    dca_cli.configure_fpga.assert_not_called()
    
    # 6. configure_record is not called after FPGA configuration failure
    dca_cli.configure_record.assert_not_called()
    
    # 8. Attempt safe stop_record cleanup
    dca_cli.stop_record.assert_called_once()
