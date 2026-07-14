"""Full configurable DSP pipeline.

load → preprocess → range FFT → clutter → Doppler FFT → CFAR

Every result is tagged with the complete configuration that produced it.
The source adc_cube is never modified in place.
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

import numpy as np

from awr2944_dca.awr2944_adc import parse_awr2944_real
from awr2944_dca.dsp.axes import range_axis, velocity_axis
from awr2944_dca.dsp.cfar import cfar_1d, cfar_2d
from awr2944_dca.dsp.config import (
    PipelineConfig,
    RadarProfile,
    RxCombination,
)
from awr2944_dca.dsp.doppler_fft import compute_doppler_fft
from awr2944_dca.dsp.range_fft import compute_range_fft
from awr2944_dca.dsp.types import (
    DetectionTable,
    PipelineResult,
)


def load_canonical_cube(
    path: str | Path,
    profile: RadarProfile,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Load the canonical capture through the production parser.

    Returns
    -------
    adc_cube : ndarray, int16, shape [frame, chirp, rx, sample]
    metadata : dict
    """
    path = Path(path)

    # SHA256 of the raw file
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)

    adc_cube = parse_awr2944_real(
        path,
        frames=profile.frame_count,
        chirps=profile.chirps_per_frame,
        rx=profile.rx_count,
        samples=profile.adc_samples,
    )

    metadata = {
        "source_path": str(path.resolve()),
        "raw_sha256": sha.hexdigest(),
        "parser_layout_version": "awr2944_real_2lane_dca4slot_v1",
        "shape": list(adc_cube.shape),
        "dtype": str(adc_cube.dtype),
        "load_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "profile": profile.to_dict(),
    }

    return adc_cube, metadata


def run_pipeline(
    adc_cube: np.ndarray,
    config: PipelineConfig | None = None,
    *,
    run_cfar: bool = True,
) -> PipelineResult:
    """Run the full DSP pipeline.

    Parameters
    ----------
    adc_cube : ndarray, int16
        Shape [frame, chirp, rx, sample]. NEVER modified.
    config : PipelineConfig, optional
    run_cfar : bool
        Whether to run CFAR detection.

    Returns
    -------
    PipelineResult
    """
    if config is None:
        config = PipelineConfig()

    timings: dict[str, float] = {}
    profile = config.profile

    # Convert to float32 (preserve original)
    t0 = time.perf_counter()
    adc_float = adc_cube.astype(np.float32, copy=True)
    timings["float_conversion_s"] = time.perf_counter() - t0

    # Range FFT
    t0 = time.perf_counter()
    range_result = compute_range_fft(
        adc_cube, profile, config.range_cfg, kaiser_beta=config.kaiser_beta
    )
    timings["range_fft_s"] = time.perf_counter() - t0

    # Doppler FFT
    t0 = time.perf_counter()
    doppler_result = compute_doppler_fft(
        range_result.complex_cube, profile, config.doppler_cfg,
        kaiser_beta=config.kaiser_beta,
    )
    timings["doppler_fft_s"] = time.perf_counter() - t0

    # CFAR
    detection_table = None
    if run_cfar:
        t0 = time.perf_counter()
        r_axis = range_axis(profile, config.range_cfg.nfft)
        v_axis = velocity_axis(profile, config.doppler_cfg.nfft)

        all_detections = []
        for frame_idx in range(adc_cube.shape[0]):
            rd_map = doppler_result.rx_combined_power[frame_idx]  # [doppler, range]
            dets = cfar_2d(
                rd_map,
                config.cfar_cfg,
                range_axis_m=r_axis,
                velocity_axis_mps=v_axis,
                frame=frame_idx,
            )
            all_detections.extend(dets)

        detection_table = DetectionTable(
            detections=all_detections,
            config_dict=config.cfar_cfg.to_dict(),
        )
        timings["cfar_s"] = time.perf_counter() - t0

    timings["total_s"] = sum(timings.values())

    return PipelineResult(
        adc_cube=adc_cube,
        adc_float=adc_float,
        dc_removed=range_result.complex_cube,  # post-DC-removal is embedded in range
        range_result=range_result,
        doppler_result=doppler_result,
        detections=detection_table,
        config_dict=config.to_dict(),
        timings=timings,
    )
