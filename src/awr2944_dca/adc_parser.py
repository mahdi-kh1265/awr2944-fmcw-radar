"""Minimal ADC binary parser for validated adc_data.bin files.

Parses post-processed adc_data.bin (NOT adc_data_Raw_0.bin) into a
numpy cube shaped (frames, chirps, rx, samples) of complex64.

No FFT, no Doppler, no angle processing.  This is the raw-data
loading and inspection layer only.

.. deprecated::
    **INVALID FOR AWR2944 RAW CAPTURES.**
    The AWR2944 outputs Real int16 ADC data (not complex I/Q) over
    2 LVDS lanes.  DCA1000 raw files from AWR2944 contain 4-word-slot
    frames with inactive-lane filler in slots 2/3.  Interpreting such
    files as complex int16 [I,Q,I,Q,...] produces meaningless results.

    Use ``awr2944_adc.parse_awr2944_real()`` instead for AWR2944.

    This module may still be valid for devices that produce complex ADC
    output (e.g., xWR14xx, xWR16xx, AWR2243) but must NOT be used for
    AWR2944 without explicit device/layout metadata confirming complex
    format.

Validated binary assumptions (parser v1):
    adc_data.bin size : 4,194,304 bytes
    sample format     : complex int16 (I int16 + Q int16 = 4 bytes)
    default shape     : (8 frames, 128 chirps, 4 RX, 256 samples)
    expected complex  : 1,048,576
    expected int16    : 2,097,152

Layout assumption:
    The default layout ``frame_chirp_rx_sample`` is a hypothesis based
    on the validated capture.  It has NOT been confirmed against TI
    MATLAB reference scripts or controlled synthetic captures.
"""


from __future__ import annotations

import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Literal

import numpy as np


@dataclass
class AdcParserConfig:
    """Configuration for ADC binary parsing."""

    frames: int = 8
    chirps: int = 128
    rx: int = 4
    samples: int = 256
    sample_format: str = "complex_int16"
    iq_order: Literal["iq", "qi"] = "iq"
    layout: str = "frame_chirp_rx_sample"


def expected_adc_bytes(config: AdcParserConfig | None = None) -> int:
    """Return expected file size in bytes for the given config.

    Each complex sample is 4 bytes (I int16 + Q int16).
    """
    if config is None:
        config = AdcParserConfig()
    return config.frames * config.chirps * config.rx * config.samples * 4


def load_adc_int16(path: str | Path) -> np.ndarray:
    """Read an ADC binary file as a flat array of little-endian int16 values.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file contains an odd number of bytes (not
            aligned to int16) or is empty.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"ADC file not found: {path}")

    data = np.fromfile(path, dtype="<i2")  # little-endian int16

    if data.size == 0:
        raise ValueError(f"ADC file is empty: {path}")

    # np.fromfile with int16 dtype will already reject odd-byte files
    # but let's be explicit about the file size check
    file_size = path.stat().st_size
    if file_size % 2 != 0:
        raise ValueError(
            f"ADC file has odd byte count ({file_size}), "
            f"not aligned to int16: {path}"
        )

    return data


def parse_complex_int16(
    path: str | Path,
    config: AdcParserConfig | None = None,
) -> np.ndarray:
    """Parse an ADC binary file into a complex64 cube.

    Returns:
        numpy array shaped (frames, chirps, rx, samples) of complex64.

    Raises:
        ValueError: If file size does not match expected bytes, or if
            the int16 count is odd (cannot pair into complex samples).
    """
    if config is None:
        config = AdcParserConfig()

    path = Path(path)
    file_size = path.stat().st_size
    expected = expected_adc_bytes(config)

    if file_size != expected:
        raise ValueError(
            f"ADC file size mismatch: got {file_size:,} bytes, "
            f"expected {expected:,} bytes "
            f"({config.frames}f × {config.chirps}c × {config.rx}rx × "
            f"{config.samples}s × 4 bytes/sample). "
            f"File: {path}"
        )

    raw = load_adc_int16(path)

    if raw.size % 2 != 0:
        raise ValueError(
            f"Odd int16 count ({raw.size}), cannot pair into complex "
            f"samples: {path}"
        )

    # Pair int16 values into complex samples
    i_vals = raw[0::2].astype(np.float32)
    q_vals = raw[1::2].astype(np.float32)

    if config.iq_order == "iq":
        complex_data = i_vals + 1j * q_vals
    elif config.iq_order == "qi":
        complex_data = q_vals + 1j * i_vals
    else:
        raise ValueError(f"Unknown iq_order: {config.iq_order!r}")

    # Reshape to (frames, chirps, rx, samples)
    total_complex = config.frames * config.chirps * config.rx * config.samples
    if complex_data.size != total_complex:
        raise ValueError(
            f"Complex sample count {complex_data.size} does not match "
            f"expected {total_complex}"
        )

    cube = complex_data.reshape(
        config.frames, config.chirps, config.rx, config.samples
    )
    return cube


def inspect_adc_file(
    path: str | Path,
    config: AdcParserConfig | None = None,
) -> dict:
    """Inspect an ADC binary file and return structured metadata + statistics.

    Does NOT raise on size mismatch — returns error info in the dict instead.
    """
    if config is None:
        config = AdcParserConfig()

    path = Path(path)
    result: dict = {
        "file_path": str(path.resolve()),
        "file_size": 0,
        "expected_bytes": expected_adc_bytes(config),
        "size_match": False,
        "config": asdict(config),
        "layout_assumption": config.layout,
        "layout_assumption_confirmed": False,
        "error": None,
    }

    if not path.exists():
        result["error"] = f"File not found: {path}"
        return result

    file_size = path.stat().st_size
    result["file_size"] = file_size

    # SHA256
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    result["sha256"] = sha.hexdigest()

    expected = expected_adc_bytes(config)
    result["size_match"] = file_size == expected

    if file_size != expected:
        result["error"] = (
            f"Size mismatch: {file_size:,} != {expected:,} bytes"
        )
        return result

    if file_size % 2 != 0:
        result["error"] = f"Odd byte count: {file_size}"
        return result

    # Load raw int16
    raw = load_adc_int16(path)
    result["int16_count"] = int(raw.size)
    result["complex_count"] = int(raw.size // 2)
    result["first_16_int16_values"] = raw[:16].tolist()

    # Parse complex
    try:
        cube = parse_complex_int16(path, config)
    except ValueError as e:
        result["error"] = str(e)
        return result

    result["shape"] = list(cube.shape)
    result["dtype"] = str(cube.dtype)

    # First 8 complex values
    flat = cube.ravel()
    first_8 = flat[:8]
    result["first_8_complex_values"] = [
        {"real": float(c.real), "imag": float(c.imag)} for c in first_8
    ]

    # Statistics
    real_part = cube.real
    imag_part = cube.imag

    result["real_min"] = float(np.min(real_part))
    result["real_max"] = float(np.max(real_part))
    result["real_mean"] = float(np.mean(real_part))
    result["real_std"] = float(np.std(real_part))
    result["imag_min"] = float(np.min(imag_part))
    result["imag_max"] = float(np.max(imag_part))
    result["imag_mean"] = float(np.mean(imag_part))
    result["imag_std"] = float(np.std(imag_part))

    # Zero fraction
    zero_count = int(np.count_nonzero(cube == 0))
    total = int(cube.size)
    result["zero_fraction"] = float(zero_count / total) if total > 0 else 0.0
    result["all_zero"] = bool(np.all(cube == 0))

    # Per-RX RMS (axis=-1 is samples, collapse frames and chirps too)
    per_rx_rms = []
    for rx_idx in range(config.rx):
        rx_slice = cube[:, :, rx_idx, :]  # (frames, chirps, samples)
        rms = float(np.sqrt(np.mean(np.abs(rx_slice) ** 2)))
        per_rx_rms.append({"rx": rx_idx, "rms": rms})
    result["per_rx_rms"] = per_rx_rms

    return result
