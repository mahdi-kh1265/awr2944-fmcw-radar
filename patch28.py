with open('tests/conftest.py', 'a', encoding='utf-8') as f:
    f.write('\n\n# WORKAROUND: Pytest on Windows frequently fails with PermissionError\n')
    f.write('import _pytest.pathlib\n')
    f.write('_pytest.pathlib.cleanup_dead_symlinks = lambda root: None\n')