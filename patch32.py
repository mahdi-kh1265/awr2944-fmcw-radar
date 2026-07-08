import re

with open('src/awr2944_dca/mmws/gui_connect.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add _get_powershell_candidates
new_func = '''
def _get_powershell_candidates(verbose_log: Callable[[str], None] | None = None) -> list[dict[str, Any]]:
    \"\"\"Query PowerShell for candidate mmWave Studio processes using WMI/process objects.\"\"\"
    import subprocess
    import json
    vlog = verbose_log or (lambda s: None)
    
    script = (
        'Get-Process | '
        'Where-Object { .ProcessName -match "mmwave|rstd|radarstudio" -or .MainWindowTitle -match "mmwave|rstd|radar|lua" } | '
        'Select-Object Id, ProcessName, MainWindowHandle, MainWindowTitle, Responding, Path | '
        'ConvertTo-Json -Depth 3'
    )
    try:
        output = subprocess.check_output(["powershell", "-NoProfile", "-Command", script], text=True)
        if not output.strip():
            return []
        data = json.loads(output)
        if isinstance(data, dict):
            return [data]
        return data
    except Exception as e:
        vlog(f"PowerShell candidate enumeration failed: {e}")
        return []
'''

# Find the right place to insert, e.g., before _enumerate_uia_windows
if '_get_powershell_candidates' not in content:
    content = content.replace('def _enumerate_uia_windows(', new_func + '\n\ndef _enumerate_uia_windows(')


with open('src/awr2944_dca/mmws/gui_connect.py', 'w', encoding='utf-8') as f:
    f.write(content)