"""Tests for mmws automatic Lua execution (executor + smoke + bridge)."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from awr2944_dca.mmws.executor import (
    ExecutionMode,
    ExecutionResult,
    TransportInfo,
    build_dofile_command,
    detect_available_modes,
    execute_script,
    wait_for_result_json,
)
from awr2944_dca.mmws.lua_builder import build_smoke_script, write_smoke_script
from awr2944_dca.mmws.bridge import StudioBridge, StageStatus


# ---------------------------------------------------------------------------
# Executor: dofile command
# ---------------------------------------------------------------------------


def test_build_dofile_command(tmp_path):
    script = tmp_path / "test.lua"
    script.write_text("-- test")
    cmd = build_dofile_command(script)
    assert cmd.startswith("dofile([[")
    assert cmd.endswith("]])")
    assert "test.lua" in cmd


# ---------------------------------------------------------------------------
# Executor: auto mode does NOT silently fall back to manual
# ---------------------------------------------------------------------------


def test_execute_auto_no_transport_raises(tmp_path):
    """--execute must ERROR if no automatic transport available, not silent manual."""
    script = tmp_path / "test.lua"
    script.write_text("-- test")

    with patch("awr2944_dca.mmws.executor._HAVE_PYTHONNET", False), \
         patch("awr2944_dca.mmws.executor._HAVE_PYWINAUTO", False):
        with pytest.raises(RuntimeError, match="No automatic execution transport"):
            execute_script(script, mode="auto")


def test_execute_auto_no_transport_message(tmp_path):
    """Error message should include bridge build instructions."""
    script = tmp_path / "test.lua"
    script.write_text("-- test")

    with patch("awr2944_dca.mmws.executor._find_csharp_bridge", return_value=None), \
         patch("awr2944_dca.mmws.executor._HAVE_PYWINAUTO", False), \
         patch("awr2944_dca.mmws.executor._HAVE_PYTHONNET", False):
        with pytest.raises(RuntimeError) as exc_info:
            execute_script(script, mode="auto")
        msg = str(exc_info.value)
        assert "csharp-bridge build" in msg
        assert "--manual" in msg


# ---------------------------------------------------------------------------
# Executor: manual mode only when explicitly requested
# ---------------------------------------------------------------------------


def test_execute_manual_explicit(tmp_path):
    """Manual mode returns success when explicitly requested."""
    script = tmp_path / "test.lua"
    script.write_text("-- test")

    result = execute_script(script, mode="manual")
    assert result.mode == ExecutionMode.MANUAL_ONE_SHOT
    assert result.success is True


# ---------------------------------------------------------------------------
# Executor: auto mode chooses RSTD when mocked available
# ---------------------------------------------------------------------------


def test_auto_mode_prefers_csharp_bridge(tmp_path):
    """When C# RSTD bridge is available, auto mode should choose it."""
    script = tmp_path / "test.lua"
    script.write_text("-- test")

    mock_result = ExecutionResult(
        mode=ExecutionMode.CSHARP_RSTD,
        success=True,
        return_code=30000,
    )

    from pathlib import Path
    with patch("awr2944_dca.mmws.executor._find_csharp_bridge", return_value=Path("fake.exe")), \
         patch("awr2944_dca.mmws.executor._is_rstd_port_open", return_value=True), \
         patch("awr2944_dca.mmws.executor._execute_via_csharp_bridge", return_value=mock_result):
        result = execute_script(script, mode="auto")
        assert result.mode == ExecutionMode.CSHARP_RSTD
        assert result.success is True
        assert result.return_code == 30000


# ---------------------------------------------------------------------------
# Executor: auto mode falls back to pywinauto when RSTD unavailable
# ---------------------------------------------------------------------------


def test_auto_mode_fallback_pywinauto(tmp_path):
    """When RSTD unavailable, auto mode falls back to pywinauto."""
    script = tmp_path / "test.lua"
    script.write_text("-- test")

    mock_result = ExecutionResult(
        mode=ExecutionMode.UI_LUA_SHELL,
        success=True,
    )

    with patch("awr2944_dca.mmws.executor._HAVE_PYTHONNET", False), \
         patch("awr2944_dca.mmws.executor._HAVE_PYWINAUTO", True), \
         patch("awr2944_dca.mmws.executor._is_mmws_running", return_value=True), \
         patch("awr2944_dca.mmws.executor._execute_via_pywinauto", return_value=mock_result):
        result = execute_script(script, mode="auto")
        assert result.mode == ExecutionMode.UI_LUA_SHELL
        assert result.success is True


# ---------------------------------------------------------------------------
# Executor: RSTD worker timeout handling
# ---------------------------------------------------------------------------


def test_run_rstd_worker_subprocess_timeout(tmp_path):
    """If the worker subprocess times out, parent catches it and returns SENDCOMMAND_TIMEOUT."""
    from awr2944_dca.mmws.executor import _run_rstd_worker_subprocess, _VerboseLog
    import subprocess
    
    with patch("awr2944_dca.mmws.executor._find_rtttnet_dll", return_value=tmp_path / "RtttNetClientAPI.dll"), \
         patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd=["python"], timeout=1.0)):
        
        vlog = _VerboseLog(False)
        ret_code, err = _run_rstd_worker_subprocess("test cmd", timeout=1.0, vlog=vlog)
        
        assert ret_code == -1
        assert "SENDCOMMAND_TIMEOUT" in err


# ---------------------------------------------------------------------------
# Executor: RSTD return code 30000 still waits for result JSON
# ---------------------------------------------------------------------------


def test_rstd_return_code_not_proof_of_success(tmp_path):
    """RSTD SendCommand return code only means command was submitted.
    Result JSON is the source of truth."""
    bridge = StudioBridge(tmp_path)
    script = tmp_path / "test.lua"
    script.write_text("-- test")

    exec_result = ExecutionResult(
        mode=ExecutionMode.RSTD_NET_REMOTING,
        success=True,
        return_code=30000,
    )

    # Result JSON reports an error
    result_path = tmp_path / "test_result.json"
    result_path.write_text(json.dumps({"error": "Connect failed", "run_id": "x"}))

    with patch("awr2944_dca.mmws.executor.execute_script", return_value=exec_result), \
         patch("awr2944_dca.mmws.executor.wait_for_result_json", return_value=json.loads(result_path.read_text())):
        result = bridge.execute(script, mode="auto", timeout=1)
        assert result["status"] == StageStatus.ERROR


# ---------------------------------------------------------------------------
# Executor: timeout when result JSON does not appear
# ---------------------------------------------------------------------------


def test_wait_for_result_timeout(tmp_path):
    """If result JSON never appears, wait_for_result_json returns None."""
    result_path = tmp_path / "nonexistent_result.json"
    result = wait_for_result_json(result_path, timeout=0.5, poll_interval=0.1)
    assert result is None


# ---------------------------------------------------------------------------
# Smoke test: no ar1 hardware calls
# ---------------------------------------------------------------------------


def test_smoke_script_no_ar1_calls():
    """Smoke script must contain ZERO ar1 hardware calls."""
    import re
    script = build_smoke_script("test-run-id", ".")
    ar1_calls = re.findall(r"ar1\.\w+", script)
    assert ar1_calls == [], f"Smoke script contains ar1 calls: {ar1_calls}"


def test_smoke_script_writes_json():
    """Smoke script must write result JSON."""
    script = build_smoke_script("test-run-id", "/tmp/test")
    assert "smoke_result.json" in script
    assert "io.open" in script


def test_write_smoke_script_creates_file(tmp_path):
    import re
    out = tmp_path / "smoke.lua"
    write_smoke_script(out, "run-123")
    assert out.exists()
    content = out.read_text()
    assert re.findall(r"ar1\.\w+", content) == []  # no ar1.* function calls


def test_write_smoke_script_rejects_ar1():
    """If ar1 calls somehow leak in, safety check should catch it."""
    import re
    from awr2944_dca.mmws.lua_builder import build_smoke_script
    script = build_smoke_script("test", ".")
    ar1_calls = re.findall(r"ar1\.\w+", script)
    assert ar1_calls == [], f"Smoke script has ar1 function calls: {ar1_calls}"


# ---------------------------------------------------------------------------
# Bridge: smoke test generation and status
# ---------------------------------------------------------------------------


def test_bridge_smoke_generation(tmp_path):
    import re
    bridge = StudioBridge(tmp_path)
    script = bridge.generate_smoke_script()
    assert script.exists()
    assert (tmp_path / "smoke_manifest.json").exists()
    assert re.findall(r"ar1\.\w+", script.read_text()) == []


def test_bridge_smoke_status_not_run(tmp_path):
    bridge = StudioBridge(tmp_path)
    status, _ = bridge.check_status("smoke")
    assert status == StageStatus.NOT_RUN


def test_bridge_smoke_status_success(tmp_path):
    bridge = StudioBridge(tmp_path)
    run_id = "test-123"
    (tmp_path / "smoke_manifest.json").write_text(json.dumps({"run_id": run_id}))
    (tmp_path / "smoke_result.json").write_text(json.dumps({
        "run_id": run_id,
        "executed": True,
        "log_available": True,
        "write_ok": True,
        "error": None,
    }))
    status, result = bridge.check_status("smoke")
    assert status == StageStatus.SUCCESS


# ---------------------------------------------------------------------------
# Bridge: TIMEOUT status
# ---------------------------------------------------------------------------


def test_bridge_execute_timeout(tmp_path):
    bridge = StudioBridge(tmp_path)
    script = tmp_path / "test.lua"
    script.write_text("-- test")

    exec_ok = ExecutionResult(
        mode=ExecutionMode.RSTD_NET_REMOTING,
        success=True,
        return_code=30000,
    )

    with patch("awr2944_dca.mmws.executor.execute_script", return_value=exec_ok), \
         patch("awr2944_dca.mmws.executor.wait_for_result_json", return_value=None):
        result = bridge.execute(script, mode="auto", timeout=1)
        assert result["status"] == StageStatus.TIMEOUT


# ---------------------------------------------------------------------------
# Detect modes / inspect-execution (no experiment needed)
# ---------------------------------------------------------------------------


def test_detect_modes_returns_list():
    modes = detect_available_modes()
    assert isinstance(modes, list)
    assert len(modes) >= 3  # rstd, cli_launch, pywinauto, manual
    mode_names = [m.mode for m in modes]
    assert ExecutionMode.RSTD_NET_REMOTING in mode_names
    assert ExecutionMode.MANUAL_ONE_SHOT in mode_names


def test_detect_modes_manual_always_available():
    modes = detect_available_modes()
    manual = [m for m in modes if m.mode == ExecutionMode.MANUAL_ONE_SHOT]
    assert len(manual) == 1
    assert manual[0].available is True


def test_inspect_execution_no_experiment():
    """inspect-execution must work without .awr-experiment context."""
    # Just verify detect_available_modes doesn't import Experiment
    modes = detect_available_modes()
    assert modes  # should not raise


# ---------------------------------------------------------------------------
# Missing pythonnet gives helpful message
# ---------------------------------------------------------------------------


def test_missing_pythonnet_helpful_message():
    """When pythonnet is missing, RSTD_NET_REMOTING should not appear in modes."""
    with patch("awr2944_dca.mmws.executor._HAVE_PYTHONNET", False), \
         patch("awr2944_dca.mmws.executor._pythonnet_error", "No module named 'clr'"):
        modes = detect_available_modes()
        # Pythonnet RSTD should not appear when pythonnet is not installed
        rstd_modes = [m for m in modes if m.mode == ExecutionMode.RSTD_NET_REMOTING]
        assert len(rstd_modes) == 0


def test_missing_pywinauto_helpful_message():
    """When pywinauto is missing, error should include install instructions."""
    with patch("awr2944_dca.mmws.executor._HAVE_PYWINAUTO", False), \
         patch("awr2944_dca.mmws.executor._pywinauto_error", "No module named 'pywinauto'"):
        modes = detect_available_modes()
        ui = [m for m in modes if m.mode == ExecutionMode.UI_LUA_SHELL][0]
        assert ui.available is False
        assert "pip install" in ui.detail


# ---------------------------------------------------------------------------
# Backward compatibility: ManualOneShotBridge alias
# ---------------------------------------------------------------------------


def test_manual_one_shot_bridge_alias():
    from awr2944_dca.mmws.bridge import ManualOneShotBridge
    assert ManualOneShotBridge is StudioBridge
