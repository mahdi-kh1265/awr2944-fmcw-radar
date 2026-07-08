import json

new_tests = '''
# ---------------------------------------------------------------------------
# UIA Attach PID Diagnostics Tests
# ---------------------------------------------------------------------------

import awr2944_dca.mmws.gui_connect as gc

def test_uia_attach_no_candidates(monkeypatch):
    monkeypatch.setattr(gc, "_get_powershell_candidates", lambda **kw: [])
    with pytest.raises(RuntimeError, match="No visible candidate processes found"):
        gc.attach_mmwave_studio(pid=None, probe_dir=Path("ti/probe_logs"))

def test_uia_attach_multiple_visible_candidates(monkeypatch):
    cands = [
        {"Id": 100, "ProcessName": "mmWaveStudio", "MainWindowHandle": 1234, "MainWindowTitle": "mmWave Studio"},
        {"Id": 200, "ProcessName": "mmWaveStudio", "MainWindowHandle": 5678, "MainWindowTitle": "mmWave Studio"},
    ]
    monkeypatch.setattr(gc, "_get_powershell_candidates", lambda **kw: cands)
    with pytest.raises(RuntimeError, match="Multiple visible candidate processes found"):
        gc.attach_mmwave_studio(pid=None, probe_dir=Path("ti/probe_logs"))

def test_uia_attach_pid_with_no_window(monkeypatch):
    cands = [
        {"Id": 999, "ProcessName": "mmWaveStudio", "MainWindowHandle": 0, "MainWindowTitle": ""},
    ]
    monkeypatch.setattr(gc, "_get_powershell_candidates", lambda **kw: cands)
    with pytest.raises(RuntimeError) as exc:
        gc.attach_mmwave_studio(pid=999, probe_dir=Path("ti/probe_logs"))
    
    assert "No windows for that process could be found (MainWindowHandle == 0)" in str(exc.value)
    assert "If mmWave Studio was launched as Administrator" in str(exc.value)
    assert "PID=999" in str(exc.value)

def test_uia_attach_one_visible_candidate_proceeds(monkeypatch):
    cands = [
        {"Id": 123, "ProcessName": "mmWaveStudio", "MainWindowHandle": 0, "MainWindowTitle": ""},
        {"Id": 456, "ProcessName": "mmWaveStudio", "MainWindowHandle": 9876, "MainWindowTitle": "mmWave Studio"},
    ]
    monkeypatch.setattr(gc, "_get_powershell_candidates", lambda **kw: cands)
    monkeypatch.setattr(gc, "_is_process_elevated", lambda pid: False)
    
    class DummyWindow:
        def window_text(self): return "mmWave Studio dummy"
        
    class DummyApp:
        def top_window(self): return DummyWindow()
        
    class DummyApplication:
        def __init__(self, backend): pass
        def connect(self, process, timeout):
            assert process == 456
            return DummyApp()
            
    # We must patch pywinauto.Application inside gui_connect if it's imported locally
    import sys
    class DummyPywinauto:
        Application = DummyApplication
    sys.modules["pywinauto"] = DummyPywinauto()
    
    # We also must mock _enumerate_uia_windows so it doesn't fail
    monkeypatch.setattr(gc, "_enumerate_uia_windows", lambda **kw: [])
    
    try:
        app, win = gc.attach_mmwave_studio(pid=None, probe_dir=Path("ti/probe_logs"))
        assert isinstance(app, DummyApp)
    finally:
        del sys.modules["pywinauto"]

def test_uia_attach_powershell_fail(monkeypatch):
    def fake_subprocess_check_output(*args, **kwargs):
        raise RuntimeError("Powershell failed")
        
    import subprocess
    monkeypatch.setattr(subprocess, "check_output", fake_subprocess_check_output)
    
    cands = gc._get_powershell_candidates()
    assert cands == []
'''

with open('tests/test_run_tools.py', 'a', encoding='utf-8') as f:
    f.write(new_tests)