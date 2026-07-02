"""Tests for Pydantic config schema and derived parameters."""

from __future__ import annotations

from pathlib import Path

import pytest

from awr2944_dca.config.derived import compute_derived
from awr2944_dca.config.schema import AntennaMode, RadarConfig


EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "configs"


class TestConfigLoading:
    """Test loading and validating YAML configs."""

    def test_load_first_capture(self, first_capture_config: RadarConfig) -> None:
        cfg = first_capture_config
        assert cfg.experiment.name == "first_capture"
        assert cfg.adc.is_complex is False
        assert cfg.adc.layout == "awr2944_real_interleaved_2lane_unvalidated"
        assert cfg.adc.num_lvds_lanes == 2
        assert cfg.hardware.antenna_mode == AntennaMode.SINGLE_TX

    def test_load_walking_person(self, walking_person_config: RadarConfig) -> None:
        cfg = walking_person_config
        assert cfg.experiment.name == "walking_person"
        assert cfg.hardware.antenna_mode == AntennaMode.TDM_MIMO
        assert cfg.hardware.num_tx == 4
        assert cfg.hardware.num_rx == 4

    def test_load_corner_reflector(self, corner_reflector_config: RadarConfig) -> None:
        cfg = corner_reflector_config
        assert cfg.calibration_target is not None
        assert cfg.calibration_target.type == "corner_reflector"
        assert cfg.calibration_target.range_m == 2.0

    def test_all_example_configs_load(self) -> None:
        """All example YAML configs should parse without error."""
        for yaml_file in EXAMPLES_DIR.glob("*.yaml"):
            cfg = RadarConfig.from_yaml(yaml_file)
            assert cfg.experiment.name  # Has a non-empty name


class TestConfigValidation:
    """Test that bad configs raise validation errors."""

    def test_negative_samples_rejected(self) -> None:
        with pytest.raises(Exception):
            RadarConfig.model_validate({
                "experiment": {"name": "bad"},
                "adc": {"samples_per_chirp": -1},
            })

    def test_invalid_tx_channel(self) -> None:
        with pytest.raises(Exception):
            RadarConfig.model_validate({
                "experiment": {"name": "bad"},
                "hardware": {"tx_enabled": [5]},
            })

    def test_invalid_rx_channel(self) -> None:
        with pytest.raises(Exception):
            RadarConfig.model_validate({
                "experiment": {"name": "bad"},
                "hardware": {"rx_enabled": [-1]},
            })

    def test_zero_frames_rejected(self) -> None:
        with pytest.raises(Exception):
            RadarConfig.model_validate({
                "experiment": {"name": "bad"},
                "frame": {"num_frames": 0},
            })


class TestAdcConfig:
    """Test ADC config properties."""

    def test_real_adc_bytes_per_sample(self) -> None:
        cfg = RadarConfig.model_validate({
            "experiment": {"name": "t"},
            "adc": {"is_complex": False, "bits": 16},
        })
        assert cfg.adc.bytes_per_sample_per_rx == 2

    def test_complex_adc_bytes_per_sample(self) -> None:
        cfg = RadarConfig.model_validate({
            "experiment": {"name": "t"},
            "adc": {"is_complex": True, "bits": 16},
        })
        assert cfg.adc.bytes_per_sample_per_rx == 4


class TestDerivedParams:
    """Test derived parameter computation."""

    def test_first_capture_derived(self, first_capture_config: RadarConfig) -> None:
        d = compute_derived(first_capture_config)

        # Bandwidth = 60 MHz/μs × 60 μs = 3600 MHz
        assert abs(d.bandwidth_mhz - 3600.0) < 0.01

        # Range resolution = c / (2 × 3.6 GHz) ≈ 0.0416 m
        assert 0.04 < d.range_resolution_m < 0.05

        # Expected file size: 256 samples × 4 RX × 128 chirps × 10 frames × 2 bytes
        # = 256 × 4 × 128 × 10 × 2 = 2,621,440 bytes
        assert d.expected_file_size_bytes == 2_621_440

    def test_walking_person_tdm_mimo(self, walking_person_config: RadarConfig) -> None:
        d = compute_derived(walking_person_config)

        # TDM-MIMO: 4 TX × 4 RX = 16 virtual antennas
        assert d.num_virtual_antennas == 16

        # File size: 256 × 4 × 128 × 200 × 2 = 52,428,800
        assert d.expected_file_size_bytes == 52_428_800

    def test_bandwidth_formula(self) -> None:
        """Verify B = slope × ramp_time (TI FMCW deck)."""
        cfg = RadarConfig.model_validate({
            "experiment": {"name": "t"},
            "profile": {"slope_mhz_per_us": 100.0, "ramp_end_time_us": 40.0},
        })
        d = compute_derived(cfg)
        assert abs(d.bandwidth_mhz - 4000.0) < 0.01
