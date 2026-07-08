import re

with open('src/awr2944_dca/cli.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. watch_run
watch = re.search(r'(@mmws_post_app\.command\("watch-run"\).*?)(def mmws_post_watch_run\([^)]+\)\s*->\s*None:\s*"""[^"]+""")', content, re.DOTALL)
if watch and 'watch_run_impl' not in content:
    wrapper_def = watch.group(2)
    new_wrapper = wrapper_def + '''\n    watch_run_impl(run_id, timeout, probe_dir)\n\ndef watch_run_impl(run_id: str, timeout: int, probe_dir: str = None) -> None:\n'''
    content = content.replace(wrapper_def, new_wrapper)

# 2. summarize_session
sum_cmd = re.search(r'(@mmws_post_app\.command\("summarize-session"\).*?)(def mmws_post_summarize_session\([^)]+\)\s*->\s*None:\s*"""[^"]+""")', content, re.DOTALL)
if sum_cmd and 'summarize_session_impl' not in content:
    wrapper_def = sum_cmd.group(2)
    # Check if probe_dir is in the signature, if not add it
    if 'probe_dir' not in wrapper_def:
        wrapper_def = wrapper_def.replace(') -> None:', ',\n    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written")\n) -> None:')
        content = content.replace(sum_cmd.group(2), wrapper_def)
    
    new_wrapper = wrapper_def + '''\n    summarize_session_impl(firmware_run_id, config_run_id, probe_dir)\n\ndef summarize_session_impl(firmware_run_id: str, config_run_id: str, probe_dir: str = None) -> None:\n'''
    content = content.replace(wrapper_def, new_wrapper)

# 3. record_validation
rec_cmd = re.search(r'(@mmws_post_app\.command\("record-validation"\).*?)(def mmws_post_record_validation\([^)]+\)\s*->\s*None:\s*"""[^"]+""")', content, re.DOTALL)
if rec_cmd and 'record_validation_impl' not in content:
    wrapper_def = rec_cmd.group(2)
    if 'probe_dir' not in wrapper_def:
        wrapper_def = wrapper_def.replace(') -> None:', ',\n    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written")\n) -> None:')
        content = content.replace(rec_cmd.group(2), wrapper_def)

    new_wrapper = wrapper_def + '''\n    record_validation_impl(firmware_run_id, config_run_id, label, probe_dir)\n\ndef record_validation_impl(firmware_run_id: str, config_run_id: str, label: str, probe_dir: str = None) -> None:\n'''
    content = content.replace(wrapper_def, new_wrapper)

with open('src/awr2944_dca/cli.py', 'w', encoding='utf-8') as f:
    f.write(content)