import pytest
import json
from pathlib import Path
from awr2944_dca._config import ProjectConfig, ConfigMismatchError

def test_project_config_defaults(tmp_path):
    config = ProjectConfig(tmp_path)
    
    assert config.portable.project_name == "unnamed_project"
    assert config.local.host_ip == ""
    
    assert config.local.com_port == ""
    assert config.local.aux_com_port == ""

def test_project_config_save_load(tmp_path):
    config = ProjectConfig(tmp_path)
    config.portable.project_name = "test_save"
    config.local.com_port = "COM99"
    config.save()
    
    # Reload from disk
    config2 = ProjectConfig(tmp_path)
    assert config2.portable.project_name == "test_save"
    assert config2.local.com_port == "COM99"

def test_cf_json_validation_success(tmp_path):
    config = ProjectConfig(tmp_path)
    cf_path = tmp_path / "cf.json"
    
    cf_data = {
        "DCA1000Config": {
            "ethernetConfigUpdate": {
                "systemIPAddress": "192.168.33.30",
                "DCA1000IPAddress": "192.168.33.180",
                "DCA1000ConfigPort": 4096,
                "DCA1000DataPort": 4098
            }
        }
    }
    with open(cf_path, "w") as f:
        json.dump(cf_data, f)
        
    config.local.cf_json_path = str(cf_path)
    config.local.host_ip = "192.168.33.30"
    # Should not raise
    config.validate_cf_json()

def test_cf_json_validation_mismatch(tmp_path):
    config = ProjectConfig(tmp_path)
    cf_path = tmp_path / "cf.json"
    
    cf_data = {
        "DCA1000Config": {
            "ethernetConfigUpdate": {
                "systemIPAddress": "192.168.33.31", # Mismatch
                "DCA1000IPAddress": "192.168.33.180",
                "DCA1000ConfigPort": 4096,
                "DCA1000DataPort": 4098
            }
        }
    }
    with open(cf_path, "w") as f:
        json.dump(cf_data, f)
        
    config.local.cf_json_path = str(cf_path)
    config.local.host_ip = "192.168.33.30"
    
    with pytest.raises(ConfigMismatchError, match="Host IP mismatch"):
        config.validate_cf_json()
