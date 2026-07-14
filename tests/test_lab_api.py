"""Tests for Jupyter-friendly lab API (lab.py).

All tests use tmp_path and monkeypatched preflight.
No hardware, no real mmWave Studio, no real adc_data.bin.
"""

import json
import datetime
import os
import time
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from awr2944_dca.lab import (
    CaptureSmokeRun,
    EthernetManager,
    RadarCapture,
    RadarProject,
)
from awr2944_dca.project import (
    add_capture_note,
    add_capture_tags,
    bind_mmws_output,
    get_defaults,
    init_project,
    inspect_capture,
    new_capture,
    set_defaults,
)
from awr2944_dca.dca.workflow import (
    CaptureWorkflowState,
    RunMeta,
    save_state,
    start_workflow,
    resume_workflow,
)
from awr2944_dca.eth import (
    EthernetPairing,
    save_pairing,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fake_preflight_ready(monkeypatch):
    """Monkeypatch preflight to return READY_WITH_WARNINGS."""
    from awr2944_dca.dca.preflight import PreflightCheck, PreflightReport

    def fake_preflight(**kwargs):
        return PreflightReport(
            overall="READY_WITH_WARNINGS",
            checks=[
                PreflightCheck("Adapter IP", "PASS", "OK"),
                PreflightCheck("Ping", "WARN", "No replies"),
                PreflightCheck("ARP", "PASS", "OK"),
            ],
        )

    monkeypatch.setattr("awr2944_dca.dca.workflow.run_dca_preflight", fake_preflight)


def _make_project(tmp_path: Path, name: str = "test_proj", **kwargs) -> dict:
    """Initialize a project in tmp_path."""
    return init_project(name=name, root=tmp_path, **kwargs)


def _generate_synthetic_adc(path: Path, size: int = 4_194_304) -> None:
    """Generate a synthetic ADC binary file."""
    rng = np.random.RandomState(42)
    data = rng.randint(-32768, 32767, size=size // 2, dtype=np.int16)
    data.tofile(str(path))


def _make_fake_postproc(tmp_path: Path) -> Path:
    """Create a fake PostProc directory."""
    pp = tmp_path / "PostProc"
    pp.mkdir()
    _generate_synthetic_adc(pp / "adc_data.bin")
    (pp / "cf.json").write_text('{"test": true}', encoding="utf-8")
    (pp / "LogFile.txt").write_text("log content", encoding="utf-8")
    return pp


def _write_success_result(path: Path, run_id: str, stage: str = ""):
    """Write a successful run result JSON."""
    path.write_text(json.dumps({
        "run_id": run_id,
        "executed": True,
        "success": True,
        "error": "",
        "warnings": [],
        "stage": stage,
    }), encoding="utf-8")


def _fake_eth_ready(monkeypatch, project_root: Path):
    """Monkeypatch eth to appear ready."""
    save_pairing(project_root, EthernetPairing(
        interface_alias="Eth5",
        interface_index=5,
        host_adapter_mac="AA:05",
        paired_at="2026-07-10T12:00:00",
    ))

    def fake_check_status(pairing, host_ip="192.168.33.30"):
        return {
            "found": True, "status": "Up",
            "has_correct_ip": True, "ready": True,
            "ipv4_addresses": ["192.168.33.30"],
        }

    monkeypatch.setattr("awr2944_dca.eth.check_adapter_status", fake_check_status)


# ---------------------------------------------------------------------------
# Project operations
# ---------------------------------------------------------------------------

def test_open_project(tmp_path):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)
    assert lab.name == "test_proj"
    assert lab.root == tmp_path.resolve()


def test_open_here_finds_project(tmp_path, monkeypatch):
    _make_project(tmp_path)
    nested = tmp_path / "notebooks"
    nested.mkdir(exist_ok=True)
    monkeypatch.chdir(nested)
    lab = RadarProject.open_here()
    assert lab.name == "test_proj"


def test_status_returns_dict(tmp_path):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)
    st = lab.status()
    assert isinstance(st, dict)
    assert st["project_name"] == "test_proj"
    assert st["capture_count"] == 0


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

def test_set_defaults_persists(tmp_path):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)

    result = lab.set_defaults(firmware_run_id="abc123", config_run_id="def456")
    assert result["firmware_run_id"] == "abc123"
    assert result["config_run_id"] == "def456"

    # Persisted across re-open
    lab2 = RadarProject.open(tmp_path)
    defaults = lab2.show_defaults()
    assert defaults["firmware_run_id"] == "abc123"
    assert defaults["config_run_id"] == "def456"
    # Other defaults retain fallback values
    assert defaults["archive_existing"] is True
    assert defaults["confirm_startframe"] is True
    assert defaults["bind_force"] is False


def test_set_defaults_rejects_unknown_keys(tmp_path):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)

    with pytest.raises(ValueError, match="Unknown default keys"):
        lab.set_defaults(nonexistent_key="bad")


# ---------------------------------------------------------------------------
# Captures
# ---------------------------------------------------------------------------

def test_captures_returns_list(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    new_capture(tmp_path, "cap1")
    new_capture(tmp_path, "cap2")

    lab = RadarProject.open(tmp_path)
    caps = lab.captures()
    assert len(caps) == 2
    assert all(isinstance(c, RadarCapture) for c in caps)


def test_get_capture_exact_match(tmp_path):
    _make_project(tmp_path)
    manifest = new_capture(tmp_path, "exact_test")
    cid = manifest["capture_id"]

    lab = RadarProject.open(tmp_path)
    cap = lab.get_capture(cid)
    assert cap.capture_id == cid


def test_get_capture_fuzzy_prefix(tmp_path):
    _make_project(tmp_path)
    manifest = new_capture(tmp_path, "fuzzy_test",
                          _now=datetime.datetime(2026, 1, 1, 12, 0, 0))
    cid = manifest["capture_id"]

    lab = RadarProject.open(tmp_path)
    # Match by date prefix
    cap = lab.get_capture("20260101")
    assert cap.capture_id == cid


def test_get_capture_no_match_error(tmp_path):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)

    with pytest.raises(ValueError, match="No capture matching"):
        lab.get_capture("nonexistent")


def test_get_capture_ambiguous_error(tmp_path):
    _make_project(tmp_path)
    new_capture(tmp_path, "ambig_one",
               _now=datetime.datetime(2026, 1, 1, 12, 0, 0))
    new_capture(tmp_path, "ambig_two",
               _now=datetime.datetime(2026, 1, 1, 12, 0, 1))

    lab = RadarProject.open(tmp_path)
    with pytest.raises(ValueError, match="Ambiguous"):
        lab.get_capture("ambig")


def test_latest_capture(tmp_path):
    _make_project(tmp_path)
    new_capture(tmp_path, "old_cap",
               _now=datetime.datetime(2026, 1, 1, 12, 0, 0))
    m2 = new_capture(tmp_path, "new_cap",
                    _now=datetime.datetime(2026, 6, 15, 12, 0, 0))

    lab = RadarProject.open(tmp_path)
    cap = lab.latest_capture()
    assert cap.capture_id == m2["capture_id"]


# ---------------------------------------------------------------------------
# Capture smoke workflow
# ---------------------------------------------------------------------------

def test_capture_smoke_creates_workflow(tmp_path, monkeypatch):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    set_defaults(tmp_path, firmware_run_id="", config_run_id="")
    _fake_preflight_ready(monkeypatch)
    _fake_eth_ready(monkeypatch, tmp_path)

    lab = RadarProject.open(tmp_path)
    run = lab.capture_smoke("test_smoke")

    assert isinstance(run, CaptureSmokeRun)
    assert run.workflow_id
    assert "dca_setup" in run.status()["current_stage"]


def test_capture_smoke_uses_defaults(tmp_path, monkeypatch):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))

    # Set firmware/config IDs
    fw_result_path = tmp_path / "ti" / "probe_logs" / "fw123_result.json"
    fw_result_path.parent.mkdir(parents=True, exist_ok=True)
    _write_success_result(fw_result_path, "fw123", "firmware_power")

    cfg_result_path = tmp_path / "ti" / "probe_logs" / "cfg456_result.json"
    _write_success_result(cfg_result_path, "cfg456", "smoke_config")

    set_defaults(tmp_path, firmware_run_id="fw123", config_run_id="cfg456")
    _fake_preflight_ready(monkeypatch)
    _fake_eth_ready(monkeypatch, tmp_path)

    lab = RadarProject.open(tmp_path)
    run = lab.capture_smoke("defaults_test")

    # Verify the workflow picked up the defaults
    st = run.status()
    assert st["workflow_id"]


def test_capture_smoke_skip_eth(tmp_path, monkeypatch):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    set_defaults(tmp_path, firmware_run_id="", config_run_id="")
    _fake_preflight_ready(monkeypatch)

    lab = RadarProject.open(tmp_path)
    # ensure_eth=False should skip the check even without pairing
    run = lab.capture_smoke("no_eth_test", ensure_eth=False)
    assert isinstance(run, CaptureSmokeRun)


def test_run_next_returns_dofile(tmp_path, monkeypatch):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    set_defaults(tmp_path, firmware_run_id="", config_run_id="")
    _fake_preflight_ready(monkeypatch)
    _fake_eth_ready(monkeypatch, tmp_path)

    lab = RadarProject.open(tmp_path)
    run = lab.capture_smoke("dofile_test")

    action = run.next()
    assert "dofile" in action.lower() or "paste" in action.lower()

    dofile = run.dofile()
    assert "dofile" in dofile.lower()


def test_run_resume_advances_workflow(tmp_path, monkeypatch):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    set_defaults(tmp_path, firmware_run_id="", config_run_id="")
    _fake_preflight_ready(monkeypatch)
    _fake_eth_ready(monkeypatch, tmp_path)

    lab = RadarProject.open(tmp_path)
    run = lab.capture_smoke("resume_test")

    # Write a successful result for the dca_setup step
    state = run._state
    result_path = Path(state.dca_setup.result_path)
    _write_success_result(result_path, state.dca_setup.run_id, "dca_setup")
    time.sleep(0.1)  # ensure mtime > generated_at

    run = run.resume()
    # Should have advanced past dca_setup
    assert run.status()["current_stage"] != "dca_setup_script_generated"


def test_resume_always_returns_self(tmp_path, monkeypatch):
    """CaptureSmokeRun.resume() must always return CaptureSmokeRun, not RadarCapture."""
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    set_defaults(tmp_path, firmware_run_id="", config_run_id="")
    _fake_preflight_ready(monkeypatch)
    _fake_eth_ready(monkeypatch, tmp_path)

    lab = RadarProject.open(tmp_path)
    run = lab.capture_smoke("resume_self_test")

    result = run.resume()
    assert isinstance(result, CaptureSmokeRun)


def test_completed_run_returns_capture(tmp_path, monkeypatch):
    """After a full workflow, run.capture() should return RadarCapture."""
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    set_defaults(tmp_path, firmware_run_id="", config_run_id="")
    _fake_preflight_ready(monkeypatch)
    _fake_eth_ready(monkeypatch, tmp_path)

    lab = RadarProject.open(tmp_path)
    run = lab.capture_smoke("full_workflow_test")

    # archive_existing=True moved the original adc_data.bin.
    # Recreate it to simulate mmWave Studio producing a fresh file
    # after DCA setup + capture + postproc.
    _generate_synthetic_adc(pp / "adc_data.bin")

    # Step through entire workflow with fake results
    state = run._state

    # DCA setup
    _write_success_result(Path(state.dca_setup.result_path), state.dca_setup.run_id)
    time.sleep(0.1)
    run = run.resume()

    # Capture trigger
    state = run._state
    _write_success_result(
        Path(state.capture_trigger.result_path),
        state.capture_trigger.run_id,
    )
    time.sleep(0.1)
    run = run.resume()

    # Postproc — ensure adc_data.bin is present (postproc produces it)
    _generate_synthetic_adc(pp / "adc_data.bin")
    state = run._state
    _write_success_result(Path(state.postproc.result_path), state.postproc.run_id)
    time.sleep(0.1)
    run = run.resume()

    # Now should be complete
    assert run._state.completed
    cap = run.capture()
    assert cap is not None
    assert isinstance(cap, RadarCapture)


# ---------------------------------------------------------------------------
# RadarCapture
# ---------------------------------------------------------------------------

def test_verify_wraps_verify_capture(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    manifest = new_capture(tmp_path, "verify_test")
    bind_mmws_output(tmp_path, manifest["capture_id"], postproc_dir=str(pp))
    inspect_capture(tmp_path, manifest["capture_id"], refresh_adc_inspect=True)

    cap = RadarCapture(tmp_path, manifest["capture_id"])
    result = cap.verify()
    assert isinstance(result, dict)
    assert "passed" in result


def test_inspect_adc_wraps_inspect_capture(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    manifest = new_capture(tmp_path, "inspect_test")
    bind_mmws_output(tmp_path, manifest["capture_id"], postproc_dir=str(pp))

    cap = RadarCapture(tmp_path, manifest["capture_id"])
    result = cap.inspect_adc(refresh=True)
    assert isinstance(result, dict)
    assert "adc_inspect" in result


def test_add_note_appends_timestamped(tmp_path):
    _make_project(tmp_path)
    manifest = new_capture(tmp_path, "note_test")

    cap = RadarCapture(tmp_path, manifest["capture_id"])
    cap.add_note("Corner reflector at 2m")

    content = cap.notes()
    assert "Corner reflector at 2m" in content
    assert "**[" in content  # timestamped


def test_add_tags_updates_manifest(tmp_path):
    _make_project(tmp_path)
    manifest = new_capture(tmp_path, "tag_test")

    cap = RadarCapture(tmp_path, manifest["capture_id"])
    result = cap.add_tags("baseline", "corner-reflector")
    assert "baseline" in result
    assert "corner-reflector" in result

    # Verify through manifest
    cap.refresh()
    assert "baseline" in cap.manifest["tags"]


def test_notes_reads_content(tmp_path):
    _make_project(tmp_path)
    manifest = new_capture(tmp_path, "notes_read_test")

    cap = RadarCapture(tmp_path, manifest["capture_id"])
    content = cap.notes()
    assert "notes_read_test" in content  # default heading


# ---------------------------------------------------------------------------
# Workflow recovery
# ---------------------------------------------------------------------------

def test_workflows_lists_state_files(tmp_path, monkeypatch):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    set_defaults(tmp_path, firmware_run_id="", config_run_id="")
    _fake_preflight_ready(monkeypatch)
    _fake_eth_ready(monkeypatch, tmp_path)

    lab = RadarProject.open(tmp_path)
    run = lab.capture_smoke("wf_list_test")

    wfs = lab.workflows()
    assert len(wfs) >= 1
    assert any(w["workflow_id"] == run.workflow_id for w in wfs)


def test_latest_workflow_reconnects(tmp_path, monkeypatch):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    set_defaults(tmp_path, firmware_run_id="", config_run_id="")
    _fake_preflight_ready(monkeypatch)
    _fake_eth_ready(monkeypatch, tmp_path)

    lab = RadarProject.open(tmp_path)
    run = lab.capture_smoke("latest_wf_test")

    recovered = lab.latest_workflow()
    assert recovered.workflow_id == run.workflow_id


def test_get_workflow_by_id(tmp_path, monkeypatch):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    set_defaults(tmp_path, firmware_run_id="", config_run_id="")
    _fake_preflight_ready(monkeypatch)
    _fake_eth_ready(monkeypatch, tmp_path)

    lab = RadarProject.open(tmp_path)
    run = lab.capture_smoke("get_wf_test")

    recovered = lab.get_workflow(run.workflow_id)
    assert recovered.workflow_id == run.workflow_id


# ---------------------------------------------------------------------------
# Repr / display
# ---------------------------------------------------------------------------

def test_project_repr(tmp_path):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)
    r = repr(lab)
    assert "RadarProject" in r
    assert "test_proj" in r


def test_project_repr_html(tmp_path):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)
    html = lab._repr_html_()
    assert "<div" in html
    assert "test_proj" in html


def test_capture_repr_html(tmp_path):
    _make_project(tmp_path)
    manifest = new_capture(tmp_path, "repr_test")
    cap = RadarCapture(tmp_path, manifest["capture_id"])
    html = cap._repr_html_()
    assert "<div" in html
    assert "repr_test" in html


def test_run_repr(tmp_path, monkeypatch):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    set_defaults(tmp_path, firmware_run_id="", config_run_id="")
    _fake_preflight_ready(monkeypatch)
    _fake_eth_ready(monkeypatch, tmp_path)

    lab = RadarProject.open(tmp_path)
    run = lab.capture_smoke("repr_run_test")
    r = repr(run)
    assert "CaptureSmokeRun" in r

# ---------------------------------------------------------------------------
# open_viewer Tests
# ---------------------------------------------------------------------------

def test_open_viewer_missing_canonical(tmp_path, capsys):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)
    manifest = new_capture(tmp_path, "missing_bin_cap")
    cap = lab.get_capture("missing_bin_cap")
    
    cap.open_viewer()
    out, _ = capsys.readouterr()
    assert "Canonical raw data missing" in out

def test_open_viewer_delegates_to_production_viewer(tmp_path, monkeypatch):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)
    manifest = new_capture(tmp_path, "viewer_cap")
    capture_id = manifest["capture_id"]
    
    # Create a fake canonical file
    cap_dir = tmp_path / "captures" / capture_id
    cap_dir.mkdir(parents=True, exist_ok=True)
    canonical = cap_dir / "adc_data_canonical.bin"
    canonical.write_bytes(b"dummy")
    
    # Inject a fake radar config into the manifest
    # (this simulates a real capture's manifest)
    from awr2944_dca.radar_config import smoke_config_preset
    cfg_lines = smoke_config_preset().to_lua().splitlines()
    manifest["radar_config"] = cfg_lines
    manifest_path = cap_dir / "capture_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    
    cap = lab.get_capture("viewer_cap")
    
    # Mock the viewer launcher
    mock_args = {}
    def mock_launch(capture_path, profile, mode, matlab_script_dir):
        mock_args["capture_path"] = capture_path
        mock_args["profile"] = profile
        mock_args["mode"] = mode
        mock_args["matlab_script_dir"] = matlab_script_dir
        
    monkeypatch.setattr("awr2944_dca.viewer.export_viewer_payload_and_launch", mock_launch)
    
    cap.open_viewer()
    
    assert mock_args["capture_path"] == canonical
    assert mock_args["mode"] == "standalone"
    # Profile should have the frame count from the config
    assert mock_args["profile"] is not None
    assert "viewer" in str(mock_args["matlab_script_dir"])
