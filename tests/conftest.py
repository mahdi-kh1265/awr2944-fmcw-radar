"""Shared pytest fixtures for AWR2944 DCA Lab tests."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from awr2944_dca.config.schema import RadarConfig


EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "configs"


@pytest.fixture
def first_capture_config() -> RadarConfig:
    """Load the first_capture.yaml example config."""
    return RadarConfig.from_yaml(EXAMPLES_DIR / "first_capture.yaml")


@pytest.fixture
def walking_person_config() -> RadarConfig:
    """Load the walking_person.yaml example config."""
    return RadarConfig.from_yaml(EXAMPLES_DIR / "walking_person.yaml")


@pytest.fixture
def corner_reflector_config() -> RadarConfig:
    """Load the corner_reflector.yaml example config."""
    return RadarConfig.from_yaml(EXAMPLES_DIR / "corner_reflector.yaml")


@pytest.fixture
def small_real_config() -> RadarConfig:
    """Create a small real-ADC config for fast testing."""
    return RadarConfig.model_validate({
        "experiment": {"name": "test_small_real", "operator": "test"},
        "hardware": {
            "tx_enabled": [0],
            "rx_enabled": [0, 1, 2, 3],
            "antenna_mode": "single_tx",
        },
        "adc": {
            "samples_per_chirp": 64,
            "bits": 16,
            "is_complex": False,
            "num_lvds_lanes": 2,
            "layout": "awr2944_real_2lane_interleaved_candidate",
        },
        "frame": {
            "chirps_per_frame": 16,
            "num_frames": 4,
        },
    })


@pytest.fixture
def small_complex_config() -> RadarConfig:
    """Create a small complex-ADC config for fast testing."""
    return RadarConfig.model_validate({
        "experiment": {"name": "test_small_complex", "operator": "test"},
        "hardware": {
            "tx_enabled": [0],
            "rx_enabled": [0, 1, 2, 3],
            "antenna_mode": "single_tx",
        },
        "adc": {
            "samples_per_chirp": 64,
            "bits": 16,
            "is_complex": True,
            "num_lvds_lanes": 4,
            "layout": "xwr14xx_complex_4lane",
        },
        "frame": {
            "chirps_per_frame": 16,
            "num_frames": 4,
        },
    })


# WORKAROUND: Pytest on Windows frequently fails with PermissionError
import _pytest.pathlib
_pytest.pathlib.cleanup_dead_symlinks = lambda root: None
