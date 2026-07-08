import re

with open('src/awr2944_dca/cli.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_command = '''
@mmws_post_app.command("list-windows")
def mmws_post_list_windows() -> None:
    """List candidate mmWave Studio processes and their window states."""
    from .mmws.gui_connect import _get_powershell_candidates
    from rich.table import Table
    
    candidates = _get_powershell_candidates()
    
    table = Table(title="Candidate mmWave Studio Processes")
    table.add_column("PID", justify="right", style="cyan")
    table.add_column("Process Name", style="magenta")
    table.add_column("Window Handle", justify="right", style="green")
    table.add_column("Window Title", style="yellow")
    table.add_column("Responding", style="blue")
    
    if not candidates:
        console.print("[yellow]No candidate mmWave Studio processes found.[/yellow]")
        return
        
    for c in candidates:
        pid = str(c.get("Id", ""))
        name = str(c.get("ProcessName", ""))
        handle = str(c.get("MainWindowHandle", ""))
        title = str(c.get("MainWindowTitle", ""))
        resp = str(c.get("Responding", ""))
        table.add_row(pid, name, handle, title, resp)
        
    console.print(table)
'''

# Find a good place to insert this, for example just above @mmws_post_app.command("guided-validate")
if 'def mmws_post_list_windows' not in content:
    content = content.replace('@mmws_post_app.command("guided-validate")', new_command + '\n@mmws_post_app.command("guided-validate")')
    with open('src/awr2944_dca/cli.py', 'w', encoding='utf-8') as f:
        f.write(content)