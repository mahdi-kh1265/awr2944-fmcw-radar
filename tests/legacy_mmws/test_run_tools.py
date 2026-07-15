import pytest
pytestmark = pytest.mark.legacy_mmws
import pytest
import subprocess
import tempfile
from pathlib import Path
import json
import uuid

def test_check_run_firmware_success(tmp_path):
    run_id = "testfwok"
    manifest = {
        "run_id": run_id,
        "stage": "firmware_power",
        "lua_path": str(tmp_path / f"{run_id}_fw.lua"),
        "result_path": str(tmp_path / f"{run_id}_fw_result.json"),
        "progress_path": str(tmp_path / f"{run_id}_fw_progress.jsonl")
    }
    (tmp_path / f"{run_id}_manifest.json").write_text(json.dumps(manifest))
    
    (tmp_path / f"{run_id}_fw_result.json").write_text(json.dumps({"success": True}))
    
    prog_lines = [
        {"ts": "0.0", "cmd": "DownloadBSSFw", "ret": 0, "ok": True},
        {"ts": "0.1", "cmd": "GetBSSFwVersion", "ret": "02.04.05.03 (20/04/22", "ok": True},
        {"ts": "0.2", "cmd": "RfEnable", "ret": 0, "ok": True}
    ]
    with open(tmp_path / f"{run_id}_fw_progress.jsonl", "w") as f:
        for p in prog_lines:
            f.write(json.dumps(p) + "\n")
            
    # Mock _lua_launch_probe_dir to return tmp_path by monkeypatching or setting an env var?
    # Actually, we can run awr cli with a monkeypatch on the probe dir, or just use the python entrypoint.
    # For a subprocess test, we'll just run it against the real script but we need the CLI to look at tmp_path.
    # Let's use monkeypatch in a direct function call instead of subprocess.
    from awr2944_dca.cli import mmws_post_check_run, _lua_launch_probe_dir
    import awr2944_dca.cli
    
    original_probe = awr2944_dca.cli._lua_launch_probe_dir
    awr2944_dca.cli._lua_launch_probe_dir = lambda override=None: tmp_path
    try:
        # Should not raise any Exit(1)
        mmws_post_check_run(run_id=run_id)
    finally:
        awr2944_dca.cli._lua_launch_probe_dir = original_probe


def test_check_run_firmware_failure(tmp_path):
    run_id = "testfwfail"
    manifest = {
        "run_id": run_id,
        "stage": "firmware_power",
        "result_path": str(tmp_path / f"{run_id}_fw_result.json"),
        "progress_path": str(tmp_path / f"{run_id}_fw_progress.jsonl")
    }
    (tmp_path / f"{run_id}_manifest.json").write_text(json.dumps(manifest))
    
    (tmp_path / f"{run_id}_fw_result.json").write_text(json.dumps({"success": False, "error": "RfEnable failed: -1"}))
    
    prog_lines = [
        {"ts": "0.0", "cmd": "DownloadBSSFw", "ret": 0, "ok": True},
        {"ts": "0.2", "cmd": "RfEnable", "ret": -1, "ok": True} # -1 numeric return for critical command
    ]
    with open(tmp_path / f"{run_id}_fw_progress.jsonl", "w") as f:
        for p in prog_lines:
            f.write(json.dumps(p) + "\n")
            
    from awr2944_dca.cli import mmws_post_check_run
    import awr2944_dca.cli
    
    original_probe = awr2944_dca.cli._lua_launch_probe_dir
    awr2944_dca.cli._lua_launch_probe_dir = lambda override=None: tmp_path
    try:
        mmws_post_check_run(run_id=run_id)
    finally:
        awr2944_dca.cli._lua_launch_probe_dir = original_probe


def test_check_run_smoke_success(tmp_path):
    run_id = "testsmk"
    manifest = {
        "run_id": run_id,
        "stage": "smoke_known_awr2944",
        "result_path": str(tmp_path / f"{run_id}_smk_result.json"),
        "progress_path": str(tmp_path / f"{run_id}_smk_progress.jsonl")
    }
    (tmp_path / f"{run_id}_manifest.json").write_text(json.dumps(manifest))
    
    (tmp_path / f"{run_id}_smk_result.json").write_text(json.dumps({"success": True}))
    
    prog_lines = [
        {"ts": "0.0", "cmd": "ChanNAdcConfig", "ret": 0, "ok": True},
        {"ts": "0.1", "cmd": "ProfileConfig", "ret": 0, "ok": True},
    ]
    with open(tmp_path / f"{run_id}_smk_progress.jsonl", "w") as f:
        for p in prog_lines:
            f.write(json.dumps(p) + "\n")
            
    from awr2944_dca.cli import mmws_post_check_run
    import awr2944_dca.cli
    
    original_probe = awr2944_dca.cli._lua_launch_probe_dir
    awr2944_dca.cli._lua_launch_probe_dir = lambda override=None: tmp_path
    try:
        mmws_post_check_run(run_id=run_id)
    finally:
        awr2944_dca.cli._lua_launch_probe_dir = original_probe


def test_watch_run_timeout(tmp_path):
    run_id = "testwait"
    manifest = {
        "run_id": run_id,
        "stage": "smoke_known_awr2944",
        "result_path": str(tmp_path / f"{run_id}_wait_result.json"),
        "progress_path": str(tmp_path / f"{run_id}_wait_progress.jsonl")
    }
    (tmp_path / f"{run_id}_manifest.json").write_text(json.dumps(manifest))
    
    # Do NOT write result JSON, so it times out.
    
    from awr2944_dca.cli import mmws_post_watch_run
    import awr2944_dca.cli
    import typer
    
    original_probe = awr2944_dca.cli._lua_launch_probe_dir
    awr2944_dca.cli._lua_launch_probe_dir = lambda override=None: tmp_path
    try:
        with pytest.raises(typer.Exit) as e:
            # Short timeout to make test fast
            mmws_post_watch_run(run_id=run_id, timeout=1)
        assert e.value.exit_code == 1
    finally:
        awr2944_dca.cli._lua_launch_probe_dir = original_probe

def test_watch_run_success(tmp_path):
    run_id = "testwaitok"
    manifest = {
        "run_id": run_id,
        "stage": "smoke_known_awr2944",
        "result_path": str(tmp_path / f"{run_id}_wait_result.json"),
        "progress_path": str(tmp_path / f"{run_id}_wait_progress.jsonl")
    }
    (tmp_path / f"{run_id}_manifest.json").write_text(json.dumps(manifest))
    
    (tmp_path / f"{run_id}_wait_result.json").write_text(json.dumps({"success": True}))
    
    from awr2944_dca.cli import mmws_post_watch_run
    import awr2944_dca.cli
    import typer
    
    original_probe = awr2944_dca.cli._lua_launch_probe_dir
    awr2944_dca.cli._lua_launch_probe_dir = lambda override=None: tmp_path
    try:
        with pytest.raises(SystemExit) as e:
            mmws_post_watch_run(run_id=run_id, timeout=2)
        assert e.value.code == 0
    finally:
        awr2944_dca.cli._lua_launch_probe_dir = original_probe

def test_watch_run_mismatch_reconciliation(tmp_path):
    run_id = "testmismatch"
    manifest = {
        "run_id": run_id,
        "stage": "smoke_known_awr2944",
        "result_path": str(tmp_path / f"{run_id}_wait_result.json"),
        "progress_path": str(tmp_path / f"{run_id}_wait_progress.jsonl")
    }
    (tmp_path / f"{run_id}_manifest.json").write_text(json.dumps(manifest))
    
    # Simulates what happened with run 68222a75: result JSON is present and says success, but timeout hits
    (tmp_path / f"{run_id}_wait_result.json").write_text(json.dumps({"success": True}))
    
    from awr2944_dca.cli import mmws_post_watch_run
    import awr2944_dca.cli
    import typer
    
    original_probe = awr2944_dca.cli._lua_launch_probe_dir
    awr2944_dca.cli._lua_launch_probe_dir = lambda override=None: tmp_path
    try:
        with pytest.raises(SystemExit) as e:
            # We set timeout=0 so the while loop immediately exits, which triggers the final reconciliation fallback.
            mmws_post_watch_run(run_id=run_id, timeout=0)
        assert e.value.code == 0
    finally:
        awr2944_dca.cli._lua_launch_probe_dir = original_probe

def test_guided_summary_option_leak(tmp_path, monkeypatch):
    from awr2944_dca.legacy_mmws.guided_runner import step_summarize, step_record, GuidedWorkflowState
    from pathlib import Path

    # Monkeypatch the impls
    import awr2944_dca.cli as cli
    
    summarize_called = []
    def mock_summarize_impl(firmware_run_id, config_run_id, probe_dir=None):
        summarize_called.append(probe_dir)
        # probe_dir must be string or None or Path, NOT OptionInfo
        assert getattr(probe_dir, '__class__', None).__name__ != 'OptionInfo'
    
    record_called = []
    def mock_record_impl(firmware_run_id, config_run_id, label, probe_dir=None):
        record_called.append(probe_dir)
        assert getattr(probe_dir, '__class__', None).__name__ != 'OptionInfo'

    monkeypatch.setattr(cli, 'summarize_session_impl', mock_summarize_impl)
    monkeypatch.setattr(cli, 'record_validation_impl', mock_record_impl)

    state = GuidedWorkflowState(
        workflow_id="testopt",
        label="Option leak test",
        pid=None,
        state_path=str(tmp_path / "guided_testopt_state.json"),
        firmware_run_id="fwok",
        config_run_id="cfgok",
        current_stage="config_validated",
    )
    
    # Run summarize
    step_summarize(state, dry_run=False)
    assert len(summarize_called) == 1
    assert summarize_called[0] == str(tmp_path)
    
    # Run record
    step_record(state, dry_run=False)
    assert len(record_called) == 1
    assert record_called[0] == str(tmp_path)

# ---------------------------------------------------------------------------
# UIA Attach PID Diagnostics Tests
# ---------------------------------------------------------------------------

import awr2944_dca.legacy_mmws.gui_connect as gc

def test_uia_attach_no_candidates(monkeypatch):
    """Auto-resolve with no candidates raises with clear message."""
    monkeypatch.setattr(gc, "_get_powershell_candidates", lambda **kw: [])
    with pytest.raises(RuntimeError, match="No visible strong candidate processes found"):
        gc.attach_mmwave_studio(pid=None, probe_dir=Path("ti/probe_logs"))

def test_uia_attach_multiple_strong_visible_candidates(monkeypatch):
    """Auto-resolve with multiple strong visible candidates refuses."""
    cands = [
        {"Id": 100, "ProcessName": "mmWaveStudio", "MainWindowHandle": 1234, "MainWindowTitle": "mmWave Studio"},
        {"Id": 200, "ProcessName": "mmWaveStudio", "MainWindowHandle": 5678, "MainWindowTitle": "mmWave Studio"},
    ]
    monkeypatch.setattr(gc, "_get_powershell_candidates", lambda **kw: cands)
    with pytest.raises(RuntimeError, match="Multiple visible strong candidate"):
        gc.attach_mmwave_studio(pid=None, probe_dir=Path("ti/probe_logs"))

def test_uia_attach_pid_with_no_window(monkeypatch):
    """Explicit PID with MainWindowHandle == 0 rejects immediately with diagnostics."""
    cands = [
        {"Id": 999, "ProcessName": "mmWaveStudio", "MainWindowHandle": 0, "MainWindowTitle": ""},
    ]
    monkeypatch.setattr(gc, "_get_powershell_candidates", lambda **kw: cands)
    with pytest.raises(RuntimeError) as exc:
        gc.attach_mmwave_studio(pid=999, probe_dir=Path("ti/probe_logs"))

    assert "No windows for that process could be found (MainWindowHandle == 0)" in str(exc.value)
    assert "If mmWave Studio was launched as Administrator" in str(exc.value)
    assert "PID=999" in str(exc.value)

def test_uia_attach_one_strong_visible_candidate_proceeds(monkeypatch):
    """Auto-resolve succeeds when exactly one strong visible candidate exists.

    Uses app.windows() instead of top_window() — the proven minimal sequence.
    """
    cands = [
        {"Id": 123, "ProcessName": "mmWaveStudio", "MainWindowHandle": 0, "MainWindowTitle": ""},
        {"Id": 456, "ProcessName": "mmWaveStudio", "MainWindowHandle": 9876, "MainWindowTitle": "mmWave Studio"},
    ]
    monkeypatch.setattr(gc, "_get_powershell_candidates", lambda **kw: cands)
    monkeypatch.setattr(gc, "_is_process_elevated", lambda pid: False)

    class DummyWindow:
        handle = 9876
        def window_text(self): return "mmWave Studio 3.1.4.4"

    class DummyApp:
        def windows(self): return [DummyWindow()]
        def window(self, handle=None): return DummyWindow()

    class DummyApplication:
        def __init__(self, backend): pass
        def connect(self, process=None, handle=None, timeout=None):
            return DummyApp()

    import sys
    class DummyPywinauto:
        Application = DummyApplication
    sys.modules["pywinauto"] = DummyPywinauto()

    try:
        app, win = gc.attach_mmwave_studio(pid=None, probe_dir=Path("ti/probe_logs"))
        assert isinstance(app, DummyApp)
        assert win.window_text() == "mmWave Studio 3.1.4.4"
    finally:
        del sys.modules["pywinauto"]

def test_uia_attach_weak_candidates_dont_block_auto_resolve(monkeypatch):
    """Chrome/IDE windows with 'radar' in title should NOT block auto-resolve
    when exactly one strong mmWaveStudio candidate exists."""
    cands = [
        {"Id": 111, "ProcessName": "chrome", "MainWindowHandle": 5555, "MainWindowTitle": "radar docs - Chrome"},
        {"Id": 222, "ProcessName": "Code", "MainWindowHandle": 6666, "MainWindowTitle": "awr2944-fmcw-radar - VS Code"},
        {"Id": 333, "ProcessName": "mmWaveStudio", "MainWindowHandle": 7777, "MainWindowTitle": "mmWave Studio 3.1.4.4"},
    ]
    monkeypatch.setattr(gc, "_get_powershell_candidates", lambda **kw: cands)
    monkeypatch.setattr(gc, "_is_process_elevated", lambda pid: False)

    class DummyWindow:
        handle = 7777
        def window_text(self): return "mmWave Studio 3.1.4.4"

    class DummyApp:
        def windows(self): return [DummyWindow()]
        def window(self, handle=None): return DummyWindow()

    class DummyApplication:
        def __init__(self, backend): pass
        def connect(self, process=None, handle=None, timeout=None):
            assert process == 333 or handle == 7777
            return DummyApp()

    import sys
    class DummyPywinauto:
        Application = DummyApplication
    sys.modules["pywinauto"] = DummyPywinauto()

    try:
        app, win = gc.attach_mmwave_studio(pid=None, probe_dir=Path("ti/probe_logs"))
        assert isinstance(app, DummyApp)
        assert win.window_text() == "mmWave Studio 3.1.4.4"
    finally:
        del sys.modules["pywinauto"]

def test_uia_attach_explicit_pid_uses_windows_not_top_window(monkeypatch):
    """Regression test for the real contradiction: connect(process=pid).windows()
    returns windows, but the old top_window() call would have failed. The new code
    must succeed because it uses app.windows() instead of app.top_window()."""
    cands = [
        {"Id": 12012, "ProcessName": "mmWaveStudio", "MainWindowHandle": 1119094,
         "MainWindowTitle": "mmWave Studio 3.1.4.4"},
    ]
    monkeypatch.setattr(gc, "_get_powershell_candidates", lambda **kw: cands)
    monkeypatch.setattr(gc, "_is_process_elevated", lambda pid: False)

    class DummyWindow:
        handle = 1119094
        def window_text(self): return "mmWave Studio 3.1.4.4"

    class DummyApp:
        def windows(self): return [DummyWindow()]
        def window(self, handle=None): return DummyWindow()
        def top_window(self):
            # This is what the OLD code called — it would throw
            raise RuntimeError("No windows for that process could be found")

    class DummyApplication:
        def __init__(self, backend): pass
        def connect(self, process=None, handle=None, timeout=None):
            return DummyApp()

    import sys
    class DummyPywinauto:
        Application = DummyApplication
    sys.modules["pywinauto"] = DummyPywinauto()

    try:
        # This MUST succeed — the fix is using app.windows() not top_window()
        app, win = gc.attach_mmwave_studio(pid=12012, probe_dir=Path("ti/probe_logs"))
        assert win.window_text() == "mmWave Studio 3.1.4.4"
        assert win.handle == 1119094
    finally:
        del sys.modules["pywinauto"]

def test_uia_attach_powershell_fail(monkeypatch):
    """PowerShell failure should return empty list, not crash."""
    def fake_subprocess_check_output(*args, **kwargs):
        raise RuntimeError("Powershell failed")

    import subprocess
    monkeypatch.setattr(subprocess, "check_output", fake_subprocess_check_output)

    cands = gc._get_powershell_candidates()
    assert cands == []

def test_strong_candidate_classification():
    """Verify _is_strong_candidate correctly classifies processes."""
    assert gc._is_strong_candidate(
        {"ProcessName": "mmWaveStudio", "MainWindowTitle": ""}
    ) is True
    assert gc._is_strong_candidate(
        {"ProcessName": "RSTD", "MainWindowTitle": ""}
    ) is True
    assert gc._is_strong_candidate(
        {"ProcessName": "RadarStudio", "MainWindowTitle": ""}
    ) is True
    assert gc._is_strong_candidate(
        {"ProcessName": "MmwsRstdBridge", "MainWindowTitle": ""}
    ) is True
    assert gc._is_strong_candidate(
        {"ProcessName": "someapp", "MainWindowTitle": "mmWave Studio 3.1.4.4"}
    ) is True
    # Weak: Chrome with radar in title
    assert gc._is_strong_candidate(
        {"ProcessName": "chrome", "MainWindowTitle": "radar docs - Chrome"}
    ) is False
    # Weak: VS Code with radar in title
    assert gc._is_strong_candidate(
        {"ProcessName": "Code", "MainWindowTitle": "awr2944-fmcw-radar - VS Code"}
    ) is False


# ---------------------------------------------------------------------------
# Manual Check Diagnostics & Override Tests
# ---------------------------------------------------------------------------

def test_manual_check_empty_extraction_includes_diagnostics():
    """When Device Status extraction returns empty, error message must
    include diagnostic details, not just 'Found: ''.  """
    class DummyWindow:
        def child_window(self, **kw):
            class NullCtrl:
                def exists(self, timeout=None): return False
                def wrapper_object(self): return self
            return NullCtrl()
        def descendants(self): return []

    result = gc.manual_check(DummyWindow(), probe_dir=Path("ti/probe_logs"))
    assert result.status == "MANUAL_CONNECTION_NOT_VALID"
    assert "Device Status extraction returned empty string" in result.error
    assert "m_ConsoleText found:" in result.error
    assert "Snapshot:" in result.error


def test_read_device_status_console_text_fallback():
    """m_ConsoleText containing a Device Status line should be extracted."""
    console_text = (
        "mmWave Studio initialized\n"
        "Board detected\n"
        "Device Status : AWR2944/GP/ASIL-B/SOP:2/ES:2.0\n"
        "Ready\n"
    )

    class DummyOutputDoc:
        def window_text(self):
            return console_text

    class DummyControls:
        device_status_label = None
        output_document = DummyOutputDoc()
        rs232_status_label = None
        spi_status_label = None

    class DummyWindow:
        def child_window(self, **kw):
            class NullCtrl:
                def exists(self, timeout=None): return False
            return NullCtrl()
        def descendants(self): return []

    result = gc.read_device_status(DummyWindow(), DummyControls())
    assert result["valid"] is True
    assert result["device"] == "AWR2944"
    assert result["type"] == "GP"
    assert result["sop"] == "2"
    assert result["_extraction"]["extraction_source"] == "console_text"


def test_read_device_status_descendants_fallback():
    """When m_ConsoleText is empty, descendants search should find Device Status."""
    class DummyChild:
        def window_text(self):
            return "Device Status : AWR2944/GP/ASIL-B/SOP:2/ES:2.0"
        def automation_id(self):
            return "some_hidden_control"

    class DummyControls:
        device_status_label = None
        output_document = None
        rs232_status_label = None
        spi_status_label = None

    class DummyWindow:
        def child_window(self, **kw):
            class NullCtrl:
                def exists(self, timeout=None): return False
            return NullCtrl()
        def descendants(self):
            return [DummyChild()]

    result = gc.read_device_status(DummyWindow(), DummyControls())
    assert result["valid"] is True
    assert result["device"] == "AWR2944"
    assert result["_extraction"]["extraction_source"] == "descendants"
    assert result["_extraction"]["descendants_searched"] is True


def test_manual_override_records_state(tmp_path):
    """--assume-manual-connected should record override in state and not fail."""
    from awr2944_dca.legacy_mmws.guided_runner import step_manual_check, GuidedWorkflowState

    state = GuidedWorkflowState(
        workflow_id="override_test",
        label="Test override",
        pid=None,
        state_path=str(tmp_path / "state.json"),
        current_stage="created",
    )

    step_manual_check(state, pid=None, dry_run=False, assume_manual_connected=True)

    assert state.manual_connection_override is True
    assert state.manual_connection_source == "user_confirmed"


def test_manual_override_does_not_mark_hardware_touched(tmp_path):
    """Manual override by itself should not mark hardware_touched=True."""
    from awr2944_dca.legacy_mmws.guided_runner import step_manual_check, GuidedWorkflowState

    state = GuidedWorkflowState(
        workflow_id="hw_test",
        label="Hardware test",
        pid=None,
        state_path=str(tmp_path / "state.json"),
        current_stage="created",
    )

    step_manual_check(state, pid=None, dry_run=False, assume_manual_connected=True)

    assert state.hardware_touched is False


def test_manual_override_still_requires_firmware_validation(tmp_path, monkeypatch):
    """After manual override, firmware validation must still run (not be skipped)."""
    from awr2944_dca.legacy_mmws.guided_runner import (
        GuidedWorkflowState, step_manual_check, step_preflight_firmware
    )

    state = GuidedWorkflowState(
        workflow_id="fw_test",
        label="FW validation test",
        pid=None,
        state_path=str(tmp_path / "state.json"),
        current_stage="created",
        manual_connection_override=True,
        manual_connection_source="user_confirmed",
    )

    # Override should pass
    step_manual_check(state, pid=None, dry_run=False, assume_manual_connected=True)
    assert state.manual_connection_override is True

    # Firmware preflight should still run (and fail because audit is None)
    with pytest.raises(Exception):
        step_preflight_firmware(state, audit=None, dry_run=False, assume_manual_connected=True)


def test_find_by_auto_id_uiawrapper_fallback():
    """When root has no child_window (UIAWrapper), descendants fallback should find controls."""
    class DummyChild:
        def automation_id(self):
            return "m_ConsoleText"
        def window_text(self):
            return "Some console output text"

    class DummyOtherChild:
        def automation_id(self):
            return "m_unrelated"
        def window_text(self):
            return "unrelated"

    class UIAWrapperLike:
        """Mock UIAWrapper-like object: has descendants() but NOT child_window()."""
        def descendants(self):
            return [DummyOtherChild(), DummyChild()]

    # Must NOT have child_window
    root = UIAWrapperLike()
    assert not hasattr(root, 'child_window')

    result = gc._find_by_auto_id(root, "m_ConsoleText")
    assert result is not None
    assert result.window_text() == "Some console output text"


def test_find_by_auto_id_no_attribute_error():
    """_find_by_auto_id must never raise AttributeError for missing child_window."""
    class UIAWrapperLike:
        def descendants(self):
            return []

    root = UIAWrapperLike()
    assert not hasattr(root, 'child_window')

    # Should return None, not raise AttributeError
    result = gc._find_by_auto_id(root, "m_btnSetSop")
    assert result is None


def test_manual_status_probe_no_attribute_error():
    """manual_status_probe must not produce 'UIAWrapper has no attribute child_window'."""
    class DummyChild:
        def automation_id(self):
            return "m_ConsoleText"
        def window_text(self):
            return "Device Status : AWR2944/GP/ASIL-B/SOP:2/ES:2.0"

    class DummyWindow:
        """Has child_window (WindowSpecification-like)."""
        handle = 12345
        def window_text(self):
            return "mmWave Studio 3.1.4.4"
        def child_window(self, **kw):
            class NullCtrl:
                def exists(self, timeout=None): return False
                def wrapper_object(self): return self
            return NullCtrl()
        def descendants(self):
            return [DummyChild()]

    log_messages = []
    result = gc.manual_status_probe(
        DummyWindow(), probe_dir=Path("ti/probe_logs"),
        verbose_log=lambda m: log_messages.append(m)
    )

    # Must not contain the old error
    for msg in log_messages:
        assert "'UIAWrapper' object has no attribute 'child_window'" not in msg

    assert result["window_title"] == "mmWave Studio 3.1.4.4"


def test_override_bypasses_rs232_gate_in_preflight(tmp_path):
    """--assume-manual-connected should bypass RS232 identity gate in preflight."""
    from awr2944_dca.legacy_mmws.guided_runner import step_preflight_firmware, GuidedWorkflowState
    from awr2944_dca.legacy_mmws.post_connect import SessionAudit

    state = GuidedWorkflowState(
        workflow_id="gate_test",
        label="RS232 gate bypass test",
        pid=None,
        state_path=str(tmp_path / "state.json"),
        current_stage="created",
        manual_connection_override=True,
    )

    # Audit with rs232_valid=False — would normally fail preflight
    audit = SessionAudit(rs232_valid=False)

    # Without override: should fail
    from awr2944_dca.legacy_mmws.post_connect import preflight_firmware
    passed, reasons = preflight_firmware(audit)
    assert not passed
    assert any("RS232 identity gate" in r for r in reasons)

    # With override in step_preflight_firmware: should pass
    # (the step filters out the RS232 reason)
    step_preflight_firmware(state, audit=audit, dry_run=False, assume_manual_connected=True)
    assert state.rs232_identity_gate_override is True


def test_preflight_strict_without_override(tmp_path):
    """Without override, RS232 identity gate failure must block firmware generation."""
    from awr2944_dca.legacy_mmws.guided_runner import step_preflight_firmware, GuidedWorkflowState
    from awr2944_dca.legacy_mmws.post_connect import SessionAudit

    state = GuidedWorkflowState(
        workflow_id="strict_test",
        label="Strict preflight test",
        pid=None,
        state_path=str(tmp_path / "state.json"),
        current_stage="created",
    )

    audit = SessionAudit(rs232_valid=False)

    with pytest.raises(RuntimeError, match="Firmware preflight failed"):
        step_preflight_firmware(state, audit=audit, dry_run=False, assume_manual_connected=False)


def test_override_does_not_mask_other_preflight_failures(tmp_path):
    """Override should not mask non-RS232 preflight failures like firmware already attempted."""
    from awr2944_dca.legacy_mmws.guided_runner import step_preflight_firmware, GuidedWorkflowState
    from awr2944_dca.legacy_mmws.post_connect import SessionAudit

    state = GuidedWorkflowState(
        workflow_id="mask_test",
        label="Mask test",
        pid=None,
        state_path=str(tmp_path / "state.json"),
        current_stage="created",
        manual_connection_override=True,
    )

    # Both RS232 invalid AND firmware already attempted
    audit = SessionAudit(rs232_valid=False, firmware_power_already_attempted=True)

    with pytest.raises(RuntimeError, match="even with override"):
        step_preflight_firmware(state, audit=audit, dry_run=False, assume_manual_connected=True)
