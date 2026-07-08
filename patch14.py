import re

with open('tests/test_failure_report.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I will write progress for cfgsym as well in test_failure_report_new_summary_bug
to_replace = '''    # Write progress JSONL (touched hardware)
    prog_path = tmp_path / f"{fw_id}_firmware_power_progress.jsonl"
    prog_path.write_text(json.dumps({"cmd": "PowerOn", "ret": 0, "ok": True}) + "\\n", encoding="utf-8")'''

replacement = '''    # Write progress JSONL (touched hardware)
    prog_path = tmp_path / f"{fw_id}_firmware_power_progress.jsonl"
    prog_path.write_text(json.dumps({"cmd": "PowerOn", "ret": 0, "ok": True}) + "\\n", encoding="utf-8")
    prog_path2 = tmp_path / f"{cfg_id}_config_progress.jsonl"
    prog_path2.write_text(json.dumps({"cmd": "ProfileConfig", "ret": 0, "ok": True}) + "\\n", encoding="utf-8")'''

content = content.replace(to_replace, replacement)

with open('tests/test_failure_report.py', 'w', encoding='utf-8') as f:
    f.write(content)