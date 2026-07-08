import glob
import re
import json

for log_file in glob.glob(r'C:\Users\khams008\.gemini\antigravity-ide\brain\*\.system_generated\logs\transcript_full.jsonl'):
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'def small_real_config.*?def small_complex_config', content, re.DOTALL)
        if match:
            idx = match.start()
            start = content.rfind('{', 0, idx)
            
            # Count braces to find the end of the JSON object
            count = 0
            end = -1
            for i in range(start, len(content)):
                if content[i] == '{': count += 1
                elif content[i] == '}': count -= 1
                if count == 0:
                    end = i + 1
                    break
                    
            try:
                data = json.loads(content[start:end])
                code = data.get('CodeContent')
                with open('tests/conftest.py', 'w', encoding='utf-8') as cf:
                    cf.write(code)
                print("Successfully restored tests/conftest.py!")
                break
            except Exception as e:
                print("Failed to parse:", e)