"""Tests for project/capture scaffolding (Phase 0).

All tests use tmp_path.  No hardware, no real mmWave Studio, no real
adc_data.bin.  Synthetic ADC files are generated in tmp_path.
"""

import json
import datetime
import hashlib
import numpy as np
from pathlib import Path

import pytest

from awr2944_dca.project import (
    atomic_json_write,
    bind_mmws_output,
    find_project_root,
    import_raw,
    init_project,
    inspect_capture,
    load_project,
    new_capture,
    project_status,
    safe_slug,
    GITIGNORE_RULES,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_project(tmp_path: Path, name: str = "test_proj", **kwargs) -> dict:
    """Initialize a project in tmp_path and return project dict."""
    return init_project(name=name, root=tmp_path, **kwargs)


def _make_capture(tmp_path: Path, capture_name: str = "test_cap",
                  _now: datetime.datetime | None = None) -> dict:
    """Create a capture in an already-initialized project."""
    return new_capture(tmp_path, capture_name, _now=_now)


def _generate_synthetic_adc(path: Path, size: int = 4_194_304) -> None:
    """Generate a synthetic ADC binary file of exactly *size* bytes.

    Uses int16 random values so the ADC parser can inspect it.
    """
    rng = np.random.RandomState(42)
    n_int16 = size // 2
    data = rng.randint(-32768, 32767, size=n_int16, dtype=np.int16)
    data.tofile(str(path))


def _make_fake_postproc(tmp_path: Path) -> Path:
    """Create a fake PostProc staging folder with adc_data.bin and metadata."""
    pp = tmp_path / "PostProc"
    pp.mkdir()
    _generate_synthetic_adc(pp / "adc_data.bin")
    (pp / "cf.json").write_text('{"test": true}', encoding="utf-8")
    (pp / "LogFile.txt").write_text("log content", encoding="utf-8")
    (pp / "CLI_LogFile.txt").write_text("cli log", encoding="utf-8")
    (pp / "dca_validation_abc.json").write_text('{"valid": true}', encoding="utf-8")
    # Static files that should NOT be copied
    (pp / "DCA1000EVM_CLI_Record.exe").write_bytes(b"\x00" * 100)
    (pp / "RF_API.dll").write_bytes(b"\x00" * 100)
    (pp / "Packet_Reorder_Zerofill.exe").write_bytes(b"\x00" * 100)
    return pp


# ---------------------------------------------------------------------------
# project init
# ---------------------------------------------------------------------------

def test_init_creates_project_json_and_dirs(tmp_path):
    proj = _make_project(tmp_path)

    pj = tmp_path / "project.json"
    assert pj.exists()
    data = json.loads(pj.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["name"] == "test_proj"
    assert data["project_id"]
    assert data["default_adc_config"]["frames"] == 8
    assert data["default_adc_config"]["layout_assumption_confirmed"] is False

    # Directories
    assert (tmp_path / "configs" / "mmws" / "lua").is_dir()
    assert (tmp_path / "configs" / "mmws" / "manifests").is_dir()
    assert (tmp_path / "configs" / "mmws" / "results").is_dir()
    assert (tmp_path / "configs" / "mmws" / "snapshots").is_dir()
    assert (tmp_path / "captures").is_dir()
    assert (tmp_path / "logs").is_dir()
    assert (tmp_path / "notebooks").is_dir()


def test_init_refuses_existing_without_force(tmp_path):
    _make_project(tmp_path)
    with pytest.raises(FileExistsError, match="already exists"):
        _make_project(tmp_path)


def test_init_force_overwrites(tmp_path):
    _make_project(tmp_path, name="old_name")
    proj = _make_project(tmp_path, name="new_name", force=True)
    assert proj["name"] == "new_name"
    data = json.loads((tmp_path / "project.json").read_text(encoding="utf-8"))
    assert data["name"] == "new_name"


def test_init_prints_absolute_paths(tmp_path):
    """Verify project dict contains absolute paths for root and postproc."""
    proj = _make_project(tmp_path, postproc_dir=str(tmp_path / "fake_pp"))
    assert Path(proj["root_path_abs"]).is_absolute()
    assert Path(proj["postproc_dir_abs"]).is_absolute()


# ---------------------------------------------------------------------------
# project status
# ---------------------------------------------------------------------------

def test_project_status_text(tmp_path):
    _make_project(tmp_path)
    status = project_status(tmp_path)
    assert status["project_name"] == "test_proj"
    assert status["capture_count"] == 0
    assert status["newest_capture"] is None


def test_project_status_json_valid(tmp_path):
    _make_project(tmp_path)
    status = project_status(tmp_path)
    # Must be JSON-serializable
    serialized = json.dumps(status, default=str)
    parsed = json.loads(serialized)
    assert parsed["project_name"] == "test_proj"


def test_project_status_counts_only_managed_captures(tmp_path):
    """Unmanaged folders under captures/ are not counted."""
    _make_project(tmp_path)

    # Create a managed capture
    _make_capture(tmp_path, "managed_one",
                  _now=datetime.datetime(2026, 1, 1, 12, 0, 0))

    # Create an unmanaged folder (no capture_manifest.json)
    unmanaged = tmp_path / "captures" / "random_folder"
    unmanaged.mkdir(parents=True)

    status = project_status(tmp_path)
    assert status["capture_count"] == 1


# ---------------------------------------------------------------------------
# .gitignore
# ---------------------------------------------------------------------------

def test_gitignore_entries_added(tmp_path):
    _make_project(tmp_path)
    gi = tmp_path / ".gitignore"
    assert gi.exists()
    content = gi.read_text(encoding="utf-8")
    assert "captures/**/raw/*.bin" in content
    assert "captures/**/processed/*.npy" in content
    assert "captures/**/metadata/mmws_logs/*.mat" in content


def test_gitignore_no_duplicates(tmp_path):
    _make_project(tmp_path)
    # Re-init with force — should not duplicate rules
    _make_project(tmp_path, force=True)
    content = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert content.count("captures/**/raw/*.bin") == 1


def test_gitignore_does_not_ignore_manifest_or_notes(tmp_path):
    _make_project(tmp_path)
    content = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "capture_manifest.json" not in content
    assert "notes.md" not in content
    # metadata/*.json should NOT be ignored
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue
        assert "metadata/*.json" not in stripped or "mmws_logs" in stripped


# ---------------------------------------------------------------------------
# capture new
# ---------------------------------------------------------------------------

def test_capture_new_creates_structure(tmp_path):
    _make_project(tmp_path)
    now = datetime.datetime(2026, 7, 10, 14, 30, 0)
    manifest = _make_capture(tmp_path, "Test Capture One", _now=now)

    cap_id = manifest["capture_id"]
    assert cap_id == "20260710_143000_test_capture_one"

    cap_dir = tmp_path / "captures" / cap_id
    assert cap_dir.is_dir()
    assert (cap_dir / "raw").is_dir()
    assert (cap_dir / "metadata" / "mmws_logs").is_dir()
    assert (cap_dir / "processed").is_dir()
    assert (cap_dir / "notes.md").exists()
    assert (cap_dir / "capture_manifest.json").exists()

    m = json.loads((cap_dir / "capture_manifest.json").read_text(encoding="utf-8"))
    assert m["schema_version"] == 1
    assert m["status"] == "created"
    assert m["capture_name"] == "Test Capture One"
    assert m["workflow_id"] is None
    assert m["firmware_run_id"] is None


def test_capture_slug_safe(tmp_path):
    _make_project(tmp_path)
    now = datetime.datetime(2026, 1, 1, 0, 0, 0)
    manifest = _make_capture(tmp_path, "My Test! @Capture#123", _now=now)
    slug_part = manifest["capture_id"].split("_", 2)[2]  # after YYYYMMDD_HHMMSS_
    assert " " not in slug_part
    assert slug_part == slug_part.lower()
    assert all(c.isalnum() or c in ("_", "-") for c in slug_part)


def test_capture_new_refuses_collision(tmp_path):
    _make_project(tmp_path)
    now = datetime.datetime(2026, 1, 1, 12, 0, 0)
    _make_capture(tmp_path, "same_name", _now=now)
    with pytest.raises(FileExistsError, match="already exists"):
        _make_capture(tmp_path, "same_name", _now=now)


# ---------------------------------------------------------------------------
# import-raw
# ---------------------------------------------------------------------------

def test_import_raw_copies_file(tmp_path):
    _make_project(tmp_path)
    now = datetime.datetime(2026, 1, 1, 12, 0, 0)
    manifest = _make_capture(tmp_path, "import_test", _now=now)

    src = tmp_path / "source_adc.bin"
    _generate_synthetic_adc(src)

    result = import_raw(tmp_path, manifest["capture_id"], source_path=src)

    dest = tmp_path / "captures" / manifest["capture_id"] / "raw" / "adc_data.bin"
    assert dest.exists()
    assert dest.stat().st_size == 4_194_304
    assert result["status"] in ("imported", "inspected")


def test_import_raw_sha256_and_size(tmp_path):
    _make_project(tmp_path)
    now = datetime.datetime(2026, 1, 1, 12, 0, 0)
    manifest = _make_capture(tmp_path, "hash_test", _now=now)

    src = tmp_path / "source_adc.bin"
    _generate_synthetic_adc(src)

    result = import_raw(tmp_path, manifest["capture_id"], source_path=src)

    assert result["actual_raw_file_size"] == 4_194_304
    assert result["raw_file_sha256"]
    assert len(result["raw_file_sha256"]) == 64  # hex SHA-256


def test_import_raw_refuses_overwrite_without_force(tmp_path):
    _make_project(tmp_path)
    now = datetime.datetime(2026, 1, 1, 12, 0, 0)
    manifest = _make_capture(tmp_path, "overwrite_test", _now=now)

    src = tmp_path / "source_adc.bin"
    _generate_synthetic_adc(src)
    import_raw(tmp_path, manifest["capture_id"], source_path=src)

    src2 = tmp_path / "source_adc2.bin"
    _generate_synthetic_adc(src2)
    with pytest.raises(FileExistsError, match="already exists"):
        import_raw(tmp_path, manifest["capture_id"], source_path=src2)


def test_import_raw_move_removes_source(tmp_path):
    _make_project(tmp_path)
    now = datetime.datetime(2026, 1, 1, 12, 0, 0)
    manifest = _make_capture(tmp_path, "move_test", _now=now)

    src = tmp_path / "source_adc.bin"
    _generate_synthetic_adc(src)

    import_raw(tmp_path, manifest["capture_id"], source_path=src, move=True)

    assert not src.exists()  # Source should be gone
    dest = tmp_path / "captures" / manifest["capture_id"] / "raw" / "adc_data.bin"
    assert dest.exists()


def test_import_raw_inspect_saves_json(tmp_path):
    _make_project(tmp_path)
    now = datetime.datetime(2026, 1, 1, 12, 0, 0)
    manifest = _make_capture(tmp_path, "inspect_test", _now=now)

    src = tmp_path / "source_adc.bin"
    _generate_synthetic_adc(src)

    result = import_raw(tmp_path, manifest["capture_id"], source_path=src,
                        inspect=True)

    inspect_path = (tmp_path / "captures" / manifest["capture_id"]
                    / "metadata" / "adc_inspect.json")
    assert inspect_path.exists()
    inspect_data = json.loads(inspect_path.read_text(encoding="utf-8"))
    assert inspect_data["size_match"] is True
    assert inspect_data["shape"] == [8, 128, 4, 256]
    assert result["status"] == "inspected"


def test_import_raw_rejects_wrong_size(tmp_path):
    _make_project(tmp_path)
    now = datetime.datetime(2026, 1, 1, 12, 0, 0)
    manifest = _make_capture(tmp_path, "wrong_size_test", _now=now)

    src = tmp_path / "bad_adc.bin"
    src.write_bytes(b"\x00" * 1000)  # Wrong size

    with pytest.raises(ValueError, match="size mismatch"):
        import_raw(tmp_path, manifest["capture_id"], source_path=src)

    # Manifest should be marked as error, not imported
    m_path = (tmp_path / "captures" / manifest["capture_id"]
              / "capture_manifest.json")
    m = json.loads(m_path.read_text(encoding="utf-8"))
    assert m["status"] == "error"
    assert len(m["errors"]) > 0


# ---------------------------------------------------------------------------
# bind-mmws-output
# ---------------------------------------------------------------------------

def test_bind_mmws_copies_adc_data(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    now = datetime.datetime(2026, 1, 1, 12, 0, 0)
    manifest = _make_capture(tmp_path, "bind_test", _now=now)

    result = bind_mmws_output(
        tmp_path, manifest["capture_id"], postproc_dir=str(pp)
    )

    dest = tmp_path / "captures" / manifest["capture_id"] / "raw" / "adc_data.bin"
    assert dest.exists()
    assert dest.stat().st_size == 4_194_304
    assert result["raw_file_sha256"]


def test_bind_mmws_copies_metadata_files(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    now = datetime.datetime(2026, 1, 1, 12, 0, 0)
    manifest = _make_capture(tmp_path, "meta_test", _now=now)

    result = bind_mmws_output(
        tmp_path, manifest["capture_id"], postproc_dir=str(pp)
    )

    meta_dir = (tmp_path / "captures" / manifest["capture_id"]
                / "metadata" / "mmws_logs")
    assert (meta_dir / "cf.json").exists()
    assert (meta_dir / "LogFile.txt").exists()
    assert (meta_dir / "CLI_LogFile.txt").exists()
    assert (meta_dir / "dca_validation_abc.json").exists()

    # Provenance recorded
    copied = result["copied_mmws_files"]
    assert len(copied) >= 3
    for entry in copied:
        assert "source_abs" in entry
        assert "dest_rel" in entry
        assert "size" in entry
        assert "sha256" in entry


def test_bind_mmws_does_not_move_postproc_files(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    now = datetime.datetime(2026, 1, 1, 12, 0, 0)
    manifest = _make_capture(tmp_path, "no_move_test", _now=now)

    bind_mmws_output(tmp_path, manifest["capture_id"], postproc_dir=str(pp))

    # All source files must still exist
    assert (pp / "adc_data.bin").exists()
    assert (pp / "cf.json").exists()
    assert (pp / "LogFile.txt").exists()
    assert (pp / "DCA1000EVM_CLI_Record.exe").exists()


def test_bind_mmws_does_not_copy_executables(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    now = datetime.datetime(2026, 1, 1, 12, 0, 0)
    manifest = _make_capture(tmp_path, "no_exe_test", _now=now)

    result = bind_mmws_output(
        tmp_path, manifest["capture_id"], postproc_dir=str(pp)
    )

    meta_dir = (tmp_path / "captures" / manifest["capture_id"]
                / "metadata" / "mmws_logs")
    # No executables or DLLs should be present
    assert not (meta_dir / "DCA1000EVM_CLI_Record.exe").exists()
    assert not (meta_dir / "RF_API.dll").exists()
    assert not (meta_dir / "Packet_Reorder_Zerofill.exe").exists()

    # Check provenance list doesn't include them
    for entry in result["copied_mmws_files"]:
        assert not entry["dest_rel"].endswith(".exe")
        assert not entry["dest_rel"].endswith(".dll")


# ---------------------------------------------------------------------------
# capture inspect
# ---------------------------------------------------------------------------

def test_capture_inspect_text(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    now = datetime.datetime(2026, 1, 1, 12, 0, 0)
    manifest = _make_capture(tmp_path, "inspect_text", _now=now)
    bind_mmws_output(tmp_path, manifest["capture_id"], postproc_dir=str(pp))

    info = inspect_capture(tmp_path, manifest["capture_id"])
    assert info["capture_id"] == manifest["capture_id"]
    assert info["raw_file_exists"] is True
    assert info["raw_file_size"] == 4_194_304
    assert info["size_match"] is True


def test_capture_inspect_json_valid(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    now = datetime.datetime(2026, 1, 1, 12, 0, 0)
    manifest = _make_capture(tmp_path, "inspect_json", _now=now)
    bind_mmws_output(tmp_path, manifest["capture_id"], postproc_dir=str(pp))

    info = inspect_capture(tmp_path, manifest["capture_id"])
    serialized = json.dumps(info, default=str)
    parsed = json.loads(serialized)
    assert parsed["capture_id"] == manifest["capture_id"]


def test_capture_inspect_refresh(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    now = datetime.datetime(2026, 1, 1, 12, 0, 0)
    manifest = _make_capture(tmp_path, "refresh_test", _now=now)
    bind_mmws_output(tmp_path, manifest["capture_id"], postproc_dir=str(pp))

    # Delete existing adc_inspect.json
    inspect_path = (tmp_path / "captures" / manifest["capture_id"]
                    / "metadata" / "adc_inspect.json")
    if inspect_path.exists():
        inspect_path.unlink()

    info = inspect_capture(
        tmp_path, manifest["capture_id"], refresh_adc_inspect=True
    )
    assert inspect_path.exists()
    assert info["adc_inspect"] is not None
    assert info["adc_inspect"]["shape"] == [8, 128, 4, 256]


# ---------------------------------------------------------------------------
# find_project_root
# ---------------------------------------------------------------------------

def test_find_project_root_from_nested(tmp_path):
    _make_project(tmp_path)
    nested = tmp_path / "captures" / "some_capture" / "raw"
    nested.mkdir(parents=True)

    found = find_project_root(nested)
    assert found == tmp_path.resolve()


def test_find_project_root_not_found(tmp_path):
    with pytest.raises(FileNotFoundError, match="project.json"):
        find_project_root(tmp_path)


# ---------------------------------------------------------------------------
# verify_capture
# ---------------------------------------------------------------------------

from awr2944_dca.project import verify_capture

def test_verify_capture_passes(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    now = datetime.datetime(2026, 1, 1, 12, 0, 0)
    manifest = _make_capture(tmp_path, "verify_pass", _now=now)
    bind_mmws_output(tmp_path, manifest["capture_id"], postproc_dir=str(pp))
    
    # Needs adc_inspect.json to pass completely if we generated it, but bind_mmws_output
    # doesn't generate adc_inspect.json by default unless inspect_capture does.
    # Let's run inspect_capture first.
    inspect_capture(tmp_path, manifest["capture_id"], refresh_adc_inspect=True)

    result = verify_capture(tmp_path, manifest["capture_id"])
    assert result["passed"] is True
    assert not result["errors"]

def test_verify_capture_missing_raw(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    manifest = _make_capture(tmp_path, "verify_missing_raw")
    bind_mmws_output(tmp_path, manifest["capture_id"], postproc_dir=str(pp))
    
    raw_path = tmp_path / "captures" / manifest["capture_id"] / "raw" / "adc_data.bin"
    raw_path.unlink()
    
    result = verify_capture(tmp_path, manifest["capture_id"])
    assert result["passed"] is False
    assert any("Raw file missing" in e for e in result["errors"])

def test_verify_capture_hash_mismatch(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    manifest = _make_capture(tmp_path, "verify_hash")
    bind_mmws_output(tmp_path, manifest["capture_id"], postproc_dir=str(pp))
    
    raw_path = tmp_path / "captures" / manifest["capture_id"] / "raw" / "adc_data.bin"
    raw_path.write_bytes(b"\x00" * 4_194_304) # overwrite with zeros, keeping size
    
    result = verify_capture(tmp_path, manifest["capture_id"])
    assert result["passed"] is False
    assert any("Actual raw SHA256" in e for e in result["errors"])

def test_verify_capture_missing_adc_inspect(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    manifest = _make_capture(tmp_path, "verify_missing_inspect")
    bind_mmws_output(tmp_path, manifest["capture_id"], postproc_dir=str(pp))
    inspect_capture(tmp_path, manifest["capture_id"], refresh_adc_inspect=True)
    
    inspect_path = tmp_path / "captures" / manifest["capture_id"] / "metadata" / "adc_inspect.json"
    inspect_path.unlink()
    
    result = verify_capture(tmp_path, manifest["capture_id"])
    assert result["passed"] is False
    assert any("adc_inspect.json missing" in e for e in result["errors"])

def test_verify_capture_adc_inspect_hash_mismatch(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    manifest = _make_capture(tmp_path, "verify_inspect_hash")
    bind_mmws_output(tmp_path, manifest["capture_id"], postproc_dir=str(pp))
    inspect_capture(tmp_path, manifest["capture_id"], refresh_adc_inspect=True)
    
    inspect_path = tmp_path / "captures" / manifest["capture_id"] / "metadata" / "adc_inspect.json"
    data = json.loads(inspect_path.read_text(encoding="utf-8"))
    data["sha256"] = "badhash"
    inspect_path.write_text(json.dumps(data), encoding="utf-8")
    
    result = verify_capture(tmp_path, manifest["capture_id"])
    assert result["passed"] is False
    assert any("adc_inspect sha256" in e for e in result["errors"])

def test_verify_capture_copied_mmws_hash_mismatch(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    manifest = _make_capture(tmp_path, "verify_copied_hash")
    bind_mmws_output(tmp_path, manifest["capture_id"], postproc_dir=str(pp))
    
    cf_path = tmp_path / "captures" / manifest["capture_id"] / "metadata" / "mmws_logs" / "cf.json"
    cf_path.write_text("bad data", encoding="utf-8")
    
    result = verify_capture(tmp_path, manifest["capture_id"])
    assert result["passed"] is False
    assert any("Copied file SHA256 mismatch" in e for e in result["errors"])

def test_project_status_counts_and_errors(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    
    # 1 bound
    m1 = _make_capture(tmp_path, "cap1")
    bind_mmws_output(tmp_path, m1["capture_id"], postproc_dir=str(pp))
    
    # 1 created
    m2 = _make_capture(tmp_path, "cap2")
    
    # 1 error
    m3 = _make_capture(tmp_path, "cap3")
    src = tmp_path / "bad_adc.bin"
    src.write_bytes(b"\x00" * 1000)
    try:
        import_raw(tmp_path, m3["capture_id"], source_path=src)
    except ValueError:
        pass
        
    status = project_status(tmp_path)
    assert status["capture_count"] == 3
    assert status["status_counts"]["inspected"] == 1
    assert status["status_counts"]["created"] == 1
    assert status["status_counts"]["error"] == 1
    
    assert len(status["error_captures"]) == 1
    assert status["error_captures"][0]["capture_id"] == m3["capture_id"]


from unittest.mock import patch

def test_verify_capture_passes_under_ignored_root(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    manifest = _make_capture(tmp_path, "verify_ignored")
    bind_mmws_output(tmp_path, manifest["capture_id"], postproc_dir=str(pp))
    inspect_capture(tmp_path, manifest["capture_id"], refresh_adc_inspect=True)
    # Using subprocess.run mock to simulate ignored root
    with patch("subprocess.run") as mock_run, patch("shutil.which", return_value="git"):
        mock_run.return_value.returncode = 0  # 0 means ignored in check-ignore
        result = verify_capture(tmp_path, manifest["capture_id"])
        assert result["passed"] is True
        assert any("ignored by Git; skipped" in w for w in result["warnings"])

def test_verify_capture_catches_hash_under_ignored_root(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    manifest = _make_capture(tmp_path, "verify_ignored_bad")
    bind_mmws_output(tmp_path, manifest["capture_id"], postproc_dir=str(pp))
    inspect_capture(tmp_path, manifest["capture_id"], refresh_adc_inspect=True)
    
    raw_path = tmp_path / "captures" / manifest["capture_id"] / "raw" / "adc_data.bin"
    raw_path.write_bytes(b"\x00" * 4194304)  # Break hash but keep size
    
    with patch("subprocess.run") as mock_run, patch("shutil.which", return_value="git"):
        mock_run.return_value.returncode = 0  # ignored root
        result = verify_capture(tmp_path, manifest["capture_id"])
        assert result["passed"] is False
        assert any("Actual raw SHA256" in e for e in result["errors"])
        assert any("ignored by Git; skipped" in w for w in result["warnings"])

def test_verify_capture_enforces_gitignore_on_normal_root(tmp_path):
    pp = _make_fake_postproc(tmp_path)
    _make_project(tmp_path, postproc_dir=str(pp))
    manifest = _make_capture(tmp_path, "verify_normal")
    bind_mmws_output(tmp_path, manifest["capture_id"], postproc_dir=str(pp))
    inspect_capture(tmp_path, manifest["capture_id"], refresh_adc_inspect=True)
    
    def mock_subprocess_run(args, **kwargs):
        from subprocess import CompletedProcess
        # is-inside-work-tree -> 0 (yes)
        if "rev-parse" in args:
            return CompletedProcess(args, 0, stdout=b"true")
        # root check-ignore -> 1 (not ignored)
        if args[-1] == str(tmp_path):
            return CompletedProcess(args, 1)
        # Let's say raw.bin IS NOT ignored (which is an error)
        if "adc_data.bin" in args[-1]:
            return CompletedProcess(args, 1)
        # Everything else is not ignored (which is fine for manifest/inspect)
        return CompletedProcess(args, 1)
    
    with patch("subprocess.run", side_effect=mock_subprocess_run), patch("shutil.which", return_value="git"):
        result = verify_capture(tmp_path, manifest["capture_id"])
        assert result["passed"] is False
        assert any("raw ADC file is not ignored by git" in e for e in result["errors"])

