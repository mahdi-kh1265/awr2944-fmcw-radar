"""Doppler FFT and range-Doppler processing.

Operates on the complex range FFT cube [frame, chirp, rx, range_bin].
Each frame is processed independently — chirps are never concatenated
across frame boundaries.

Pipeline per frame:
    1. Optional clutter removal (slow-time mean subtraction along chirp axis)
    2. Apply Doppler window along chirp axis
    3. FFT along chirp axis
    4. fftshift to center zero-Doppler
    5. Noncoherent RX power combination (optional)

Output shape: [frame, doppler, rx, range_bin]
"""

from __future__ import annotations

import numpy as np

from awr2944_dca.dsp.config import (
    ClutterRemovalMode,
    DopplerProcessingConfig,
    RadarProfile,
    RxCombination,
)
from awr2944_dca.dsp.clutter import remove_clutter
from awr2944_dca.dsp.types import DopplerResult
from awr2944_dca.dsp.windows import get_window


def compute_doppler_fft(
    range_cube: np.ndarray,
    profile: RadarProfile,
    config: DopplerProcessingConfig | None = None,
    *,
    kaiser_beta: float = 6.0,
) -> DopplerResult:
    """Compute the Doppler FFT on a complex range cube.

    Parameters
    ----------
    range_cube : ndarray, complex64
        Shape [frame, chirp, rx, range_bin] — output of range FFT.
    profile : RadarProfile
    config : DopplerProcessingConfig, optional
    kaiser_beta : float
        Beta for Kaiser window.

    Returns
    -------
    DopplerResult
        Contains complex cube [frame, doppler, rx, range_bin],
        power_db, and rx_combined_power arrays.
    """
    if config is None:
        config = DopplerProcessingConfig()

    cube = range_cube.copy()
    num_chirps = cube.shape[1]

    # 1. Clutter removal
    cube = remove_clutter(cube, config.clutter_removal, config.zero_doppler_notch_bins)

    # 2. Doppler window along chirp axis
    win, cg = get_window(
        config.window,
        num_chirps,
        normalize=config.normalize_window,
        kaiser_beta=kaiser_beta,
    )
    # Reshape for broadcasting: [1, chirps, 1, 1]
    win_4d = win.reshape(1, -1, 1, 1)
    cube = cube * win_4d

    # 3. FFT along chirp axis (axis=1)
    complex_cube = np.fft.fft(cube, n=config.nfft, axis=1).astype(np.complex64)

    # 4. fftshift along Doppler axis
    complex_cube = np.fft.fftshift(complex_cube, axes=1)

    # 5. Power in dB
    magnitude = np.abs(complex_cube)
    eps = np.finfo(np.float32).tiny
    power_db = (20.0 * np.log10(np.maximum(magnitude, eps))).astype(np.float32)

    # 6. RX combination
    if config.rx_combination == RxCombination.NONCOHERENT_POWER:
        # Sum power across RX channels: |X|^2 summed over rx axis
        rx_power = np.sum(magnitude ** 2, axis=2)  # [frame, doppler, range_bin]
        rx_combined_db = (10.0 * np.log10(np.maximum(rx_power, eps))).astype(np.float32)
    else:
        # No combination — pick RX0 as placeholder
        rx_combined_db = power_db[:, :, 0, :]

    return DopplerResult(
        complex_cube=complex_cube,
        power_db=power_db,
        rx_combined_power=rx_combined_db,
        config_dict={
            "profile": profile.to_dict(),
            "doppler_config": config.to_dict(),
            "kaiser_beta": kaiser_beta,
            "coherent_gain": cg,
            "num_input_chirps": num_chirps,
            "nfft": config.nfft,
        },
    )
