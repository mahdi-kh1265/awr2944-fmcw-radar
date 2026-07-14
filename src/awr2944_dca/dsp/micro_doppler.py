"""Micro-Doppler infrastructure for future longer captures.

The current canonical capture spans approximately 0.32 seconds
(8 frames × 40 ms) and is too short for meaningful walking/gait
micro-Doppler analysis.

This module provides the infrastructure for:
    - range-gated slow-time signal extraction
    - STFT spectrogram
    - cadence/velocity visualization
    - dominant-frequency tracking

These functions will produce valid shapes and code paths on the
current dataset but should NOT be over-interpreted.

A multi-second capture (5–10 s minimum) is required for meaningful
micro-Doppler analysis.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import stft as scipy_stft

from awr2944_dca.dsp.config import RadarProfile


@dataclass
class MicroDopplerResult:
    """Output of micro-Doppler spectrogram computation."""
    spectrogram: np.ndarray        # [time_bins, frequency_bins] float32
    time_axis_s: np.ndarray        # [time_bins]
    frequency_axis_hz: np.ndarray  # [frequency_bins]
    velocity_axis_mps: np.ndarray  # [frequency_bins]
    range_bin: int
    range_m: float
    warning: str = ""


def extract_range_gated_signal(
    range_cube: np.ndarray,
    range_bin: int,
    rx: int = 0,
) -> np.ndarray:
    """Extract the slow-time complex signal at a specific range bin.

    Parameters
    ----------
    range_cube : ndarray, complex64
        Shape [frame, chirp, rx, range_bin].
    range_bin : int
    rx : int

    Returns
    -------
    ndarray, complex64
        Shape (total_chirps,) — all chirps concatenated across frames.

    WARNING: This concatenates across frame boundaries.
    For multi-frame captures with inter-frame gaps, the time axis
    will have discontinuities.
    """
    # [frame, chirp] -> flatten
    signal = range_cube[:, :, rx, range_bin]
    return signal.ravel()


def compute_micro_doppler(
    range_cube: np.ndarray,
    profile: RadarProfile,
    range_bin: int,
    rx: int = 0,
    *,
    nperseg: int = 64,
    noverlap: int | None = None,
) -> MicroDopplerResult:
    """Compute micro-Doppler spectrogram at a selected range gate.

    Parameters
    ----------
    range_cube : ndarray, complex64
        Shape [frame, chirp, rx, range_bin].
    profile : RadarProfile
    range_bin : int
    rx : int
    nperseg : int
        STFT window length in chirps.
    noverlap : int, optional
        STFT overlap in chirps. Default: nperseg // 2.

    Returns
    -------
    MicroDopplerResult
    """
    if noverlap is None:
        noverlap = nperseg // 2

    signal = extract_range_gated_signal(range_cube, range_bin, rx)

    # Sampling rate of the slow-time signal = 1/Tc
    fs_slow = 1.0 / profile.chirp_repetition_interval_s

    f, t, Zxx = scipy_stft(
        signal, fs=fs_slow, nperseg=nperseg, noverlap=noverlap,
        return_onesided=False,
    )

    # fftshift for centered display
    f = np.fft.fftshift(f)
    Zxx = np.fft.fftshift(Zxx, axes=0)

    power = np.abs(Zxx) ** 2
    eps = np.finfo(np.float32).tiny
    power_db = (10.0 * np.log10(np.maximum(power, eps))).astype(np.float32)

    # Convert frequency to velocity
    lam = profile.wavelength_m
    v_axis = lam * f / 2.0

    # Range of this bin
    from awr2944_dca.dsp.axes import range_axis
    r_axis = range_axis(profile)
    range_m = float(r_axis[range_bin]) if range_bin < len(r_axis) else 0.0

    total_duration = signal.size * profile.chirp_repetition_interval_s
    warning = ""
    if total_duration < 1.0:
        warning = (
            f"Total slow-time duration is only {total_duration*1000:.1f} ms. "
            f"Micro-Doppler analysis requires multi-second captures (5-10 s minimum)."
        )

    return MicroDopplerResult(
        spectrogram=power_db,
        time_axis_s=t,
        frequency_axis_hz=f,
        velocity_axis_mps=v_axis,
        range_bin=range_bin,
        range_m=range_m,
        warning=warning,
    )
