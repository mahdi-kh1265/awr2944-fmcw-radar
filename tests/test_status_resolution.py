import json
from pathlib import Path
import pytest
from awr2944_dca.lab import RadarProject
from awr2944_dca.api._status_resolver import resolve_capture_status

def test_resolve_capture_status_created():
    # facade created + no production manifest -> created
    f_man = {"status": "created"}
    res = resolve_capture_status(f_man, None)
    assert res["status"] == "created"
    assert res["status_source"] == "facade"

def test_resolve_capture_status_complete():
    # facade created + production complete/success -> complete
    f_man = {"status": "created"}
    p_man = {"status": "complete", "success": True}
    res = resolve_capture_status(f_man, p_man)
    assert res["status"] == "complete"
    assert res["status_source"] == "production"
    assert res["success"] is True

def test_resolve_capture_status_failed():
    # facade created + production failure -> failed
    f_man = {"status": "created"}
    p_man = {"status": "complete", "success": False}
    res = resolve_capture_status(f_man, p_man)
    assert res["status"] == "failed"
    assert res["status_source"] == "production"
    assert res["success"] is False

def test_resolve_capture_status_explicit_accepted():
    # explicit facade accepted + production complete -> accepted
    f_man = {"status": "accepted"}
    p_man = {"status": "complete", "success": True}
    res = resolve_capture_status(f_man, p_man)
    assert res["status"] == "accepted"
    assert res["status_source"] == "facade"

def test_resolve_capture_status_malformed_production():
    # malformed production manifest -> honest non-success status
    f_man = {"status": "created"}
    p_man = {"status": "crashed"} # success is missing
    res = resolve_capture_status(f_man, p_man)
    assert res["status"] == "crashed"
    assert res["status_source"] == "production"

@pytest.fixture
def mock_multi_project(tmp_path):
    (tmp_path / "awr2944.toml").write_text("")
    
    cap_dir1 = tmp_path / "captures" / "cap1"
    cap_dir1.mkdir(parents=True)
    (cap_dir1 / "capture_manifest.json").write_text(json.dumps({"capture_id": "cap1", "status": "created"}))
    
    cap_dir2 = tmp_path / "captures" / "cap2"
    cap_dir2.mkdir(parents=True)
    (cap_dir2 / "capture_manifest.json").write_text(json.dumps({"capture_id": "cap2", "status": "created"}))
    (cap_dir2 / "manifest.json").write_text(json.dumps({"status": "complete", "success": True}))
    
    return tmp_path

def test_collection_listing_and_direct_status_agree(mock_multi_project):
    project = RadarProject.open(mock_multi_project)
    
    captures = project.captures.list()
    assert len(captures) == 2
    
    cap1_from_list = next(c for c in captures if c.capture_id == "cap1")
    cap2_from_list = next(c for c in captures if c.capture_id == "cap2")
    
    # Collection listing
    status1_list = cap1_from_list.status()
    status2_list = cap2_from_list.status()
    
    assert status1_list["status"] == "created"
    assert status2_list["status"] == "complete"
    
    # Direct RadarCapture
    cap1_direct = project.captures.get("cap1")
    cap2_direct = project.captures.get("cap2")
    
    assert cap1_direct.status()["status"] == "created"
    assert cap2_direct.status()["status"] == "complete"
