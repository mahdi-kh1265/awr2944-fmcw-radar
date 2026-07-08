import sys
import dis
import marshal
try:
    with open('tests/__pycache__/conftest.cpython-312.pyc', 'rb') as f:
        f.read(16) # skip magic
        code = marshal.load(f)
    print("Code object found!")
except Exception as e:
    print("Error:", e)