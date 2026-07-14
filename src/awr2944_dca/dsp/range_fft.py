"""Range FFT for real-valued ADC data.

Uses np.fft.rfft to exploit Hermitian symmetry of real inputs:
    output bins = NFFT // 2 + 1

Pipeline per chirp:
    1. DC removal (dispatched externally)
    2. Apply window (with coherent-gain normalization)
    3. np.fft.rfft along sample axis
    4. Return complex range spectrum

For NFFT = 256, output has 129 bins.
"""

from __future__ import annotations

import numpy as np

from awr2944_dca.dsp.config import (
    RadarProfile,
    RangeProcessingConfig,
    WindowType,
)
from awr2944_dca.dsp.preprocessing import remove_dc
from awr2944_dca.dsp.types import RangeResult
from awr2944_dca.dsp.windows import get_window


def compute_range_fft(
    adc_cube: np.ndarray,
    profile: RadarProfile,
    config: RangeProcessingConfig | None = None,
    *,
    kaiser_beta: float = 6.0,
) -> RangeResult:
    """Compute the range FFT on a real ADC cube.

    Parameters
    ----------
    adc_cube : ndarray, int16 or float32
        Shape [frame, chirp, rx, sample].
    profile : RadarProfile
    config : RangeProcessingConfig, optional
    kaiser_beta : float
        Beta for Kaiser window.

    Returns
    -------
    RangeResult
        Contains complex cube [frame, chirp, rx, nfft//2+1],
        magnitude, and power_db arrays.
    """
    if config is None:
        config = RangeProcessingConfig()

    # Convert to float32 (never mutate the original)
    cube = adc_cube.astype(np.float32, copy=True)

    # 1. DC removal
    cube = remove_dc(cube, config.dc_removal)

    # 2. Apply window
    num_samples = cube.shape[-1]
    win, cg = get_window(
        config.window,
        num_samples,
        normalize=config.normalize_window,
        kaiser_beta=kaiser_beta,
    )
    cube = cube * win  # broadcast across [frame, chirp, rx]

    # 3. rfft along sample axis (last axis)
    complex_cube = np.fft.rfft(cube, n=config.nfft, axis=-1).astype(np.complex64)

    # 4. Magnitude and power
    magnitude = np.abs(complex_cube)
    eps = np.finfo(np.float32).tiny
    power_db = 20.0 * np.log10(np.maximum(magnitude, eps))

    return RangeResult(
        complex_cube=complex_cube,
        magnitude=magnitude,
        power_db=power_db.astype(np.float32),
        config_dict={
            "profile": profile.to_dict(),
            "range_config": config.to_dict(),
            "kaiser_beta": kaiser_beta,
            "coherent_gain": cg,
            "num_input_samples": num_samples,
            "nfft": config.nfft,
            "num_output_bins": complex_cube.shape[-1],
        },
    )
