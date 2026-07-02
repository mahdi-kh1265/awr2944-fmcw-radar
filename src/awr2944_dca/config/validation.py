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

    # --- Load Specs ---
    try:
        from awr2944_dca.config.specs import load_radar_spec, load_capture_card_spec
        radar_spec = load_radar_spec(cfg.rig.radar)
        capture_spec = load_capture_card_spec(cfg.rig.capture_card)
    except FileNotFoundError as e:
        results.append(ValidationResult(
            field="rig",
            severity=Severity.ERROR,
            message=f"Missing spec for device: {e}",
        ))
        return results

    # --- TX/RX Limits from Spec ---
    if cfg.hardware.num_tx > radar_spec.hardware_limits.max_tx_channels:
        results.append(ValidationResult(
            field="hardware.tx_enabled",
            severity=Severity.ERROR,
            message=f"TX count={cfg.hardware.num_tx} exceeds maximum ({radar_spec.hardware_limits.max_tx_channels}).",
        ))
    if cfg.hardware.num_rx > radar_spec.hardware_limits.max_rx_channels:
        results.append(ValidationResult(
            field="hardware.rx_enabled",
            severity=Severity.ERROR,
            message=f"RX count={cfg.hardware.num_rx} exceeds maximum ({radar_spec.hardware_limits.max_rx_channels}).",
        ))
    if cfg.hardware.num_tx <= radar_spec.hardware_limits.max_tx_channels and cfg.hardware.num_rx <= radar_spec.hardware_limits.max_rx_channels:
        results.append(ValidationResult(
            field="hardware.channels",
            severity=Severity.OK,
            message=f"TX ({cfg.hardware.num_tx}) and RX ({cfg.hardware.num_rx}) counts within limits.",
        ))

    # --- Frequency Limits from Spec ---
    freq = cfg.profile.start_freq_ghz
    if freq < radar_spec.hardware_limits.min_frequency_ghz or freq > radar_spec.hardware_limits.max_frequency_ghz:
        results.append(ValidationResult(
            field="profile.start_freq_ghz",
            severity=Severity.ERROR,
            message=f"Frequency {freq} GHz outside supported range [{radar_spec.hardware_limits.min_frequency_ghz}, {radar_spec.hardware_limits.max_frequency_ghz}].",
        ))
    else:
        results.append(ValidationResult(
            field="profile.start_freq_ghz",
            severity=Severity.OK,
            message=f"Frequency {freq} GHz is within supported range.",
        ))

    # --- ADC Bits from Spec ---
    if cfg.adc.bits not in radar_spec.hardware_limits.supported_adc_bits:
        results.append(ValidationResult(
            field="adc.bits",
            severity=Severity.ERROR,
            message=f"ADC bits={cfg.adc.bits} not supported by {radar_spec.device_name} (supports: {radar_spec.hardware_limits.supported_adc_bits}).",
        ))
    else:
        results.append(ValidationResult(
            field="adc.bits",
            severity=Severity.OK,
            message=f"ADC bits={cfg.adc.bits} is supported.",
        ))

    # --- Layout vs Spec ---
    layout = cfg.adc.layout
    if layout not in radar_spec.capture_support.supported_layouts:
        results.append(ValidationResult(
            field="adc.layout",
            severity=Severity.WARNING,
            message=f"Layout '{layout}' not in known supported list for {radar_spec.device_name}.",
        ))

    # --- ADC mode vs layout consistency ---
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

    # --- LVDS lanes vs spec ---
    if cfg.adc.num_lvds_lanes not in radar_spec.capture_support.supported_lvds_lanes:
        results.append(ValidationResult(
            field="adc.num_lvds_lanes",
            severity=Severity.ERROR,
            message=f"LVDS lanes {cfg.adc.num_lvds_lanes} not supported by {radar_spec.device_name} (supports: {radar_spec.capture_support.supported_lvds_lanes}).",
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

    # --- Expected file size ---
    expected_bytes = (
        cfg.adc.samples_per_chirp
        * cfg.hardware.num_rx
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
