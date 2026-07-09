"""Generate an offline Markdown report from a probe artifact bundle."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath
from typing import Any, Sequence


HARDWARE_COMMANDS = (
    "PowerOn",
    "RfEnable",
    "RfInit",
    "ProfileConfig",
    "ChirpConfig",
    "FrameConfig",
    "StartFrame",
)


class BundleReportError(RuntimeError):
    """Raised when a probe bundle cannot be read."""


@dataclass
class JsonRecord:
    path: str
    data: Any | None
    error: str | None = None


@dataclass
class RunResult:
    path: str
    run_id: str
    stage: str
    success: bool | None
    error: Any
    warnings: Any
    parse_error: str | None = None


@dataclass
class ProgressLog:
    path: str
    run_id: str
    command_count: int
    failed_command_count: int
    hardware_commands: list[str]
    last_command: str
    parse_errors: list[str]


@dataclass
class ArtifactIndexes:
    results_by_run_id: dict[str, list[RunResult]]
    progress_by_run_id: dict[str, list[ProgressLog]]
    manifests_by_run_id: dict[str, list[JsonRecord]]


@dataclass
class BundleContents:
    bundle_path: Path
    names: list[str]
    manifest: JsonRecord | None
    raw_bin_files: list[str]
    json_errors: list[str]
    guided_states: list[JsonRecord]
    run_results: list[RunResult]
    progress_logs: list[ProgressLog]
    run_manifests: list[JsonRecord]
    validations: list[JsonRecord]
    indexes: ArtifactIndexes


@dataclass
class LinkedArtifactSummary:
    firmware_result_found: bool
    firmware_progress_found: bool
    config_result_found: bool
    config_progress_found: bool
    unrelated_ignored_count: int


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an offline Markdown report from a probe artifact bundle."
    )
    parser.add_argument("--bundle", required=True, type=Path, help="Probe bundle zip to read.")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional Markdown output path. Omit to write the report to stdout.",
    )
    return parser.parse_args(argv)


def _basename(path: str) -> str:
    return PurePosixPath(path).name


def _matches(path: str, pattern: str) -> bool:
    return fnmatchcase(_basename(path), pattern)


def _decode_member(bundle: zipfile.ZipFile, name: str) -> str:
    return bundle.read(name).decode("utf-8", errors="replace")


def _load_json_member(bundle: zipfile.ZipFile, name: str) -> JsonRecord:
    text = _decode_member(bundle, name)
    try:
        return JsonRecord(path=name, data=json.loads(text))
    except json.JSONDecodeError as exc:
        return JsonRecord(
            path=name,
            data=None,
            error=f"Malformed JSON in {name}: line {exc.lineno} column {exc.colno}",
        )


def _coerce_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "1", "ok", "success"}:
            return True
        if normalized in {"false", "no", "0", "failed", "fail", "error"}:
            return False
    return None


def _first_present(data: dict[str, Any], keys: Sequence[str]) -> Any:
    for key in keys:
        if key in data:
            return data[key]
    return None


def _format_bool(value: bool | None) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return "-"


def _format_value(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return _format_bool(value)
    if isinstance(value, list):
        if not value:
            return "none"
        return "; ".join(_format_value(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    text = str(value)
    return text if text else "-"


def _valid_run_id(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text in {"-", "None"} or text.lower() in {"none", "null"}:
        return None
    return text


def _infer_from_result_name(path: str) -> tuple[str, str]:
    name = _basename(path)
    stem = name.removesuffix("_result.json")
    return _infer_run_id_and_stage(stem)


def _infer_from_progress_name(path: str) -> tuple[str, str]:
    name = _basename(path)
    stem = name.removesuffix("_progress.jsonl")
    stem = stem.removesuffix("_result")
    return _infer_run_id_and_stage(stem)


def _infer_from_manifest_name(path: str) -> tuple[str, str]:
    name = _basename(path)
    stem = name.removesuffix("_manifest.json")
    return _infer_run_id_and_stage(stem)


def _looks_like_run_id_prefix(value: str) -> bool:
    if re.fullmatch(r"[0-9A-Fa-f]{6,16}", value):
        return True
    return bool(
        re.fullmatch(r"[A-Za-z0-9]{6,16}", value)
        and any(character.isdigit() for character in value)
    )


def _infer_run_id_and_stage(stem: str) -> tuple[str, str]:
    parts = stem.split("_") if stem else []
    if parts and _looks_like_run_id_prefix(parts[0]):
        return parts[0], "_".join(parts[1:]) or "-"
    return stem or "-", stem or "-"


def _command_text(record: Any) -> str:
    if isinstance(record, str):
        return record
    if not isinstance(record, dict):
        return ""
    for key in ("command", "cmd", "lua", "api", "function", "name", "text", "command_name"):
        value = record.get(key)
        if value is not None:
            return str(value)
    return ""


def _progress_record_failed(record: Any) -> bool:
    if not isinstance(record, dict):
        return False
    if _coerce_bool(record.get("ok")) is False:
        return True
    if _coerce_bool(record.get("success")) is False:
        return True
    status = str(record.get("status", "")).strip().lower()
    if status in {"fail", "failed", "error"}:
        return True
    return bool(record.get("error"))


def _parse_progress_log(bundle: zipfile.ZipFile, name: str) -> ProgressLog:
    inferred_run_id, _stage = _infer_from_progress_name(name)
    command_count = 0
    failed_command_count = 0
    hardware_seen: list[str] = []
    parse_errors: list[str] = []
    last_command = "-"

    for line_no, line in enumerate(_decode_member(bundle, name).splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            record = json.loads(stripped)
        except json.JSONDecodeError as exc:
            parse_errors.append(
                f"Malformed JSONL in {name}: line {line_no} column {exc.colno}"
            )
            continue

        command_count += 1
        if _progress_record_failed(record):
            failed_command_count += 1
        command = _command_text(record)
        if command:
            last_command = command
        for hardware_command in HARDWARE_COMMANDS:
            if hardware_command in command and hardware_command not in hardware_seen:
                hardware_seen.append(hardware_command)

    return ProgressLog(
        path=name,
        run_id=inferred_run_id,
        command_count=command_count,
        failed_command_count=failed_command_count,
        hardware_commands=hardware_seen,
        last_command=last_command,
        parse_errors=parse_errors,
    )


def _parse_run_result(record: JsonRecord) -> RunResult:
    inferred_run_id, stage = _infer_from_result_name(record.path)
    if not isinstance(record.data, dict):
        return RunResult(
            path=record.path,
            run_id=inferred_run_id,
            stage=stage,
            success=None,
            error="-",
            warnings="-",
            parse_error=record.error,
        )

    run_id = str(record.data.get("run_id") or inferred_run_id)
    success = _coerce_bool(_first_present(record.data, ("success", "ok")))
    return RunResult(
        path=record.path,
        run_id=run_id,
        stage=stage,
        success=success,
        error=_first_present(record.data, ("error", "errors", "exception")),
        warnings=_first_present(record.data, ("warnings", "warning")),
    )


def _manifest_run_id(record: JsonRecord) -> str:
    inferred_run_id, _stage = _infer_from_manifest_name(record.path)
    if isinstance(record.data, dict):
        value = _first_present(record.data, ("run_id", "id"))
        return _valid_run_id(value) or inferred_run_id
    return inferred_run_id


def _manifest_hashes_present(manifest: JsonRecord | None) -> bool:
    if manifest is None or not isinstance(manifest.data, dict):
        return False
    files = manifest.data.get("files")
    if not isinstance(files, list):
        return False
    return all(isinstance(entry, dict) and bool(entry.get("sha256")) for entry in files)


def _metadata_file_count(contents: BundleContents) -> int:
    manifest = contents.manifest
    if manifest and isinstance(manifest.data, dict):
        file_count = manifest.data.get("file_count")
        if isinstance(file_count, int):
            return file_count
    return len(contents.names)


def _guided_failed(record: JsonRecord) -> bool:
    if not isinstance(record.data, dict):
        return False
    if _coerce_bool(record.data.get("success")) is False:
        return True
    if _coerce_bool(record.data.get("failed")) is True:
        return True
    status = str(record.data.get("status", "")).strip().lower()
    if status in {"fail", "failed", "error"}:
        return True
    errors = _first_present(record.data, ("errors", "error"))
    if isinstance(errors, list):
        return bool(errors)
    return bool(errors)


def _guided_linked_run_ids(record: JsonRecord) -> dict[str, str]:
    if not isinstance(record.data, dict):
        return {}

    linked: dict[str, str] = {}
    for label, key in (
        ("firmware", "firmware_run_id"),
        ("config", "config_run_id"),
        ("run", "run_id"),
    ):
        run_id = _valid_run_id(record.data.get(key))
        if run_id and run_id not in linked.values():
            linked[label] = run_id
    return linked


def _validation_git_commit(data: dict[str, Any]) -> Any:
    for key in ("git_commit", "commit", "git_sha", "git_commit_hash"):
        if data.get(key):
            return data[key]
    git = data.get("git")
    if isinstance(git, dict):
        return _first_present(git, ("commit", "sha", "head"))
    return None


def _validation_sort_key(record: JsonRecord) -> str:
    return _basename(record.path)


def _best_validation_record(validations: Sequence[JsonRecord]) -> JsonRecord | None:
    validated = [
        record
        for record in validations
        if isinstance(record.data, dict)
        and _coerce_bool(record.data.get("post_connection_config_validated")) is True
    ]
    if not validated:
        return None
    return max(validated, key=_validation_sort_key)


def _append_indexed_value(index: dict[str, list[Any]], run_id: str, value: Any) -> None:
    cleaned = _valid_run_id(run_id)
    if cleaned:
        index.setdefault(cleaned, []).append(value)


def _build_indexes(
    run_results: Sequence[RunResult],
    progress_logs: Sequence[ProgressLog],
    run_manifests: Sequence[JsonRecord],
) -> ArtifactIndexes:
    results_by_run_id: dict[str, list[RunResult]] = {}
    progress_by_run_id: dict[str, list[ProgressLog]] = {}
    manifests_by_run_id: dict[str, list[JsonRecord]] = {}

    for result in run_results:
        _append_indexed_value(results_by_run_id, result.run_id, result)
    for progress in progress_logs:
        _append_indexed_value(progress_by_run_id, progress.run_id, progress)
    for manifest in run_manifests:
        _append_indexed_value(manifests_by_run_id, _manifest_run_id(manifest), manifest)

    return ArtifactIndexes(
        results_by_run_id=results_by_run_id,
        progress_by_run_id=progress_by_run_id,
        manifests_by_run_id=manifests_by_run_id,
    )


def _read_bundle(bundle_path: Path) -> BundleContents:
    if not bundle_path.exists():
        raise BundleReportError(f"bundle does not exist: {bundle_path}")
    if not bundle_path.is_file():
        raise BundleReportError(f"bundle is not a file: {bundle_path}")

    try:
        with zipfile.ZipFile(bundle_path) as bundle:
            names = sorted(info.filename for info in bundle.infolist() if not info.is_dir())
            manifest = (
                _load_json_member(bundle, "bundle_manifest.json")
                if "bundle_manifest.json" in names
                else None
            )
            guided_states = [
                _load_json_member(bundle, name)
                for name in names
                if _matches(name, "guided_*_state.json")
            ]
            result_records = [
                _load_json_member(bundle, name)
                for name in names
                if _matches(name, "*_result.json")
            ]
            run_results = [_parse_run_result(record) for record in result_records]
            progress_logs = [
                _parse_progress_log(bundle, name)
                for name in names
                if _matches(name, "*_progress.jsonl")
            ]
            run_manifests = [
                _load_json_member(bundle, name)
                for name in names
                if name != "bundle_manifest.json" and _matches(name, "*_manifest.json")
            ]
            validations = [
                _load_json_member(bundle, name)
                for name in names
                if _matches(name, "validation_*.json")
            ]
    except zipfile.BadZipFile as exc:
        raise BundleReportError(f"bundle is not a valid zip file: {bundle_path}") from exc

    json_errors: list[str] = []
    for record in [item for item in guided_states + run_manifests + validations if item.error]:
        json_errors.append(str(record.error))
    for result in run_results:
        if result.parse_error:
            json_errors.append(result.parse_error)
    for progress in progress_logs:
        json_errors.extend(progress.parse_errors)
    if manifest and manifest.error:
        json_errors.append(manifest.error)

    indexes = _build_indexes(run_results, progress_logs, run_manifests)
    return BundleContents(
        bundle_path=bundle_path,
        names=names,
        manifest=manifest,
        raw_bin_files=[name for name in names if _basename(name).lower().endswith(".bin")],
        json_errors=json_errors,
        guided_states=guided_states,
        run_results=run_results,
        progress_logs=progress_logs,
        run_manifests=run_manifests,
        validations=validations,
        indexes=indexes,
    )


def _linked_progress_for_guided(contents: BundleContents, guided: JsonRecord) -> list[ProgressLog]:
    linked_run_ids = _guided_linked_run_ids(guided).values()
    progress: list[ProgressLog] = []
    for run_id in linked_run_ids:
        progress.extend(contents.indexes.progress_by_run_id.get(run_id, []))
    return progress


def _linked_artifact_summary(contents: BundleContents, guided: JsonRecord) -> LinkedArtifactSummary:
    linked = _guided_linked_run_ids(guided)
    firmware_id = linked.get("firmware")
    config_id = linked.get("config")
    linked_ids = set(linked.values())

    unrelated_count = 0
    for index in (
        contents.indexes.results_by_run_id,
        contents.indexes.progress_by_run_id,
        contents.indexes.manifests_by_run_id,
    ):
        for run_id, artifacts in index.items():
            if run_id not in linked_ids:
                unrelated_count += len(artifacts)

    return LinkedArtifactSummary(
        firmware_result_found=bool(firmware_id and contents.indexes.results_by_run_id.get(firmware_id)),
        firmware_progress_found=bool(
            firmware_id and contents.indexes.progress_by_run_id.get(firmware_id)
        ),
        config_result_found=bool(config_id and contents.indexes.results_by_run_id.get(config_id)),
        config_progress_found=bool(config_id and contents.indexes.progress_by_run_id.get(config_id)),
        unrelated_ignored_count=unrelated_count,
    )


def _build_suspicious_findings(contents: BundleContents) -> list[str]:
    findings: list[str] = []
    if contents.manifest is None:
        findings.append("Missing bundle_manifest.json")
    if contents.raw_bin_files:
        findings.append("Raw .bin files included: " + ", ".join(contents.raw_bin_files))
    findings.extend(contents.json_errors)

    for result in contents.run_results:
        if result.success is False:
            findings.append(f"Result {result.path} reports success=false")

    for progress in contents.progress_logs:
        if progress.failed_command_count:
            findings.append(
                f"Progress {progress.path} contains {progress.failed_command_count} failed command(s)"
            )

    for guided in contents.guided_states:
        if not isinstance(guided.data, dict):
            continue

        linked = _guided_linked_run_ids(guided)
        dry_run = _coerce_bool(guided.data.get("dry_run")) is True
        linked_progress = _linked_progress_for_guided(contents, guided)

        if _guided_failed(guided):
            for run_id in sorted(linked.values()):
                for result in contents.indexes.results_by_run_id.get(run_id, []):
                    if result.success is True:
                        findings.append(
                            f"Guided state {guided.path} failed but linked result {result.path} reports success=true"
                        )

        if dry_run:
            if _coerce_bool(guided.data.get("lua_generated")) is True:
                findings.append(f"Dry-run guided state {guided.path} has lua_generated=true")
            if _coerce_bool(guided.data.get("validation_recorded")) is True:
                findings.append(
                    f"Dry-run guided state {guided.path} has validation_recorded=true"
                )
            for progress in linked_progress:
                if progress.hardware_commands:
                    findings.append(
                        f"Dry-run guided state {guided.path} linked progress {progress.path} contains hardware commands: "
                        + ", ".join(progress.hardware_commands)
                    )
            continue

        if _coerce_bool(guided.data.get("hardware_touched")) is False:
            for progress in linked_progress:
                if progress.hardware_commands:
                    findings.append(
                        f"Guided state {guided.path} has hardware_touched=false but linked progress {progress.path} contains hardware commands: "
                        + ", ".join(progress.hardware_commands)
                    )

    return findings


def _append_best_validation(lines: list[str], validations: Sequence[JsonRecord]) -> None:
    lines.extend(["## Best Validation Found"])
    record = _best_validation_record(validations)
    if record is None or not isinstance(record.data, dict):
        lines.extend(["- No post-connection validation record found.", ""])
        return

    data = record.data
    lines.extend(
        [
            f"- file: `{record.path}`",
            f"- label: {_format_value(data.get('label'))}",
            f"- firmware_run_id: {_format_value(data.get('firmware_run_id'))}",
            f"- config_run_id: {_format_value(data.get('config_run_id'))}",
            f"- git commit: {_format_value(_validation_git_commit(data))}",
            "",
        ]
    )


def generate_report(bundle: str | Path) -> str:
    """Return a Markdown report for a probe bundle zip."""
    bundle_path = Path(bundle).expanduser().resolve()
    contents = _read_bundle(bundle_path)
    manifest_exists = contents.manifest is not None
    hashes_present = _manifest_hashes_present(contents.manifest)
    findings = _build_suspicious_findings(contents)

    lines: list[str] = ["# Probe Bundle Report", ""]
    lines.extend(
        [
            "## Bundle Metadata",
            f"- Bundle path: `{bundle_path}`",
            f"- Number of files: {_metadata_file_count(contents)}",
            f"- bundle_manifest.json exists: {_format_bool(manifest_exists)}",
            f"- SHA256 hashes are present: {_format_bool(hashes_present)}",
        ]
    )
    raw_present = bool(contents.raw_bin_files)
    raw_line = f"- Raw .bin files present: {_format_bool(raw_present)}"
    if raw_present:
        raw_line += " (WARNING: raw ADC .bin files were included)"
    lines.extend([raw_line, ""])

    _append_best_validation(lines, contents.validations)

    lines.extend(["## Guided Workflow States"])
    if not contents.guided_states:
        lines.append("- No guided workflow states found.")
    for record in contents.guided_states:
        lines.extend([f"### `{record.path}`"])
        if not isinstance(record.data, dict):
            lines.append(f"- errors: {_format_value(record.error)}")
            continue
        data = record.data
        lines.extend(
            [
                f"- workflow_id: {_format_value(data.get('workflow_id'))}",
                f"- label: {_format_value(data.get('label'))}",
                f"- current_stage: {_format_value(data.get('current_stage'))}",
                f"- firmware_run_id: {_format_value(data.get('firmware_run_id'))}",
                f"- config_run_id: {_format_value(data.get('config_run_id'))}",
                f"- dry_run: {_format_value(data.get('dry_run'))}",
                f"- hardware_touched: {_format_value(data.get('hardware_touched'))}",
                f"- lua_generated: {_format_value(data.get('lua_generated'))}",
                f"- validation_recorded: {_format_value(data.get('validation_recorded'))}",
                f"- errors: {_format_value(_first_present(data, ('errors', 'error')))}",
                "#### Linked Artifacts",
            ]
        )
        linked_summary = _linked_artifact_summary(contents, record)
        lines.extend(
            [
                "- linked firmware result found: "
                + _format_bool(linked_summary.firmware_result_found),
                "- linked firmware progress found: "
                + _format_bool(linked_summary.firmware_progress_found),
                "- linked config result found: "
                + _format_bool(linked_summary.config_result_found),
                "- linked config progress found: "
                + _format_bool(linked_summary.config_progress_found),
                f"- unrelated artifacts ignored: {linked_summary.unrelated_ignored_count}",
            ]
        )
    lines.append("")

    lines.extend(["## Run Results"])
    if not contents.run_results:
        lines.append("- No run result files found.")
    for result in contents.run_results:
        lines.extend(
            [
                f"### `{result.path}`",
                f"- run_id: {_format_value(result.run_id)}",
                f"- stage: {_format_value(result.stage)}",
                f"- success: {_format_bool(result.success)}",
                f"- error: {_format_value(result.parse_error or result.error)}",
                f"- warnings: {_format_value(result.warnings)}",
            ]
        )
    lines.append("")

    lines.extend(["## Progress Logs"])
    if not contents.progress_logs:
        lines.append("- No progress logs found.")
    for progress in contents.progress_logs:
        lines.extend(
            [
                f"### `{progress.path}`",
                f"- run_id: {_format_value(progress.run_id)}",
                f"- command count: {progress.command_count}",
                f"- failed command count: {progress.failed_command_count}",
                "- hardware commands observed: "
                + (", ".join(progress.hardware_commands) if progress.hardware_commands else "none"),
                f"- last command: {_format_value(progress.last_command)}",
            ]
        )
    lines.append("")

    lines.extend(["## Validation Records"])
    if not contents.validations:
        lines.append("- No validation records found.")
    for record in contents.validations:
        lines.extend([f"### `{record.path}`"])
        if not isinstance(record.data, dict):
            lines.append(f"- error: {_format_value(record.error)}")
            continue
        data = record.data
        lines.extend(
            [
                f"- label: {_format_value(data.get('label'))}",
                f"- firmware_run_id: {_format_value(data.get('firmware_run_id'))}",
                f"- config_run_id: {_format_value(data.get('config_run_id'))}",
                "- post_connection_config_validated: "
                + _format_value(data.get("post_connection_config_validated")),
                f"- git commit: {_format_value(_validation_git_commit(data))}",
            ]
        )
    lines.append("")

    lines.extend(["## Suspicious Findings"])
    if findings:
        lines.extend(f"- {finding}" for finding in findings)
    else:
        lines.append("- No suspicious findings found.")
    lines.append("")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        report = generate_report(args.bundle)
    except BundleReportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.out is None:
        print(report, end="")
        return 0

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"Wrote probe bundle report to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())