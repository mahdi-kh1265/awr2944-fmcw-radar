from pathlib import Path
from awr2944_dca.ti.workflow_map import extract_workflow, FIRST_CAPTURE_MAP

def test_extract_workflow_parsing(tmp_path):
    # Setup fake Lua file
    lua_file = tmp_path / "DataCaptureDemo_xWR.lua"
    lua_content = """
-- Some comment
ar1.SOPControl(2)
if (ar1.Connect(4, 921600, 1000) == 0) then
if (ar1.DownloadBSSFw("fw.bin") == 0) then
-- ignore me ar1.RfInit()
if (ar1.AdvanceFrameConfig(1, 2, 3) == 0) then
    """
    lua_file.write_text(lua_content)
    
    steps = extract_workflow(tmp_path, "DataCaptureDemo_xWR.lua")
    
    assert len(steps) == 4
    assert steps[0].name == "SOPControl"
    assert steps[0].args == "2"
    assert steps[0].yaml_fields == []
    
    assert steps[1].name == "Connect"
    assert steps[1].args == "4, 921600, 1000"
    
    assert steps[2].name == "DownloadBSSFw"
    
    assert steps[3].name == "AdvanceFrameConfig"

def test_extract_workflow_missing_file(tmp_path):
    steps = extract_workflow(tmp_path, "DoesNotExists.lua")
    assert len(steps) == 0

def test_first_capture_map_keys():
    # Ensure some critical keys exist
    assert "SOPControl" in FIRST_CAPTURE_MAP
    assert "ChanNAdcConfig" in FIRST_CAPTURE_MAP
    assert "StartRecord" not in FIRST_CAPTURE_MAP # We use CaptureCardConfig_StartRecord
    assert "CaptureCardConfig_StartRecord" in FIRST_CAPTURE_MAP
