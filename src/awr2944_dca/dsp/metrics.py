"""Signal quality metrics for radar processing.

SNR estimation, noise floor, peak prominence, and comparison metrics
for evaluating processing configurations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class NoiseFloorEstimate:
    """Noise floor estimate from a range or range-Doppler profile."""
    noise_floor_db: float
    estimation_method: str
    num_samples: int


def estimate_noise_floor(
    spectrum_db: np.ndarray,
    *,
    method: str = "median",
    percentile: float = 25.0,
) -> NoiseFloorEstimate:
    """Estimate the noise floor of a power spectrum.

    Parameters
    ----------
    spectrum_db : ndarray
        Power spectrum in dB.
    method : str
        "median" — median of all bins
        "percentile" — specified percentile
        "tail" — mean of the upper half of range bins (far range, less clutter)
    percentile : float
        Percentile for the "percentile" method.

    Returns
    -------
    NoiseFloorEstimate
    """
    flat = spectrum_db.ravel()
    finite = flat[np.isfinite(flat)]

    if len(finite) == 0:
        return NoiseFloorEstimate(
            noise_floor_db=float("nan"),
            estimation_method=method,
            num_samples=0,
        )

    if method == "median":
        nf = float(np.median(finite))
    elif method == "percentile":
        nf = float(np.percentile(finite, percentile))
    elif method == "tail":
        half = len(finite) // 2
        nf = float(np.mean(finite[half:]))
    else:
        raise ValueError(f"Unknown noise floor method: {method}")

    return NoiseFloorEstimate(
        noise_floor_db=nf,
        estimation_method=method,
        num_samples=len(finite),
    )


def estimate_snr(
    signal_db: float,
    noise_floor: NoiseFloorEstimate,
) -> float:
    """Estimate SNR in dB."""
    return signal_db - noise_floor.noise_floor_db


def processing_comparison(
    original_db: np.ndarray,
    processed_db: np.ndarray,
    *,
    label: str = "",
) -> dict[str, Any]:
    """Compare two power spectra to assess processing effects.

    Parameters
    ----------
    original_db, processed_db : ndarray
        Same shape, power in dB.
    label : str
        Description of the processing step.

    Returns
    -------
    dict with comparison metrics.
    """
    diff = processed_db - original_db

    nf_orig = estimate_noise_floor(original_db)
    nf_proc = estimate_noise_floor(processed_db)

    peak_orig = float(np.max(original_db))
    peak_proc = float(np.max(processed_db))

    return {
        "label": label,
        "noise_floor_original_db": nf_orig.noise_floor_db,
        "noise_floor_processed_db": nf_proc.noise_floor_db,
        "noise_reduction_db": nf_orig.noise_floor_db - nf_proc.noise_floor_db,
        "peak_original_db": peak_orig,
        "peak_processed_db": peak_proc,
        "peak_change_db": peak_proc - peak_orig,
        "snr_original_db": peak_orig - nf_orig.noise_floor_db,
        "snr_processed_db": peak_proc - nf_proc.noise_floor_db,
        "snr_improvement_db": (
            (peak_proc - nf_proc.noise_floor_db)
            - (peak_orig - nf_orig.noise_floor_db)
        ),
        "mean_change_db": float(np.mean(diff)),
        "max_change_db": float(np.max(diff)),
        "min_change_db": float(np.min(diff)),
    }
