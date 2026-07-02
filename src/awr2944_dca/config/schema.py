"""Pydantic v2 models for AWR2944 + DCA1000 experiment configuration.

The YAML config mirrors the structure defined in docs/CONFIG_SCHEMA.md.
All fields map directly to TI mmWave Studio / DCA1000 chirp/frame parameters.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Annotated

import yaml
from pydantic import BaseModel, Field, model_validator


class AntennaMode(str, Enum):
    """TX antenna operating mode."""

    SINGLE_TX = "single_tx"
    TDM_MIMO = "tdm_mimo"


class IQOrder(str, Enum):
    """IQ sample ordering in the binary stream."""

    IQ = "IQ"
    QI = "QI"


# ---------------------------------------------------------------------------
# Config section models
# ---------------------------------------------------------------------------


class ExperimentConfig(BaseModel):
    """Experiment metadata."""

    name: str
    operator: str = ""
    description: str = ""
    notes: str = ""


class RigConfig(BaseModel):
    """Hardware rig identification."""

    name: str = "awr2944-dca1000"
    radar: str = "AWR2944EVM"
    capture_card: str = "DCA1000EVM"


class HardwareConfig(BaseModel):
    """TX/RX channel configuration."""

    tx_enabled: list[int] = Field(default_factory=lambda: [0])
    rx_enabled: list[int] = Field(default_factory=lambda: [0, 1, 2, 3])
    antenna_mode: AntennaMode = AntennaMode.SINGLE_TX

    @property
    def num_tx(self) -> int:
        return len(self.tx_enabled)

    @property
    def num_rx(self) -> int:
        return len(self.rx_enabled)


class AdcConfig(BaseModel):
    """ADC sampling configuration.

    Note: AWR2944 default is real ADC (is_complex=False) with 2 LVDS lanes.
    Complex ADC is possible but must be explicitly configured and validated.
    """

    samples_per_chirp: Annotated[int, Field(gt=0)] = 256
    bits: int = 16
    is_complex: bool = False  # AWR2944 default: real ADC
    iq_order: IQOrder = IQOrder.IQ
    num_lvds_lanes: int = 2  # AWR2944 default: 2 LVDS lanes
    channel_interleave: int = 1  # 0: interleaved, 1: non-interleaved
    layout: str = "awr2944_real_2lane_noninterleaved_candidate"

    @property
    def bytes_per_sample_component(self) -> int:
        """Bytes for one real or one I/Q component (always 2 for 16-bit)."""
        return self.bits // 8

    @property
    def bytes_per_sample_per_rx(self) -> int:
        """Bytes per ADC sample per RX channel.

        Real mode: 2 bytes (one int16).
        Complex mode: 4 bytes (I int16 + Q int16).
        """
        multiplier = 2 if self.is_complex else 1
        return self.bytes_per_sample_component * multiplier


class ProfileConfig(BaseModel):
    """Chirp profile RF parameters.

    Maps to TI mmWave Studio profile configuration.
    """

    start_freq_ghz: float = 77.0
    slope_mhz_per_us: Annotated[float, Field(gt=0)] = 60.0
    sample_rate_ksps: Annotated[float, Field(gt=0)] = 10000.0
    idle_time_us: Annotated[float, Field(ge=0)] = 10.0
    ramp_end_time_us: Annotated[float, Field(gt=0)] = 60.0

    @property
    def bandwidth_mhz(self) -> float:
        """Chirp bandwidth B = slope × ramp_end_time.

        Ref: TI mmwaveSensing FMCW deck — B = S × Tc (chirp duration).
        """
        return self.slope_mhz_per_us * self.ramp_end_time_us

    @property
    def chirp_period_us(self) -> float:
        """Total chirp period = idle_time + ramp_end_time."""
        return self.idle_time_us + self.ramp_end_time_us


class FrameConfig(BaseModel):
    """Frame timing configuration."""

    chirps_per_frame: Annotated[int, Field(gt=0)] = 128
    num_frames: Annotated[int, Field(gt=0)] = 10
    frame_period_ms: Annotated[float, Field(gt=0)] = 50.0


class CaptureConfig(BaseModel):
    """Capture output and DCA1000 settings."""

    output_root: str = "experiments"
    packet_delay_us: int = 25
    save_raw_packets: bool = True
    raw_files: list[str] = Field(default_factory=list)
    adc_file: str = "raw/adc_data.bin"


class CalibrationTargetConfig(BaseModel):
    """Optional known calibration target metadata."""

    type: str = ""
    range_m: float = 0.0
    azimuth_deg: float = 0.0
    elevation_deg: float = 0.0


# ---------------------------------------------------------------------------
# Top-level config
# ---------------------------------------------------------------------------


class RadarConfig(BaseModel):
    """Top-level experiment configuration composing all sections.

    Load from YAML with RadarConfig.from_yaml(path).
    """

    experiment: ExperimentConfig
    rig: RigConfig = RigConfig()
    hardware: HardwareConfig = HardwareConfig()
    adc: AdcConfig = AdcConfig()
    profile: ProfileConfig = ProfileConfig()
    frame: FrameConfig = FrameConfig()
    capture: CaptureConfig = CaptureConfig()
    calibration_target: CalibrationTargetConfig | None = None

    @model_validator(mode="after")
    def _validate_channels(self) -> "RadarConfig":
        """Sanity-check channel indices."""
        for tx in self.hardware.tx_enabled:
            if tx < 0 or tx > 3:
                raise ValueError(f"TX channel {tx} out of range [0..3]")
        for rx in self.hardware.rx_enabled:
            if rx < 0 or rx > 3:
                raise ValueError(f"RX channel {rx} out of range [0..3]")
        return self

    @classmethod
    def from_yaml(cls, path: str | Path) -> "RadarConfig":
        """Load and validate a YAML config file."""
        path = Path(path)
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)
