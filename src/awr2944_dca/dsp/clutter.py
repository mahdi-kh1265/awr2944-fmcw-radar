"""Clutter removal operations for range-Doppler processing.

Distinct from DC removal (preprocessing.py), which operates in the
fast-time domain before range FFT.  Clutter removal operates in the
slow-time domain on the complex range FFT output.

Operations:
    A. Slow-time mean subtraction — at every (rx, range_bin), subtract
       the mean across chirps.
    B. Zero-Doppler notch — after Doppler FFT, suppress configurable
       bins near 0 m/s (applied before fftshift in this module's helper,
       or post-fftshift on the centered spectrum).
"""

from __future__ import annotations

import numpy as np

from awr2944_dca.dsp.config import ClutterRemovalMode


def remove_clutter(
    range_cube: np.ndarray,
    mode: ClutterRemovalMode = ClutterRemovalMode.SLOW_TIME_MEAN,
    zero_doppler_notch_bins: int = 0,
) -> np.ndarray:
    """Apply the selected clutter removal strategy.

    Parameters
    ----------
    range_cube : ndarray, complex64
        Shape [frame, chirp, rx, range_bin].
    mode : ClutterRemovalMode
    zero_doppler_notch_bins : int
        Number of bins to notch near zero-Doppler (only for ZERO_DOPPLER_NOTCH).

    Returns
    -------
    ndarray, complex64
        Clutter-removed cube (new allocation).
    """
    if mode == ClutterRemovalMode.NONE:
        return range_cube.copy()
    elif mode == ClutterRemovalMode.SLOW_TIME_MEAN:
        return _slow_time_mean(range_cube)
    elif mode == ClutterRemovalMode.ZERO_DOPPLER_NOTCH:
        return _zero_doppler_notch(range_cube, zero_doppler_notch_bins)
    else:
        raise ValueError(f"Unknown clutter removal mode: {mode}")


def _slow_time_mean(cube: np.ndarray) -> np.ndarray:
    """X_clean[f,c,r,k] = X[f,c,r,k] - mean_c(X[f,c,r,k])

    Subtracts the mean across chirps (axis=1) at every (frame, rx, range_bin).
    This removes the zero-Doppler (stationary) component.
    """
    mean = cube.mean(axis=1, keepdims=True)
    return cube - mean


def _zero_doppler_notch(cube: np.ndarray, notch_bins: int) -> np.ndarray:
    """Suppress zero-Doppler bins by performing a temporary FFT along chirps,
    zeroing the central bins, and inverse-FFTing back.

    This is more selective than full mean subtraction but requires the FFT/IFFT
    round-trip.
    """
    if notch_bins <= 0:
        return cube.copy()

    # FFT along chirp axis
    spectrum = np.fft.fft(cube, axis=1)
    spectrum = np.fft.fftshift(spectrum, axes=1)

    num_chirps = cube.shape[1]
    center = num_chirps // 2
    half = notch_bins // 2

    lo = max(center - half, 0)
    hi = min(center + half + 1, num_chirps)
    spectrum[:, lo:hi, :, :] = 0

    # Inverse FFT back
    spectrum = np.fft.ifftshift(spectrum, axes=1)
    return np.fft.ifft(spectrum, axis=1).astype(np.complex64)
