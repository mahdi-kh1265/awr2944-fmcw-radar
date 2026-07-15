"""Project and capture folder management for AWR2944 radar experiments.

Provides importable functions for creating, organizing, and managing
mmWave Studio/DCA captures with structured metadata, ADC parser
inspection results, and reproducible project scaffolding.

This module is the library layer.  CLI commands in ``cli.py`` are thin
wrappers over these functions.  Future Jupyter integration should call
this layer directly.

Phase 0 constraints:
    - Filesystem/data-model scaffolding only
    - No hardware capture automation
    - No mmWave Studio GUI automation
    - No automatic Lua execution
    - No FFT/DSP
    - PostProc directory treated as read-only staging
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import shutil
import tempfile
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Literal


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_VERSION = 1
PROJECT_MARKER = "project.json"

DEFAULT_POSTPROC_DIR = r"C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc"
DEFAULT_PROBE_DIR = r"ti\probe_logs"
DEFAULT_EXPECTED_BYTES = 4_194_304

GITIGNORE_RULES = [
    "# AWR project: large binary artifacts (auto-managed)",
    "captures/**/raw/*.bin",
    "captures/**/raw/*.dat",
    "captures/**/processed/*.npy",
    "captures/**/processed/*.npz",
    "captures/**/processed/*.mat",
    "captures/**/processed/*.fig",
    "captures/**/processed/*.png",
    "captures/**/metadata/mmws_logs/*.mat",
    "captures/**/metadata/mmws_logs/*.fig",
    "captures/**/metadata/mmws_logs/*.png",
]

# PostProc static files that should never be copied
_POSTPROC_STATIC_EXTENSIONS = frozenset({
    ".exe", ".dll", ".pdb", ".lib", ".exp",
})

# PostProc metadata files worth copying (by exact name or glob pattern)
_POSTPROC_METADATA_FILES = [
    "cf.json",
    "LogFile.txt",
    "CLI_LogFile.txt",
    "adc_data_LogFile.txt",
    "adc_data_Raw_LogFile.csv",
]

# Glob patterns for validation JSONs
_POSTPROC_VALIDATION_GLOB = "dca_validation_*.json"

# Maximum size for PackFile.mat copy (50 MB)
_MAX_MAT_FILE_BYTES = 50 * 1024 * 1024

# Default values for project.json["defaults"]
PROJECT_DEFAULTS = {
    "firmware_run_id": "",
    "config_run_id": "",
    "expected_bytes": DEFAULT_EXPECTED_BYTES,
    "archive_existing": True,
    "confirm_startframe": True,
    "bind_force": False,
    "ensure_eth": True,
}

# Default values for project.json["dca_profile"]
DCA_PROFILE_DEFAULTS = {
    "host_ip": "192.168.33.30",
    "prefix_length": 24,
    "dca_ip": "192.168.33.180",
    "dca_mac": "",
    "config_port": 4096,
    "data_port": 4098,
}


# ---------------------------------------------------------------------------
# Utility: atomic JSON write
# ---------------------------------------------------------------------------

def atomic_json_write(path: Path, data: Any, indent: int = 2) -> None:
    """Write JSON to *path* atomically via temp-file + os.replace()."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        dir=str(path.parent), suffix=".tmp", prefix=".awr_"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, default=str)
            f.write("\n")
        import stat
        if path.exists():
            try:
                path.chmod(stat.S_IWRITE)
            except Exception:
                pass
        os.replace(tmp, str(path))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# Utility: safe slug
# ---------------------------------------------------------------------------

def safe_slug(name: str) -> str:
    """Convert *name* to a lowercase, filesystem-safe slug.

    Replaces spaces and unsafe characters with underscores, strips
    leading/trailing underscores, and collapses runs of underscores.
    """
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9_\-]", "_", s)
    s = re.sub(r"_+", "_", s)
    s = s.strip("_")
    if not s:
        s = "unnamed"
    return s


# ---------------------------------------------------------------------------
# Utility: SHA-256
# ---------------------------------------------------------------------------

def _sha256(path: Path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


# ---------------------------------------------------------------------------
# Utility: find project root
# ---------------------------------------------------------------------------

def find_project_root(start_path: Path | str) -> Path:
    """Walk upward from *start_path* looking for ``project.json``.

    Returns the directory containing ``project.json``.

    Raises:
        FileNotFoundError: If no ``project.json`` is found.
    """
    p = Path(start_path).resolve()
    if p.is_file():
        p = p.parent
    for ancestor in [p, *p.parents]:
        if (ancestor / PROJECT_MARKER).is_file():
            return ancestor
    raise FileNotFoundError(
        f"No {PROJECT_MARKER} found in {start_path} or any parent directory."
    )


# ---------------------------------------------------------------------------
# .gitignore management
# ---------------------------------------------------------------------------

def _ensure_gitignore(root: Path) -> list[str]:
    """Append missing AWR ignore rules to .gitignore. Returns added lines."""
    gi = root / ".gitignore"
    existing_lines: set[str] = set()
    if gi.exists():
        existing_lines = set(gi.read_text(encoding="utf-8").splitlines())

    added: list[str] = []
    to_append: list[str] = []
    for rule in GITIGNORE_RULES:
        if rule not in existing_lines:
            to_append.append(rule)
            added.append(rule)

    if to_append:
        with open(gi, "a", encoding="utf-8") as f:
            if existing_lines and "" not in existing_lines:
                f.write("\n")
            f.write("\n".join(to_append) + "\n")

    return added


# ---------------------------------------------------------------------------
# init_project
# ---------------------------------------------------------------------------

def init_project(
    name: str,
    root: Path | str = ".",
    postproc_dir: Path | str = DEFAULT_POSTPROC_DIR,
    probe_dir: str = DEFAULT_PROBE_DIR,
    expected_bytes: int = DEFAULT_EXPECTED_BYTES,
    force: bool = False,
) -> dict:
    """Create ``project.json`` and scaffold directory tree.

    Returns the project dict.

    Raises:
        FileExistsError: If ``project.json`` already exists and *force*
            is ``False``.
    """
    root = Path(root).resolve()
    pj = root / PROJECT_MARKER

    if pj.exists() and not force:
        raise FileExistsError(
            f"{PROJECT_MARKER} already exists at {pj}. "
            "Use --force to overwrite."
        )

    # Create directory tree
    dirs = [
        root / "configs" / "radar",
        root / "configs" / "mmws" / "lua",
        root / "configs" / "mmws" / "manifests",
        root / "configs" / "mmws" / "results",
        root / "configs" / "mmws" / "snapshots",
        root / "captures",
        root / "logs",
        root / "notebooks",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    project_id = str(uuid.uuid4())[:8]
    now = datetime.datetime.now().isoformat()
    postproc_abs = str(Path(postproc_dir).resolve())

    project = {
        "schema_version": SCHEMA_VERSION,
        "project_id": project_id,
        "name": name,
        "created_at": now,
        "root_path_abs": str(root),
        "postproc_dir_abs": postproc_abs,
        "probe_dir_rel": probe_dir,
        "expected_bytes": expected_bytes,
        "default_adc_config": {
            "frames": 8,
            "chirps": 128,
            "rx": 4,
            "samples": 256,
            "sample_format": "complex_int16",
            "iq_order": "iq",
            "layout": "frame_chirp_rx_sample",
            "layout_assumption_confirmed": False,
        },
    }

    atomic_json_write(pj, project)

    # .gitignore
    _ensure_gitignore(root)

    return project


# ---------------------------------------------------------------------------
# load_project
# ---------------------------------------------------------------------------

def load_project(root: Path | str) -> dict:
    """Load and return ``project.json`` from *root*.

    Raises:
        FileNotFoundError: If ``project.json`` does not exist.
    """
    root = Path(root).resolve()
    pj = root / PROJECT_MARKER
    if not pj.exists():
        raise FileNotFoundError(f"{PROJECT_MARKER} not found at {pj}")
    return json.loads(pj.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# project_status
# ---------------------------------------------------------------------------

def project_status(root: Path | str) -> dict:
    """Build a status summary dict for the project at *root*.

    Counts only managed captures (those with ``capture_manifest.json``).
    """
    root = Path(root).resolve()
    try:
        proj = load_project(root)
        postproc_exists = Path(proj["postproc_dir_abs"]).exists()
        probe_exists = (root / proj["probe_dir_rel"]).exists()
    except FileNotFoundError:
        proj = {
            "name": root.name,
            "project_id": "unknown",
            "postproc_dir_abs": "",
            "probe_dir_rel": "ti/probe_logs",
            "expected_bytes": 0,
        }
        postproc_exists = False
        probe_exists = False

    captures_dir = root / "captures"
    managed_captures: list[dict] = []
    if captures_dir.exists():
        for manifest_path in sorted(captures_dir.glob("*/capture_manifest.json")):
            try:
                m = json.loads(manifest_path.read_text(encoding="utf-8"))
                managed_captures.append({
                    "capture_id": m.get("capture_id", ""),
                    "capture_name": m.get("capture_name", ""),
                    "status": m.get("status", ""),
                    "created_at": m.get("created_at", ""),
                })
            except (json.JSONDecodeError, IOError):
                pass

    # Check gitignore
    gi = root / ".gitignore"
    gitignore_ok = False
    if gi.exists():
        content = gi.read_text(encoding="utf-8")
        required_rules = [r for r in GITIGNORE_RULES if not r.startswith("#")]
        gitignore_ok = all(r in content for r in required_rules)

    newest = managed_captures[-1] if managed_captures else None

    # Aggregate status counts
    status_counts: dict[str, int] = {
        "created": 0,
        "imported": 0,
        "inspected": 0,
        "bound": 0,
        "complete": 0,
        "verify_failed": 0,
        "bind_failed": 0,
        "error": 0,
    }
    error_captures: list[dict] = []
    
    for c in managed_captures:
        st = c["status"]
        if st in status_counts:
            status_counts[st] += 1
        else:
            status_counts[st] = 1
            
        if st == "error":
            error_captures.append(c)

    return {
        "project_name": proj["name"],
        "project_id": proj["project_id"],
        "root_path_abs": str(root),
        "postproc_dir_abs": proj["postproc_dir_abs"],
        "postproc_dir_exists": postproc_exists,
        "probe_dir_rel": proj["probe_dir_rel"],
        "probe_dir_exists": probe_exists,
        "expected_bytes": proj["expected_bytes"],
        "capture_count": len(managed_captures),
        "status_counts": status_counts,
        "error_captures": error_captures,
        "captures": managed_captures,
        "newest_capture": newest,
        "gitignore_ok": gitignore_ok,
    }


# ---------------------------------------------------------------------------
# new_capture
# ---------------------------------------------------------------------------

def new_capture(
    root: Path | str,
    capture_name: str,
    mode: Literal["import", "direct"] = "import",
    notes: str = "",
    *,
    radar_config: Any | None = None,
    radar_config_lua_path: str = "",
    _now: datetime.datetime | None = None,
) -> dict:
    """Create a new capture folder and manifest.

    The ``_now`` parameter is for deterministic testing only; production
    callers should not set it.

    Returns the capture manifest dict.

    Raises:
        FileExistsError: If the capture folder already exists.
    """
    root = Path(root).resolve()
    proj = load_project(root)

    now = _now or datetime.datetime.now()
    ts = now.strftime("%Y%m%d_%H%M%S")
    slug = safe_slug(capture_name)
    capture_id = f"{ts}_{slug}"

    cap_dir = root / "captures" / capture_id
    if cap_dir.exists():
        raise FileExistsError(
            f"Capture folder already exists: {cap_dir}"
        )

    # Create directories
    raw_dir = cap_dir / "raw"
    meta_dir = cap_dir / "metadata" / "mmws_logs"
    proc_dir = cap_dir / "processed"
    raw_dir.mkdir(parents=True)
    meta_dir.mkdir(parents=True)
    proc_dir.mkdir(parents=True)

    # Notes
    notes_path = cap_dir / "notes.md"
    notes_content = f"# {capture_name}\n\nCreated: {now.isoformat()}\n"
    if notes:
        notes_content += f"\n{notes}\n"
    notes_path.write_text(notes_content, encoding="utf-8")

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "capture_id": capture_id,
        "capture_name": capture_name,
        "project_id": proj["project_id"],
        "project_name": proj["name"],
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "status": "created",
        "mode": mode,
        "root_path_abs": str(root),
        "capture_dir_rel": f"captures/{capture_id}",
        "capture_dir_abs": str(cap_dir),
        "raw_dir_rel": f"captures/{capture_id}/raw",
        "metadata_dir_rel": f"captures/{capture_id}/metadata",
        "processed_dir_rel": f"captures/{capture_id}/processed",
        "notes_path_rel": f"captures/{capture_id}/notes.md",
        "postproc_dir_abs": proj["postproc_dir_abs"],
        "expected_bytes": proj["expected_bytes"],
        "actual_raw_file_size": None,
        "raw_file_name": None,
        "raw_file_rel": None,
        "raw_file_sha256": None,
        "radar_config_name": getattr(radar_config, "name", None) if radar_config else None,
        "radar_config_path": None,
        "radar_config_sha256": None,
        "radar_config_lua_path": radar_config_lua_path or None,
        "radar_config_lua_sha256": None,
        "adc_inspect_path_rel": None,
        "validation_records": [],
        "copied_mmws_files": [],
        "mmws_output_snapshot_path_rel": None,
        "firmware_run_id": None,
        "config_run_id": None,
        "dca_setup_run_id": None,
        "capture_trigger_run_id": None,
        "postproc_run_id": None,
        "workflow_id": None,
        "warnings": [],
        "errors": [],
        "tags": [],
        "notes": notes,
    }

    atomic_json_write(cap_dir / "capture_manifest.json", manifest)

    return manifest


# ---------------------------------------------------------------------------
# import_raw
# ---------------------------------------------------------------------------

def import_raw(
    root: Path | str,
    capture_id: str,
    source_path: Path | str,
    move: bool = False,
    force: bool = False,
    inspect: bool = True,
    allow_size_mismatch: bool = False,
) -> dict:
    """Copy (or move) a raw ADC binary into a capture's ``raw/`` folder.

    Returns the updated manifest dict.

    Raises:
        FileNotFoundError: If source or capture folder not found.
        FileExistsError: If raw file already exists and *force* is False.
        ValueError: If file size does not match expected and
            *allow_size_mismatch* is False.
    """
    root = Path(root).resolve()
    proj = load_project(root)
    source = Path(source_path).resolve()

    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    cap_dir = root / "captures" / capture_id
    manifest_path = cap_dir / "capture_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Capture manifest not found: {manifest_path}"
        )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    dest = cap_dir / "raw" / "adc_data.bin"
    if dest.exists() and not force:
        raise FileExistsError(
            f"Raw file already exists: {dest}. Use --force to overwrite."
        )

    # Size check (strict by default)
    file_size = source.stat().st_size
    expected = proj["expected_bytes"]
    if file_size != expected and not allow_size_mismatch:
        manifest["status"] = "error"
        manifest["errors"].append(
            f"Size mismatch: got {file_size:,} bytes, "
            f"expected {expected:,} bytes"
        )
        manifest["updated_at"] = datetime.datetime.now().isoformat()
        atomic_json_write(manifest_path, manifest)
        raise ValueError(
            f"ADC file size mismatch: got {file_size:,} bytes, "
            f"expected {expected:,} bytes. "
            f"Use --allow-size-mismatch to override."
        )

    # Copy or move
    if move:
        shutil.move(str(source), str(dest))
    else:
        shutil.copy2(str(source), str(dest))

    # Hash
    sha = _sha256(dest)

    # Update manifest
    manifest["actual_raw_file_size"] = file_size
    manifest["raw_file_name"] = "adc_data.bin"
    manifest["raw_file_rel"] = f"captures/{capture_id}/raw/adc_data.bin"
    manifest["raw_file_sha256"] = sha
    manifest["updated_at"] = datetime.datetime.now().isoformat()

    if file_size != expected:
        manifest["warnings"].append(
            f"Size mismatch accepted: {file_size:,} vs expected {expected:,}"
        )
        manifest["status"] = "imported"
    else:
        manifest["status"] = "imported"

    # ADC inspection
    if inspect:
        try:
            from awr2944_dca.adc_parser import AdcParserConfig, inspect_adc_file

            adc_cfg = proj.get("default_adc_config", {})
            parser_config = AdcParserConfig(
                frames=adc_cfg.get("frames", 8),
                chirps=adc_cfg.get("chirps", 128),
                rx=adc_cfg.get("rx", 4),
                samples=adc_cfg.get("samples", 256),
                iq_order=adc_cfg.get("iq_order", "iq"),
            )
            inspect_result = inspect_adc_file(dest, parser_config)

            inspect_path = cap_dir / "metadata" / "adc_inspect.json"
            atomic_json_write(inspect_path, inspect_result)

            manifest["adc_inspect_path_rel"] = (
                f"captures/{capture_id}/metadata/adc_inspect.json"
            )
            manifest["status"] = "inspected"
        except Exception as e:
            manifest["warnings"].append(f"ADC inspection failed: {e}")

    manifest["updated_at"] = datetime.datetime.now().isoformat()
    atomic_json_write(manifest_path, manifest)

    return manifest


# ---------------------------------------------------------------------------
# bind_mmws_output
# ---------------------------------------------------------------------------

def bind_mmws_output(
    root: Path | str,
    capture_id: str,
    postproc_dir: Path | str | None = None,
    force: bool = False,
    copy_logs: bool = True,
    inspect: bool = True,
) -> dict:
    """Copy adc_data.bin + metadata from mmWave Studio PostProc staging.

    Never moves or deletes files from PostProc.

    Returns the updated manifest dict.

    Raises:
        FileNotFoundError: If source adc_data.bin or capture not found.
        FileExistsError: If raw file already exists and *force* is False.
    """
    root = Path(root).resolve()
    proj = load_project(root)

    if postproc_dir is None:
        postproc_dir = proj["postproc_dir_abs"]
    postproc = Path(postproc_dir).resolve()

    cap_dir = root / "captures" / capture_id
    manifest_path = cap_dir / "capture_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Capture manifest not found: {manifest_path}"
        )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    # Copy adc_data.bin
    src_adc = postproc / "adc_data.bin"
    if not src_adc.exists():
        raise FileNotFoundError(
            f"adc_data.bin not found in PostProc: {src_adc}"
        )

    dest_adc = cap_dir / "raw" / "adc_data.bin"
    if dest_adc.exists() and not force:
        raise FileExistsError(
            f"Raw file already exists: {dest_adc}. Use --force to overwrite."
        )

    shutil.copy2(str(src_adc), str(dest_adc))
    file_size = dest_adc.stat().st_size
    sha = _sha256(dest_adc)

    manifest["actual_raw_file_size"] = file_size
    manifest["raw_file_name"] = "adc_data.bin"
    manifest["raw_file_rel"] = f"captures/{capture_id}/raw/adc_data.bin"
    manifest["raw_file_sha256"] = sha
    manifest["postproc_dir_abs"] = str(postproc)

    # Size validation
    expected = proj["expected_bytes"]
    if file_size != expected:
        manifest["warnings"].append(
            f"Size mismatch: {file_size:,} vs expected {expected:,}"
        )

    # Copy metadata files
    copied_files: list[dict] = []
    if copy_logs:
        meta_dest = cap_dir / "metadata" / "mmws_logs"
        meta_dest.mkdir(parents=True, exist_ok=True)

        # Named files
        for fname in _POSTPROC_METADATA_FILES:
            src = postproc / fname
            if src.exists() and src.is_file():
                dst = meta_dest / fname
                shutil.copy2(str(src), str(dst))
                copied_files.append({
                    "source_abs": str(src),
                    "dest_rel": f"captures/{capture_id}/metadata/mmws_logs/{fname}",
                    "size": src.stat().st_size,
                    "sha256": _sha256(dst),
                })

        # Validation JSONs
        for src in postproc.glob(_POSTPROC_VALIDATION_GLOB):
            if src.is_file():
                dst = meta_dest / src.name
                shutil.copy2(str(src), str(dst))
                copied_files.append({
                    "source_abs": str(src),
                    "dest_rel": f"captures/{capture_id}/metadata/mmws_logs/{src.name}",
                    "size": src.stat().st_size,
                    "sha256": _sha256(dst),
                })
                manifest["validation_records"].append(
                    f"captures/{capture_id}/metadata/mmws_logs/{src.name}"
                )

        # PackFile.mat — only if small enough
        mat_src = postproc / "PackFile.mat"
        if mat_src.exists() and mat_src.is_file():
            if mat_src.stat().st_size <= _MAX_MAT_FILE_BYTES:
                dst = meta_dest / "PackFile.mat"
                shutil.copy2(str(mat_src), str(dst))
                copied_files.append({
                    "source_abs": str(mat_src),
                    "dest_rel": f"captures/{capture_id}/metadata/mmws_logs/PackFile.mat",
                    "size": mat_src.stat().st_size,
                    "sha256": _sha256(dst),
                })
            else:
                manifest["warnings"].append(
                    f"PackFile.mat skipped: {mat_src.stat().st_size:,} bytes "
                    f"exceeds {_MAX_MAT_FILE_BYTES:,} byte limit"
                )

    manifest["copied_mmws_files"] = copied_files
    manifest["status"] = "bound"

    # ADC inspection
    if inspect:
        try:
            from awr2944_dca.adc_parser import AdcParserConfig, inspect_adc_file

            adc_cfg = proj.get("default_adc_config", {})
            parser_config = AdcParserConfig(
                frames=adc_cfg.get("frames", 8),
                chirps=adc_cfg.get("chirps", 128),
                rx=adc_cfg.get("rx", 4),
                samples=adc_cfg.get("samples", 256),
                iq_order=adc_cfg.get("iq_order", "iq"),
            )
            inspect_result = inspect_adc_file(dest_adc, parser_config)

            inspect_path = cap_dir / "metadata" / "adc_inspect.json"
            atomic_json_write(inspect_path, inspect_result)

            manifest["adc_inspect_path_rel"] = (
                f"captures/{capture_id}/metadata/adc_inspect.json"
            )
            manifest["status"] = "inspected"
        except Exception as e:
            manifest["warnings"].append(f"ADC inspection failed: {e}")

    manifest["updated_at"] = datetime.datetime.now().isoformat()
    atomic_json_write(manifest_path, manifest)

    return manifest


# ---------------------------------------------------------------------------
# inspect_capture
# ---------------------------------------------------------------------------

def inspect_capture(
    root: Path | str,
    capture_id: str,
    refresh_adc_inspect: bool = False,
) -> dict:
    """Build an inspection summary for a capture.

    Returns a dict suitable for JSON serialization or text display.
    """
    root = Path(root).resolve()
    proj = load_project(root)

    cap_dir = root / "captures" / capture_id
    manifest_path = cap_dir / "capture_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Capture manifest not found: {manifest_path}"
        )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    # Raw file status
    raw_path = cap_dir / "raw" / "adc_data.bin"
    raw_exists = raw_path.exists()
    raw_size = raw_path.stat().st_size if raw_exists else None
    raw_sha256 = _sha256(raw_path) if raw_exists else None

    # Refresh ADC inspect
    if refresh_adc_inspect and raw_exists:
        from awr2944_dca.adc_parser import AdcParserConfig, inspect_adc_file

        adc_cfg = proj.get("default_adc_config", {})
        parser_config = AdcParserConfig(
            frames=adc_cfg.get("frames", 8),
            chirps=adc_cfg.get("chirps", 128),
            rx=adc_cfg.get("rx", 4),
            samples=adc_cfg.get("samples", 256),
            iq_order=adc_cfg.get("iq_order", "iq"),
        )
        inspect_result = inspect_adc_file(raw_path, parser_config)

        inspect_out = cap_dir / "metadata" / "adc_inspect.json"
        atomic_json_write(inspect_out, inspect_result)
        manifest["adc_inspect_path_rel"] = (
            f"captures/{capture_id}/metadata/adc_inspect.json"
        )
        manifest["updated_at"] = datetime.datetime.now().isoformat()
        atomic_json_write(manifest_path, manifest)

    # Load ADC inspect if available
    adc_inspect: dict | None = None
    inspect_json = cap_dir / "metadata" / "adc_inspect.json"
    if inspect_json.exists():
        try:
            adc_inspect = json.loads(inspect_json.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            pass

    return {
        "capture_id": manifest["capture_id"],
        "capture_name": manifest["capture_name"],
        "status": manifest["status"],
        "mode": manifest["mode"],
        "created_at": manifest["created_at"],
        "updated_at": manifest["updated_at"],
        "raw_file_exists": raw_exists,
        "raw_file_size": raw_size,
        "raw_file_sha256": raw_sha256,
        "expected_bytes": manifest["expected_bytes"],
        "size_match": raw_size == manifest["expected_bytes"] if raw_exists else None,
        "adc_inspect": adc_inspect,
        "validation_records": manifest.get("validation_records", []),
        "copied_mmws_files": manifest.get("copied_mmws_files", []),
        "warnings": manifest.get("warnings", []),
        "errors": manifest.get("errors", []),
        "tags": manifest.get("tags", []),
        "notes": manifest.get("notes", ""),
        "firmware_run_id": manifest.get("firmware_run_id"),
        "config_run_id": manifest.get("config_run_id"),
        "workflow_id": manifest.get("workflow_id"),
    }


# ---------------------------------------------------------------------------
# verify_capture
# ---------------------------------------------------------------------------

def verify_capture(root: Path | str, capture_id: str) -> dict:
    """Verify a capture's manifest, files, and hashes.

    Returns a dict with:
        passed (bool): True if no errors
        errors (list[str]): List of error messages
        warnings (list[str]): List of warning messages
        details (dict): Raw values checked
    """
    root = Path(root).resolve()
    try:
        proj = load_project(root)
    except FileNotFoundError:
        return {"passed": False, "errors": ["project.json not found"], "warnings": [], "details": {}}

    cap_dir = root / "captures" / capture_id
    manifest_path = cap_dir / "capture_manifest.json"
    
    errors = []
    warnings = []
    details = {}

    if not manifest_path.exists():
        errors.append(f"Manifest not found: {manifest_path}")
        return {"passed": False, "errors": errors, "warnings": warnings, "details": details}
        
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"Manifest failed to parse: {e}")
        return {"passed": False, "errors": errors, "warnings": warnings, "details": details}

    # ID match
    if manifest.get("capture_id") != capture_id:
        errors.append(f"Manifest capture_id ({manifest.get('capture_id')}) does not match folder name ({capture_id})")

    status = manifest.get("status", "")
    expected_bytes = manifest.get("expected_bytes", 0)

    # Raw file checks
    if status in ("imported", "inspected", "bound", "complete"):
        raw_rel = manifest.get("raw_file_rel")
        if not raw_rel:
            errors.append(f"raw_file_rel is empty but status is {status}")
        else:
            raw_abs = root / raw_rel
            if not raw_abs.exists():
                errors.append(f"Raw file missing: {raw_abs}")
            else:
                actual_size = raw_abs.stat().st_size
                details["actual_raw_size"] = actual_size
                
                if manifest.get("actual_raw_file_size") != actual_size:
                    errors.append(f"Actual raw size ({actual_size}) != manifest actual_raw_file_size ({manifest.get('actual_raw_file_size')})")
                
                if actual_size != expected_bytes and status != "error":
                    errors.append(f"Actual raw size ({actual_size}) != expected_bytes ({expected_bytes})")
                    
                actual_sha = _sha256(raw_abs)
                if manifest.get("raw_file_sha256") != actual_sha:
                    errors.append(f"Actual raw SHA256 ({actual_sha}) != manifest raw_file_sha256 ({manifest.get('raw_file_sha256')})")

    # ADC inspect checks
    adc_inspect_rel = manifest.get("adc_inspect_path_rel")
    if adc_inspect_rel:
        adc_abs = root / adc_inspect_rel
        if not adc_abs.exists():
            errors.append(f"adc_inspect.json missing: {adc_abs}")
        else:
            try:
                adc_data = json.loads(adc_abs.read_text(encoding="utf-8"))
                if adc_data.get("sha256") != manifest.get("raw_file_sha256"):
                    errors.append(f"adc_inspect sha256 ({adc_data.get('sha256')}) != manifest raw_file_sha256 ({manifest.get('raw_file_sha256')})")
                if adc_data.get("file_size") != manifest.get("actual_raw_file_size"):
                    errors.append(f"adc_inspect file_size ({adc_data.get('file_size')}) != manifest actual_raw_file_size ({manifest.get('actual_raw_file_size')})")
            except json.JSONDecodeError:
                errors.append(f"Failed to parse adc_inspect.json: {adc_abs}")

    # Copied mmws files hashes
    copied_files = manifest.get("copied_mmws_files", [])
    for cf in copied_files:
        dest_rel = cf.get("dest_rel")
        if dest_rel:
            dest_abs = root / dest_rel
            if not dest_abs.exists():
                errors.append(f"Copied file missing: {dest_abs}")
            else:
                actual_sha = _sha256(dest_abs)
                if actual_sha != cf.get("sha256"):
                    errors.append(f"Copied file SHA256 mismatch for {dest_rel}: actual={actual_sha}, expected={cf.get('sha256')}")
        else:
            errors.append("Copied file entry missing dest_rel")

    # Notes.md
    notes_path = cap_dir / "notes.md"
    if not notes_path.exists():
        errors.append(f"notes.md missing: {notes_path}")

    # Gitignore checks
    import subprocess
    if shutil.which("git"):
        try:
            # First, check if root is in a git repo
            res_repo = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=str(root),
                capture_output=True
            )
            if res_repo.returncode != 0:
                warnings.append("Project root is not inside a Git repository; skipped gitignore checks.")
            else:
                # Check if root itself is ignored
                res_root = subprocess.run(
                    ["git", "check-ignore", "-q", str(root)],
                    cwd=str(root)
                )
                if res_root.returncode == 0:
                    warnings.append("Project root is ignored by Git; skipped gitignore checks.")
                else:
                    # Check raw.bin
                    raw_path = cap_dir / "raw" / "adc_data.bin"
                    res = subprocess.run(["git", "check-ignore", "-q", str(raw_path)], cwd=str(root))
                    if res.returncode != 0:
                        errors.append(f"raw ADC file is not ignored by git: {raw_path}")
                        
                    # Check manifest
                    res = subprocess.run(["git", "check-ignore", "-q", str(manifest_path)], cwd=str(root))
                    if res.returncode == 0:
                        errors.append(f"capture_manifest.json is ignored by git, but should be tracked: {manifest_path}")
                        
                    # Check inspect
                    if adc_inspect_rel:
                        adc_abs = root / adc_inspect_rel
                        res = subprocess.run(["git", "check-ignore", "-q", str(adc_abs)], cwd=str(root))
                        if res.returncode == 0:
                            errors.append(f"adc_inspect.json is ignored by git, but should be tracked: {adc_abs}")
                        
        except subprocess.SubprocessError as e:
            warnings.append(f"Git check failed: {e}")
    else:
        warnings.append("Git not found; skipped gitignore checks.")

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "details": details,
    }


# ---------------------------------------------------------------------------
# get_defaults / set_defaults
# ---------------------------------------------------------------------------

def get_defaults(root: Path | str) -> dict:
    """Return merged project defaults from ``project.json["defaults"]``.

    Keys not present in the saved defaults are filled from
    ``PROJECT_DEFAULTS``.
    """
    proj = load_project(root)
    saved = proj.get("defaults", {})
    merged = {**PROJECT_DEFAULTS, **saved}
    return merged


def set_defaults(root: Path | str, **kwargs: Any) -> dict:
    """Update project defaults and persist to ``project.json``.

    Only keys present in ``PROJECT_DEFAULTS`` are accepted.
    Returns the updated defaults dict.

    Raises:
        ValueError: If an unknown key is provided.
    """
    unknown = set(kwargs) - set(PROJECT_DEFAULTS)
    if unknown:
        raise ValueError(
            f"Unknown default keys: {unknown}. "
            f"Valid keys: {sorted(PROJECT_DEFAULTS)}"
        )

    root = Path(root).resolve()
    proj = load_project(root)
    saved = proj.get("defaults", {})
    saved.update(kwargs)
    proj["defaults"] = saved
    proj["updated_at"] = datetime.datetime.now().isoformat()
    atomic_json_write(root / PROJECT_MARKER, proj)
    return {**PROJECT_DEFAULTS, **saved}


# ---------------------------------------------------------------------------
# DCA profile
# ---------------------------------------------------------------------------

def get_dca_profile(root: Path | str) -> dict:
    """Return merged DCA profile from ``project.json["dca_profile"]``."""
    proj = load_project(root)
    saved = proj.get("dca_profile", {})
    return {**DCA_PROFILE_DEFAULTS, **saved}


def set_dca_profile(root: Path | str, **kwargs: Any) -> dict:
    """Update DCA profile and persist to ``project.json``.

    Only keys present in ``DCA_PROFILE_DEFAULTS`` are accepted.
    """
    unknown = set(kwargs) - set(DCA_PROFILE_DEFAULTS)
    if unknown:
        raise ValueError(
            f"Unknown DCA profile keys: {unknown}. "
            f"Valid keys: {sorted(DCA_PROFILE_DEFAULTS)}"
        )

    root = Path(root).resolve()
    proj = load_project(root)
    saved = proj.get("dca_profile", {})
    saved.update(kwargs)
    proj["dca_profile"] = saved
    proj["updated_at"] = datetime.datetime.now().isoformat()
    atomic_json_write(root / PROJECT_MARKER, proj)
    return {**DCA_PROFILE_DEFAULTS, **saved}


# ---------------------------------------------------------------------------
# Capture notes and tags
# ---------------------------------------------------------------------------

def add_capture_note(root: Path | str, capture_id: str, text: str) -> None:
    """Append a timestamped note to the capture's ``notes.md``."""
    root = Path(root).resolve()
    cap_dir = root / "captures" / capture_id
    notes_path = cap_dir / "notes.md"
    if not cap_dir.exists():
        raise FileNotFoundError(f"Capture folder not found: {cap_dir}")

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n**[{ts}]** {text}\n"

    with open(notes_path, "a", encoding="utf-8") as f:
        f.write(entry)


def add_capture_tags(root: Path | str, capture_id: str, *tags: str) -> list[str]:
    """Add tags to a capture manifest. Returns the updated tag list."""
    root = Path(root).resolve()
    cap_dir = root / "captures" / capture_id
    manifest_path = cap_dir / "capture_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    existing = set(manifest.get("tags", []))
    existing.update(tags)
    manifest["tags"] = sorted(existing)
    manifest["updated_at"] = datetime.datetime.now().isoformat()
    atomic_json_write(manifest_path, manifest)
    return manifest["tags"]
