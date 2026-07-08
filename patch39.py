with open('src/awr2944_dca/mmws/gui_connect.py', 'r', encoding='utf-8') as f:
    content = f.read()

fixed = content.replace('Where-Object { .ProcessName', 'Where-Object { $_.ProcessName').replace('-or .MainWindowTitle', '-or $_.MainWindowTitle')

with open('src/awr2944_dca/mmws/gui_connect.py', 'w', encoding='utf-8') as f:
    f.write(fixed)