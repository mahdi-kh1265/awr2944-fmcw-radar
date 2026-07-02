"""Hardware and software specs loading and validation."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel


class HardwareLimits(BaseModel):
    max_tx_channels: int
    max_rx_channels: int
    min_frequency_ghz: float
    max_frequency_ghz: float
    supported_adc_bits: list[int]


class PowerSupply(BaseModel):
    voltage_v: float
    min_current_a: float
    note: str


class CaptureSupport(BaseModel):
    direct_dca1000_supported: bool
    supported_lvds_lanes: list[int]
    supported_layouts: list[str]


class RadarSpec(BaseModel):
    """Specification for a radar device (e.g. AWR2944)."""

    device_name: str
    description: str
    hardware_limits: HardwareLimits
    power_supply: PowerSupply
    capture_support: CaptureSupport


class NetworkSpec(BaseModel):
    default_pc_static_ip: str
    default_device_ip: str
    subnet_mask: str
    config_udp_port: int
    data_udp_port: int


class FileFormatSpec(BaseModel):
    description: str
    extension: str


class CaptureCardSpec(BaseModel):
    """Specification for a capture card (e.g. DCA1000)."""

    device_name: str
    description: str
    network: NetworkSpec
    file_formats: dict[str, FileFormatSpec]


_SPECS_DIR = Path(__file__).parent.parent / "specs"


def load_radar_spec(name: str) -> RadarSpec:
    """Load a radar specification by name (e.g., 'AWR2944EVM')."""
    # Normalize name to filename
    filename = name.lower().replace("evm", "") + ".yaml"
    path = _SPECS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"No spec found for radar: {name} at {path}")

    with open(path) as f:
        data = yaml.safe_load(f)
    return RadarSpec.model_validate(data)


def load_capture_card_spec(name: str) -> CaptureCardSpec:
    """Load a capture card specification by name (e.g., 'DCA1000EVM')."""
    filename = name.lower().replace("evm", "") + ".yaml"
    path = _SPECS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"No spec found for capture card: {name} at {path}")

    with open(path) as f:
        data = yaml.safe_load(f)
    return CaptureCardSpec.model_validate(data)
