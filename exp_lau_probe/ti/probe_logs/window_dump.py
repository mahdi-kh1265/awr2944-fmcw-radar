from pywinauto import Desktop

print("=== UIA windows ===")
for w in Desktop(backend="uia").windows():
    title = w.window_text()
    if title.strip():
        try:
            pid = w.process_id()
        except Exception:
            pid = "?"
        print(f"PID={pid} TITLE={title!r}")
