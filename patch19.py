import re

with open('tests/test_failure_report.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix mock data in test_hardware_likely_touched
content = content.replace('{"command": "WriteToLog"}', '{"cmd": "WriteToLog"}')
content = content.replace('{"command": "PowerOn"}', '{"cmd": "PowerOn"}')

with open('tests/test_failure_report.py', 'w', encoding='utf-8') as f:
    f.write(content)