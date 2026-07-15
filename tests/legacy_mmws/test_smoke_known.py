import pytest
pytestmark = pytest.mark.legacy_mmws
"""Golden tests for smoke-from-known-awr2944 script generation.

These tests verify that the generated Lua script contains the exact
frozen GUI-derived AWR2944 commands and does NOT contain any known
bad patterns that previously caused RadarAPI and GUI errors.
"""

import re
from pathlib import Path

import pytest

from awr2944_dca.legacy_mmws.post_connect import (
    generate_smoke_known_awr2944,
    VALIDATED_AWR2944_SMOKE_V0,
    _KNOWN_BAD_PATTERNS,
    _parse_frozen_command,
)


@pytest.fixture
def generated_script(tmp_path: Path) -> str:
    """Generate the smoke-from-known-awr2944 script and return its text."""
    out_path = tmp_path / "test_smoke_known_awr2944.lua"
    generated = generate_smoke_known_awr2944("testrun1", out_path)
    return generated.script


class TestFrozenCommandsPresent:
    """Verify every frozen command appears in an executable (non-comment) line."""
    
    @pytest.mark.parametrize("cmd_line", VALIDATED_AWR2944_SMOKE_V0.commands)
    def test_frozen_command_in_executable_line(self, generated_script: str, cmd_line: str):
        """Each frozen command must appear in a non-comment line containing ar1.<cmd>."""
        expected = f"ar1.{cmd_line}"
        found = False
        for line in generated_script.splitlines():
            stripped = line.strip()
            if stripped.startswith("--"):
                continue  # skip comment lines
            if expected in stripped:
                found = True
                break
        assert found, (
            f"Frozen command not found in executable line: ar1.{cmd_line}\n"
            f"This is a release-blocker regression."
        )
    
    def test_all_commands_present(self, generated_script: str):
        """All frozen commands must be present in the script."""
        missing = []
        for cmd_line in VALIDATED_AWR2944_SMOKE_V0.commands:
            expected = f"ar1.{cmd_line}"
            if expected not in generated_script:
                missing.append(cmd_line)
        assert not missing, f"Missing frozen commands: {missing}"


class TestKnownBadPatternsAbsent:
    """Verify no known bad patterns appear in executable lines."""
    
    @pytest.mark.parametrize("bad_pattern", _KNOWN_BAD_PATTERNS)
    def test_bad_pattern_not_in_executable_line(self, generated_script: str, bad_pattern: str):
        """Known bad patterns must NOT appear in executable (non-comment) lines."""
        for line in generated_script.splitlines():
            stripped = line.strip()
            if stripped.startswith("--"):
                continue
            assert bad_pattern not in stripped, (
                f"Known bad pattern found in executable line: {bad_pattern!r}\n"
                f"Line: {stripped}\n"
                f"This was previously a release-blocker regression."
            )


class TestScriptStructure:
    """Verify structural properties of the generated script."""
    
    def test_has_run_begin_marker(self, generated_script: str):
        assert "AWR_RUN_BEGIN" in generated_script
    
    def test_has_run_end_success_marker(self, generated_script: str):
        assert "AWR_RUN_END" in generated_script
        assert "success=true" in generated_script
    
    def test_has_safe_call_for_each_command(self, generated_script: str):
        for cmd_line in VALIDATED_AWR2944_SMOKE_V0.commands:
            func, _ = _parse_frozen_command(cmd_line)
            assert f'safeCall("{func}"' in generated_script, (
                f"No safeCall wrapper for {func}"
            )
    
    def test_rfinit_has_sleep(self, generated_script: str):
        lines = generated_script.splitlines()
        for i, line in enumerate(lines):
            if "ar1.RfInit()" in line:
                # Next non-empty line should be RSTD.Sleep
                for j in range(i + 1, min(i + 3, len(lines))):
                    if lines[j].strip():
                        assert "RSTD.Sleep" in lines[j], "RfInit should be followed by RSTD.Sleep"
                        break
                break
    
    def test_result_json_source_is_frozen(self, tmp_path: Path):
        out_path = tmp_path / "test.lua"
        generated = generate_smoke_known_awr2944("testrun1", out_path)
        
        # Verify structured metadata
        assert generated.metadata["source"] == "frozen_gui_derived_awr2944"
        assert generated.metadata["replay_validated"] is True
        
        # Verify script comments for human/debug visibility
        assert "-- source: frozen_gui_derived_awr2944" in generated.script
        assert "-- replay_validated: true" in generated.script


class TestParseFrozenCommand:
    """Test the _parse_frozen_command helper."""
    
    def test_simple(self):
        func, args = _parse_frozen_command("RfInit()")
        assert func == "RfInit"
        assert args == ""
    
    def test_with_args(self):
        func, args = _parse_frozen_command("ChanNAdcConfig(1, 1, 0, 0, 1, 1, 0, 0, 2, 0, 0)")
        assert func == "ChanNAdcConfig"
        assert args == "1, 1, 0, 0, 1, 1, 0, 0, 2, 0, 0"
    
    def test_hex_arg(self):
        func, args = _parse_frozen_command("RfLdoBypassConfig(0x0)")
        assert func == "RfLdoBypassConfig"
        assert args == "0x0"
