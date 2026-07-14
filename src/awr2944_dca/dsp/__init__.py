"""DSP processing package for AWR2944 FMCW radar.

Public API re-exports from sub-modules.
"""

from awr2944_dca.dsp.config import (
    RadarProfile,
    RangeProcessingConfig,
    DopplerProcessingConfig,
    CfarConfig,
    BackgroundConfig,
    PipelineConfig,
    DCRemovalMode,
    WindowType,
    ClutterRemovalMode,
    CfarMode,
    BackgroundMode,
    OutputScale,
    RxCombination,
)
from awr2944_dca.dsp.types import (
    RangeResult,
    DopplerResult,
    CfarDetection,
    DetectionTable,
    PipelineResult,
)
from awr2944_dca.dsp.pipeline import load_canonical_cube, run_pipeline
from awr2944_dca.dsp.range_fft import compute_range_fft
from awr2944_dca.dsp.doppler_fft import compute_doppler_fft
from awr2944_dca.dsp.preprocessing import remove_dc
from awr2944_dca.dsp.axes import range_axis, velocity_axis, range_bin_spacing_m, velocity_bin_spacing_mps
from awr2944_dca.dsp.windows import get_window
from awr2944_dca.dsp.cfar import cfar_1d, cfar_2d
from awr2944_dca.dsp.metrics import estimate_noise_floor, estimate_snr, processing_comparison
from awr2944_dca.dsp.calibration import RangeCalibration
from awr2944_dca.dsp.matlab_export import export_to_mat

__all__ = [
    # Config
    "RadarProfile", "RangeProcessingConfig", "DopplerProcessingConfig",
    "CfarConfig", "BackgroundConfig", "PipelineConfig",
    "DCRemovalMode", "WindowType", "ClutterRemovalMode",
    "CfarMode", "BackgroundMode", "OutputScale", "RxCombination",
    # Types
    "RangeResult", "DopplerResult", "CfarDetection", "DetectionTable",
    "PipelineResult",
    # Pipeline
    "load_canonical_cube", "run_pipeline",
    # Processing
    "compute_range_fft", "compute_doppler_fft", "remove_dc",
    "range_axis", "velocity_axis", "range_bin_spacing_m", "velocity_bin_spacing_mps",
    "get_window", "cfar_1d", "cfar_2d",
    # Metrics
    "estimate_noise_floor", "estimate_snr", "processing_comparison",
    # Calibration
    "RangeCalibration",
    # Export
    "export_to_mat",
]
