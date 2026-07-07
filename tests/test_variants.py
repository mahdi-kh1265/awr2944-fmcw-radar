import pytest
import json
from pathlib import Path
from typer.testing import CliRunner
from awr2944_dca.cli import mmws_post_app
from awr2944_dca.mmws.post_connect import VALIDATED_AWR2944_SMOKE_V0

runner = CliRunner()

def test_validate_frozen_config():
    result = runner.invoke(mmws_post_app, ["validate-frozen-config"])
    assert result.exit_code == 0
    assert "Frozen config validation PASSED" in result.stdout

def test_generate_config_variant_dry_run_only():
    # Calling without --dry-run should fail
    result = runner.invoke(mmws_post_app, ["generate-config-variant", "--variant", "tx0-only"])
    assert result.exit_code != 0
    assert "--dry-run MUST be provided" in result.stdout

def test_generate_config_variant_unknown():
    result = runner.invoke(mmws_post_app, ["generate-config-variant", "--variant", "unknown-variant", "--dry-run"])
    assert result.exit_code != 0
    assert "Unknown variant" in result.stdout

def test_generate_config_variant_tx0_only(tmp_path, monkeypatch):
    # Ensure no files are written by mocking out probe dir to tmp_path
    import awr2944_dca.cli
    monkeypatch.setattr(awr2944_dca.cli, "_lua_launch_probe_dir", lambda: tmp_path)
    
    # Save original baseline commands to check immutability
    orig_cmds = list(VALIDATED_AWR2944_SMOKE_V0.commands)
    
    result = runner.invoke(mmws_post_app, ["generate-config-variant", "--variant", "tx0-only", "--dry-run", "--format", "json"])
    assert result.exit_code == 0
    
    data = json.loads(result.stdout)
    assert data["variant"] == "tx0-only"
    
    # Check diffs
    diffs = {d["command"]: d for d in data["diffs"]}
    assert "ChanNAdcConfig" in diffs
    assert "arg2: 1 -> 0" in diffs["ChanNAdcConfig"]["arg_diffs"]
    
    assert "ChirpConfig" in diffs
    assert "arg9: 1 -> 0" in diffs["ChirpConfig"]["arg_diffs"]
    
    # No files should be written
    assert len(list(tmp_path.glob("*"))) == 0
    
    # Baseline must be completely unchanged
    assert VALIDATED_AWR2944_SMOKE_V0.commands == orig_cmds
    
    # We can also double-check by re-running validation
    val_res = runner.invoke(mmws_post_app, ["validate-frozen-config"])
    assert val_res.exit_code == 0

def test_generate_config_variant_samples_128():
    result = runner.invoke(mmws_post_app, ["generate-config-variant", "--variant", "samples-128", "--dry-run", "--format", "json"])
    assert result.exit_code == 0
    
    data = json.loads(result.stdout)
    diffs = {d["command"]: d for d in data["diffs"]}
    assert "ProfileConfig" in diffs
    assert "arg16: 256 -> 128" in diffs["ProfileConfig"]["arg_diffs"]
    
    # Warning should exist
    assert any("numAdcSamples changed to 128" in w for w in data["warnings"])

def test_frozen_config_inspect_json():
    result = runner.invoke(mmws_post_app, ["frozen-config-inspect", "--format", "json"])
    assert result.exit_code == 0
    
    data = json.loads(result.stdout)
    assert data["metadata"]["validation_status"] == "replay-validated locally"
    assert "channel_adc" in data["groups"]

def test_frozen_config_explain_json():
    result = runner.invoke(mmws_post_app, ["frozen-config-explain", "--format", "json"])
    assert result.exit_code == 0
    
    data = json.loads(result.stdout)
    assert len(data) == 13
    assert data[0]["command"] == "ChanNAdcConfig"
    assert data[0]["arg_count"] == 11
    assert data[0]["expected_arg_count"] == 11
