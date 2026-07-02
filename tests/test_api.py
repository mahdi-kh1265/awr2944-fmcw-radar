import pytest
from pathlib import Path
from awr2944_dca.api.experiment import Experiment

def test_experiment_init(tmp_path):
    exp = Experiment.init(name="test_exp", preset="first-capture", root=tmp_path)
    assert (tmp_path / "test_exp" / ".awr-experiment").exists()
    assert exp.root_dir == tmp_path / "test_exp"
    assert exp.config_path.exists()
    
def test_experiment_open(tmp_path):
    exp_init = Experiment.init(name="test_exp2", preset="first-capture", root=tmp_path)
    
    # Open from root
    exp_open = Experiment.open(tmp_path / "test_exp2")
    assert exp_open.root_dir == exp_init.root_dir
    
    # Open from a subdirectory
    (exp_init.root_dir / "raw").mkdir(exist_ok=True)
    exp_open_sub = Experiment.open(tmp_path / "test_exp2" / "raw")
    assert exp_open_sub.root_dir == exp_init.root_dir

def test_experiment_set_device_capture(tmp_path):
    exp = Experiment.init(name="test_exp_set", preset="first-capture", root=tmp_path)
    exp.set_device("NEW_RADAR")
    exp.set_capture("NEW_CARD")
    
    cfg = exp.get_config()
    assert cfg.rig.radar == "NEW_RADAR"
    assert cfg.rig.capture_card == "NEW_CARD"

def test_generate_probe_script(tmp_path):
    exp = Experiment.init(name="test_exp_probe", preset="first-capture", root=tmp_path)
    probe_lua = exp.generate_ti_probe()
    
    assert probe_lua.exists()
    content = probe_lua.read_text(encoding="utf-8")
    
    # Requirements
    assert "os.exit()" not in content
    assert "ar1.Connect" not in content  # no hardware commands
    assert "probe_result.json" in content
    assert "pcall" in content
