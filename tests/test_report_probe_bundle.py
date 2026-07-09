from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import zipfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "tools" / "report_probe_bundle.py"
SPEC = importlib.util.spec_from_file_location("report_probe_bundle", SCRIPT_PATH)
assert SPEC is not None
reporter = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = reporter
assert SPEC.loader is not None
SPEC.loader.exec_module(reporter)


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True) + "\n").encode("utf-8")


def _write_bundle(path: Path, files: dict[str, bytes | str], *, manifest: bool = True) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized: dict[str, bytes] = {}
    for name, content in files.items():
        normalized[name] = content.encode("utf-8") if isinstance(content, str) else content

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, content in normalized.items():
            bundle.writestr(name, content)
        if manifest:
            manifest_data = {
                "schema_version": 1,
                "file_count": len(normalized),
                "files": [
                    {
                        "path": name,
                        "size": len(content),
                        "sha256": hashlib.sha256(content).hexdigest(),
                    }
                    for name, content in sorted(normalized.items())
                ],
            }
            bundle.writestr("bundle_manifest.json", _json_bytes(manifest_data))
    return path


def _synthetic_bundle(tmp_path: Path, *, include_bin: bool = False) -> Path:
    files: dict[str, bytes | str] = {
        "guided_smoke_state.json": _json_bytes(
            {
                "workflow_id": "workflow-1",
                "label": "Smoke validation",
                "current_stage": "firmware",
                "firmware_run_id": "abc123",
                "config_run_id": "def456",
                "dry_run": False,
                "hardware_touched": False,
                "lua_generated": True,
                "validation_recorded": True,
                "errors": ["firmware stage failed"],
            }
        ),
        "abc123_firmware_power_result.json": _json_bytes(
            {"run_id": "abc123", "success": True, "warnings": ["warm boot"]}
        ),
        "def456_config_result.json": _json_bytes(
            {"run_id": "def456", "success": False, "error": "config failed"}
        ),
        "abc123_firmware_power_progress.jsonl": "\n".join(
            [
                json.dumps({"command": "ar1.PowerOn(1)", "ok": True}),
                json.dumps({"command": "ar1.RfInit()", "ok": False}),
                json.dumps({"command": "ar1.StartFrame()", "ok": True}),
            ]
        )
        + "\n",
        "validation_20260708_120000.json": _json_bytes(
            {
                "label": "Smoke validation",
                "firmware_run_id": "abc123",
                "config_run_id": "def456",
                "post_connection_config_validated": True,
                "git": {"commit": "deadbeef"},
            }
        ),
    }
    if include_bin:
        files["capture.bin"] = b"raw-adc"
    return _write_bundle(tmp_path / "bundle.zip", files)


def test_report_generated_from_synthetic_bundle(tmp_path):
    bundle = _synthetic_bundle(tmp_path)
    out = tmp_path / "report.md"

    rc = reporter.main(["--bundle", str(bundle), "--out", str(out)])

    report = out.read_text(encoding="utf-8")
    assert rc == 0
    assert "# Probe Bundle Report" in report
    assert "## Bundle Metadata" in report
    assert "- Number of files: 5" in report
    assert "- bundle_manifest.json exists: yes" in report
    assert "- SHA256 hashes are present: yes" in report
    assert "- workflow_id: workflow-1" in report
    assert "- label: Smoke validation" in report
    assert "- run_id: abc123" in report
    assert "- stage: firmware_power" in report
    assert "- git commit: deadbeef" in report


def test_stdout_mode_works(tmp_path, capsys):
    bundle = _synthetic_bundle(tmp_path)

    rc = reporter.main(["--bundle", str(bundle)])

    captured = capsys.readouterr()
    assert rc == 0
    assert captured.err == ""
    assert captured.out.startswith("# Probe Bundle Report")
    assert "## Suspicious Findings" in captured.out


def test_detects_guided_failed_result_success_mismatch(tmp_path):
    report = reporter.generate_report(_synthetic_bundle(tmp_path))

    assert "failed but linked result abc123_firmware_power_result.json reports success=true" in report


def test_detects_hardware_command_presence(tmp_path):
    report = reporter.generate_report(_synthetic_bundle(tmp_path))

    assert "- hardware commands observed: PowerOn, RfInit, StartFrame" in report
    assert "hardware_touched=false" in report
    assert "contains hardware commands: PowerOn, RfInit, StartFrame" in report
    assert "contains 1 failed command(s)" in report


def test_detects_raw_bin_warning(tmp_path):
    report = reporter.generate_report(_synthetic_bundle(tmp_path, include_bin=True))

    assert "- Raw .bin files present: yes (WARNING: raw ADC .bin files were included)" in report
    assert "- Raw .bin files included: capture.bin" in report


def test_handles_missing_bundle_manifest_gracefully(tmp_path):
    bundle = _write_bundle(
        tmp_path / "missing_manifest.zip",
        {"probe_result.json": _json_bytes({"run_id": "probe", "success": True})},
        manifest=False,
    )

    report = reporter.generate_report(bundle)

    assert "- bundle_manifest.json exists: no" in report
    assert "- SHA256 hashes are present: no" in report
    assert "- Missing bundle_manifest.json" in report


def test_handles_malformed_json_gracefully(tmp_path):
    bundle = _write_bundle(
        tmp_path / "malformed.zip",
        {
            "bad_result.json": "{not json",
            "guided_bad_state.json": "{also bad",
        },
        manifest=True,
    )

    report = reporter.generate_report(bundle)

    assert "Malformed JSON in bad_result.json" in report
    assert "Malformed JSON in guided_bad_state.json" in report
    assert "### `bad_result.json`" in report
    assert "### `guided_bad_state.json`" in report


def test_handles_empty_bundle_gracefully(tmp_path):
    bundle = tmp_path / "empty.zip"
    with zipfile.ZipFile(bundle, "w"):
        pass

    report = reporter.generate_report(bundle)

    assert "- Number of files: 0" in report
    assert "- bundle_manifest.json exists: no" in report
    assert "- No guided workflow states found." in report
    assert "- No run result files found." in report
    assert "- No progress logs found." in report
    assert "- No validation records found." in report
    assert "- Missing bundle_manifest.json" in report

def _suspicious_section(report: str) -> str:
    return report.split("## Suspicious Findings", 1)[1]


def test_dry_run_without_run_ids_ignores_unrelated_hardware_progress(tmp_path):
    bundle = _write_bundle(
        tmp_path / "dry_run_unrelated.zip",
        {
            "guided_dry_state.json": _json_bytes(
                {
                    "workflow_id": "dry",
                    "dry_run": True,
                    "hardware_touched": False,
                    "lua_generated": False,
                    "validation_recorded": False,
                }
            ),
            "645cdf51_firmware_power_progress.jsonl": json.dumps(
                {"command": "ar1.PowerOn(1)", "ok": True}
            )
            + "\n",
            "62d8a837_smoke_config_progress.jsonl": json.dumps(
                {"command": "ar1.RfEnable()", "ok": True}
            )
            + "\n",
        },
    )

    report = reporter.generate_report(bundle)
    suspicious = _suspicious_section(report)

    assert "### `guided_dry_state.json`" in report
    assert "- linked firmware progress found: no" in report
    assert "- linked config progress found: no" in report
    assert "- unrelated artifacts ignored: 2" in report
    assert "hardware_touched=false" not in suspicious
    assert "Dry-run guided state guided_dry_state.json" not in suspicious


def test_linked_firmware_progress_hardware_is_suspicious(tmp_path):
    bundle = _write_bundle(
        tmp_path / "firmware_hardware.zip",
        {
            "guided_failed_state.json": _json_bytes(
                {
                    "workflow_id": "guided",
                    "current_stage": "failed",
                    "firmware_run_id": "68222a75",
                    "hardware_touched": False,
                    "dry_run": False,
                    "errors": ["firmware failed"],
                }
            ),
            "68222a75_firmware_power_progress.jsonl": "\n".join(
                [
                    json.dumps({"command": "ar1.PowerOn(1)", "ok": True}),
                    json.dumps({"command": "ar1.RfEnable()", "ok": True}),
                ]
            )
            + "\n",
        },
    )

    report = reporter.generate_report(bundle)

    assert "linked progress 68222a75_firmware_power_progress.jsonl" in report
    assert "contains hardware commands: PowerOn, RfEnable" in report
    assert "- linked firmware progress found: yes" in report


def test_linked_config_result_success_mismatch_is_suspicious(tmp_path):
    bundle = _write_bundle(
        tmp_path / "config_success_mismatch.zip",
        {
            "guided_failed_state.json": _json_bytes(
                {
                    "workflow_id": "guided",
                    "current_stage": "failed",
                    "config_run_id": "62d8a837",
                    "dry_run": False,
                    "errors": ["config stage failed"],
                }
            ),
            "62d8a837_smoke_config_result.json": _json_bytes(
                {"run_id": "62d8a837", "success": True}
            ),
        },
    )

    report = reporter.generate_report(bundle)

    assert (
        "Guided state guided_failed_state.json failed but linked result "
        "62d8a837_smoke_config_result.json reports success=true"
    ) in report
    assert "- linked config result found: yes" in report


def test_multiple_guided_states_do_not_cross_contaminate(tmp_path):
    bundle = _write_bundle(
        tmp_path / "multi_guided.zip",
        {
            "guided_a_state.json": _json_bytes(
                {
                    "workflow_id": "a",
                    "firmware_run_id": "aaaaaa11",
                    "dry_run": False,
                    "hardware_touched": False,
                }
            ),
            "guided_b_state.json": _json_bytes(
                {
                    "workflow_id": "b",
                    "firmware_run_id": "bbbbbb22",
                    "dry_run": False,
                    "hardware_touched": False,
                }
            ),
            "aaaaaa11_firmware_power_progress.jsonl": json.dumps(
                {"command": "ar1.PowerOn(1)", "ok": True}
            )
            + "\n",
            "bbbbbb22_firmware_power_progress.jsonl": json.dumps(
                {"command": "GetBSSPatchFwVersion", "ok": True}
            )
            + "\n",
        },
    )

    report = reporter.generate_report(bundle)
    suspicious = _suspicious_section(report)

    assert "Guided state guided_a_state.json has hardware_touched=false" in suspicious
    assert "aaaaaa11_firmware_power_progress.jsonl" in suspicious
    assert "Guided state guided_b_state.json has hardware_touched=false" not in suspicious
    assert "bbbbbb22_firmware_power_progress.jsonl contains hardware commands" not in suspicious


def test_only_linked_run_ids_are_used_for_guided_checks(tmp_path):
    bundle = _write_bundle(
        tmp_path / "linked_only.zip",
        {
            "guided_linked_state.json": _json_bytes(
                {
                    "workflow_id": "linked",
                    "firmware_run_id": "11111111",
                    "dry_run": False,
                    "hardware_touched": False,
                }
            ),
            "11111111_firmware_power_progress.jsonl": json.dumps(
                {"command": "GetBSSPatchFwVersion", "ok": True}
            )
            + "\n",
            "22222222_firmware_power_progress.jsonl": json.dumps(
                {"command": "ar1.RfInit()", "ok": True}
            )
            + "\n",
            "22222222_firmware_power_result.json": _json_bytes(
                {"run_id": "22222222", "success": True}
            ),
        },
    )

    report = reporter.generate_report(bundle)
    suspicious = _suspicious_section(report)

    assert "guided_linked_state.json has hardware_touched=false" not in suspicious
    assert "22222222_firmware_power_progress.jsonl contains hardware commands" not in suspicious
    assert "- linked firmware progress found: yes" in report
    assert "- unrelated artifacts ignored: 2" in report


def test_dry_run_flags_only_own_linked_hardware_and_dry_run_side_effects(tmp_path):
    bundle = _write_bundle(
        tmp_path / "dry_run_linked.zip",
        {
            "guided_dry_state.json": _json_bytes(
                {
                    "workflow_id": "dry",
                    "run_id": "dryrun01",
                    "dry_run": True,
                    "hardware_touched": False,
                    "lua_generated": True,
                    "validation_recorded": True,
                }
            ),
            "dryrun01_probe_progress.jsonl": json.dumps(
                {"command": "ar1.FrameConfig()", "ok": True}
            )
            + "\n",
            "other01_probe_progress.jsonl": json.dumps(
                {"command": "ar1.PowerOn(1)", "ok": True}
            )
            + "\n",
        },
    )

    report = reporter.generate_report(bundle)
    suspicious = _suspicious_section(report)

    assert "Dry-run guided state guided_dry_state.json has lua_generated=true" in suspicious
    assert "Dry-run guided state guided_dry_state.json has validation_recorded=true" in suspicious
    assert "linked progress dryrun01_probe_progress.jsonl contains hardware commands: FrameConfig" in suspicious
    assert "other01_probe_progress.jsonl contains hardware commands" not in suspicious