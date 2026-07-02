"""Compare our capture.yaml config against a TI config file.

Reports mismatches with severity: ERROR for critical fields (ADC mode,
bits, interleave, RX count), WARNING for frame/chirp/sample counts.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from awr2944_dca.config.schema import RadarConfig
from awr2944_dca.ti.inspect import UNKNOWN, TiExtractedConfig, inspect_ti_file


class CompSeverity(str, Enum):
    MATCH = "MATCH"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"  # TI field is UNKNOWN


@dataclass
class CompareResult:
    """A single comparison result between our config and TI config."""

    field: str
    our_value: str
    ti_value: str
    severity: CompSeverity
    message: str


def _safe_int(val: str) -> int | None:
    if val == UNKNOWN:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def _safe_float(val: str) -> float | None:
    if val == UNKNOWN:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _bitmask_to_count(mask_str: str) -> int | None:
    val = _safe_int(mask_str)
    if val is None:
        return None
    return bin(val).count("1")


def compare_configs(
    cfg: RadarConfig,
    ti_file: str | Path,
) -> list[CompareResult]:
    """Compare our RadarConfig against a TI config file.

    Returns a list of CompareResult with severity levels.
    """
    extracted = inspect_ti_file(ti_file)
    results: list[CompareResult] = []

    # --- ADC mode (is_complex vs adc_fmt) ---
    ti_fmt = _safe_int(extracted.adc_fmt)
    if ti_fmt is not None:
        ti_complex = ti_fmt != 0
        our_complex = cfg.adc.is_complex
        if our_complex != ti_complex:
            results.append(CompareResult(
                field="ADC mode",
                our_value="complex" if our_complex else "real",
                ti_value="complex" if ti_complex else "real",
                severity=CompSeverity.ERROR,
                message="ADC mode mismatch — this will produce garbled data!",
            ))
        else:
            results.append(CompareResult(
                field="ADC mode",
                our_value="complex" if our_complex else "real",
                ti_value="complex" if ti_complex else "real",
                severity=CompSeverity.MATCH,
                message="ADC mode matches.",
            ))
    else:
        results.append(CompareResult(
            field="ADC mode",
            our_value="complex" if cfg.adc.is_complex else "real",
            ti_value=UNKNOWN,
            severity=CompSeverity.SKIPPED,
            message="TI adcFmt not found in file.",
        ))

    # --- ADC bits ---
    ti_bits = _safe_int(extracted.adc_bits)
    if ti_bits is not None:
        # TI enum: 0=12, 1=14, 2=16 or direct value
        actual_bits = {0: 12, 1: 14, 2: 16}.get(ti_bits, ti_bits)
        if cfg.adc.bits != actual_bits:
            results.append(CompareResult(
                field="ADC bits",
                our_value=str(cfg.adc.bits),
                ti_value=str(actual_bits),
                severity=CompSeverity.ERROR,
                message="ADC bit depth mismatch.",
            ))
        else:
            results.append(CompareResult(
                field="ADC bits",
                our_value=str(cfg.adc.bits),
                ti_value=str(actual_bits),
                severity=CompSeverity.MATCH,
                message="ADC bits match.",
            ))
    else:
        results.append(CompareResult(
            field="ADC bits",
            our_value=str(cfg.adc.bits),
            ti_value=UNKNOWN,
            severity=CompSeverity.SKIPPED,
            message="TI adcBits not found in file.",
        ))

    # --- channel_interleave ---
    ti_ch = _safe_int(extracted.ch_interleave)
    if ti_ch is not None:
        if cfg.adc.channel_interleave != ti_ch:
            results.append(CompareResult(
                field="channel_interleave",
                our_value=str(cfg.adc.channel_interleave),
                ti_value=str(ti_ch),
                severity=CompSeverity.ERROR,
                message="Channel interleave mismatch — will produce scrambled RX data!",
            ))
        else:
            results.append(CompareResult(
                field="channel_interleave",
                our_value=str(cfg.adc.channel_interleave),
                ti_value=str(ti_ch),
                severity=CompSeverity.MATCH,
                message="Channel interleave matches.",
            ))
    else:
        results.append(CompareResult(
            field="channel_interleave",
            our_value=str(cfg.adc.channel_interleave),
            ti_value=UNKNOWN,
            severity=CompSeverity.SKIPPED,
            message="TI chInterleave not found in file.",
        ))

    # --- RX count ---
    ti_rx_count = _bitmask_to_count(extracted.rx_channel_en)
    if ti_rx_count is not None:
        if cfg.hardware.num_rx != ti_rx_count:
            results.append(CompareResult(
                field="RX count",
                our_value=str(cfg.hardware.num_rx),
                ti_value=str(ti_rx_count),
                severity=CompSeverity.ERROR,
                message="RX channel count mismatch.",
            ))
        else:
            results.append(CompareResult(
                field="RX count",
                our_value=str(cfg.hardware.num_rx),
                ti_value=str(ti_rx_count),
                severity=CompSeverity.MATCH,
                message="RX count matches.",
            ))
    else:
        results.append(CompareResult(
            field="RX count",
            our_value=str(cfg.hardware.num_rx),
            ti_value=UNKNOWN,
            severity=CompSeverity.SKIPPED,
            message="TI rxChannelEn not found in file.",
        ))

    # --- samples_per_chirp ---
    ti_samples = _safe_int(extracted.num_adc_samples)
    if ti_samples is not None:
        if cfg.adc.samples_per_chirp != ti_samples:
            results.append(CompareResult(
                field="samples_per_chirp",
                our_value=str(cfg.adc.samples_per_chirp),
                ti_value=str(ti_samples),
                severity=CompSeverity.WARNING,
                message="Samples per chirp mismatch.",
            ))
        else:
            results.append(CompareResult(
                field="samples_per_chirp",
                our_value=str(cfg.adc.samples_per_chirp),
                ti_value=str(ti_samples),
                severity=CompSeverity.MATCH,
                message="Samples per chirp match.",
            ))
    else:
        results.append(CompareResult(
            field="samples_per_chirp",
            our_value=str(cfg.adc.samples_per_chirp),
            ti_value=UNKNOWN,
            severity=CompSeverity.SKIPPED,
            message="TI numAdcSamples not found in file.",
        ))

    # --- chirps_per_frame ---
    ti_chirps = _safe_int(extracted.chirps_per_frame)
    if ti_chirps is not None:
        if cfg.frame.chirps_per_frame != ti_chirps:
            results.append(CompareResult(
                field="chirps_per_frame",
                our_value=str(cfg.frame.chirps_per_frame),
                ti_value=str(ti_chirps),
                severity=CompSeverity.WARNING,
                message="Chirps per frame mismatch.",
            ))
        else:
            results.append(CompareResult(
                field="chirps_per_frame",
                our_value=str(cfg.frame.chirps_per_frame),
                ti_value=str(ti_chirps),
                severity=CompSeverity.MATCH,
                message="Chirps per frame match.",
            ))
    else:
        results.append(CompareResult(
            field="chirps_per_frame",
            our_value=str(cfg.frame.chirps_per_frame),
            ti_value=UNKNOWN,
            severity=CompSeverity.SKIPPED,
            message="TI chirps_per_frame not found in file.",
        ))

    # --- num_frames ---
    ti_frames = _safe_int(extracted.num_frames)
    if ti_frames is not None:
        if cfg.frame.num_frames != ti_frames:
            results.append(CompareResult(
                field="num_frames",
                our_value=str(cfg.frame.num_frames),
                ti_value=str(ti_frames),
                severity=CompSeverity.WARNING,
                message="Number of frames mismatch.",
            ))
        else:
            results.append(CompareResult(
                field="num_frames",
                our_value=str(cfg.frame.num_frames),
                ti_value=str(ti_frames),
                severity=CompSeverity.MATCH,
                message="Number of frames match.",
            ))
    else:
        results.append(CompareResult(
            field="num_frames",
            our_value=str(cfg.frame.num_frames),
            ti_value=UNKNOWN,
            severity=CompSeverity.SKIPPED,
            message="TI numFrames not found in file.",
        ))

    return results
