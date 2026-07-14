"""Typed configuration objects for the AWR2944 DSP processing pipeline.

Every processed artifact retains the complete configuration that generated it.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Speed of light
# ---------------------------------------------------------------------------
C_MPS = 299_792_458.0


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class DCRemovalMode(str, Enum):
    """DC offset removal strategy applied before range FFT."""
    NONE = "none"
    PER_CHIRP = "per_chirp"          # subtract mean along sample axis per chirp
    PER_RX_GLOBAL = "per_rx_global"  # subtract mean across all frames/chirps per RX


class WindowType(str, Enum):
    RECTANGULAR = "rectangular"
    HANN = "hann"
    HAMMING = "hamming"
    BLACKMAN = "blackman"
    BLACKMAN_HARRIS = "blackman_harris"
    KAISER = "kaiser"


class ClutterRemovalMode(str, Enum):
    NONE = "none"
    SLOW_TIME_MEAN = "slow_time_mean"
    ZERO_DOPPLER_NOTCH = "zero_doppler_notch"


class CfarMode(str, Enum):
    CA = "ca"      # Cell-Averaging
    GO = "go"      # Greatest-Of
    SO = "so"      # Smallest-Of
    OS = "os"      # Ordered-Statistic


class BackgroundMode(str, Enum):
    NONE = "none"
    SAVED = "saved"
    ADAPTIVE = "adaptive"


class OutputScale(str, Enum):
    LINEAR = "linear"
    POWER = "power"
    DB = "db"
    DBFS = "dbfs"


class RxCombination(str, Enum):
    NONE = "none"
    NONCOHERENT_POWER = "noncoherent_power"


# ---------------------------------------------------------------------------
# Radar profile
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RadarProfile:
    """Physical radar profile parameters extracted from the chirp configuration.

    All quantities in SI base units (Hz, seconds, meters).
    """
    start_frequency_hz: float
    slope_hz_per_s: float
    adc_sample_rate_hz: float
    adc_samples: int
    idle_time_s: float
    ramp_end_time_s: float
    chirps_per_frame: int
    frame_count: int
    frame_period_s: float
    rx_count: int
    tx_mask: int
    sample_format: str       # "real_int16"
    cube_layout: str          # "frame_chirp_rx_sample"

    # Derived (computed, not stored in chirp config)
    @property
    def adc_duration_s(self) -> float:
        """Duration of ADC sampling window."""
        return self.adc_samples / self.adc_sample_rate_hz

    @property
    def sampled_bandwidth_hz(self) -> float:
        """Bandwidth swept during ADC sampling: S × T_adc."""
        return self.slope_hz_per_s * self.adc_duration_s

    @property
    def chirp_repetition_interval_s(self) -> float:
        """Nominal CRI = idle_time + ramp_end_time."""
        return self.idle_time_s + self.ramp_end_time_s

    @property
    def wavelength_m(self) -> float:
        return C_MPS / self.start_frequency_hz

    @property
    def range_resolution_m(self) -> float:
        """Physical range resolution: c / (2 × B_sampled)."""
        return C_MPS / (2.0 * self.sampled_bandwidth_hz)

    @property
    def max_unambiguous_range_m(self) -> float:
        """Nyquist max range for real ADC: fs × c / (2 × S)."""
        return (self.adc_sample_rate_hz * C_MPS) / (2.0 * self.slope_hz_per_s)

    @property
    def max_unambiguous_velocity_mps(self) -> float:
        """±v_max = λ / (4 × T_c)."""
        return self.wavelength_m / (4.0 * self.chirp_repetition_interval_s)

    @property
    def velocity_resolution_mps(self) -> float:
        """v_res = λ / (2 × N_chirps × T_c)."""
        return self.wavelength_m / (
            2.0 * self.chirps_per_frame * self.chirp_repetition_interval_s
        )

    @property
    def active_frame_duration_s(self) -> float:
        return self.chirps_per_frame * self.chirp_repetition_interval_s

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_smoke_v1(cls) -> "RadarProfile":
        """Factory for the validated smoke_v1 capture profile."""
        return cls(
            start_frequency_hz=77e9,
            slope_hz_per_s=29.982e12,
            adc_sample_rate_hz=10e6,
            adc_samples=256,
            idle_time_s=100e-6,
            ramp_end_time_s=60e-6,
            chirps_per_frame=128,
            frame_count=8,
            frame_period_s=40e-3,
            rx_count=4,
            tx_mask=3,            # TX0+TX1 simultaneous
            sample_format="real_int16",
            cube_layout="frame_chirp_rx_sample",
        )


# ---------------------------------------------------------------------------
# Processing configurations
# ---------------------------------------------------------------------------

@dataclass
class RangeProcessingConfig:
    dc_removal: DCRemovalMode = DCRemovalMode.PER_CHIRP
    window: WindowType = WindowType.HANN
    nfft: int = 256
    normalize_window: bool = True
    output_scale: OutputScale = OutputScale.DB

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["dc_removal"] = self.dc_removal.value
        d["window"] = self.window.value
        d["output_scale"] = self.output_scale.value
        return d


@dataclass
class DopplerProcessingConfig:
    clutter_removal: ClutterRemovalMode = ClutterRemovalMode.SLOW_TIME_MEAN
    window: WindowType = WindowType.HANN
    nfft: int = 128
    normalize_window: bool = True
    rx_combination: RxCombination = RxCombination.NONCOHERENT_POWER
    output_scale: OutputScale = OutputScale.DB
    zero_doppler_notch_bins: int = 0  # 0 = disabled

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["clutter_removal"] = self.clutter_removal.value
        d["window"] = self.window.value
        d["rx_combination"] = self.rx_combination.value
        d["output_scale"] = self.output_scale.value
        return d


@dataclass
class CfarConfig:
    mode: CfarMode = CfarMode.CA
    guard_cells_range: int = 2
    training_cells_range: int = 8
    guard_cells_doppler: int = 2
    training_cells_doppler: int = 4
    threshold_factor_db: float = 15.0
    minimum_snr_db: float = 6.0
    edge_guard: bool = True

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["mode"] = self.mode.value
        return d


@dataclass
class BackgroundConfig:
    mode: BackgroundMode = BackgroundMode.NONE
    alpha: float = 0.1
    saved_background_path: str = ""
    protection_mask: bool = True

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["mode"] = self.mode.value
        return d


@dataclass
class PipelineConfig:
    """Complete pipeline configuration — attached to every result."""
    profile: RadarProfile = field(default_factory=RadarProfile.from_smoke_v1)
    range_cfg: RangeProcessingConfig = field(default_factory=RangeProcessingConfig)
    doppler_cfg: DopplerProcessingConfig = field(default_factory=DopplerProcessingConfig)
    cfar_cfg: CfarConfig = field(default_factory=CfarConfig)
    background_cfg: BackgroundConfig = field(default_factory=BackgroundConfig)
    dynamic_range_db: float = 60.0
    kaiser_beta: float = 6.0  # only used when window == KAISER

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": self.profile.to_dict(),
            "range": self.range_cfg.to_dict(),
            "doppler": self.doppler_cfg.to_dict(),
            "cfar": self.cfar_cfg.to_dict(),
            "background": self.background_cfg.to_dict(),
            "dynamic_range_db": self.dynamic_range_db,
            "kaiser_beta": self.kaiser_beta,
        }
