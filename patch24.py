import glob
import json

for log_file in glob.glob(r'C:\Users\khams008\.gemini\antigravity-ide\brain\*\.system_generated\logs\transcript_full.jsonl'):
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            if 'def small_real_config' in line:
                try:
                    data = json.loads(line)
                    for tc in data.get('tool_calls', []):
                        args_str = tc.get('function', {}).get('arguments', '{}')
                        if 'def small_real_config' in args_str:
                            args = json.loads(args_str)
                            print(args.get('CodeContent', '') or args.get('Code', '') or args_str[:500])
                            exit(0)
                except Exception as e:
                    pass