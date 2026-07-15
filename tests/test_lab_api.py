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
from awr2944_dca.lab import EthernetManager, RadarCapture, RadarProject
from awr2944_dca.project import add_capture_note, add_capture_tags, bind_mmws_output, get_defaults, init_project, inspect_capture, new_capture, set_defaults
from awr2944_dca.dca.workflow import CaptureWorkflowState, RunMeta, save_state, start_workflow, resume_workflow
from awr2944_dca.eth import EthernetPairing, save_pairing

def _fake_preflight_ready(monkeypatch):
    """Monkeypatch preflight to return READY_WITH_WARNINGS."""
    from awr2944_dca.dca.preflight import PreflightCheck, PreflightReport

    def fake_preflight(**kwargs):
        return PreflightReport(overall='READY_WITH_WARNINGS', checks=[PreflightCheck('Adapter IP', 'PASS', 'OK'), PreflightCheck('Ping', 'WARN', 'No replies'), PreflightCheck('ARP', 'PASS', 'OK')])
    monkeypatch.setattr('awr2944_dca.dca.workflow.run_dca_preflight', fake_preflight)

def _make_project(tmp_path: Path, name: str='test_proj', **kwargs) -> dict:
    """Initialize a project in tmp_path."""
    return init_project(name=name, root=tmp_path, **kwargs)

def _generate_synthetic_adc(path: Path, size: int=4194304) -> None:
    """Generate a synthetic ADC binary file."""
    rng = np.random.RandomState(42)
    data = rng.randint(-32768, 32767, size=size // 2, dtype=np.int16)
    data.tofile(str(path))

def _make_fake_postproc(tmp_path: Path) -> Path:
    """Create a fake PostProc directory."""
    pp = tmp_path / 'PostProc'
    pp.mkdir()
    _generate_synthetic_adc(pp / 'adc_data.bin')
    (pp / 'cf.json').write_text('{"test": true}', encoding='utf-8')
    (pp / 'LogFile.txt').write_text('log content', encoding='utf-8')
    return pp

def _write_success_result(path: Path, run_id: str, stage: str=''):
    """Write a successful run result JSON."""
    path.write_text(json.dumps({'run_id': run_id, 'executed': True, 'success': True, 'error': '', 'warnings': [], 'stage': stage}), encoding='utf-8')

def _fake_eth_ready(monkeypatch, project_root: Path):
    """Monkeypatch eth to appear ready."""
    save_pairing(project_root, EthernetPairing(interface_alias='Eth5', interface_index=5, host_adapter_mac='AA:05', paired_at='2026-07-10T12:00:00'))

    def fake_check_status(pairing, host_ip='192.168.33.30'):
        return {'found': True, 'status': 'Up', 'has_correct_ip': True, 'ready': True, 'ipv4_addresses': ['192.168.33.30']}
    monkeypatch.setattr('awr2944_dca.eth.check_adapter_status', fake_check_status)

def test_open_project(tmp_path):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)
    assert lab.name == 'test_proj'
    assert lab.root == tmp_path.resolve()

def test_open_here_finds_project(tmp_path, monkeypatch):
    _make_project(tmp_path)
    nested = tmp_path / 'notebooks'
    nested.mkdir(exist_ok=True)
    monkeypatch.chdir(nested)
    lab = RadarProject.open_here()
    assert lab.name == 'test_proj'

def test_status_returns_dict(tmp_path):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)
    st = lab.status()
    assert isinstance(st, dict)
    assert st['project_name'] == 'test_proj'
    assert st['capture_count'] == 0

def test_set_defaults_persists(tmp_path):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)
    result = lab.set_defaults(firmware_run_id='abc123', config_run_id='def456')
    assert result['firmware_run_id'] == 'abc123'
    assert result['config_run_id'] == 'def456'
    lab2 = RadarProject.open(tmp_path)
    defaults = lab2.show_defaults()
    assert defaults['firmware_run_id'] == 'abc123'
    assert defaults['config_run_id'] == 'def456'
    assert defaults['archive_existing'] is True
    assert defaults['confirm_startframe'] is True
    assert defaults['bind_force'] is False

def test_set_defaults_rejects_unknown_keys(tmp_path):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)
    with pytest.raises(ValueError, match='Unknown default keys'):
        lab.set_defaults(nonexistent_key='bad')

def test_captures_returns_list(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    new_capture(tmp_path, 'cap1')
    new_capture(tmp_path, 'cap2')
    lab = RadarProject.open(tmp_path)
    caps = lab.captures()
    assert len(caps) == 2
    for c in caps:
        assert type(c).__name__ == "RadarCapture"

def test_get_capture_exact_match(tmp_path):
    _make_project(tmp_path)
    manifest = new_capture(tmp_path, 'exact_test')
    cid = manifest['capture_id']
    lab = RadarProject.open(tmp_path)
    cap = lab.get_capture(cid)
    assert cap.capture_id == cid

def test_get_capture_fuzzy_prefix(tmp_path):
    _make_project(tmp_path)
    manifest = new_capture(tmp_path, 'fuzzy_test', _now=datetime.datetime(2026, 1, 1, 12, 0, 0))
    cid = manifest['capture_id']
    lab = RadarProject.open(tmp_path)
    cap = lab.get_capture('20260101')
    assert cap.capture_id == cid

def test_get_capture_no_match_error(tmp_path):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)
    with pytest.raises(ValueError, match='No capture matching'):
        lab.get_capture('nonexistent')

def test_get_capture_ambiguous_error(tmp_path):
    _make_project(tmp_path)
    new_capture(tmp_path, 'ambig_one', _now=datetime.datetime(2026, 1, 1, 12, 0, 0))
    new_capture(tmp_path, 'ambig_two', _now=datetime.datetime(2026, 1, 1, 12, 0, 1))
    lab = RadarProject.open(tmp_path)
    with pytest.raises(ValueError, match='Ambiguous'):
        lab.get_capture('ambig')

def test_latest_capture(tmp_path):
    _make_project(tmp_path)
    new_capture(tmp_path, 'old_cap', _now=datetime.datetime(2026, 1, 1, 12, 0, 0))
    m2 = new_capture(tmp_path, 'new_cap', _now=datetime.datetime(2026, 6, 15, 12, 0, 0))
    lab = RadarProject.open(tmp_path)
    cap = lab.latest_capture()
    assert cap.capture_id == m2['capture_id']

def test_verify_wraps_verify_capture(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    manifest = new_capture(tmp_path, 'verify_test')
    bind_mmws_output(tmp_path, manifest['capture_id'], postproc_dir=str(pp))
    inspect_capture(tmp_path, manifest['capture_id'], refresh_adc_inspect=True)
    cap = RadarCapture(tmp_path, manifest['capture_id'])
    result = cap.verify()
    # CaptureVerificationReport supports dict-style access
    assert 'passed' in result

def test_inspect_adc_wraps_inspect_capture(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    manifest = new_capture(tmp_path, 'inspect_test')
    bind_mmws_output(tmp_path, manifest['capture_id'], postproc_dir=str(pp))
    cap = RadarCapture(tmp_path, manifest['capture_id'])
    result = cap.inspect_adc(refresh=True)
    assert isinstance(result, dict)
    assert 'adc_inspect' in result

def test_add_note_appends_timestamped(tmp_path):
    _make_project(tmp_path)
    manifest = new_capture(tmp_path, 'note_test')
    cap = RadarCapture(tmp_path, manifest['capture_id'])
    cap.add_note('Corner reflector at 2m')
    content = cap.notes()
    assert 'Corner reflector at 2m' in content
    assert '**[' in content

def test_add_tags_updates_manifest(tmp_path):
    _make_project(tmp_path)
    manifest = new_capture(tmp_path, 'tag_test')
    cap = RadarCapture(tmp_path, manifest['capture_id'])
    result = cap.add_tags('baseline', 'corner-reflector')
    assert 'baseline' in result
    assert 'corner-reflector' in result
    cap.refresh()
    assert 'baseline' in cap.project_record['tags']

def test_notes_reads_content(tmp_path):
    _make_project(tmp_path)
    manifest = new_capture(tmp_path, 'notes_read_test')
    cap = RadarCapture(tmp_path, manifest['capture_id'])
    content = cap.notes()
    assert 'notes_read_test' in content

def test_project_repr(tmp_path):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)
    r = repr(lab)
    assert 'RadarProject' in r
    assert 'test_proj' in r

def test_project_repr_html(tmp_path):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)
    html = lab._repr_html_()
    assert '<div' in html
    assert 'test_proj' in html

def test_capture_repr_html(tmp_path):
    _make_project(tmp_path)
    manifest = new_capture(tmp_path, 'repr_test')
    cap = RadarCapture(tmp_path, manifest['capture_id'])
    html = cap._repr_html_()
    assert '<div' in html
    assert 'repr_test' in html

def test_open_viewer_missing_canonical(tmp_path, capsys):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)
    manifest = new_capture(tmp_path, 'missing_bin_cap')
    cap = lab.get_capture('missing_bin_cap')
    cap.open_viewer()
    out, _ = capsys.readouterr()
    assert 'Canonical raw data missing' in out

def test_open_viewer_delegates_to_production_viewer(tmp_path, monkeypatch):
    _make_project(tmp_path)
    lab = RadarProject.open(tmp_path)
    manifest = new_capture(tmp_path, 'viewer_cap')
    capture_id = manifest['capture_id']
    cap_dir = tmp_path / 'captures' / capture_id
    cap_dir.mkdir(parents=True, exist_ok=True)
    canonical = cap_dir / 'adc_data_canonical.bin'
    canonical.write_bytes(b'dummy')
    from awr2944_dca.radar_config import smoke_config_preset
    cfg_lines = smoke_config_preset().to_lua().splitlines()
    manifest['radar_config'] = cfg_lines
    manifest_path = cap_dir / 'capture_manifest.json'
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    cap = lab.get_capture('viewer_cap')
    mock_args = {}

    def mock_launch(capture_path, profile, mode, matlab_script_dir):
        mock_args['capture_path'] = capture_path
        mock_args['profile'] = profile
        mock_args['mode'] = mode
        mock_args['matlab_script_dir'] = matlab_script_dir
    monkeypatch.setattr('awr2944_dca.viewer.export_viewer_payload_and_launch', mock_launch)
    cap.open_viewer()
    assert mock_args['capture_path'] == canonical
    assert mock_args['mode'] == 'standalone'
    assert mock_args['profile'] is not None
    assert 'viewer' in str(mock_args['matlab_script_dir'])
def test_capture_path_accessor(tmp_path):
    _make_project(tmp_path)
    manifest = new_capture(tmp_path, 'path_test')
    cap = RadarCapture(tmp_path, manifest['capture_id'])
    assert hasattr(cap, 'path')
    expected_path = tmp_path / 'captures' / manifest['capture_id']
    assert cap.path == expected_path
    assert cap.path.is_absolute() == tmp_path.is_absolute()
