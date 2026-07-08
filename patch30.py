import psutil
try:
    from pywinauto import Desktop
except ImportError:
    pass

def find_mmwave_processes():
    for p in psutil.process_iter(['pid', 'name']):
        name = p.info['name']
        if name and 'mmwave' in name.lower():
            print(p.info)

find_mmwave_processes()