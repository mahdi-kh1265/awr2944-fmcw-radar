import json
from pathlib import Path
from typer.testing import CliRunner

from awr2944_dca.cli import app
from awr2944_dca.api.experiment import Experiment
from awr2944_dca.ti.classify import classify_key, scan_ti_scripts, generate_classification

runner = CliRunner()

def test_classify_key():
    # Category and risk check
    assert classify_key("ar1.PowerOn") == ("connection/setup", "state_changing")
    assert classify_key("ar1.GetVersion") == ("harmless/read-only", "safe_offline")
    assert classify_key("ar1.RfEnable") == ("RF/hardware action", "capture_triggering")
    assert classify_key("ar1.DownloadBSSFw") == ("firmware/loading", "state_changing")
    assert classify_key("ar1.ChanNAdcConfig") == ("static config", "safe_with_board_no_rf")
    assert classify_key("ar1.ProfileConfig") == ("profile/chirp/frame config", "safe_with_board_no_rf")
    assert classify_key("ar1.CaptureCardConfig_StartRecord") == ("DCA/capture", "state_changing")
    
    # Unknown default
    assert classify_key("ar1.SomeRandomThing") == ("unknown", "dangerous_or_unknown")


def test_scan_ti_scripts(tmp_path):
    lua_file = tmp_path / "test.lua"
    lua_file.write_text("ar1.Connect()\nar1.PowerOn()\n-- ar1.DoNotIncludeMe()\n")
    
    results = scan_ti_scripts(tmp_path)
    assert "Connect" in results
    assert "PowerOn" in results
    assert "DoNotIncludeMe" not in results
    
    assert len(results["Connect"]) == 1
    assert results["Connect"][0]["line"] == 1
    assert "test.lua" in results["Connect"][0]["file"]


def test_generate_classification():
    inventory_json = {
        "ar1_keys": {
            "PowerOn": {"type": "function", "value": ""},
            "GetVersion": {"type": "function", "value": ""}
        }
    }
    
    keys = generate_classification(inventory_json, ti_scripts_dir=None)
    assert len(keys) == 2
    
    # Assert ordering and fields
    k0 = keys[0] # safe_offline goes before state_changing
    assert k0.name == "GetVersion"
    assert k0.risk == "safe_offline"
    assert k0.category == "harmless/read-only"
    
    k1 = keys[1]
    assert k1.name == "PowerOn"
    assert k1.risk == "state_changing"


