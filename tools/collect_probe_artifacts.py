"""Collect mmWave Studio probe logs into a portable debug bundle.

This script is intentionally standalone: it imports no awr2944_dca modules and
does not touch hardware-facing code paths.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
import sys
import time
import zipfile
from pathlib import Path
from typing import Sequence


INCLUDE_PATTERNS = (
    "guided_*_state.json",
    "*_manifest.json",
    "*_result.json",
    "*_progress.jsonl",
    "*_snapshot.txt",
    "manual_check_*",
    "gui_connect_windows.txt",
    "validation_*.json",
)


class ArtifactCollectionError(RuntimeError):
    """Raised when probe artifacts cannot be collected safely."""


def _non_negative_float(value: str) -> float:
    try:
        minutes = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value!r} is not a number") from exc
    if minutes < 0:
        raise argparse.ArgumentTypeError("latest minutes must be non-negative")
    return minutes


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Package recent mmWave Studio / AWR2944 probe logs into a zip bundle."
    )
    parser.add_argument(
        "--probe-dir",
        required=True,
        type=Path,
        help="Probe log directory to read, for example exp_lau_probe/ti/probe_logs.",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="Output zip path. The path must be outside --probe-dir.",
    )
    parser.add_argument(
        "--latest-minutes",
        "--latest",
        dest="latest_minutes",
        type=_non_negative_float,
        default=None,
        help="Only include matching files modified within the last N minutes.",
    )
    return parser.parse_args(argv)


def _format_utc(timestamp: float) -> str:
    value = dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc)
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _matches_artifact_name(path: Path) -> bool:
    return any(fnmatch.fnmatchcase(path.name, pattern) for pattern in INCLUDE_PATTERNS)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iter_matching_files(
    probe_dir: Path,
    *,
    latest_minutes: float | None,
    now: float,
) -> list[tuple[str, Path, os.stat_result]]:
    cutoff = None
    if latest_minutes is not None:
        cutoff = now - (latest_minutes * 60.0)

    matches: list[tuple[str, Path, os.stat_result]] = []
    for path in probe_dir.rglob("*"):
        if not path.is_file() or not _matches_artifact_name(path):
            continue
        stat = path.stat()
        if cutoff is not None and stat.st_mtime < cutoff:
            continue
        rel_path = path.relative_to(probe_dir).as_posix()
        matches.append((rel_path, path, stat))

    matches.sort(key=lambda item: item[0])
    return matches


def collect_artifacts(
    probe_dir: str | Path,
    out: str | Path,
    *,
    latest_minutes: float | None = None,
    now: float | None = None,
) -> dict[str, object]:
    """Create a zip bundle of matching probe artifacts and return its manifest."""
    source_dir = Path(probe_dir).expanduser()
    if not source_dir.exists():
        raise ArtifactCollectionError(f"probe_dir does not exist: {source_dir}")
    if not source_dir.is_dir():
        raise ArtifactCollectionError(f"probe_dir is not a directory: {source_dir}")

    source_dir = source_dir.resolve()
    out_path = Path(out).expanduser().resolve()
    if out_path == source_dir or _is_relative_to(out_path, source_dir):
        raise ArtifactCollectionError(
            "out path must be outside probe_dir to keep collection read-only"
        )

    collected_at = time.time() if now is None else now
    matches = _iter_matching_files(
        source_dir,
        latest_minutes=latest_minutes,
        now=collected_at,
    )

    manifest_files: list[dict[str, object]] = []
    for rel_path, path, stat in matches:
        manifest_files.append(
            {
                "path": rel_path,
                "size": stat.st_size,
                "mtime": stat.st_mtime,
                "mtime_ns": stat.st_mtime_ns,
                "mtime_utc": _format_utc(stat.st_mtime),
                "sha256": _sha256_file(path),
            }
        )

    manifest: dict[str, object] = {
        "schema_version": 1,
        "generated_at_utc": _format_utc(collected_at),
        "probe_dir": str(source_dir),
        "latest_minutes": latest_minutes,
        "include_patterns": list(INCLUDE_PATTERNS),
        "file_count": len(manifest_files),
        "files": manifest_files,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, mode="w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for rel_path, path, _stat in matches:
            bundle.write(path, arcname=rel_path)
        bundle.writestr(
            "bundle_manifest.json",
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        )

    return manifest


def _manifest_total_size(manifest: dict[str, object]) -> int:
    return sum(int(entry["size"]) for entry in manifest["files"])


def _manifest_has_path_matching(manifest: dict[str, object], pattern: str) -> bool:
    return any(
        fnmatch.fnmatchcase(Path(str(entry["path"])).name, pattern)
        for entry in manifest["files"]
    )


def _format_yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _print_success_summary(out_path: Path, manifest: dict[str, object]) -> None:
    guided_states_included = _manifest_has_path_matching(manifest, "guided_*_state.json")
    validation_records_included = _manifest_has_path_matching(manifest, "validation_*.json")

    print("Probe artifact bundle created:")
    print(f"  output_zip: {out_path}")
    print(f"  files_included: {manifest['file_count']}")
    print(f"  total_uncompressed_bytes: {_manifest_total_size(manifest)}")
    print(f"  guided_states_included: {_format_yes_no(guided_states_included)}")
    print(f"  validation_records_included: {_format_yes_no(validation_records_included)}")
    print("  note: raw ADC .bin files are excluded by default")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        manifest = collect_artifacts(
            args.probe_dir,
            args.out,
            latest_minutes=args.latest_minutes,
        )
    except ArtifactCollectionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    _print_success_summary(Path(args.out).expanduser().resolve(), manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())