import glob
import json
import os

found = False
for log_file in glob.glob(r'C:\Users\khams008\.gemini\antigravity-ide\brain\*\.system_generated\logs\transcript_full.jsonl'):
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            if 'def small_real_config' in line:
                print("Found in:", log_file)
                try:
                    data = json.loads(line)
                    for tc in data.get('tool_calls', []):
                        args = tc.get('function', {}).get('arguments', '')
                        if 'def small_real_config' in args:
                            print(args)
                            found = True
                except:
                    pass
                if found: break
    if found: break
if not found:
    print("Not found in any transcript.")