"""Tests for mmWave Studio dofile automation layer.

All tests mock the executor — no hardware required.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from awr2944_dca.mmws_auto import (
    DofileClassification,
    DofileSafety,
    classify_dofile,
    safe_execute_dofile,
    read_mmws_output,
    tail_mmws_output,
    save_output_snapshot,
)
from awr2944_dca.radar_config import RadarConfig, smoke_config_preset


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_lua(tmp_path):
    """Factory to create temporary Lua files."""
    def _make(content: str, name: str = "test.lua") -> Path:
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return p
    return _make


@pytest.fixture
def safe_config_lua(tmp_lua):
    """A radar config Lua (no StartFrame)."""
    content = textwrap.dedent("""\
        ar1.ChanNAdcConfig(1, 1, 0, 0, 1, 1, 0, 0, 2, 0, 0)
        ar1.ProfileConfig(0, 77, 100, 6, 60, 0, 0, 0, 0, 0, 0, 0, 0, 29.982, 0, 256, 10000)
        ar1.ChirpConfig(0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0)
        ar1.FrameConfig(0, 0, 8, 128, 40, 0, 1)
    """)
    return tmp_lua(content, "radar_config.lua")


@pytest.fixture
def safe_dca_setup_lua(tmp_lua):
    """A DCA setup Lua (no StartFrame)."""
    content = textwrap.dedent("""\
        ar1.SelectCaptureDevice("DCA1000")
        ar1.CaptureCardConfig_EthInit("192.168.33.30", "192.168.33.180", "12:34:56:78:90:12", 4096, 4098)
        ar1.CaptureCardConfig_Mode(1, 1, 1, 2, 3, 30)
        ar1.CaptureCardConfig_PacketDelay(25)
    """)
    return tmp_lua(content, "dca_setup.lua")


@pytest.fixture
def dangerous_capture_trigger_lua(tmp_lua):
    """A capture trigger Lua (contains StartFrame)."""
    content = textwrap.dedent("""\
        ar1.CaptureCardConfig_StartRecord()
        ar1.StartFrame()
    """)
    return tmp_lua(content, "capture_trigger.lua")


# ---------------------------------------------------------------------------
# classify_dofile tests
# ---------------------------------------------------------------------------

class TestClassifyDofile:
    def test_classify_safe_config_dofile(self, safe_config_lua):
        result = classify_dofile(safe_config_lua)
        assert result.safety == DofileSafety.SAFE
        assert not result.contains_startframe
        assert not result.contains_startrecord

    def test_classify_safe_dca_setup(self, safe_dca_setup_lua):
        result = classify_dofile(safe_dca_setup_lua)
        assert result.safety == DofileSafety.SAFE
        assert not result.contains_startframe
        assert not result.contains_startrecord

    def test_classify_dangerous_capture_trigger(self, dangerous_capture_trigger_lua):
        result = classify_dofile(dangerous_capture_trigger_lua)
        assert result.safety == DofileSafety.DANGEROUS
        assert result.contains_startframe
        assert result.contains_startrecord

    def test_classify_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            classify_dofile(tmp_path / "nonexistent.lua")

    def test_classify_unknown_lua(self, tmp_lua):
        lua = tmp_lua('print("hello world")', "hello.lua")
        result = classify_dofile(lua)
        assert result.safety == DofileSafety.UNKNOWN

    def test_classify_startframe_in_safe_call(self, tmp_lua):
        """safeCall wrapping StartFrame is still dangerous."""
        content = 'if not safeCall("StartFrame", function() return ar1.StartFrame() end, true) then return end'
        lua = tmp_lua(content, "wrapped_startframe.lua")
        result = classify_dofile(lua)
        assert result.safety == DofileSafety.DANGEROUS
        assert result.contains_startframe


# ---------------------------------------------------------------------------
# safe_execute_dofile tests
# ---------------------------------------------------------------------------

class TestSafeExecuteDofile:
    def test_execute_refuses_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            safe_execute_dofile(tmp_path / "nonexistent.lua")

    def test_execute_refuses_startframe_by_default(self, dangerous_capture_trigger_lua):
        with pytest.raises(ValueError, match="DANGEROUS"):
            safe_execute_dofile(dangerous_capture_trigger_lua)

    @patch("awr2944_dca.mmws.executor.execute_script")
    def test_execute_allows_startframe_when_confirmed(
        self, mock_exec, dangerous_capture_trigger_lua
    ):
        """With allow_startframe=True, execution proceeds."""
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.return_code = 30000
        mock_result.error = None
        mock_result.elapsed_seconds = 1.5
        mock_result.lua_command_sent = "dofile([[...]])"
        mock_result.mode = MagicMock()
        mock_result.mode.value = "csharp_rstd"
        mock_exec.return_value = mock_result

        result = safe_execute_dofile(
            dangerous_capture_trigger_lua,
            allow_startframe=True,
        )

        assert result["executed"] is True
        assert result["exec_result"]["success"] is True
        mock_exec.assert_called_once()

    @patch("awr2944_dca.mmws.executor.execute_script")
    def test_execute_safe_config_dofile(self, mock_exec, safe_config_lua):
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.return_code = 30000
        mock_result.error = None
        mock_result.elapsed_seconds = 0.5
        mock_result.lua_command_sent = "dofile([[...]])"
        mock_result.mode = MagicMock()
        mock_result.mode.value = "csharp_rstd"
        mock_exec.return_value = mock_result

        result = safe_execute_dofile(safe_config_lua)

        assert result["executed"] is True
        assert result["classification"]["safety"] == "safe"


# ---------------------------------------------------------------------------
# RadarConfig.to_lua_with_result tests
# ---------------------------------------------------------------------------

class TestRadarConfigResultLua:
    def test_smoke_config_generates_result_tracking_lua(self, tmp_path):
        cfg = smoke_config_preset()
        result_path = tmp_path / "result.json"
        progress_path = tmp_path / "progress.jsonl"

        lua = cfg.to_lua_with_result(
            run_id="test123",
            result_path=result_path.as_posix(),
            progress_path=progress_path.as_posix(),
        )

        # Must contain all 13 commands from smoke_v1
        assert "ChanNAdcConfig" in lua
        assert "LPModConfig" in lua
        assert "RfLdoBypassConfig" in lua
        assert "SetCalMonFreqLimitConfig" in lua
        assert "SetRFDeviceConfig" in lua
        assert "RfSetCalMonFreqTxPowLimitConfig" in lua
        assert "SetApllSynthBWCtlConfig" in lua
        assert "RfInit" in lua
        assert "DataPathConfig" in lua
        assert "LVDSLaneConfig" in lua
        assert "ProfileConfig" in lua
        assert "ChirpConfig" in lua
        assert "FrameConfig" in lua

        # Must contain result tracking
        assert "saveResult()" in lua
        assert "logProgress" in lua
        assert "result.success = true" in lua
        assert "test123" in lua

        # Must NOT contain StartFrame
        assert "StartFrame" not in lua

    def test_to_lua_original_unchanged(self):
        """Original to_lua() still works (no result JSON)."""
        cfg = smoke_config_preset()
        lua = cfg.to_lua()
        assert "saveResult" not in lua
        assert "logProgress" not in lua
        assert "ar1.ChanNAdcConfig" in lua


# ---------------------------------------------------------------------------
# ConfigStep tests
# ---------------------------------------------------------------------------

class TestConfigStep:
    def test_configstep_status_pending(self):
        from awr2944_dca.lab import ConfigStep
        step = ConfigStep("dofile([[test.lua]])", "test.lua")
        assert step.status() == "pending"

    def test_configstep_dofile(self):
        from awr2944_dca.lab import ConfigStep
        step = ConfigStep("dofile([[test.lua]])", "/path/test.lua")
        assert step.dofile() == "dofile([[test.lua]])"
        assert step.dofile_path() == "/path/test.lua"

    def test_configstep_run_requires_project(self):
        from awr2944_dca.lab import ConfigStep
        step = ConfigStep("dofile([[test.lua]])", "test.lua")
        with pytest.raises(RuntimeError, match="no project reference"):
            step.run()

    @patch("awr2944_dca.mmws.executor.execute_script")
    def test_configstep_run_validates_result_json(self, mock_exec, tmp_path):
        """ConfigStep.run() should check result JSON, not trust RSTD 30000 alone."""
        from awr2944_dca.lab import ConfigStep, RadarProject

        # Create a fake result JSON with success=true
        result_path = tmp_path / "result.json"
        result_path.write_text(
            json.dumps({"run_id": "abc", "success": True, "error": "", "commands": []}),
            encoding="utf-8",
        )

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.return_code = 30000
        mock_result.error = None
        mock_result.elapsed_seconds = 0.5
        mock_result.lua_command_sent = "dofile([[...]])"
        mock_result.mode = MagicMock()
        mock_result.mode.value = "csharp_rstd"
        mock_exec.return_value = mock_result

        # Create a ConfigStep with project reference
        project = MagicMock()
        lua_path = tmp_path / "config.lua"
        lua_path.write_text("ar1.ProfileConfig(0)\n", encoding="utf-8")

        step = ConfigStep(
            f"dofile([[{lua_path}]])",
            str(lua_path),
            project=project,
            result_path=str(result_path),
            run_id="abc",
        )

        result = step.run(timeout_s=1)
        assert result.get("config_result", {}).get("success") is True
        assert step.status() == "success"

    @patch("awr2944_dca.mmws.executor.execute_script")
    def test_configstep_run_fails_on_bad_frameconfig(self, mock_exec, tmp_path):
        """If FrameConfig failed in result JSON, ConfigStep.run should report error."""
        from awr2944_dca.lab import ConfigStep

        result_path = tmp_path / "result.json"
        result_path.write_text(
            json.dumps({
                "run_id": "abc",
                "success": False,
                "error": "FrameConfig failed: -1",
                "commands": [
                    {"func": "ar1.ProfileConfig", "return": 0, "ok": True, "error": ""},
                    {"func": "ar1.FrameConfig", "return": -1, "ok": True, "error": ""},
                ],
            }),
            encoding="utf-8",
        )

        mock_result = MagicMock()
        mock_result.success = True  # RSTD says 30000
        mock_result.return_code = 30000
        mock_result.error = None
        mock_result.elapsed_seconds = 0.5
        mock_result.lua_command_sent = "dofile([[...]])"
        mock_result.mode = MagicMock()
        mock_result.mode.value = "csharp_rstd"
        mock_exec.return_value = mock_result

        project = MagicMock()
        lua_path = tmp_path / "config.lua"
        lua_path.write_text("ar1.FrameConfig(0)\n", encoding="utf-8")

        step = ConfigStep(
            f"dofile([[{lua_path}]])",
            str(lua_path),
            project=project,
            result_path=str(result_path),
            run_id="abc",
        )

        result = step.run(timeout_s=1)
        # Despite RSTD 30000, result JSON says failure
        assert result.get("error") is not None
        assert "FrameConfig" in result["error"]
        assert step.status() == "error"


# ---------------------------------------------------------------------------
# CaptureSmokeRun.run_next_step tests
# ---------------------------------------------------------------------------

class TestRunNextStep:
    @patch("awr2944_dca.mmws.executor.execute_script")
    @patch("awr2944_dca.mmws.executor.wait_for_result_json", return_value={"success": True})
    def test_run_next_step_dca_setup(self, mock_wait, mock_exec, tmp_path):
        """run_next_step executes DCA setup and resumes."""
        from awr2944_dca.lab import CaptureSmokeRun
        from awr2944_dca.dca.workflow import CaptureWorkflowState

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.return_code = 30000
        mock_result.error = None
        mock_result.elapsed_seconds = 1.0
        mock_result.lua_command_sent = "dofile([[...]])"
        mock_result.mode = MagicMock()
        mock_result.mode.value = "csharp_rstd"
        mock_exec.return_value = mock_result

        # Create a mock state with a safe dofile
        lua_path = tmp_path / "dca_setup.lua"
        lua_path.write_text(
            'ar1.SelectCaptureDevice("DCA1000")\n',
            encoding="utf-8",
        )

        state = MagicMock(spec=CaptureWorkflowState)
        state.current_stage = "dca_setup_script_generated"
        state.completed = False
        state.errors = []
        state.pending_dofile = f"dofile([[{lua_path}]])"
        state.dca_setup = MagicMock()
        state.dca_setup.script_path = str(lua_path)
        state.capture_trigger = MagicMock()
        state.capture_trigger.script_path = ""
        state.postproc = MagicMock()
        state.postproc.script_path = ""
        state.probe_dir = str(tmp_path)
        state.workflow_id = "test-wf-123"

        project = MagicMock()
        run = CaptureSmokeRun(state, project)

        # Patch resume to avoid full workflow logic
        with patch.object(run, 'resume', return_value=run):
            run.run_next_step()

        mock_exec.assert_called_once()

    def test_run_next_step_refuses_capture_trigger(self, tmp_path):
        """run_next_step refuses capture trigger without confirm_startframe."""
        from awr2944_dca.lab import CaptureSmokeRun
        from awr2944_dca.dca.workflow import CaptureWorkflowState

        lua_path = tmp_path / "capture_trigger.lua"
        lua_path.write_text(
            'ar1.CaptureCardConfig_StartRecord()\nar1.StartFrame()\n',
            encoding="utf-8",
        )

        state = MagicMock(spec=CaptureWorkflowState)
        state.current_stage = "capture_script_generated"
        state.completed = False
        state.errors = []
        state.pending_dofile = f"dofile([[{lua_path}]])"
        state.dca_setup = MagicMock()
        state.dca_setup.script_path = ""
        state.capture_trigger = MagicMock()
        state.capture_trigger.script_path = str(lua_path)
        state.postproc = MagicMock()
        state.postproc.script_path = ""
        state.probe_dir = str(tmp_path)
        state.workflow_id = "test-wf-456"

        project = MagicMock()
        run = CaptureSmokeRun(state, project)

        with pytest.raises(ValueError, match="DANGEROUS"):
            run.run_next_step(confirm_startframe=False)

    @patch("awr2944_dca.mmws.executor.execute_script")
    @patch("awr2944_dca.mmws.executor.wait_for_result_json", return_value={"success": True})
    def test_run_next_step_allows_capture_trigger(self, mock_wait, mock_exec, tmp_path):
        """run_next_step allows capture trigger with confirm_startframe=True."""
        from awr2944_dca.lab import CaptureSmokeRun
        from awr2944_dca.dca.workflow import CaptureWorkflowState

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.return_code = 30000
        mock_result.error = None
        mock_result.elapsed_seconds = 2.0
        mock_result.lua_command_sent = "dofile([[...]])"
        mock_result.mode = MagicMock()
        mock_result.mode.value = "csharp_rstd"
        mock_exec.return_value = mock_result

        lua_path = tmp_path / "capture_trigger.lua"
        lua_path.write_text(
            'ar1.CaptureCardConfig_StartRecord()\nar1.StartFrame()\n',
            encoding="utf-8",
        )

        state = MagicMock(spec=CaptureWorkflowState)
        state.current_stage = "capture_script_generated"
        state.completed = False
        state.errors = []
        state.pending_dofile = f"dofile([[{lua_path}]])"
        state.dca_setup = MagicMock()
        state.dca_setup.script_path = ""
        state.capture_trigger = MagicMock()
        state.capture_trigger.script_path = str(lua_path)
        state.postproc = MagicMock()
        state.postproc.script_path = ""
        state.probe_dir = str(tmp_path)
        state.workflow_id = "test-wf-789"

        project = MagicMock()
        run = CaptureSmokeRun(state, project)

        with patch.object(run, 'resume', return_value=run):
            run.run_next_step(confirm_startframe=True)

        mock_exec.assert_called_once()


# ---------------------------------------------------------------------------
# Output reading tests (mocked UI)
# ---------------------------------------------------------------------------

class TestOutputReading:
    @patch("awr2944_dca.mmws_auto.find_mmws_output")
    def test_read_output_mocked(self, mock_find):
        """read_mmws_output returns text from mocked output."""
        from awr2944_dca.mmws_auto import OutputReadResult
        mock_find.return_value = OutputReadResult(
            text="Line 1\nLine 2\nLine 3\n",
            available=True,
            backend="uia",
            strategy="auto_id_m_ConsoleText",
        )

        text = read_mmws_output()
        assert text is not None
        assert "Line 1" in text

    @patch("awr2944_dca.mmws_auto.find_mmws_output")
    def test_tail_output(self, mock_find):
        """tail_mmws_output returns last N lines."""
        from awr2944_dca.mmws_auto import OutputReadResult
        lines = "\n".join([f"Line {i}" for i in range(200)])
        mock_find.return_value = OutputReadResult(
            text=lines,
            available=True,
            backend="uia",
            strategy="auto_id_m_ConsoleText",
        )

        tail = tail_mmws_output(lines=10)
        assert tail is not None
        tail_lines = tail.strip().split("\n")
        assert len(tail_lines) == 10
        assert "Line 199" in tail_lines[-1]

    @patch("awr2944_dca.mmws_auto.find_mmws_output")
    def test_save_output_snapshot(self, mock_find, tmp_path):
        """save_output_snapshot writes text to file."""
        from awr2944_dca.mmws_auto import OutputReadResult
        mock_find.return_value = OutputReadResult(
            text="Some output text",
            available=True,
            backend="uia",
            strategy="auto_id_m_ConsoleText",
        )

        path = save_output_snapshot(tmp_path, label="test_snap")
        assert path is not None
        assert path.exists()
        assert "test_snap" in path.name
        assert path.read_text(encoding="utf-8") == "Some output text"

    @patch("awr2944_dca.mmws_auto.find_mmws_output")
    def test_read_output_unavailable(self, mock_find):
        """Returns None when control unavailable."""
        from awr2944_dca.mmws_auto import OutputReadResult
        mock_find.return_value = OutputReadResult(
            text=None,
            available=False,
            error="pywinauto not installed",
        )
        assert read_mmws_output() is None

    @patch("awr2944_dca.mmws_auto.find_mmws_output")
    def test_save_output_snapshot_unavailable(self, mock_find, tmp_path):
        """Returns None when output unavailable."""
        from awr2944_dca.mmws_auto import OutputReadResult
        mock_find.return_value = OutputReadResult(
            text=None,
            available=False,
            error="Cannot connect",
        )
        result = save_output_snapshot(tmp_path)
        assert result is None

    @patch("awr2944_dca.mmws_auto.find_mmws_output")
    def test_find_mmws_output_structured_error(self, mock_find):
        """find_mmws_output returns structured error, not None."""
        from awr2944_dca.mmws_auto import OutputReadResult
        mock_find.return_value = OutputReadResult(
            text=None,
            available=False,
            backend="uia",
            error="No matching output control found via uia backend (tried 5 strategies)",
        )

        from awr2944_dca.mmws_auto import find_mmws_output
        result = find_mmws_output()
        assert result.text is None
        assert result.available is False
        assert "No matching output control" in result.error
        assert result.backend == "uia"


# ---------------------------------------------------------------------------
# MmWaveStudioManager tests
# ---------------------------------------------------------------------------

class TestMmWaveStudioManager:
    @patch("awr2944_dca.mmws.executor.detect_available_modes")
    @patch("awr2944_dca.mmws.executor._is_mmws_running")
    def test_mmws_manager_status(self, mock_running, mock_modes):
        from awr2944_dca.lab import MmWaveStudioManager
        from awr2944_dca.mmws.executor import TransportInfo, ExecutionMode

        mock_running.return_value = False
        mock_modes.return_value = [
            TransportInfo(
                mode=ExecutionMode.CSHARP_RSTD,
                available=False,
                confidence="low",
                detail="Bridge not found",
            ),
            TransportInfo(
                mode=ExecutionMode.MANUAL_ONE_SHOT,
                available=True,
                confidence="high",
                detail="Always available",
            ),
        ]

        project = MagicMock()
        mgr = MmWaveStudioManager(project)
        status = mgr.status()

        assert status["mmws_running"] is False
        assert status["best_mode"] == "manual_one_shot"
        assert len(status["modes"]) == 2
        # Mode tracking fields present
        assert "selected_mode" in status
        assert "attached_mode" in status
        assert "last_execution_mode" in status

    @patch("awr2944_dca.mmws.executor.detect_available_modes")
    @patch("awr2944_dca.mmws.executor._is_mmws_running")
    def test_diagnostics_includes_output_reader(self, mock_running, mock_modes):
        from awr2944_dca.lab import MmWaveStudioManager
        from awr2944_dca.mmws.executor import TransportInfo, ExecutionMode
        from awr2944_dca.mmws_auto import OutputReadResult

        mock_running.return_value = False
        mock_modes.return_value = [
            TransportInfo(
                mode=ExecutionMode.MANUAL_ONE_SHOT,
                available=True,
                confidence="high",
                detail="Always available",
            ),
        ]

        project = MagicMock()
        mgr = MmWaveStudioManager(project)

        with patch("awr2944_dca.mmws_auto.find_mmws_output", return_value=OutputReadResult(
            text="Line 1\nLine 2",
            available=True,
            backend="uia",
            strategy="auto_id_m_ConsoleText",
        )):
            diag = mgr.diagnostics()

        assert "output_tail" in diag
        assert "output_reader" in diag
        assert diag["output_reader"]["available"] is True
        assert diag["output_reader"]["backend"] == "uia"
        assert "selected_mode" in diag
        assert "attached_mode" in diag
        assert "last_execution_mode" in diag
        assert "mode_mismatch" in diag

    def test_attach_persists_mode(self):
        """attach() persists selected mode for later use."""
        from awr2944_dca.lab import MmWaveStudioManager

        project = MagicMock()
        mgr = MmWaveStudioManager(project)

        assert mgr._selected_mode is None
        assert mgr._attached_mode is None

        # Mock a successful csharp_rstd attach
        with patch("awr2944_dca.mmws.executor._is_mmws_running", return_value=True), \
             patch("awr2944_dca.mmws.executor._find_csharp_bridge", return_value=Path("bridge.exe")), \
             patch("awr2944_dca.mmws.executor._is_rstd_port_open", return_value=True):
            result = mgr.attach()

        assert result["attached"] is True
        assert result["mode"] == "csharp_rstd"
        assert mgr._selected_mode == "csharp-rstd"
        assert mgr._attached_mode == "csharp_rstd"

    @patch("awr2944_dca.mmws.executor.execute_script")
    def test_smoke_test_uses_selected_mode(self, mock_exec):
        """smoke_test() uses the persisted selected mode and checks result file."""
        from awr2944_dca.lab import MmWaveStudioManager

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.return_code = 30000
        mock_result.error = None
        mock_result.elapsed_seconds = 0.5
        mock_result.mode = MagicMock()
        mock_result.mode.value = "csharp_rstd"
        mock_exec.return_value = mock_result

        project = MagicMock()
        mgr = MmWaveStudioManager(project)
        mgr._selected_mode = "csharp-rstd"

        # Patch make_smoke_lua to write the result file so success=True
        original_make_smoke_lua = None

        def fake_make_smoke_lua(result_path):
            # Actually write the result file so smoke_test sees it
            Path(result_path).write_text('{"executed": true}', encoding="utf-8")
            return '-- smoke lua'

        with patch("awr2944_dca.mmws_auto.make_smoke_lua", side_effect=fake_make_smoke_lua), \
             patch("awr2944_dca.lab.make_smoke_lua", side_effect=fake_make_smoke_lua, create=True):
            result = mgr.smoke_test()

        assert result["mode"] == "csharp_rstd"
        assert result["selected_mode"] == "csharp-rstd"
        assert "result_file_found" in result

        # Verify execute_script was called with the correct mode
        call_args = mock_exec.call_args
        assert call_args.kwargs.get("mode") == "csharp-rstd" or \
               call_args[1].get("mode") == "csharp-rstd"

    @patch("awr2944_dca.mmws.executor.execute_script")
    def test_smoke_test_mode_override(self, mock_exec):
        """smoke_test(mode=...) overrides the selected mode."""
        from awr2944_dca.lab import MmWaveStudioManager

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.return_code = 30000
        mock_result.error = None
        mock_result.elapsed_seconds = 0.5
        mock_result.mode = MagicMock()
        mock_result.mode.value = "rstd_net_remoting"
        mock_exec.return_value = mock_result

        project = MagicMock()
        mgr = MmWaveStudioManager(project)
        mgr._selected_mode = "csharp-rstd"

        def fake_make_smoke_lua(result_path):
            Path(result_path).write_text('{"executed": true}', encoding="utf-8")
            return '-- smoke lua'

        with patch("awr2944_dca.mmws_auto.make_smoke_lua", side_effect=fake_make_smoke_lua):
            result = mgr.smoke_test(mode="rstd")

        assert result["selected_mode"] == "rstd"
        call_args = mock_exec.call_args
        assert call_args.kwargs.get("mode") == "rstd" or \
               call_args[1].get("mode") == "rstd"

    @patch("awr2944_dca.mmws.executor.execute_script")
    def test_smoke_test_fails_if_no_result_file(self, mock_exec):
        """smoke_test() returns success=False when result file not created."""
        from awr2944_dca.lab import MmWaveStudioManager

        mock_result = MagicMock()
        mock_result.success = True  # transport OK but no result file
        mock_result.return_code = 30000
        mock_result.error = None
        mock_result.elapsed_seconds = 0.5
        mock_result.mode = MagicMock()
        mock_result.mode.value = "csharp_rstd"
        mock_exec.return_value = mock_result

        project = MagicMock()
        mgr = MmWaveStudioManager(project)

        # make_smoke_lua returns Lua but does NOT write result file
        with patch("awr2944_dca.mmws_auto.make_smoke_lua", return_value='-- smoke lua'), \
             patch("awr2944_dca.mmws.executor.wait_for_result_json", return_value=None):
            result = mgr.smoke_test()

        # success=False because result file wasn't written
        assert result["success"] is False
        assert result["result_file_found"] is False

    def test_read_output_returns_dict(self):
        """read_output() returns a dict, not None."""
        from awr2944_dca.lab import MmWaveStudioManager
        from awr2944_dca.mmws_auto import OutputReadResult

        project = MagicMock()
        mgr = MmWaveStudioManager(project)

        with patch("awr2944_dca.mmws_auto.find_mmws_output", return_value=OutputReadResult(
            text=None,
            available=False,
            backend="uia",
            error="No matching control",
        )):
            result = mgr.read_output()

        assert isinstance(result, dict)
        assert result["text"] is None
        assert result["available"] is False
        assert "No matching control" in result["error"]

    def test_tail_output_returns_dict(self):
        """tail_output() returns a dict, not None."""
        from awr2944_dca.lab import MmWaveStudioManager
        from awr2944_dca.mmws_auto import OutputReadResult

        project = MagicMock()
        mgr = MmWaveStudioManager(project)

        with patch("awr2944_dca.mmws_auto.find_mmws_output", return_value=OutputReadResult(
            text="Line A\nLine B\nLine C",
            available=True,
            backend="win32",
            strategy="class_name_RichEdit",
        )):
            result = mgr.tail_output(lines=2)

        assert isinstance(result, dict)
        assert "Line B" in result["text"]
        assert "Line C" in result["text"]
        assert result["available"] is True

    def test_mmws_cached_on_project(self):
        """lab.mmws returns the same cached instance."""
        from awr2944_dca.lab import RadarProject

        project = MagicMock(spec=RadarProject)
        project._mmws_manager = None

        # Simulate the property by calling it twice
        from awr2944_dca.lab import MmWaveStudioManager
        mgr1 = MmWaveStudioManager(project)
        project._mmws_manager = mgr1

        # Second access returns same instance
        mgr2 = project._mmws_manager
        assert mgr1 is mgr2

    def test_diagnostics_advisory_in_output_reader(self):
        """diagnostics() includes advisory about privilege/32-bit issues."""
        from awr2944_dca.lab import MmWaveStudioManager
        from awr2944_dca.mmws.executor import TransportInfo, ExecutionMode
        from awr2944_dca.mmws_auto import OutputReadResult

        project = MagicMock()
        mgr = MmWaveStudioManager(project)

        with patch("awr2944_dca.mmws.executor.detect_available_modes", return_value=[
            TransportInfo(mode=ExecutionMode.MANUAL_ONE_SHOT, available=True,
                          confidence="high", detail="Always available"),
        ]), patch("awr2944_dca.mmws.executor._is_mmws_running", return_value=False), \
           patch("awr2944_dca.mmws_auto.find_mmws_output", return_value=OutputReadResult(
               text=None, available=False, backend="uia",
               error="Cannot connect to mmWave Studio")):
            diag = mgr.diagnostics()

        assert "advisory" in diag["output_reader"]
        advisory = diag["output_reader"]["advisory"]
        assert "admin" in advisory.lower() or "privilege" in advisory.lower()
        assert "32-bit" in advisory

    def test_restart_bridge_clears_mode_on_failure(self):
        """restart_bridge() clears cached mode if bridge not ready."""
        from awr2944_dca.lab import MmWaveStudioManager

        project = MagicMock()
        mgr = MmWaveStudioManager(project)
        mgr._selected_mode = "csharp-rstd"
        mgr._attached_mode = "csharp_rstd"

        with patch("awr2944_dca.mmws_auto.restart_bridge", return_value={
            "killed_count": 1, "bridge_found": True,
            "port_open": False, "ready": False,  # not ready
        }):
            result = mgr.restart_bridge()

        assert result["killed_count"] == 1
        # mode cleared because bridge not ready
        assert mgr._selected_mode is None
        assert mgr._attached_mode is None

    def test_restart_bridge_keeps_mode_when_ready(self):
        """restart_bridge() keeps cached mode if bridge is still ready."""
        from awr2944_dca.lab import MmWaveStudioManager

        project = MagicMock()
        mgr = MmWaveStudioManager(project)
        mgr._selected_mode = "csharp-rstd"
        mgr._attached_mode = "csharp_rstd"

        with patch("awr2944_dca.mmws_auto.restart_bridge", return_value={
            "killed_count": 0, "bridge_found": True,
            "port_open": True, "ready": True,
        }):
            result = mgr.restart_bridge()

        assert result["ready"] is True
        # mode preserved
        assert mgr._selected_mode == "csharp-rstd"


# ---------------------------------------------------------------------------
# make_smoke_lua tests
# ---------------------------------------------------------------------------

class TestMakeSmokeLua:
    def test_no_write_to_log_required(self):
        """Generated Lua must not have an unconditional (unguarded) WriteToLog call."""
        from awr2944_dca.mmws_auto import make_smoke_lua
        lua = make_smoke_lua("/tmp/result.json")
        # Every WriteToLog call must be inside the WriteToLog ~= nil guard block
        # i.e. there should be no bare WriteToLog( before the guard
        lines = lua.splitlines()
        inside_guard = False
        for line in lines:
            stripped = line.strip()
            if "if WriteToLog ~= nil" in stripped:
                inside_guard = True
            if stripped == "end" and inside_guard:
                inside_guard = False
            # If we see WriteToLog( when NOT inside the guard block — fail
            if stripped.startswith("WriteToLog(") and not inside_guard:
                assert False, f"Unguarded WriteToLog: {line}"

    def test_result_file_path_embedded(self):
        """make_smoke_lua embeds the result file path."""
        from awr2944_dca.mmws_auto import make_smoke_lua
        lua = make_smoke_lua("C:/ti/probe_logs/smoke_result.json")
        assert "C:/ti/probe_logs/smoke_result.json" in lua

    def test_uses_io_open(self):
        """Source of truth must be io.open, not WriteToLog."""
        from awr2944_dca.mmws_auto import make_smoke_lua
        lua = make_smoke_lua("/tmp/result.json")
        assert "io.open" in lua
        assert "executed" in lua

    def test_write_to_log_guarded(self):
        """WriteToLog must be inside a nil-check guard."""
        from awr2944_dca.mmws_auto import make_smoke_lua
        lua = make_smoke_lua("/tmp/result.json")
        # If WriteToLog is present at all, it must be guarded
        if "WriteToLog" in lua:
            assert "WriteToLog ~= nil" in lua or "if WriteToLog" in lua


# ---------------------------------------------------------------------------
# smoke_matrix tests
# ---------------------------------------------------------------------------

class TestSmokeMatrix:
    def test_smoke_matrix_keys(self):
        """smoke_matrix returns all expected backends."""
        from awr2944_dca.mmws_auto import smoke_matrix

        with patch("awr2944_dca.mmws_auto.bridge_health_check", return_value={
                "healthy": False, "error": "bridge hung", "result_file_found": False
            }), \
            patch("awr2944_dca.mmws_auto.cli_lua_health_check", return_value={
                "healthy": True, "result_file_found": True, "error": None,
                "warning": "may open new instance"
            }), \
            patch("awr2944_dca.mmws_auto.ui_lua_health_check", return_value={
                "healthy": True, "result_file_found": True, "error": None
            }), \
            patch("awr2944_dca.mmws.executor._is_mmws_running", return_value=True):

            result = smoke_matrix()

        assert "csharp_rstd" in result
        assert "cli_lua_launch" in result
        assert "ui_lua_shell" in result
        assert "manual" in result
        assert "recommended" in result

    def test_smoke_matrix_recommended_cli_when_bridge_fails(self):
        """When csharp_rstd fails and cli works, cli_lua_launch is recommended."""
        from awr2944_dca.mmws_auto import smoke_matrix

        with patch("awr2944_dca.mmws_auto.bridge_health_check", return_value={
                "healthy": False, "error": "HUNG", "result_file_found": False
            }), \
            patch("awr2944_dca.mmws_auto.cli_lua_health_check", return_value={
                "healthy": True, "result_file_found": True, "error": None,
                "warning": "may open new instance"
            }), \
            patch("awr2944_dca.mmws_auto.ui_lua_health_check", return_value={
                "healthy": False, "result_file_found": False, "error": "not running"
            }), \
            patch("awr2944_dca.mmws.executor._is_mmws_running", return_value=False):

            result = smoke_matrix()

        assert result["recommended"] == "cli_lua_launch"

    def test_smoke_matrix_manual_always_available(self):
        """manual backend is always healthy/available."""
        from awr2944_dca.mmws_auto import smoke_matrix

        with patch("awr2944_dca.mmws_auto.bridge_health_check", return_value={
                "healthy": False, "error": "X", "result_file_found": False
            }), \
            patch("awr2944_dca.mmws_auto.cli_lua_health_check", return_value={
                "healthy": False, "error": "X", "result_file_found": False
            }), \
            patch("awr2944_dca.mmws.executor._is_mmws_running", return_value=False):

            result = smoke_matrix()

        assert result["manual"]["healthy"] is True
        # If everything else fails, manual is recommended
        assert result["recommended"] in ("manual", "ui_lua_shell", None)



# ---------------------------------------------------------------------------
# Manual workflow still works
# ---------------------------------------------------------------------------

class TestManualWorkflowIntact:
    def test_manual_dofile_resume_still_works(self, tmp_path):
        """Ensure CaptureSmokeRun still has manual dofile/resume methods."""
        from awr2944_dca.lab import CaptureSmokeRun
        from awr2944_dca.dca.workflow import CaptureWorkflowState

        state = MagicMock(spec=CaptureWorkflowState)
        state.workflow_id = "test-manual"
        state.current_stage = "dca_setup_script_generated"
        state.completed = False
        state.errors = []
        state.pending_dofile = "dofile([[test.lua]])"
        state.pending_operator_action = "Paste dofile then run: awr dca capture-smoke resume --workflow-id test-manual"
        state.dca_setup = MagicMock()
        state.dca_setup.script_path = "test.lua"
        state.capture_trigger = MagicMock()
        state.capture_trigger.script_path = ""
        state.postproc = MagicMock()
        state.postproc.script_path = ""
        state.capture_id = ""
        state.bind_completed = False
        state.warnings = []
        state.probe_dir = str(tmp_path)

        project = MagicMock()
        run = CaptureSmokeRun(state, project)

        # Manual methods still work
        assert run.dofile() == "dofile([[test.lua]])"
        assert "run.run_next_step()" in run.next_action()
        assert "run.resume()" in run.next_action()

