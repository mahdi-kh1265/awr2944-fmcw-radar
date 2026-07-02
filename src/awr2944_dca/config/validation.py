"""Deep validation for RadarConfig beyond Pydantic schema checks.

Returns a list of ValidationResult objects with OK/WARNING/ERROR status.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from awr2944_dca.config.schema import RadarConfig


class Severity(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class ValidationResult:
    """A single validation check result."""

    field: str
    severity: Severity
    message: str


def _is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


def validate_config(cfg: "RadarConfig") -> list[ValidationResult]:
    """Run deep validation checks on a RadarConfig.

    Returns a list of ValidationResult with severity OK, WARNING, or ERROR.
    """
    results: list[ValidationResult] = []

    # --- ADC mode vs layout consistency ---
    layout = cfg.adc.layout
    is_real = not cfg.adc.is_complex

    if is_real and "complex" in layout:
        results.append(ValidationResult(
            field="adc.is_complex / adc.layout",
            severity=Severity.ERROR,
            message=f"ADC mode is real but layout '{layout}' contains 'complex'.",
        ))
    elif not is_real and "real" in layout:
        results.append(ValidationResult(
            field="adc.is_complex / adc.layout",
            severity=Severity.ERROR,
            message=f"ADC mode is complex but layout '{layout}' contains 'real'.",
        ))
    else:
        results.append(ValidationResult(
            field="adc.is_complex / adc.layout",
            severity=Severity.OK,
            message="ADC mode and layout are consistent.",
        ))

    # --- channel_interleave vs layout consistency ---
    ch_interleave = cfg.adc.channel_interleave
    if ch_interleave == 0 and "noninterleaved" in layout:
        results.append(ValidationResult(
            field="adc.channel_interleave / adc.layout",
            severity=Severity.ERROR,
            message=(
                f"channel_interleave=0 (interleaved) but layout "
                f"'{layout}' contains 'noninterleaved'."
            ),
        ))
    elif ch_interleave == 1 and "interleaved" in layout and "noninterleaved" not in layout:
        results.append(ValidationResult(
            field="adc.channel_interleave / adc.layout",
            severity=Severity.ERROR,
            message=(
                f"channel_interleave=1 (non-interleaved) but layout "
                f"'{layout}' contains 'interleaved' (without 'non')."
            ),
        ))
    else:
        results.append(ValidationResult(
            field="adc.channel_interleave / adc.layout",
            severity=Severity.OK,
            message="channel_interleave and layout are consistent.",
        ))

    # --- LVDS lanes vs layout ---
    if cfg.adc.num_lvds_lanes == 2 and "4lane" in layout:
        results.append(ValidationResult(
            field="adc.num_lvds_lanes / adc.layout",
            severity=Severity.ERROR,
            message=f"num_lvds_lanes=2 but layout '{layout}' expects 4 lanes.",
        ))
    elif cfg.adc.num_lvds_lanes == 4 and "2lane" in layout:
        results.append(ValidationResult(
            field="adc.num_lvds_lanes / adc.layout",
            severity=Severity.ERROR,
            message=f"num_lvds_lanes=4 but layout '{layout}' expects 2 lanes.",
        ))
    else:
        results.append(ValidationResult(
            field="adc.num_lvds_lanes / adc.layout",
            severity=Severity.OK,
            message="LVDS lane count and layout are consistent.",
        ))

    # --- ADC bits ---
    if cfg.adc.bits not in (12, 14, 16):
        results.append(ValidationResult(
            field="adc.bits",
            severity=Severity.ERROR,
            message=f"ADC bits={cfg.adc.bits} is not a valid TI ADC resolution (12, 14, 16).",
        ))
    else:
        results.append(ValidationResult(
            field="adc.bits",
            severity=Severity.OK,
            message=f"ADC bits={cfg.adc.bits}.",
        ))

    # --- RX count ---
    num_rx = cfg.hardware.num_rx
    if num_rx < 1 or num_rx > 4:
        results.append(ValidationResult(
            field="hardware.rx_enabled",
            severity=Severity.ERROR,
            message=f"RX count={num_rx} is out of range [1..4].",
        ))
    else:
        results.append(ValidationResult(
            field="hardware.rx_enabled",
            severity=Severity.OK,
            message=f"RX count={num_rx}.",
        ))

    # --- samples_per_chirp power of 2 ---
    if not _is_power_of_two(cfg.adc.samples_per_chirp):
        results.append(ValidationResult(
            field="adc.samples_per_chirp",
            severity=Severity.WARNING,
            message=(
                f"samples_per_chirp={cfg.adc.samples_per_chirp} is not a power of 2. "
                "FFT performance may be suboptimal."
            ),
        ))
    else:
        results.append(ValidationResult(
            field="adc.samples_per_chirp",
            severity=Severity.OK,
            message=f"samples_per_chirp={cfg.adc.samples_per_chirp} (power of 2).",
        ))

    # --- chirps_per_frame ---
    results.append(ValidationResult(
        field="frame.chirps_per_frame",
        severity=Severity.OK,
        message=f"chirps_per_frame={cfg.frame.chirps_per_frame}.",
    ))

    # --- num_frames ---
    results.append(ValidationResult(
        field="frame.num_frames",
        severity=Severity.OK,
        message=f"num_frames={cfg.frame.num_frames}.",
    ))

    # --- Expected file size ---
    expected_bytes = (
        cfg.adc.samples_per_chirp
        * num_rx
        * cfg.frame.chirps_per_frame
        * cfg.frame.num_frames
        * cfg.adc.bytes_per_sample_per_rx
    )
    expected_mb = expected_bytes / (1024 * 1024)
    results.append(ValidationResult(
        field="expected_file_size",
        severity=Severity.OK,
        message=f"Expected adc_data.bin size: {expected_bytes:,} bytes ({expected_mb:.2f} MB).",
    ))

    # --- Layout unvalidated/candidate warning ---
    if "candidate" in layout or "unvalidated" in layout:
        results.append(ValidationResult(
            field="adc.layout",
            severity=Severity.WARNING,
            message=(
                f"Layout '{layout}' is a candidate/unvalidated layout. "
                "Must be confirmed against real hardware capture."
            ),
        ))
    else:
        results.append(ValidationResult(
            field="adc.layout",
            severity=Severity.OK,
            message=f"Layout '{layout}'.",
        ))

    # --- TDM-MIMO warning ---
    if cfg.hardware.antenna_mode.value == "tdm_mimo":
        results.append(ValidationResult(
            field="hardware.antenna_mode",
            severity=Severity.WARNING,
            message=(
                "TDM-MIMO mode selected. Virtual antenna ordering is NOT validated. "
                "TX/chirp mapping must be confirmed against real captures."
            ),
        ))

    return results
