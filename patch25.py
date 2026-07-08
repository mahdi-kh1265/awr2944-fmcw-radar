import glob
import re

for log_file in glob.glob(r'C:\Users\khams008\.gemini\antigravity-ide\brain\*\.system_generated\logs\transcript_full.jsonl'):
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'def small_real_config.*?def small_complex_config', content, re.DOTALL)
        if match:
            # try to extract a broader context
            idx = match.start()
            start = content.rfind('{', 0, idx)
            end = content.find('}', idx)
            print("Found match in:", log_file)
            print(content[start:end+200][:2000])
            break