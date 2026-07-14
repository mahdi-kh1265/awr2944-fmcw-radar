"""Window functions for radar FFT processing.

Each window is returned with an optional coherent-gain normalization factor
so that the FFT peak magnitude of a pure tone equals the input amplitude.

Supported windows:
    rectangular, hann, hamming, blackman, blackman_harris, kaiser

Zero-padding with a window does NOT improve physical range resolution.
It is purely display interpolation.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import windows as _win

from awr2944_dca.dsp.config import WindowType


def get_window(
    window_type: WindowType,
    length: int,
    *,
    normalize: bool = True,
    kaiser_beta: float = 6.0,
) -> tuple[np.ndarray, float]:
    """Return a window vector and its coherent gain.

    Parameters
    ----------
    window_type : WindowType
        Window function selection.
    length : int
        Number of samples.
    normalize : bool
        If True, divide by coherent gain so peak magnitude is preserved.
    kaiser_beta : float
        Shape parameter for Kaiser window.

    Returns
    -------
    window : ndarray, float32, shape (length,)
    coherent_gain : float
        Mean of the unnormalized window. Used for documentation.
    """
    if window_type == WindowType.RECTANGULAR:
        w = np.ones(length, dtype=np.float64)
    elif window_type == WindowType.HANN:
        w = _win.hann(length, sym=False).astype(np.float64)
    elif window_type == WindowType.HAMMING:
        w = _win.hamming(length, sym=False).astype(np.float64)
    elif window_type == WindowType.BLACKMAN:
        w = _win.blackman(length, sym=False).astype(np.float64)
    elif window_type == WindowType.BLACKMAN_HARRIS:
        w = _win.blackmanharris(length, sym=False).astype(np.float64)
    elif window_type == WindowType.KAISER:
        w = _win.kaiser(length, beta=kaiser_beta, sym=False).astype(np.float64)
    else:
        raise ValueError(f"Unknown window type: {window_type}")

    coherent_gain = float(np.mean(w))

    if normalize and coherent_gain > 0:
        w = w / coherent_gain

    return w.astype(np.float32), coherent_gain
