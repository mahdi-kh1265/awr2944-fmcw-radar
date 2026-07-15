"""CaptureVerificationReport — structured offline capture verification.

Provides a report with individual checks, a summary, and
raise_for_errors() for strict mode.  Preserves dict-style
compatibility via as_dict().
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class VerificationCheck:
    """A single verification check result."""
    name: str
    status: str  # "PASS", "FAIL", "WARN", "SKIP"
    detail: str = ""


class CaptureVerificationError(Exception):
    """Raised by raise_for_errors() when verification fails."""
    def __init__(self, report: CaptureVerificationReport):
        self.report = report
        fails = [c for c in report.checks if c.status == "FAIL"]
        msg = f"Capture verification failed with {len(fails)} error(s):\n"
        for c in fails:
            msg += f"  [{c.name}] {c.detail}\n"
        super().__init__(msg)


@dataclass
class CaptureVerificationReport:
    """Structured capture verification report."""
    success: bool
    checks: list[VerificationCheck] = field(default_factory=list)

    def summary(self) -> str:
        lines = [f"Verification: {'PASS' if self.success else 'FAIL'}"]
        for c in self.checks:
            lines.append(f"  [{c.status:^4}] {c.name:<30} {c.detail}")
        return "\n".join(lines)

    def raise_for_errors(self) -> None:
        """Raise CaptureVerificationError if any check failed."""
        if not self.success:
            raise CaptureVerificationError(self)

    def as_dict(self) -> dict:
        """Dict-style compatibility for existing callers."""
        return {
            "passed": self.success,
            "errors": [c.detail for c in self.checks if c.status == "FAIL"],
            "warnings": [c.detail for c in self.checks if c.status == "WARN"],
            "checks": [
                {"name": c.name, "status": c.status, "detail": c.detail}
                for c in self.checks
            ],
        }

    # Mapping compatibility
    def __getitem__(self, key: str) -> Any:
        d = self.as_dict()
        return d[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self.as_dict().get(key, default)

    def __contains__(self, key: str) -> bool:
        return key in self.as_dict()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def verify_production_capture(capture_dir: Path, manifest: dict) -> CaptureVerificationReport:
    """Verify a production capture (manifest.json based).

    All checks are offline. Handles manifest field name variations
    across schema versions.
    """
    import json
    checks: list[VerificationCheck] = []
    
    schema_version = manifest.get("manifest_schema_version", 1)
    
    # Expected bytes fallback to manifest
    native_expected = manifest.get("native_byte_count") or manifest.get("expected_native_bytes")
    canonical_expected = manifest.get("canonical_native_byte_count")
    
    # Merge config_summary.json if present (or required for v4)
    summary_path = capture_dir / "config_summary.json"
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text())
            checks.append(VerificationCheck("config_summary_parse", "PASS"))
            if "native_dca_bytes" in summary:
                native_expected = summary["native_dca_bytes"]
            if "canonical_dca_bytes" in summary:
                canonical_expected = summary["canonical_dca_bytes"]
                
            if schema_version >= 4:
                req_keys = [
                    "config_summary_schema_version", "source_config_kind", 
                    "source_config_sha256", "resolved_config_sha256", 
                    "radar_config_sha256", "target_device", "sdk_version", 
                    "firmware_config_target"
                ]
                missing = [k for k in req_keys if k not in summary]
                if missing:
                    checks.append(VerificationCheck("config_summary_fields", "FAIL", f"Missing keys: {missing}"))
                else:
                    checks.append(VerificationCheck("config_summary_fields", "PASS"))
                    
                    # Verify resolved_config.cfg hash
                    resolved_cfg_path = capture_dir / "resolved_config.cfg"
                    if resolved_cfg_path.exists():
                        import hashlib
                        actual_resolved_sha = hashlib.sha256(resolved_cfg_path.read_bytes()).hexdigest()
                        if actual_resolved_sha == summary.get("resolved_config_sha256"):
                            checks.append(VerificationCheck("resolved_config_hash", "PASS"))
                        else:
                            checks.append(VerificationCheck("resolved_config_hash", "FAIL", "resolved_config.cfg hash mismatch"))
                    else:
                        checks.append(VerificationCheck("resolved_config_hash", "FAIL", "Missing resolved_config.cfg"))
                        
                    # Verify radar_config_sha256 == resolved_config_sha256
                    if summary.get("radar_config_sha256") == summary.get("resolved_config_sha256"):
                        checks.append(VerificationCheck("radar_config_hash_match", "PASS"))
                    else:
                        checks.append(VerificationCheck("radar_config_hash_match", "FAIL", "radar_config_sha256 != resolved_config_sha256"))
                        
                    # Verify manifest vs summary hashes
                    m_source_hash = manifest.get("source_config_sha256")
                    if m_source_hash and m_source_hash != summary.get("source_config_sha256"):
                        checks.append(VerificationCheck("manifest_summary_hash_match", "FAIL", "source_config_sha256 mismatch"))
                    else:
                        checks.append(VerificationCheck("manifest_summary_hash_match", "PASS"))
                    
        except Exception as e:
            checks.append(VerificationCheck("config_summary_parse", "FAIL", f"Malformed JSON: {e}"))
    elif schema_version >= 4:
        checks.append(VerificationCheck("config_summary_parse", "FAIL", "Missing required config_summary.json for V4 capture"))

    # --- File existence ---
    native_path = capture_dir / "adc_data.bin"
    canonical_path = capture_dir / "adc_data_canonical.bin"

    if native_path.exists():
        checks.append(VerificationCheck("native_file_exists", "PASS"))
    else:
        checks.append(VerificationCheck("native_file_exists", "FAIL", f"Missing: {native_path}"))

    if canonical_path.exists():
        checks.append(VerificationCheck("canonical_file_exists", "PASS"))
    else:
        checks.append(VerificationCheck("canonical_file_exists", "FAIL", f"Missing: {canonical_path}"))

    # --- Manifest consistency ---
    m_success = manifest.get("success", False)
    m_status = manifest.get("status", "unknown")
    if m_success and m_status == "complete":
        checks.append(VerificationCheck("manifest_consistency", "PASS", f"status={m_status}"))
    else:
        checks.append(VerificationCheck(
            "manifest_consistency", "FAIL",
            f"success={m_success}, status={m_status}, reason={manifest.get('failure_reason', 'N/A')}"
        ))

    # --- Byte count checks with field-name precedence ---
    # Native actual: captured_native_bytes → file size
    native_actual = manifest.get("captured_native_bytes")
    if native_actual is None and native_path.exists():
        native_actual = native_path.stat().st_size

    if native_path.exists() and native_expected is not None:
        actual_size = native_path.stat().st_size
        if actual_size == native_expected:
            checks.append(VerificationCheck("native_byte_count", "PASS", f"{actual_size:,}"))
        else:
            checks.append(VerificationCheck(
                "native_byte_count", "FAIL",
                f"Expected {native_expected:,}, got {actual_size:,}"
            ))
    elif not native_path.exists():
        checks.append(VerificationCheck("native_byte_count", "SKIP", "No native file"))
    else:
        checks.append(VerificationCheck("native_byte_count", "WARN", "No expected byte count in manifest"))

    # Canonical expected: canonical_native_byte_count
    if canonical_path.exists() and canonical_expected is not None:
        actual_size = canonical_path.stat().st_size
        if actual_size == canonical_expected:
            checks.append(VerificationCheck("canonical_byte_count", "PASS", f"{actual_size:,}"))
        else:
            checks.append(VerificationCheck(
                "canonical_byte_count", "FAIL",
                f"Expected {canonical_expected:,}, got {actual_size:,}"
            ))
    elif not canonical_path.exists():
        checks.append(VerificationCheck("canonical_byte_count", "SKIP", "No canonical file"))

    # --- SHA256 checks ---
    native_sha = manifest.get("native_sha256")
    if native_path.exists() and native_sha:
        actual = _sha256_file(native_path)
        if actual == native_sha:
            checks.append(VerificationCheck("native_sha256", "PASS"))
        else:
            checks.append(VerificationCheck("native_sha256", "FAIL", f"Mismatch: {actual[:16]}... vs {native_sha[:16]}..."))
    elif not native_path.exists():
        checks.append(VerificationCheck("native_sha256", "SKIP", "No native file"))

    canonical_sha = manifest.get("canonical_sha256")
    if canonical_path.exists() and canonical_sha:
        actual = _sha256_file(canonical_path)
        if actual == canonical_sha:
            checks.append(VerificationCheck("canonical_sha256", "PASS"))
        else:
            checks.append(VerificationCheck("canonical_sha256", "FAIL", f"Mismatch: {actual[:16]}... vs {canonical_sha[:16]}..."))
    elif not canonical_path.exists():
        checks.append(VerificationCheck("canonical_sha256", "SKIP", "No canonical file"))

    # --- Packet continuity ---
    # sequence_gap_count (new) → sequence_gaps (legacy)
    seq_gaps = manifest.get("sequence_gap_count", manifest.get("sequence_gaps", 0))
    byte_disc = manifest.get("byte_counter_discontinuity_count", 0)
    if seq_gaps == 0 and byte_disc == 0:
        checks.append(VerificationCheck("packet_continuity", "PASS", "0 gaps, 0 discontinuities"))
    else:
        checks.append(VerificationCheck(
            "packet_continuity", "FAIL",
            f"{seq_gaps} sequence gaps, {byte_disc} byte-counter discontinuities"
        ))

    # --- Payload integrity ---
    missing = manifest.get("missing_payload_bytes", 0)
    overlap = manifest.get("overlap_payload_bytes", 0)
    if missing == 0 and overlap == 0:
        checks.append(VerificationCheck("payload_integrity", "PASS"))
    else:
        checks.append(VerificationCheck(
            "payload_integrity", "FAIL",
            f"{missing} missing bytes, {overlap} overlap bytes"
        ))

    # --- Cube shape ---
    cube_shape = manifest.get("logical_cube_shape")
    if cube_shape and canonical_path.exists():
        try:
            from awr2944_dca.awr2944_adc import parse_awr2944_real
            frames, chirps, rx, samples = cube_shape
            cube = parse_awr2944_real(canonical_path, frames, chirps, rx, samples)
            if list(cube.shape) == cube_shape:
                checks.append(VerificationCheck("cube_shape", "PASS", str(cube_shape)))
            else:
                checks.append(VerificationCheck("cube_shape", "FAIL", f"Expected {cube_shape}, got {list(cube.shape)}"))
        except Exception as e:
            checks.append(VerificationCheck("cube_shape", "FAIL", str(e)))
    elif cube_shape:
        checks.append(VerificationCheck("cube_shape", "SKIP", "No canonical file"))

    success = not any(c.status == "FAIL" for c in checks)
    return CaptureVerificationReport(success=success, checks=checks)
