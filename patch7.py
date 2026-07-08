import re

with open('tests/test_failure_report.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"workflow_id": "oldmismatch",', '"workflow_id": "oldmismatch",\n        "label": "test",\n        "pid": None,\n        "state_path": str(state_path),')
content = content.replace('"workflow_id": "newsummary",', '"workflow_id": "newsummary",\n        "label": "test",\n        "pid": None,\n        "state_path": str(state_path),')

with open('tests/test_failure_report.py', 'w', encoding='utf-8') as f:
    f.write(content)