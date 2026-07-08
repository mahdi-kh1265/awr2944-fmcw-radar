import os
import subprocess

git_path = r'C:\Program Files\Git\bin\git.exe'
if os.path.exists(git_path):
    print("Found git!")
    subprocess.run([git_path, 'checkout', 'tests/conftest.py'])
    print("Restored!")
else:
    print("No git found.")