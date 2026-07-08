import json
import re

log_file = r'C:\Users\khams008\.gemini\antigravity-ide\brain\c904b166-8a91-4f95-8f9c-75156c56e83b\.system_generated\logs\transcript_full.jsonl'

found = False
with open(log_file, 'r', encoding='utf-8') as f:
    for line in f:
        if 'small_real_config' in line and 'def small_real_config' in line:
            print("Found in line:")
            data = json.loads(line)
            # Find the conftest.py content
            content = data.get('content', '')
            if 'conftest.py' in content:
                print(content[:500])
                found = True
                break
        
        # also check tool_calls
        try:
            data = json.loads(line)
            for tc in data.get('tool_calls', []):
                args = tc.get('function', {}).get('arguments', '')
                if 'def small_real_config' in args:
                    print("Found in tool call!")
                    print(args[:500])
                    found = True
        except:
            pass

if not found:
    print("Not found in transcript.")