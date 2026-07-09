"""Validation of DCA1000 capture output files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class CaptureFileCheck:
    filename: str
    exists: bool
    size_bytes: int
    status: str  # "PASS", "WARN", "FAIL"
    detail: str


@dataclass
class CaptureValidation:
    capture_dir: str
    expected_bytes: int
    postproc_file: CaptureFileCheck
    raw_file: CaptureFileCheck
    post_processing_status: str  # "COMPLETE", "MISSING"
    overall: str                 # "PASS", "WARN", "FAIL"
    dca_log: str | None = None   # Path or content summary of latest DCA log


def _check_content(path: Path) -> tuple[bool, str]:
    """Check if file has basic sanity (not all zeros, not all 0xFF).
    
    Reads first 1024 bytes.
    Returns (ok, detail).
    """
    try:
        with open(path, "rb") as f:
            data = f.read(1024)
        if not data:
            return False, "File is empty (0 bytes)"
        if all(b == 0 for b in data):
            return False, "First 1024 bytes all zeros"
        if all(b == 0xFF for b in data):
            return False, "First 1024 bytes all 0xFF"
        return True, "not all-zero, not all-0xFF"
    except Exception as e:
        return False, f"Read error: {e}"


def check_capture_files(
    capture_dir: str | Path,
    expected_bytes: int,
) -> CaptureValidation:
    """Validate DCA1000 capture output files.
    
    Checks both the raw UDP dump and the post-processed ADC stream.
    """
    capture_dir = Path(capture_dir)
    postproc_path = capture_dir / "adc_data.bin"
    raw_path = capture_dir / "adc_data_Raw_0.bin"

    # 1. Check Post-Processed File (adc_data.bin)
    postproc_check = CaptureFileCheck("adc_data.bin", False, 0, "FAIL", "NOT FOUND")
    if postproc_path.exists():
        postproc_check.exists = True
        size = postproc_path.stat().st_size
        postproc_check.size_bytes = size
        
        if size == 0:
            postproc_check.status = "FAIL"
            postproc_check.detail = "0 bytes"
        else:
            # Strict size check for post-processed (must be exactly right, or within small tolerance)
            # Actually, the user asked: "If adc_data.bin exists, compare it more strictly to 524288."
            # Tolerance: ±5%
            min_size = int(expected_bytes * 0.95)
            max_size = int(expected_bytes * 1.05)
            
            ok, content_detail = _check_content(postproc_path)
            
            if not ok:
                postproc_check.status = "FAIL"
                postproc_check.detail = content_detail
            elif size < min_size:
                postproc_check.status = "FAIL"
                postproc_check.detail = f"too small: {size} < {min_size}"
            elif size > max_size:
                postproc_check.status = "FAIL"
                postproc_check.detail = f"too large: {size} > {max_size}"
            elif size == expected_bytes:
                postproc_check.status = "PASS"
                postproc_check.detail = f"exact match ({content_detail})"
            else:
                postproc_check.status = "PASS"
                postproc_check.detail = f"within 5% tolerance ({content_detail})"

    # 2. Check Raw File (adc_data_Raw_0.bin)
    raw_check = CaptureFileCheck("adc_data_Raw_0.bin", False, 0, "FAIL", "NOT FOUND")
    if raw_path.exists():
        raw_check.exists = True
        size = raw_path.stat().st_size
        raw_check.size_bytes = size
        
        if size == 0:
            raw_check.status = "FAIL"
            raw_check.detail = "0 bytes"
        else:
            # Loose size check: UDP dump has headers, so it should be >= expected bytes
            ok, content_detail = _check_content(raw_path)
            
            if not ok:
                raw_check.status = "FAIL"
                raw_check.detail = content_detail
            elif size < expected_bytes:
                raw_check.status = "FAIL"
                raw_check.detail = f"too small: {size} < {expected_bytes}"
            else:
                raw_check.status = "PASS"
                raw_check.detail = f"≥ expected, raw overhead OK ({content_detail})"

    # 3. Overall Status
    if postproc_check.status == "PASS":
        post_processing_status = "COMPLETE"
        overall = "PASS"
    elif raw_check.status == "PASS":
        post_processing_status = "MISSING"
        overall = "WARN"
    else:
        post_processing_status = "MISSING"
        overall = "FAIL"

    val = CaptureValidation(
        capture_dir=str(capture_dir.resolve()),
        expected_bytes=expected_bytes,
        postproc_file=postproc_check,
        raw_file=raw_check,
        post_processing_status=post_processing_status,
        overall=overall,
    )
    if overall != "PASS":
        # Find newest .log or .txt file in capture_dir
        log_files = list(capture_dir.glob("*.log")) + list(capture_dir.glob("*.txt"))
        if log_files:
            newest_log = max(log_files, key=lambda p: p.stat().st_mtime)
            try:
                # Read last few lines
                with open(newest_log, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()
                    tail = "".join(lines[-5:]).strip()
                val.dca_log = f"{newest_log.name}: {tail}"
            except Exception as e:
                val.dca_log = f"{newest_log.name}: (Failed to read: {e})"
                
    return val
