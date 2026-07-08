import re

with open('src/awr2944_dca/mmws/gui_connect.py', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'def attach_mmwave_studio\(.*?(?=\n# -{70}|\Z)', content, re.DOTALL)
if match:
    print(match.group(0))
else:
    print("Not found")