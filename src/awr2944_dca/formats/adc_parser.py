"""Headerless adc_data.bin parser.

Parses the post-reorder/zero-fill binary file produced by TI mmWave Studio
or a custom packet reorder utility.  The file contains raw int16 ADC samples
with no headers — just interleaved sample data.

The parser delegates binary-layout-specific reshaping to BinaryLayout classes
(see formats/layouts.py).  File-size validation is layout-aware.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from awr2944_dca.config.schema import RadarConfig
from awr2944_dca.formats.layouts import BinaryLayout, get_layout


@dataclass
class FileSizeResult:
    """Result of file-size validation."""

    ok: bool
    expected_bytes: int
    actual_bytes: int
    message: str


def validate_file_size(
    path: str | Path,
    config: RadarConfig,
    layout: BinaryLayout | None = None,
) -> FileSizeResult:
    """Validate the size of an adc_data.bin file against the expected size.

    The expected size is computed by the layout (layout-aware).

    Args:
        path: Path to the binary file.
        config: Validated radar config.
        layout: Optional layout override.  If None, looks up config.adc.layout.

    Returns:
        FileSizeResult with ok flag and diagnostic message.
    """
    path = Path(path)

    if layout is None:
        layout = get_layout(config.adc.layout)

    expected = layout.expected_file_size(config)
    actual = path.stat().st_size

    if actual == expected:
        return FileSizeResult(
            ok=True,
            expected_bytes=expected,
            actual_bytes=actual,
            message=f"File size OK: {actual:,} bytes matches expected {expected:,} bytes.",
        )

    # Try to provide a diagnostic
    if actual < expected:
        pct = (actual / expected) * 100
        hint = (
            f"File is {expected - actual:,} bytes SHORT ({pct:.1f}% of expected). "
            f"Possible causes: truncated capture, dropped frames, "
            f"wrong config (samples/chirps/frames/RX count)."
        )
    else:
        ratio = actual / expected
        hint = (
            f"File is {actual - expected:,} bytes LARGER than expected ({ratio:.2f}x). "
            f"Possible causes: extra frames captured, wrong config, "
            f"file includes packet headers (use adc_data.bin, not adc_data_Raw_*.bin)."
        )

    return FileSizeResult(
        ok=False,
        expected_bytes=expected,
        actual_bytes=actual,
        message=(
            f"File size MISMATCH: expected {expected:,} bytes, got {actual:,} bytes. {hint}"
        ),
    )


def parse_adc_bin(
    path: str | Path,
    config: RadarConfig,
    layout: BinaryLayout | None = None,
    *,
    strict_size: bool = True,
) -> np.ndarray:
    """Parse a headerless adc_data.bin into a radar cube.

    Args:
        path: Path to the binary file.
        config: Validated radar config.
        layout: Optional layout override.  If None, looks up config.adc.layout.
        strict_size: If True (default), raise ValueError on file-size mismatch.
            If False, warn and try to parse anyway (may fail or produce garbage).

    Returns:
        Radar cube as numpy array:
            - Real ADC:    float32 with shape [frames, chirps, rx, samples]
            - Complex ADC: complex64 with shape [frames, chirps, rx, samples]

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If strict_size=True and file size does not match expected.
        KeyError: If the layout name is not registered.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"ADC binary file not found: {path}")

    if layout is None:
        layout = get_layout(config.adc.layout)

    # Validate file size
    size_result = validate_file_size(path, config, layout)
    if not size_result.ok:
        if strict_size:
            raise ValueError(size_result.message)
        else:
            warnings.warn(size_result.message, UserWarning, stacklevel=2)

    # Warn if layout is unvalidated
    if not layout.lab_validated:
        warnings.warn(
            f"Parsing with unvalidated layout '{layout.name}'. "
            f"Results should be verified against known reference data. "
            f"See docs/DATA_FORMATS.md for the validation checklist.",
            UserWarning,
            stacklevel=2,
        )

    # Read raw int16 samples
    raw = np.fromfile(path, dtype=np.int16)

    # Delegate reshaping to the layout
    cube = layout.reshape_samples(raw, config)

    return cube
