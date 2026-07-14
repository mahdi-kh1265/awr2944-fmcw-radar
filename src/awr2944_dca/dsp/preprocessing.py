"""DC offset removal and preprocessing for ADC data.

Three modes are provided:

- NONE: no DC removal
- PER_CHIRP: subtract the per-chirp mean along the sample axis
- PER_RX_GLOBAL: subtract the global mean across all frames and chirps per RX

The input cube must be float32 [frame, chirp, rx, sample].
The original array is never mutated.
"""

from __future__ import annotations

import numpy as np

from awr2944_dca.dsp.config import DCRemovalMode


def remove_dc(
    cube: np.ndarray,
    mode: DCRemovalMode = DCRemovalMode.PER_CHIRP,
) -> np.ndarray:
    """Apply the selected DC removal strategy.

    Parameters
    ----------
    cube : ndarray, float32
        ADC data shaped [frame, chirp, rx, sample].
    mode : DCRemovalMode
        Strategy selection.

    Returns
    -------
    ndarray, float32
        DC-removed cube (same shape, new allocation).
    """
    if mode == DCRemovalMode.NONE:
        return cube.copy()
    elif mode == DCRemovalMode.PER_CHIRP:
        return _per_chirp(cube)
    elif mode == DCRemovalMode.PER_RX_GLOBAL:
        return _per_rx_global(cube)
    else:
        raise ValueError(f"Unknown DC removal mode: {mode}")


def _per_chirp(cube: np.ndarray) -> np.ndarray:
    """x_dc[f,c,r,n] = x[f,c,r,n] - mean_n(x[f,c,r,n])"""
    mean = cube.mean(axis=-1, keepdims=True)
    return cube - mean


def _per_rx_global(cube: np.ndarray) -> np.ndarray:
    """x_dc[f,c,r,n] = x[f,c,r,n] - mean_{f,c,n}(x[f,c,r,n])

    The mean is computed per RX across all frames, chirps, and samples.
    """
    # Mean over axes 0 (frame), 1 (chirp), 3 (sample), keep rx
    mean = cube.mean(axis=(0, 1, 3), keepdims=True)
    return cube - mean
