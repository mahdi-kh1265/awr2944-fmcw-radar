"""Tests for binary layout abstraction."""

from __future__ import annotations

import warnings

import numpy as np
import pytest

from awr2944_dca.config.schema import RadarConfig
from awr2944_dca.formats.layouts import (
    Awr2944Real2LaneInterleavedCandidate,
    Awr2944Real2LaneNoninterleavedCandidate,
    BinaryLayout,
    Xwr14xxComplex4Lane,
    Xwr16xxComplex2Lane,
    get_layout,
)


class TestLayoutRegistry:
    """Test layout registration and lookup."""

    def test_list_layouts(self) -> None:
        from awr2944_dca.formats.layouts import list_layouts
        names = list_layouts()
        assert "awr2944_real_2lane_interleaved_candidate" in names
        assert "awr2944_real_2lane_noninterleaved_candidate" in names
        assert "xwr14xx_complex_4lane" in names
        assert "xwr16xx_complex_2lane" in names

    def test_get_layout(self) -> None:
        layout = get_layout("awr2944_real_2lane_interleaved_candidate")
        assert layout.name == "awr2944_real_2lane_interleaved_candidate"
        assert layout.lab_validated is False

    def test_unknown_layout_raises(self) -> None:
        with pytest.raises(KeyError, match="Unknown layout"):
            get_layout("nonexistent_layout")


class TestLayoutFlags:
    """Test layout status flags."""

    def test_awr2944_not_validated(self) -> None:
        layout = Awr2944Real2LaneInterleavedCandidate()
        assert layout.lab_validated is False
        assert layout.swra581b_reference is False
        assert layout.requires_real_capture_validation is True

    def test_xwr14xx_is_swra581b_reference(self) -> None:
        layout = Xwr14xxComplex4Lane()
        assert layout.swra581b_reference is True
        assert layout.lab_validated is False  # Not validated on our hardware

    def test_unvalidated_layout_warns(self) -> None:
        layout = Awr2944Real2LaneInterleavedCandidate()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            layout.warn_if_unvalidated()
            assert len(w) == 1
            assert "NOT been validated" in str(w[0].message)


class TestAwr2944RealLayout:
    """Test AWR2944 real-ADC 2-lane layout reshape and packing."""

    def test_expected_file_size_real(self, small_real_config: RadarConfig) -> None:
        layout = Awr2944Real2LaneInterleavedCandidate()
        # 64 samples × 4 RX × 16 chirps × 4 frames × 2 bytes = 32,768
        expected = 64 * 4 * 16 * 4 * 2
        assert layout.expected_file_size(small_real_config) == expected

    def test_reshape_produces_correct_shape(self, small_real_config: RadarConfig) -> None:
        layout = Awr2944Real2LaneInterleavedCandidate()
        cfg = small_real_config

        # Create synthetic int16 data of the right size
        num_samples = (
            cfg.adc.samples_per_chirp
            * cfg.hardware.num_rx
            * cfg.frame.chirps_per_frame
            * cfg.frame.num_frames
        )
        raw = np.arange(num_samples, dtype=np.int16) % 1000

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cube = layout.reshape_samples(raw, cfg)

        assert cube.shape == (4, 16, 4, 64)  # [frames, chirps, rx, samples]
        assert cube.dtype == np.float32


class TestXwr14xxComplexLayout:
    """Test xWR14xx complex 4-lane layout."""

    def test_expected_file_size_complex(self, small_complex_config: RadarConfig) -> None:
        layout = Xwr14xxComplex4Lane()
        # 64 samples × 4 RX × 16 chirps × 4 frames × 4 bytes = 65,536
        expected = 64 * 4 * 16 * 4 * 4
        assert layout.expected_file_size(small_complex_config) == expected

    def test_reshape_produces_correct_shape(self, small_complex_config: RadarConfig) -> None:
        layout = Xwr14xxComplex4Lane()
        cfg = small_complex_config

        # Complex: 2 int16 per sample (I+Q), 4 lanes
        num_int16 = (
            cfg.adc.samples_per_chirp * 2  # I+Q
            * cfg.hardware.num_rx
            * cfg.frame.chirps_per_frame
            * cfg.frame.num_frames
        )
        raw = np.arange(num_int16, dtype=np.int16) % 500

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cube = layout.reshape_samples(raw, cfg)

        assert cube.shape == (4, 16, 4, 64)
        assert cube.dtype == np.complex64
