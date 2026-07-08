import pytest
import sys
if __name__ == '__main__':
    pytest.main(['tests/test_guided_runner.py::test_resume_from_firmware_script_generated', 'tests/test_guided_runner.py::test_resume_records_validation', '-v', '-q', '--tb=short'])