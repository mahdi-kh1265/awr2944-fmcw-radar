"""Pydantic models for mmWave Studio configuration.

These models describe the *intended* configuration for each stage of the
mmWave Studio pipeline.  They do not execute anything — they are pure data
that the bridge layer translates into Lua/ar1 calls.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Connection Tab
# ---------------------------------------------------------------------------


class ConnectionTabConfig(BaseModel):
    """Configuration for mmWave Studio Connection tab.

    Maps to ar1.SOPControl / ar1.Connect / board variant selection.
    """

    mmwave_studio_path: str = ""
    device_variant: str = "xWR2944"  # e.g. xWR2944, xWR1843
    frequency_band: str = "77GHz"  # 77GHz or 60GHz
    rs232_com: str = ""  # e.g. "COM6"
    baud: int = 921600
    timeout_ms: int = 1000
    bss_firmware_path: str = ""
    mss_firmware_path: str = ""

    @property
    def com_number(self) -> int:
        """Extract numeric COM port value: 'COM6' -> 6."""
        import re

        m = re.search(r"\d+", self.rs232_com)
        if not m:
            raise ValueError(f"Cannot parse numeric port from '{self.rs232_com}'")
        return int(m.group(0))


# ---------------------------------------------------------------------------
# Static Config (ADC / LVDS / Channel)
# ---------------------------------------------------------------------------


class StaticConfig(BaseModel):
    """Configuration for mmWave Studio Static Config tab.

    Maps to ar1.ChanNAdcConfig, ar1.LPModConfig, ar1.DataPathConfig,
    ar1.LvdsClkConfig, ar1.LVDSLaneConfig.
    """

    tx_enable: list[int] = Field(default_factory=lambda: [0])
    rx_enable: list[int] = Field(default_factory=lambda: [0, 1, 2, 3])
    adc_bits: int = 16
    adc_format: str = "real"  # "real" or "complex"
    iq_swap: int = 0
    channel_interleave: int = 0  # 0=non-interleaved
    low_power_mode: int = 0
    lvds_lanes: int = 2
    lvds_rate: int = 1  # 0=DDR, 1=SDR  (field names per TI docs)
    data_path_mode: int = 1  # intf_sel for DataPathConfig

    @property
    def tx_mask(self) -> int:
        """Bitmask of enabled TX channels."""
        mask = 0
        for tx in self.tx_enable:
            mask |= 1 << tx
        return mask

    @property
    def rx_mask(self) -> int:
        """Bitmask of enabled RX channels."""
        mask = 0
        for rx in self.rx_enable:
            mask |= 1 << rx
        return mask


# ---------------------------------------------------------------------------
# DCA1000 Config
# ---------------------------------------------------------------------------


class DCA1000Config(BaseModel):
    """DCA1000EVM Ethernet and capture settings.

    Maps to ar1.SelectCaptureDevice, ar1.CaptureCardConfig_EthInit,
    ar1.CaptureCardConfig_Mode, ar1.CaptureCardConfig_PacketDelay.
    """

    pc_ip: str = "192.168.33.30"
    fpga_ip: str = "192.168.33.180"
    mac: str = "12:34:56:78:90:12"
    config_port: int = 4096
    record_port: int = 4098
    packet_delay: int = 25


# ---------------------------------------------------------------------------
# Sensor Config (Profile / Chirp / Frame)
# ---------------------------------------------------------------------------


class ProfileFields(BaseModel):
    """Profile parameters for ar1.ProfileConfig."""

    start_freq_ghz: float = 77.0
    slope_mhz_per_us: float = 60.0
    idle_time_us: float = 10.0
    adc_start_time_us: float = 6.0
    ramp_end_time_us: float = 60.0
    num_adc_samples: int = 256
    sample_rate_ksps: float = 10000.0
    rx_gain_db: float = 30.0


class ChirpFields(BaseModel):
    """Chirp parameters for ar1.ChirpConfig."""

    chirp_start_idx: int = 0
    chirp_end_idx: int = 0
    profile_idx: int = 0
    tx_enable: int = 1  # bitmask


class FrameFields(BaseModel):
    """Frame parameters for ar1.FrameConfig."""

    chirp_start_idx: int = 0
    chirp_end_idx: int = 0
    num_loops: int = 128
    num_frames: int = 10
    frame_periodicity_ms: float = 50.0
    trigger_mode: int = 1  # 1=software trigger, 2=hardware trigger


class SensorConfig(BaseModel):
    """Full sensor configuration combining profile, chirp, and frame."""

    profile: ProfileFields = ProfileFields()
    chirp: ChirpFields = ChirpFields()
    frame: FrameFields = FrameFields()
