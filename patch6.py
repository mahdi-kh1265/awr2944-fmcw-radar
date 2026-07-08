import sys

with open('src/awr2944_dca/cli.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_rec = '''@mmws_post_app.command("record-validation")
def mmws_post_record_validation(
    firmware_run_id: str = typer.Option(..., "--firmware-run-id", help="Run ID of the firmware sequence"),
    config_run_id: str = typer.Option(..., "--config-run-id", help="Run ID of the config sequence"),
    label: str = typer.Option(..., "--label", help="Notes or label for this validation record"),
) -> None:
    \"\"\"Record a successful full post-connection validation.\"\"\"
    import json
    import time
    import datetime
    
    probe_dir = _lua_launch_probe_dir()'''

new_rec = '''@mmws_post_app.command("record-validation")
def mmws_post_record_validation(
    firmware_run_id: str = typer.Option(..., "--firmware-run-id", help="Run ID of the firmware sequence"),
    config_run_id: str = typer.Option(..., "--config-run-id", help="Run ID of the config sequence"),
    label: str = typer.Option(..., "--label", help="Notes or label for this validation record"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written"),
) -> None:
    \"\"\"Record a successful full post-connection validation.\"\"\"
    record_validation_impl(firmware_run_id, config_run_id, label, probe_dir)

def record_validation_impl(firmware_run_id: str, config_run_id: str, label: str, probe_dir: str = None) -> None:
    import json
    import time
    import datetime
    
    probe_dir = _lua_launch_probe_dir(probe_dir)'''

content = content.replace(old_rec, new_rec)

with open('src/awr2944_dca/cli.py', 'w', encoding='utf-8') as f:
    f.write(content)