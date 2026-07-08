with open('src/awr2944_dca/mmws/gui_connect.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix literal newlines in strings manually
fixed = content.replace('        return "\n".join(', '        return "\\n".join(')
fixed = fixed.replace('                f"UIA attach failed for PID={target_pid}:\n"\n                f"No windows', '                f"UIA attach failed for PID={target_pid}:\\n"\n                f"No windows')
fixed = fixed.replace('                f"No windows for that process could be found (MainWindowHandle == 0).\n"\n                f"Verify', '                f"No windows for that process could be found (MainWindowHandle == 0).\\n"\n                f"Verify')
fixed = fixed.replace('                f"Verify the PID is correct and mmWave Studio is running.\n\n"\n                f"Candidate processes:\n{format_cands(ps_cands)}\n\n"\n                f"If', '                f"Verify the PID is correct and mmWave Studio is running.\\n\\n"\n                f"Candidate processes:\\n{format_cands(ps_cands)}\\n\\n"\n                f"If')
fixed = fixed.replace('                "Verify the PID is correct and mmWave Studio is running.\n"\n                "If mmWave Studio was launched', '                "Verify the PID is correct and mmWave Studio is running.\\n"\n                "If mmWave Studio was launched')
fixed = fixed.replace('            f"Could not auto-resolve mmWave Studio PID: No visible candidate processes found.\n\n"\n            f"Candidate processes:\n{format_cands(ps_cands)}\n\n"\n            f"Try', '            f"Could not auto-resolve mmWave Studio PID: No visible candidate processes found.\\n\\n"\n            f"Candidate processes:\\n{format_cands(ps_cands)}\\n\\n"\n            f"Try')
fixed = fixed.replace('            f"Could not auto-resolve mmWave Studio PID: Multiple visible candidate processes found.\n\n"\n            f"Candidate processes:\n{format_cands(ps_cands)}\n\n"\n            f"Please rerun', '            f"Could not auto-resolve mmWave Studio PID: Multiple visible candidate processes found.\\n\\n"\n            f"Candidate processes:\\n{format_cands(ps_cands)}\\n\\n"\n            f"Please rerun')

with open('src/awr2944_dca/mmws/gui_connect.py', 'w', encoding='utf-8') as f:
    f.write(fixed)