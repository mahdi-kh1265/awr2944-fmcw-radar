import re

with open('src/awr2944_dca/mmws/gui_connect.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_attach = r'''def attach_mmwave_studio(
    pid: int | None = None,
    title_regex: str | None = None,
    probe_dir: Path | None = None,
    verbose_log: Callable[[str], None] | None = None,
):
    """Attach to a running mmWaveStudio.exe via pywinauto UIA backend.

    Attach strategies (in order):
    1. If pid is given, attach directly by PID (with pre-flight validation).
    2. Otherwise, enumerate Windows candidates via PowerShell and auto-resolve
       if exactly one unambiguous mmWave Studio visible window is found.

    Returns (Application, top_window).
    Raises RuntimeError with descriptive messages on failure.
    Always writes ti/probe_logs/gui_connect_windows.txt on failure.
    """
    vlog = verbose_log or (lambda s: None)
    if probe_dir is None:
        probe_dir = Path("ti") / "probe_logs"
    probe_dir.mkdir(parents=True, exist_ok=True)

    try:
        from pywinauto import Application  # type: ignore[import-untyped]
    except ImportError:
        raise RuntimeError(
            "pywinauto is not installed. Install with: "
            "python -m pip install -e \".[automation]\""
        )

    ps_cands = _get_powershell_candidates(verbose_log=vlog)
    
    # Helper for formatting candidates
    def format_cands(cands) -> str:
        if not cands:
            return "  (No candidates found)"
        return "\n".join(
            f"  PID={c.get('Id')}  Name={c.get('ProcessName')}  "
            f"Handle={c.get('MainWindowHandle')}  Title={c.get('MainWindowTitle', '')!r}"
            for c in cands
        )
    
    # Optional elevation helper for the exact hint
    def check_elevation(test_pid: int) -> None:
        if _is_process_elevated(test_pid) and not _is_admin():
            raise RuntimeError(
                "If mmWave Studio was launched as Administrator, this PowerShell terminal must also be run as Administrator."
            )

    target_pid: int | None = pid

    if target_pid is not None:
        vlog(f"Attaching directly by PID={target_pid}")
        target_cand = next((c for c in ps_cands if c.get("Id") == target_pid), None)
        
        if target_cand is not None and target_cand.get("MainWindowHandle", 0) == 0:
            raise RuntimeError(
                f"UIA attach failed for PID={target_pid}:\n"
                f"No windows for that process could be found (MainWindowHandle == 0).\n"
                f"Verify the PID is correct and mmWave Studio is running.\n\n"
                f"Candidate processes:\n{format_cands(ps_cands)}\n\n"
                f"If mmWave Studio was launched as Administrator, this PowerShell terminal must also be run as Administrator."
            )
            
        check_elevation(target_pid)
        
        try:
            app = Application(backend="uia").connect(process=target_pid, timeout=10)
            main_window = app.top_window()
            vlog(f"Attached to PID={target_pid}: {main_window.window_text()!r}")
            # Write standard diagnostics (for backwards compat logging)
            candidates = _enumerate_uia_windows(verbose_log=vlog)
            for c in candidates:
                if c.pid == target_pid:
                    c.matched = True
                    c.attach_ok = True
            _write_window_diagnostics(candidates, probe_dir, vlog)
            return app, main_window
        except Exception as e:
            # Write diagnostics on failure too
            candidates = _enumerate_uia_windows(verbose_log=vlog)
            _write_window_diagnostics(candidates, probe_dir, vlog)
            raise RuntimeError(
                f"UIA attach failed for PID={target_pid}: {e}. "
                "Verify the PID is correct and mmWave Studio is running.\n"
                "If mmWave Studio was launched as Administrator, this PowerShell terminal must also be run as Administrator."
            )

    # --- Auto-resolve ---
    visible_cands = [c for c in ps_cands if c.get("MainWindowHandle", 0) != 0]
    
    if len(visible_cands) == 1:
        target_pid = visible_cands[0].get("Id")
        vlog(f"Auto-resolved unambiguous PID={target_pid}")
        check_elevation(target_pid)
        try:
            app = Application(backend="uia").connect(process=target_pid, timeout=10)
            main_window = app.top_window()
            vlog(f"Attached to PID={target_pid}: {main_window.window_text()!r}")
            # Write standard diagnostics
            candidates = _enumerate_uia_windows(verbose_log=vlog)
            for c in candidates:
                if c.pid == target_pid:
                    c.matched = True
                    c.attach_ok = True
            _write_window_diagnostics(candidates, probe_dir, vlog)
            return app, main_window
        except Exception as e:
            candidates = _enumerate_uia_windows(verbose_log=vlog)
            _write_window_diagnostics(candidates, probe_dir, vlog)
            raise RuntimeError(
                f"UIA attach failed for PID={target_pid}: {e}. "
                "Verify the PID is correct and mmWave Studio is running.\n"
                "If mmWave Studio was launched as Administrator, this PowerShell terminal must also be run as Administrator."
            )
    elif len(visible_cands) == 0:
        raise RuntimeError(
            f"Could not auto-resolve mmWave Studio PID: No visible candidate processes found.\n\n"
            f"Candidate processes:\n{format_cands(ps_cands)}\n\n"
            f"Try running with explicit --pid <PID>."
        )
    else:
        raise RuntimeError(
            f"Could not auto-resolve mmWave Studio PID: Multiple visible candidate processes found.\n\n"
            f"Candidate processes:\n{format_cands(ps_cands)}\n\n"
            f"Please rerun with an explicit: --pid <PID>"
        )
'''

content = re.sub(r'def attach_mmwave_studio\(.*?(?=\n# -{70}|\Z)', new_attach + '\n', content, flags=re.DOTALL)

with open('src/awr2944_dca/mmws/gui_connect.py', 'w', encoding='utf-8') as f:
    f.write(content)