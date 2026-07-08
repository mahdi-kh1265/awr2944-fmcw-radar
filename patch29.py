with open('tests/conftest.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"awr2944_real_interleaved_2lane_unvalidated"', '"awr2944_real_2lane_interleaved_candidate"')

with open('tests/conftest.py', 'w', encoding='utf-8') as f:
    f.write(content)