import re

with open('src/awr2944_dca/mmws/guided_runner.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_watch = '''def watch_run_sync(run_id: str, timeout: int, probe_dir: str) -> bool:
    \"\"\"Wrapper around mmws_post_watch_run that catches SystemExit/typer.Exit.\"\"\"
    from ..cli import mmws_post_watch_run
    import typer
    try:
        mmws_post_watch_run(run_id=run_id, timeout=timeout, probe_dir=probe_dir)
        return True
    except (SystemExit, typer.Exit) as e:
        code = getattr(e, 'code', getattr(e, 'exit_code', 1))
        return code == 0'''

new_watch = '''def watch_run_sync(run_id: str, timeout: int, probe_dir: str) -> bool:
    \"\"\"Wrapper around watch_run_impl that catches SystemExit/typer.Exit.\"\"\"
    from ..cli import watch_run_impl
    import typer
    try:
        watch_run_impl(run_id=run_id, timeout=timeout, probe_dir=probe_dir)
        return True
    except (SystemExit, typer.Exit) as e:
        code = getattr(e, 'code', getattr(e, 'exit_code', 1))
        return code == 0'''
content = content.replace(old_watch, new_watch)

old_sum = '''def summarize_session_sync(firmware_run_id: str, config_run_id: str) -> bool:
    \"\"\"Wrapper around summarize_session logic.\"\"\"
    from ..cli import mmws_post_summarize_session
    import typer
    try:
        mmws_post_summarize_session(firmware_run_id=firmware_run_id, config_run_id=config_run_id)
        return True
    except (SystemExit, typer.Exit) as e:
        code = getattr(e, 'code', getattr(e, 'exit_code', 1))
        return code == 0'''

new_sum = '''def summarize_session_sync(firmware_run_id: str, config_run_id: str, probe_dir: str) -> bool:
    \"\"\"Wrapper around summarize_session logic.\"\"\"
    from ..cli import summarize_session_impl
    import typer
    try:
        summarize_session_impl(firmware_run_id=firmware_run_id, config_run_id=config_run_id, probe_dir=probe_dir)
        return True
    except (SystemExit, typer.Exit) as e:
        code = getattr(e, 'code', getattr(e, 'exit_code', 1))
        return code == 0'''
content = content.replace(old_sum, new_sum)

old_rec = '''def record_validation_sync(firmware_run_id: str, config_run_id: str, label: str):
    from ..cli import mmws_post_record_validation
    import typer
    try:
        mmws_post_record_validation(firmware_run_id=firmware_run_id, config_run_id=config_run_id, label=label)
        return True
    except (SystemExit, typer.Exit) as e:
        code = getattr(e, 'code', getattr(e, 'exit_code', 1))
        return code == 0'''

new_rec = '''def record_validation_sync(firmware_run_id: str, config_run_id: str, label: str, probe_dir: str):
    from ..cli import record_validation_impl
    import typer
    try:
        record_validation_impl(firmware_run_id=firmware_run_id, config_run_id=config_run_id, label=label, probe_dir=probe_dir)
        return True
    except (SystemExit, typer.Exit) as e:
        code = getattr(e, 'code', getattr(e, 'exit_code', 1))
        return code == 0'''
content = content.replace(old_rec, new_rec)

old_step_sum = '''def step_summarize(state: GuidedWorkflowState, dry_run: bool):
    if dry_run:
        console.print("[yellow]DRY-RUN: Would summarize session[/yellow]")
        return
        
    console.print("[cyan]Running summarize-session...[/cyan]")
    ok = summarize_session_sync(state.firmware_run_id, state.config_run_id)'''
new_step_sum = '''def step_summarize(state: GuidedWorkflowState, dry_run: bool):
    if dry_run:
        console.print("[yellow]DRY-RUN: Would summarize session[/yellow]")
        return
        
    console.print("[cyan]Running summarize-session...[/cyan]")
    probe_dir = str(Path(state.state_path).parent) if state.state_path else None
    ok = summarize_session_sync(state.firmware_run_id, state.config_run_id, probe_dir)'''
content = content.replace(old_step_sum, new_step_sum)

old_step_rec = '''def step_record(state: GuidedWorkflowState, dry_run: bool):
    if dry_run:
        console.print("[yellow]DRY-RUN: Would record validation[/yellow]")
        return
        
    console.print("[cyan]Running record-validation...[/cyan]")
    ok = record_validation_sync(state.firmware_run_id, state.config_run_id, state.label)'''
new_step_rec = '''def step_record(state: GuidedWorkflowState, dry_run: bool):
    if dry_run:
        console.print("[yellow]DRY-RUN: Would record validation[/yellow]")
        return
        
    console.print("[cyan]Running record-validation...[/cyan]")
    probe_dir = str(Path(state.state_path).parent) if state.state_path else None
    ok = record_validation_sync(state.firmware_run_id, state.config_run_id, state.label, probe_dir)'''
content = content.replace(old_step_rec, new_step_rec)

with open('src/awr2944_dca/mmws/guided_runner.py', 'w', encoding='utf-8') as f:
    f.write(content)