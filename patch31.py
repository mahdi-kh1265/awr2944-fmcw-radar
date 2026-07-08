import subprocess
import json

def get_process_candidates():
    script = '''
    Get-Process | Where-Object { $_.ProcessName -match "mmwave|rstd|radarstudio" -or $_.MainWindowTitle -match "mmwave|rstd|radar|lua" } | Select-Object Id, ProcessName, MainWindowHandle, MainWindowTitle, Responding, Path | ConvertTo-Json -Compress
    '''
    try:
        output = subprocess.check_output(["powershell", "-NoProfile", "-Command", script], text=True)
        if not output.strip():
            return []
        data = json.loads(output)
        if isinstance(data, dict):
            return [data]
        return data
    except Exception as e:
        print("Error:", e)
        return []

print(get_process_candidates())