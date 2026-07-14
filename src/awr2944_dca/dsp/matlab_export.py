"""MATLAB .mat export for Python-to-MATLAB data interchange.

Exports the canonical dataset and metadata to a MATLAB v5 .mat file
using scipy.io.savemat.  For v7.3 (HDF5-based), h5py would be needed,
but v5 .mat files are readable by all MATLAB versions >= R2006b and
support the data sizes we need (< 2 GB).

DIMENSION ORDERING:
    NumPy (row-major, C order):   [frame, chirp, rx, sample]
    MATLAB (column-major, F order): last index varies fastest
    
    When MATLAB loads a NumPy-written .mat file, the dimensions appear
    reversed because of the row-major vs column-major difference.
    
    To avoid confusion, we export TWO copies:
    - adc_cube: in Python order [frame, chirp, rx, sample]
    - adc_cube_matlab: pre-transposed to [sample, rx, chirp, frame]
      so MATLAB sees it as (sample, rx, chirp, frame) — matching
      MATLAB's fastest-first convention.
    
    The MATLAB loader should use adc_cube_matlab.

Every conversion is tested (see tests/test_matlab_export.py).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import scipy.io as sio

from awr2944_dca.dsp.axes import range_axis, range_bin_spacing_m, velocity_axis, velocity_bin_spacing_mps
from awr2944_dca.dsp.config import RadarProfile


def export_to_mat(
    adc_cube: np.ndarray,
    profile: RadarProfile,
    output_path: str | Path,
    *,
    canonical_raw_sha256: str = "",
    source_raw_path: str = "",
    extra_fields: dict[str, Any] | None = None,
) -> Path:
    """Export canonical ADC cube and metadata to a MATLAB .mat file.

    Parameters
    ----------
    adc_cube : ndarray, int16
        Shape [frame, chirp, rx, sample].
    profile : RadarProfile
    output_path : str or Path
    canonical_raw_sha256 : str
    source_raw_path : str
    extra_fields : dict, optional
        Additional fields to include.

    Returns
    -------
    Path
        Path to the saved .mat file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Pre-transpose for MATLAB convenience
    adc_cube_matlab = np.ascontiguousarray(
        adc_cube.transpose(3, 2, 1, 0)  # [sample, rx, chirp, frame]
    )

    r_axis = range_axis(profile)
    v_axis = velocity_axis(profile)

    mat_dict: dict[str, Any] = {
        # Data
        "adc_cube": adc_cube,
        "adc_cube_matlab": adc_cube_matlab,

        # Dimensions
        "frame_count": np.int32(profile.frame_count),
        "chirps_per_frame": np.int32(profile.chirps_per_frame),
        "rx_count": np.int32(profile.rx_count),
        "adc_samples": np.int32(profile.adc_samples),

        # RF parameters
        "sample_rate_hz": np.float64(profile.adc_sample_rate_hz),
        "slope_hz_per_s": np.float64(profile.slope_hz_per_s),
        "start_frequency_hz": np.float64(profile.start_frequency_hz),
        "idle_time_s": np.float64(profile.idle_time_s),
        "ramp_end_time_s": np.float64(profile.ramp_end_time_s),
        "frame_period_s": np.float64(profile.frame_period_s),
        "tx_mask": np.int32(profile.tx_mask),

        # Format metadata
        "sample_format": profile.sample_format,
        "cube_layout": profile.cube_layout,
        "layout_version": "awr2944_real_2lane_dca4slot_v1",
        "canonical_raw_sha256": canonical_raw_sha256,
        "source_raw_path": source_raw_path,

        # Dimension ordering documentation
        "python_dimension_order": "frame,chirp,rx,sample",
        "matlab_dimension_order": "sample,rx,chirp,frame",

        # Axes
        "range_axis_m": r_axis,
        "velocity_axis_mps": v_axis,
        "range_bin_spacing_m": np.float64(range_bin_spacing_m(profile)),
        "max_range_m": np.float64(profile.max_unambiguous_range_m),
        "velocity_bin_spacing_mps": np.float64(velocity_bin_spacing_mps(profile)),
        "max_velocity_mps": np.float64(profile.max_unambiguous_velocity_mps),
    }

    if extra_fields:
        mat_dict.update(extra_fields)

    sio.savemat(str(output_path), mat_dict, do_compression=True)

    return output_path
