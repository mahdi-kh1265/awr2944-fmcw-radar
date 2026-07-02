import pytest
from pathlib import Path
from awr2944_dca.context import discover_context

def test_discover_context_finds_root(tmp_path):
    (tmp_path / ".awr-experiment").touch()
    (tmp_path / "capture.yaml").touch()
    
    # Create a nested directory
    nested = tmp_path / "raw" / "subfolder"
    nested.mkdir(parents=True)
    
    ctx = discover_context(nested)
    assert ctx is not None
    assert ctx.root_dir == tmp_path
    assert ctx.config_path == tmp_path / "capture.yaml"

def test_discover_context_returns_none(tmp_path):
    # No .awr-experiment
    (tmp_path / "capture.yaml").touch()
    
    ctx = discover_context(tmp_path)
    assert ctx is None
