import re

with open('src/awr2944_dca/mmws/failure_report.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('cmd = entry.get("command", "")', 'cmd = entry.get("cmd", "")')

with open('src/awr2944_dca/mmws/failure_report.py', 'w', encoding='utf-8') as f:
    f.write(content)