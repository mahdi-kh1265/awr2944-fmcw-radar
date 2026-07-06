from pywinauto import Application, Desktop
from pathlib import Path
import os
import contextlib

pid = int(os.environ["MMWS_PID"])
out = Path(r"C:\Users\khams008\Documents\awr2944-fmcw-radar\exp_lau_probe\ti\probe_logs\direct_pid_control_tree.txt")
out.parent.mkdir(parents=True, exist_ok=True)

print(f"Trying direct attach to PID={pid}")

app = Application(backend="uia").connect(process=pid, timeout=10)
win = app.top_window()

print("ATTACHED_APP_TOP_WINDOW:", repr(win.window_text()))
print("RECT:", win.rectangle())

with out.open("w", encoding="utf-8") as f:
    f.write(f"PID={pid}\n")
    f.write(f"TITLE={win.window_text()!r}\n")
    f.write(f"RECT={win.rectangle()}\n\n")
    with contextlib.redirect_stdout(f):
        win.print_control_identifiers(depth=5)

print(f"Wrote {out}")
