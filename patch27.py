with open('tests/conftest.py', 'a', encoding='utf-8') as f:
    f.write('\n\n# WORKAROUND: Pytest on Windows frequently fails with PermissionError: [WinError 5] Access is denied\n')
    f.write('# We monkeypatch cleanup_dead_symlinks to be a no-op to ensure the test suite doesn\\'t crash on teardown.\n')
    f.write('import _pytest.pathlib\n')
    f.write('_pytest.pathlib.cleanup_dead_symlinks = lambda root: None\n')