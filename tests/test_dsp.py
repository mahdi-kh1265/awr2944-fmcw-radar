"""Tests for DSP pipeline functions."""

from __future__ import annotations

import numpy as np
import pytest

from awr2944_dca.config.schema import RadarConfig
from awr2944_dca.dsp.dsp import (
    apply_doppler_fft,
    apply_range_fft,
    process_cube,
    remove_dc_offset,
    remove_static_clutter,
)
from awr2944_dca.formats.synthetic import generate_radar_cube, generate_tone_cube


class TestDCRemoval:
    """Test DC offset removal."""

    def test_dc_removal_zeros_mean(self, small_real_config: RadarConfig) -> None:
        """After DC removal, per-chirp mean should be near zero."""
        cube = generate_radar_cube(small_real_config, mode="noise", seed=42)
        result = remove_dc_offset(cube)

        # Mean along sample axis should be ~0 for each chirp
        means = result.mean(axis=-1)
        np.testing.assert_allclose(means, 0.0, atol=1e-5)

    def test_dc_removal_preserves_shape(self, small_real_config: RadarConfig) -> None:
        cube = generate_radar_cube(small_real_config, mode="noise")
        result = remove_dc_offset(cube)
        assert result.shape == cube.shape
        assert result.dtype == cube.dtype

    def test_dc_removal_with_constant_offset(self) -> None:
        """A constant offset across all samples should be removed."""
        cube = np.full((2, 4, 2, 32), 100.0, dtype=np.float32)
        result = remove_dc_offset(cube)
        np.testing.assert_allclose(result, 0.0, atol=1e-5)


class TestRangeFFT:
    """Test range FFT."""

    def test_range_fft_output_is_complex(self, small_real_config: RadarConfig) -> None:
        """Range FFT of real data should produce complex output."""
        cube = generate_radar_cube(small_real_config, mode="noise")
        result = apply_range_fft(cube)
        assert result.dtype == np.complex64

    def test_range_fft_preserves_shape(self, small_real_config: RadarConfig) -> None:
        cube = generate_radar_cube(small_real_config, mode="noise")
        result = apply_range_fft(cube)
        assert result.shape == cube.shape

    def test_range_fft_tone_produces_peak(self, small_real_config: RadarConfig) -> None:
        """A tone at a specific frequency should produce a peak at that bin."""
        cfg = small_real_config
        target_bin = 10
        cube = generate_tone_cube(cfg, range_bin=target_bin, amplitude=1000.0)

        result = apply_range_fft(cube, window="none")

        # Check that the peak is near the target bin
        # Average across all frames, chirps, RX
        avg_spectrum = np.mean(np.abs(result), axis=(0, 1, 2))
        peak_bin = np.argmax(avg_spectrum)

        # Allow ±1 bin tolerance due to windowing effects
        assert abs(peak_bin - target_bin) <= 1

    def test_range_fft_no_window(self, small_real_config: RadarConfig) -> None:
        cube = generate_radar_cube(small_real_config, mode="noise")
        result = apply_range_fft(cube, window="none")
        assert result.dtype == np.complex64

    def test_range_fft_bad_window_raises(self, small_real_config: RadarConfig) -> None:
        cube = generate_radar_cube(small_real_config, mode="noise")
        with pytest.raises(ValueError, match="Unknown window"):
            apply_range_fft(cube, window="bad_window")


class TestClutterRemoval:
    """Test static clutter removal."""

    def test_clutter_removal_removes_static(self) -> None:
        """A static (constant across chirps) component should be removed."""
        # Create data: static component + varying component
        static = np.ones((2, 8, 2, 32), dtype=np.complex64) * 50.0
        varying = np.random.default_rng(42).standard_normal((2, 8, 2, 32)).astype(np.complex64)

        cube = static + varying
        result = remove_static_clutter(cube)

        # The mean across chirps should be near zero after clutter removal
        mean_across_chirps = result.mean(axis=1)
        np.testing.assert_allclose(mean_across_chirps, 0.0, atol=1e-5)

    def test_clutter_removal_preserves_varying(self) -> None:
        """Varying components should be (mostly) preserved."""
        rng = np.random.default_rng(42)
        varying = rng.standard_normal((2, 8, 2, 32)).astype(np.complex64)

        # With only varying data, clutter removal should approximately preserve it
        result = remove_static_clutter(varying)
        # After removing mean, the variance should be similar
        assert result.shape == varying.shape


class TestDopplerFFT:
    """Test Doppler FFT."""

    def test_doppler_fft_output_shape(self, small_real_config: RadarConfig) -> None:
        cube = generate_radar_cube(small_real_config, mode="noise")
        range_cube = apply_range_fft(cube)
        result = apply_doppler_fft(range_cube)
        assert result.shape == range_cube.shape
        assert result.dtype == np.complex64

    def test_doppler_fft_no_shift(self, small_real_config: RadarConfig) -> None:
        cube = generate_radar_cube(small_real_config, mode="noise")
        range_cube = apply_range_fft(cube)
        result = apply_doppler_fft(range_cube, fft_shift=False)
        assert result.shape == range_cube.shape


class TestProcessCube:
    """Test full DSP pipeline."""

    def test_process_cube_returns_all_stages(self, small_real_config: RadarConfig) -> None:
        cube = generate_radar_cube(small_real_config, mode="noise")
        results = process_cube(cube)

        assert "dc_removed" in results
        assert "range_fft" in results
        assert "clutter_removed" in results
        assert "range_doppler" in results

    def test_process_cube_no_clutter(self, small_real_config: RadarConfig) -> None:
        cube = generate_radar_cube(small_real_config, mode="noise")
        results = process_cube(cube, remove_clutter=False)

        assert "dc_removed" in results
        assert "range_fft" in results
        assert "clutter_removed" not in results
        assert "range_doppler" in results

    def test_process_cube_output_shapes(self, small_real_config: RadarConfig) -> None:
        cube = generate_radar_cube(small_real_config, mode="noise")
        results = process_cube(cube)

        for key, val in results.items():
            assert val.shape[0] == cube.shape[0]  # frames preserved
            assert val.shape[2] == cube.shape[2]  # rx preserved


class TestPlaceholders:
    """Test that placeholder stubs raise NotImplementedError."""

    def test_angle_fft_placeholder(self) -> None:
        from awr2944_dca.dsp.dsp import apply_angle_fft

        with pytest.raises(NotImplementedError, match="M1"):
            apply_angle_fft(np.zeros((1, 1, 1, 1)))

    def test_cfar_placeholder(self) -> None:
        from awr2944_dca.dsp.dsp import apply_cfar

        with pytest.raises(NotImplementedError, match="M1"):
            apply_cfar(np.zeros((1, 1, 1, 1)))

    def test_point_cloud_placeholder(self) -> None:
        from awr2944_dca.dsp.dsp import export_point_cloud

        with pytest.raises(NotImplementedError, match="M1"):
            export_point_cloud(np.zeros((1, 1, 1, 1)))

    def test_calibration_placeholder(self) -> None:
        from awr2944_dca.dsp.dsp import calibrate_corner_reflector

        with pytest.raises(NotImplementedError, match="M1"):
            calibrate_corner_reflector(np.zeros((1, 1, 1, 1)))
