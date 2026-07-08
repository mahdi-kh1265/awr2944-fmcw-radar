import re

with open('tests/test_guided_runner.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix fake_watch_run_sync
to_replace1 = '''    def fake_watch_run_sync(run_id, timeout):
        stages_hit.append("watch_run_" + run_id)
        return True'''
replacement1 = '''    def fake_watch_run_sync(run_id, timeout, probe_dir=None):
        stages_hit.append("watch_run_" + run_id)
        return True'''
content = content.replace(to_replace1, replacement1)

# Fix fake_record
to_replace2 = '''    def fake_record(fw, cfg, label):
        recorded.append((fw, cfg, label))
        return True'''
replacement2 = '''    def fake_record(fw, cfg, label, probe_dir=None):
        recorded.append((fw, cfg, label))
        return True'''
content = content.replace(to_replace2, replacement2)

with open('tests/test_guided_runner.py', 'w', encoding='utf-8') as f:
    f.write(content)