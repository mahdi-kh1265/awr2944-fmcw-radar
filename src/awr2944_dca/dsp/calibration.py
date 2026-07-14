"""Range calibration infrastructure.

Provides a framework for calibrating the range axis using a known
corner-reflector target at a surveyed distance.

This dataset was NOT captured with a calibration target. The range
axis should be treated as nominal until a dedicated calibration
capture is performed.

Infrastructure for later use:
    - known target distance
    - measured FFT peak range
    - fixed range bias
    - optional range scale correction
    - calibration metadata and timestamp
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np


@dataclass
class RangeCalibration:
    """Range calibration parameters."""
    known_target_range_m: float = 0.0
    measured_peak_range_m: float = 0.0
    range_bias_m: float = 0.0       # measured - known
    range_scale_factor: float = 1.0  # multiplicative correction
    calibration_timestamp: str = ""
    calibration_capture_sha256: str = ""
    is_calibrated: bool = False

    @classmethod
    def from_measurement(
        cls,
        known_m: float,
        measured_m: float,
        capture_sha256: str = "",
    ) -> "RangeCalibration":
        """Create calibration from a known-target measurement."""
        bias = measured_m - known_m
        scale = known_m / measured_m if measured_m > 0 else 1.0
        return cls(
            known_target_range_m=known_m,
            measured_peak_range_m=measured_m,
            range_bias_m=bias,
            range_scale_factor=scale,
            calibration_timestamp=datetime.utcnow().isoformat() + "Z",
            calibration_capture_sha256=capture_sha256,
            is_calibrated=True,
        )

    def apply(self, range_axis_m: np.ndarray) -> np.ndarray:
        """Apply bias and scale correction to a range axis."""
        if not self.is_calibrated:
            return range_axis_m.copy()
        return (range_axis_m - self.range_bias_m) * self.range_scale_factor

    def to_dict(self) -> dict[str, Any]:
        return {
            "known_target_range_m": self.known_target_range_m,
            "measured_peak_range_m": self.measured_peak_range_m,
            "range_bias_m": self.range_bias_m,
            "range_scale_factor": self.range_scale_factor,
            "calibration_timestamp": self.calibration_timestamp,
            "calibration_capture_sha256": self.calibration_capture_sha256,
            "is_calibrated": self.is_calibrated,
        }
