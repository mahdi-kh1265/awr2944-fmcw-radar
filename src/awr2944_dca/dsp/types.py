"""Typed result containers for DSP pipeline outputs.

Every result carries the configuration that produced it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class RangeResult:
    """Output of the range FFT stage."""
    complex_cube: np.ndarray        # [frame, chirp, rx, range_bin] complex64
    magnitude: np.ndarray           # same shape, float32
    power_db: np.ndarray            # same shape, float32
    config_dict: dict[str, Any] = field(default_factory=dict)

    @property
    def shape(self) -> tuple[int, ...]:
        return self.complex_cube.shape

    @property
    def num_range_bins(self) -> int:
        return self.complex_cube.shape[-1]


@dataclass
class DopplerResult:
    """Output of the Doppler FFT stage."""
    complex_cube: np.ndarray        # [frame, doppler, rx, range_bin] complex64
    power_db: np.ndarray            # same shape, float32
    rx_combined_power: np.ndarray   # [frame, doppler, range_bin] float32
    config_dict: dict[str, Any] = field(default_factory=dict)

    @property
    def shape(self) -> tuple[int, ...]:
        return self.complex_cube.shape


@dataclass
class CfarDetection:
    """A single CFAR detection."""
    frame: int
    range_bin: int
    range_m: float
    doppler_bin: int
    velocity_mps: float
    signal_power_db: float
    noise_estimate_db: float
    snr_db: float
    threshold_db: float
    rx_combination: str = "noncoherent_power"
    config_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "frame": self.frame,
            "range_bin": self.range_bin,
            "range_m": round(self.range_m, 4),
            "doppler_bin": self.doppler_bin,
            "velocity_mps": round(self.velocity_mps, 4),
            "signal_power_db": round(self.signal_power_db, 2),
            "noise_estimate_db": round(self.noise_estimate_db, 2),
            "snr_db": round(self.snr_db, 2),
            "threshold_db": round(self.threshold_db, 2),
            "rx_combination": self.rx_combination,
            "config_id": self.config_id,
        }


@dataclass
class DetectionTable:
    """Collection of CFAR detections with metadata."""
    detections: list[CfarDetection] = field(default_factory=list)
    config_dict: dict[str, Any] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.detections)

    def to_list(self) -> list[dict[str, Any]]:
        return [d.to_dict() for d in self.detections]


@dataclass
class PipelineResult:
    """Complete pipeline output — all intermediate and final arrays."""
    adc_cube: np.ndarray              # original int16 cube (never modified)
    adc_float: np.ndarray             # float32 copy
    dc_removed: np.ndarray            # after DC removal
    range_result: RangeResult | None = None
    doppler_result: DopplerResult | None = None
    detections: DetectionTable | None = None
    config_dict: dict[str, Any] = field(default_factory=dict)
    timings: dict[str, float] = field(default_factory=dict)
