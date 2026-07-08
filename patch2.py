import sys
import re

with open('src/awr2944_dca/cli.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. check_run
check_run_sig = '''@mmws_post_app.command("check-run")
def mmws_post_check_run(
    run_id: str = typer.Option(..., "--run-id", help="Run ID to look up"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written"),
) -> None:
    \"\"\"Look up result and progress files for a run ID and summarize them.\"\"\"
    import json
    
    probe_dir_path = _lua_launch_probe_dir(probe_dir)'''

check_run_impl = '''def check_run_impl(run_id: str, probe_dir: str | None = None) -> None:
    import json
    probe_dir_path = _lua_launch_probe_dir(probe_dir)'''

check_run_wrapper = '''@mmws_post_app.command("check-run")
def mmws_post_check_run(
    run_id: str = typer.Option(..., "--run-id", help="Run ID to look up"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written"),
) -> None:
    \"\"\"Look up result and progress files for a run ID and summarize them.\"\"\"
    check_run_impl(run_id, probe_dir)'''

# Note: check_run uses probe_dir_path = _lua_launch_probe_dir(probe_dir). We just rename mmws_post_check_run to check_run_impl and add the wrapper.
old_check = '''@mmws_post_app.command("check-run")
def mmws_post_check_run(
    run_id: str = typer.Option(..., "--run-id", help="Run ID to look up"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written"),
) -> None:
    \"\"\"Look up result and progress files for a run ID and summarize them.\"\"\"'''

new_check = '''def check_run_impl(run_id: str, probe_dir: str = None) -> None:
'''

content = content.replace(old_check, check_run_wrapper + '\n\n' + new_check)

# 2. watch_run
old_watch = '''@mmws_post_app.command("watch-run")
def mmws_post_watch_run(
    run_id: str = typer.Option(..., "--run-id", help="Run ID to watch"),
    timeout: int = typer.Option(180, "--timeout", help="Timeout in seconds to wait for result"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written"),
) -> None:
    \"\"\"Watch a Lua run's progress and wait for its completion.\"\"\"'''

watch_wrapper = '''@mmws_post_app.command("watch-run")
def mmws_post_watch_run(
    run_id: str = typer.Option(..., "--run-id", help="Run ID to watch"),
    timeout: int = typer.Option(180, "--timeout", help="Timeout in seconds to wait for result"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written"),
) -> None:
    \"\"\"Watch a Lua run's progress and wait for its completion.\"\"\"
    watch_run_impl(run_id, timeout, probe_dir)

def watch_run_impl(run_id: str, timeout: int, probe_dir: str = None) -> None:
'''
content = content.replace(old_watch, watch_wrapper)

# 3. summarize_session
old_sum = '''@mmws_post_app.command("summarize-session")
def mmws_post_summarize_session(
    firmware_run_id: str = typer.Option(..., "--firmware-run-id", help="Run ID of the firmware sequence"),
    config_run_id: str = typer.Option(..., "--config-run-id", help="Run ID of the config sequence"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written"),
) -> None:
    \"\"\"Summarize a post-connection session (firmware + config runs).\"\"\"'''

sum_wrapper = '''@mmws_post_app.command("summarize-session")
def mmws_post_summarize_session(
    firmware_run_id: str = typer.Option(..., "--firmware-run-id", help="Run ID of the firmware sequence"),
    config_run_id: str = typer.Option(..., "--config-run-id", help="Run ID of the config sequence"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written"),
) -> None:
    \"\"\"Summarize a post-connection session (firmware + config runs).\"\"\"
    summarize_session_impl(firmware_run_id, config_run_id, probe_dir)

def summarize_session_impl(firmware_run_id: str, config_run_id: str, probe_dir: str = None) -> None:
'''
content = content.replace(old_sum, sum_wrapper)

# 4. record_validation
old_rec = '''@mmws_post_app.command("record-validation")
def mmws_post_record_validation(
    firmware_run_id: str = typer.Option(..., "--firmware-run-id", help="Run ID of the firmware sequence"),
    config_run_id: str = typer.Option(..., "--config-run-id", help="Run ID of the config sequence"),
    label: str = typer.Option(..., "--label", help="Notes or label for this validation record"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written"),
) -> None:
    \"\"\"Record a successful full post-connection validation.\"\"\"'''

rec_wrapper = '''@mmws_post_app.command("record-validation")
def mmws_post_record_validation(
    firmware_run_id: str = typer.Option(..., "--firmware-run-id", help="Run ID of the firmware sequence"),
    config_run_id: str = typer.Option(..., "--config-run-id", help="Run ID of the config sequence"),
    label: str = typer.Option(..., "--label", help="Notes or label for this validation record"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written"),
) -> None:
    \"\"\"Record a successful full post-connection validation.\"\"\"
    record_validation_impl(firmware_run_id, config_run_id, label, probe_dir)

def record_validation_impl(firmware_run_id: str, config_run_id: str, label: str, probe_dir: str = None) -> None:
'''
content = content.replace(old_rec, rec_wrapper)

with open('src/awr2944_dca/cli.py', 'w', encoding='utf-8') as f:
    f.write(content)