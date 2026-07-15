import json
from pathlib import Path
import pytest
from awr2944_dca.lab import RadarProject

@pytest.fixture
def mock_project(tmp_path):
    # Create awr2944.toml
    (tmp_path / "awr2944.toml").write_text("")
    
    # Create captures dir
    cap_dir = tmp_path / "captures" / "cap_complete_1"
    cap_dir.mkdir(parents=True)
    
    # Create manifest indicating complete
    manifest = {
        "capture_id": "cap_complete_1",
        "capture_name": "Test Complete",
        "status": "complete",
        "created_at": "2023-01-01T00:00:00Z"
    }
    (cap_dir / "capture_manifest.json").write_text(json.dumps(manifest))
    
    # Create raw dir
    raw_dir = cap_dir / "raw"
    raw_dir.mkdir(parents=True)
    
    return tmp_path

def test_notebook_api_calls(mock_project):
    """
    Offline regression test to ensure the public API used in the
    Phase D manual notebook actually exists and works.
    """
    # 1. Project Opening
    project = RadarProject.open(mock_project)
    
    # 2. List Captures
    captures = project.captures.list()
    assert len(captures) == 1
    
    # Check properties
    c = captures[0]
    assert c.capture_id == "cap_complete_1"
    assert c.status().get('status') == "complete"
    
    # 3. Get capture by ID
    capture = project.captures.get(c.capture_id)
    assert capture.capture_id == c.capture_id
    
    # 4. Verify API surface existence without invoking real processing:
    assert hasattr(capture, "verify")
    assert hasattr(capture, "raw")
    assert hasattr(capture, "viewer_data")
    assert hasattr(capture, "open_controlled_viewer")
    
    # Test capture.raw properties
    raw = capture.raw
    assert hasattr(raw, "native_path")
    assert hasattr(raw, "native_bytes")
    assert hasattr(raw, "canonical_path")
    assert hasattr(raw, "canonical_bytes")
    assert hasattr(raw, "iter_frames")
    
    # Test capture.viewer_data properties
    vd = capture.viewer_data
    assert hasattr(vd, "exists")
    assert hasattr(vd, "path")
    assert hasattr(vd, "load")
    
    # We do NOT test open_controlled_viewer() launching here as the user 
    # requested no MATLAB launches in automated tests.
