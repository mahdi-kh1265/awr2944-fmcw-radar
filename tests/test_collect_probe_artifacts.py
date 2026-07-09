from __future__ import annotations

import importlib.util
import json
import os
import time
import zipfile
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "tools" / "collect_probe_artifacts.py"
SPEC = importlib.util.spec_from_file_location("collect_probe_artifacts", SCRIPT_PATH)
assert SPEC is not None
collector = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(collector)


def _write(path: Path, content: str = "artifact") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_creates_zip_and_includes_expected_files(tmp_path):
    probe_dir = tmp_path / "ti" / "probe_logs"
    expected_names = {
        "guided_connect_state.json",
        "run_manifest.json",
        "run_result.json",
        "run_progress.jsonl",
        "run_snapshot.txt",
        "manual_check_result.json",
        "manual_check_output_tail.txt",
        "gui_connect_windows.txt",
        "validation_20260707_131318.json",
        "nested/nested_result.json",
    }
    ignored_names = {
        "raw_adc.bin",
        "probe.lua",
        "gui_connect_controls.txt",
        "notes.txt",
    }

    for name in expected_names | ignored_names:
        _write(probe_dir / name, content=f"content for {name}")

    out = tmp_path / "artifacts" / "debug_bundle.zip"
    manifest = collector.collect_artifacts(probe_dir, out)

    assert out.exists()
    assert manifest["file_count"] == len(expected_names)

    with zipfile.ZipFile(out) as bundle:
        names = set(bundle.namelist())
        assert "bundle_manifest.json" in names
        for name in expected_names:
            assert name in names
        for name in ignored_names:
            assert name not in names


def test_bundle_manifest_is_valid_json_with_hashes(tmp_path):
    probe_dir = tmp_path / "probe_logs"
    _write(probe_dir / "abc_result.json", '{"ok": true}\n')
    _write(probe_dir / "abc_progress.jsonl", '{"step": 1}\n')

    out = tmp_path / "bundle.zip"
    collector.collect_artifacts(probe_dir, out)

    with zipfile.ZipFile(out) as bundle:
        manifest = json.loads(bundle.read("bundle_manifest.json"))

    assert manifest["schema_version"] == 1
    assert manifest["file_count"] == 2
    assert {entry["path"] for entry in manifest["files"]} == {
        "abc_progress.jsonl",
        "abc_result.json",
    }
    for entry in manifest["files"]:
        assert entry["size"] > 0
        assert entry["mtime"] > 0
        assert entry["mtime_ns"] > 0
        assert len(entry["sha256"]) == 64


def test_source_files_are_unchanged(tmp_path):
    probe_dir = tmp_path / "probe_logs"
    source = _write(probe_dir / "unchanged_result.json", '{"status": "same"}\n')

    before_bytes = source.read_bytes()
    before_mtime_ns = source.stat().st_mtime_ns

    collector.collect_artifacts(probe_dir, tmp_path / "bundle.zip")

    assert source.read_bytes() == before_bytes
    assert source.stat().st_mtime_ns == before_mtime_ns


def test_handles_missing_probe_dir_with_clear_error(tmp_path, capsys):
    rc = collector.main(
        [
            "--probe-dir",
            str(tmp_path / "missing"),
            "--out",
            str(tmp_path / "bundle.zip"),
        ]
    )

    captured = capsys.readouterr()
    assert rc == 1
    assert "probe_dir does not exist" in captured.err


def test_handles_empty_probe_dir_gracefully(tmp_path):
    probe_dir = tmp_path / "probe_logs"
    probe_dir.mkdir()
    out = tmp_path / "empty_bundle.zip"

    manifest = collector.collect_artifacts(probe_dir, out)

    assert manifest["file_count"] == 0
    with zipfile.ZipFile(out) as bundle:
        assert bundle.namelist() == ["bundle_manifest.json"]
        bundled_manifest = json.loads(bundle.read("bundle_manifest.json"))
    assert bundled_manifest["files"] == []


def test_latest_alias_only_includes_recent_matching_files(tmp_path):
    probe_dir = tmp_path / "probe_logs"
    old_file = _write(probe_dir / "old_result.json", "old")
    recent_file = _write(probe_dir / "recent_result.json", "recent")

    now = time.time()
    os.utime(old_file, (now - 3600, now - 3600))
    os.utime(recent_file, (now - 60, now - 60))

    out = tmp_path / "latest_bundle.zip"
    rc = collector.main(
        [
            "--probe-dir",
            str(probe_dir),
            "--latest",
            "30",
            "--out",
            str(out),
        ]
    )

    assert rc == 0
    with zipfile.ZipFile(out) as bundle:
        names = set(bundle.namelist())
    assert "recent_result.json" in names
    assert "old_result.json" not in names


def test_rejects_output_inside_probe_dir(tmp_path):
    probe_dir = tmp_path / "probe_logs"
    _write(probe_dir / "abc_result.json")

    with pytest.raises(collector.ArtifactCollectionError, match="outside probe_dir"):
        collector.collect_artifacts(probe_dir, probe_dir / "debug_bundle.zip")


def test_main_prints_success_summary(tmp_path, capsys):
    probe_dir = tmp_path / "probe_logs"
    guided = _write(probe_dir / "guided_connect_state.json", "guided-state")
    validation = _write(probe_dir / "validation_20260707_131318.json", "{}\n")
    result = _write(probe_dir / "probe_result.json", "{\"ok\": true}\n")
    _write(probe_dir / "capture.bin", "raw-adc")
    out = tmp_path / "artifacts" / "debug_bundle.zip"

    rc = collector.main(
        [
            "--probe-dir",
            str(probe_dir),
            "--out",
            str(out),
        ]
    )

    captured = capsys.readouterr()
    total_size = (
        guided.stat().st_size
        + validation.stat().st_size
        + result.stat().st_size
    )
    expected_lines = [
        "Probe artifact bundle created:",
        f"  output_zip: {out.resolve()}",
        "  files_included: 3",
        f"  total_uncompressed_bytes: {total_size}",
        "  guided_states_included: yes",
        "  validation_records_included: yes",
        "  note: raw ADC .bin files are excluded by default",
    ]

    assert rc == 0
    assert captured.out.splitlines() == expected_lines
    with zipfile.ZipFile(out) as bundle:
        assert "capture.bin" not in bundle.namelist()