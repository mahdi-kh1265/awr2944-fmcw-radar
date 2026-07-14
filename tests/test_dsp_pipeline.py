"""Comprehensive tests for the DSP pipeline package.

Tests use deterministic synthetic cubes — no real captures needed.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import numpy as np
import pytest
import scipy.io as sio

from awr2944_dca.dsp.axes import (
    range_axis,
    range_bin_spacing_m,
    velocity_axis,
    velocity_bin_spacing_mps,
)
from awr2944_dca.dsp.cfar import cfar_1d, cfar_2d
from awr2944_dca.dsp.clutter import remove_clutter
from awr2944_dca.dsp.config import (
    C_MPS,
    BackgroundConfig,
    CfarConfig,
    ClutterRemovalMode,
    DCRemovalMode,
    DopplerProcessingConfig,
    PipelineConfig,
    RadarProfile,
    RangeProcessingConfig,
    RxCombination,
    WindowType,
)
from awr2944_dca.dsp.doppler_fft import compute_doppler_fft
from awr2944_dca.dsp.matlab_export import export_to_mat
from awr2944_dca.dsp.metrics import estimate_noise_floor, processing_comparison
from awr2944_dca.dsp.peaks import find_local_maxima, cluster_detections
from awr2944_dca.dsp.pipeline import run_pipeline
from awr2944_dca.dsp.preprocessing import remove_dc
from awr2944_dca.dsp.range_fft import compute_range_fft
from awr2944_dca.dsp.types import CfarDetection
from awr2944_dca.dsp.windows import get_window


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def smoke_profile() -> RadarProfile:
    return RadarProfile.from_smoke_v1()


@pytest.fixture
def small_profile() -> RadarProfile:
    return RadarProfile(
        start_frequency_hz=77e9,
        slope_hz_per_s=29.982e12,
        adc_sample_rate_hz=10e6,
        adc_samples=64,
        idle_time_s=100e-6,
        ramp_end_time_s=60e-6,
        chirps_per_frame=16,
        frame_count=4,
        frame_period_s=40e-3,
        rx_count=4,
        tx_mask=3,
        sample_format="real_int16",
        cube_layout="frame_chirp_rx_sample",
    )


def _make_tone_cube(
    profile: RadarProfile,
    range_bin: int = 10,
    amplitude: float = 1000.0,
    noise_std: float = 10.0,
    seed: int = 42,
) -> np.ndarray:
    """Generate a synthetic cube with a tone at a specific range bin."""
    rng = np.random.default_rng(seed)
    F, C, R, S = profile.frame_count, profile.chirps_per_frame, profile.rx_count, profile.adc_samples
    cube = rng.normal(0, noise_std, (F, C, R, S)).astype(np.float32)
    freq = range_bin / S
    n = np.arange(S)
    tone = amplitude * np.sin(2 * np.pi * freq * n)
    cube += tone.astype(np.float32)
    return cube.astype(np.int16)


def _make_noise_cube(profile: RadarProfile, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    F, C, R, S = profile.frame_count, profile.chirps_per_frame, profile.rx_count, profile.adc_samples
    return rng.integers(-200, 200, (F, C, R, S), dtype=np.int16)


# ---------------------------------------------------------------------------
# E1: Config and profile tests
# ---------------------------------------------------------------------------

class TestRadarProfile:
    def test_smoke_v1_profile_values(self, smoke_profile: RadarProfile) -> None:
        assert smoke_profile.start_frequency_hz == 77e9
        assert smoke_profile.adc_samples == 256
        assert smoke_profile.chirps_per_frame == 128
        assert smoke_profile.frame_count == 8
        assert smoke_profile.rx_count == 4
        assert smoke_profile.sample_format == "real_int16"

    def test_derived_properties(self, smoke_profile: RadarProfile) -> None:
        assert smoke_profile.wavelength_m == pytest.approx(C_MPS / 77e9, rel=1e-6)
        assert smoke_profile.chirp_repetition_interval_s == pytest.approx(160e-6)
        assert smoke_profile.range_resolution_m > 0
        assert smoke_profile.max_unambiguous_velocity_mps > 0

    def test_to_dict_roundtrip(self, smoke_profile: RadarProfile) -> None:
        d = smoke_profile.to_dict()
        assert isinstance(d, dict)
        assert d["adc_samples"] == 256
        json.dumps(d)  # ensure JSON serializable


# ---------------------------------------------------------------------------
# E1: Windows
# ---------------------------------------------------------------------------

class TestWindows:
    @pytest.mark.parametrize("wtype", list(WindowType))
    def test_window_shape(self, wtype: WindowType) -> None:
        w, cg = get_window(wtype, 64)
        assert w.shape == (64,)
        assert w.dtype == np.float32

    def test_rectangular_is_ones_when_unnormalized(self) -> None:
        w, cg = get_window(WindowType.RECTANGULAR, 64, normalize=False)
        np.testing.assert_allclose(w, 1.0)
        assert cg == pytest.approx(1.0)

    def test_hann_coherent_gain(self) -> None:
        w, cg = get_window(WindowType.HANN, 256, normalize=True)
        # After normalization, mean should be ~1.0
        np.testing.assert_allclose(np.mean(w), 1.0, atol=1e-5)

    def test_kaiser_beta(self) -> None:
        w1, _ = get_window(WindowType.KAISER, 64, kaiser_beta=2.0)
        w2, _ = get_window(WindowType.KAISER, 64, kaiser_beta=14.0)
        # Higher beta = narrower mainlobe = more sidelobe suppression
        # The windows should be different
        assert not np.allclose(w1, w2)


# ---------------------------------------------------------------------------
# E1: Preprocessing
# ---------------------------------------------------------------------------

class TestPreprocessing:
    def test_dc_none_is_copy(self) -> None:
        cube = np.ones((2, 4, 2, 32), dtype=np.float32) * 100
        result = remove_dc(cube, DCRemovalMode.NONE)
        np.testing.assert_array_equal(result, cube)
        assert result is not cube  # must be a copy

    def test_dc_per_chirp_zeros_mean(self) -> None:
        cube = np.random.default_rng(42).normal(50, 10, (2, 4, 2, 32)).astype(np.float32)
        result = remove_dc(cube, DCRemovalMode.PER_CHIRP)
        means = result.mean(axis=-1)
        np.testing.assert_allclose(means, 0.0, atol=1e-5)

    def test_dc_per_rx_global(self) -> None:
        cube = np.random.default_rng(42).normal(100, 10, (2, 4, 2, 32)).astype(np.float32)
        result = remove_dc(cube, DCRemovalMode.PER_RX_GLOBAL)
        # Mean per RX across all frames/chirps/samples should be ~0
        for rx in range(2):
            np.testing.assert_allclose(result[:, :, rx, :].mean(), 0.0, atol=1e-4)

    def test_source_cube_immutability(self) -> None:
        cube = np.ones((2, 4, 2, 32), dtype=np.float32) * 42
        original = cube.copy()
        remove_dc(cube, DCRemovalMode.PER_CHIRP)
        np.testing.assert_array_equal(cube, original)


# ---------------------------------------------------------------------------
# E4: Range FFT
# ---------------------------------------------------------------------------

class TestRangeFFT:
    def test_rfft_output_shape(self, small_profile: RadarProfile) -> None:
        cube = _make_noise_cube(small_profile)
        cfg = RangeProcessingConfig(nfft=64)
        result = compute_range_fft(cube, small_profile, cfg)
        # rfft: 64 samples -> 33 bins
        assert result.complex_cube.shape[-1] == 64 // 2 + 1
        assert result.complex_cube.dtype == np.complex64

    def test_tone_peak_location(self, small_profile: RadarProfile) -> None:
        target_bin = 8
        cube = _make_tone_cube(small_profile, range_bin=target_bin, amplitude=5000)
        cfg = RangeProcessingConfig(
            dc_removal=DCRemovalMode.PER_CHIRP,
            window=WindowType.RECTANGULAR,
            nfft=64,
        )
        result = compute_range_fft(cube, small_profile, cfg)
        avg_mag = np.mean(result.magnitude, axis=(0, 1, 2))
        peak_bin = np.argmax(avg_mag)
        assert abs(peak_bin - target_bin) <= 1, f"Expected bin {target_bin}, got {peak_bin}"

    def test_range_fft_preserves_frame_count(self, small_profile: RadarProfile) -> None:
        cube = _make_noise_cube(small_profile)
        cfg = RangeProcessingConfig(nfft=64)
        result = compute_range_fft(cube, small_profile, cfg)
        assert result.shape[0] == small_profile.frame_count

    def test_range_fft_config_attached(self, small_profile: RadarProfile) -> None:
        cube = _make_noise_cube(small_profile)
        cfg = RangeProcessingConfig(nfft=64)
        result = compute_range_fft(cube, small_profile, cfg)
        assert "nfft" in result.config_dict
        assert result.config_dict["nfft"] == 64

    def test_windowed_tone_still_peaks(self, small_profile: RadarProfile) -> None:
        target_bin = 10
        cube = _make_tone_cube(small_profile, range_bin=target_bin, amplitude=5000)
        for wt in [WindowType.HANN, WindowType.HAMMING, WindowType.BLACKMAN]:
            cfg = RangeProcessingConfig(window=wt, nfft=64)
            result = compute_range_fft(cube, small_profile, cfg)
            avg_mag = np.mean(result.magnitude, axis=(0, 1, 2))
            peak_bin = np.argmax(avg_mag)
            assert abs(peak_bin - target_bin) <= 1, f"Window {wt}: expected {target_bin}, got {peak_bin}"

    def test_zero_padding_increases_bins(self, small_profile: RadarProfile) -> None:
        cube = _make_noise_cube(small_profile)
        cfg = RangeProcessingConfig(nfft=128)  # 2x zero-padded
        result = compute_range_fft(cube, small_profile, cfg)
        assert result.complex_cube.shape[-1] == 128 // 2 + 1  # 65 bins


# ---------------------------------------------------------------------------
# E5: Axes
# ---------------------------------------------------------------------------

class TestAxes:
    def test_range_axis_starts_at_zero(self, smoke_profile: RadarProfile) -> None:
        r = range_axis(smoke_profile)
        assert r[0] == pytest.approx(0.0)

    def test_range_axis_length_matches_rfft(self, smoke_profile: RadarProfile) -> None:
        r = range_axis(smoke_profile, nfft=256)
        assert len(r) == 256 // 2 + 1

    def test_range_bin_spacing(self, smoke_profile: RadarProfile) -> None:
        r = range_axis(smoke_profile, nfft=256)
        spacing = r[1] - r[0]
        expected = range_bin_spacing_m(smoke_profile, nfft=256)
        assert spacing == pytest.approx(expected, rel=1e-6)

    def test_velocity_axis_centered_at_zero(self, smoke_profile: RadarProfile) -> None:
        v = velocity_axis(smoke_profile)
        # The midpoint should be near 0 m/s
        center_idx = len(v) // 2
        assert abs(v[center_idx]) < velocity_bin_spacing_mps(smoke_profile) * 1.1

    def test_velocity_axis_length(self, smoke_profile: RadarProfile) -> None:
        v = velocity_axis(smoke_profile, ndoppler=128)
        assert len(v) == 128


# ---------------------------------------------------------------------------
# E6: Doppler FFT
# ---------------------------------------------------------------------------

class TestDopplerFFT:
    def test_doppler_output_shape(self, small_profile: RadarProfile) -> None:
        cube = _make_noise_cube(small_profile)
        range_cfg = RangeProcessingConfig(nfft=64)
        range_result = compute_range_fft(cube, small_profile, range_cfg)
        dop_cfg = DopplerProcessingConfig(nfft=16)
        dop_result = compute_doppler_fft(range_result.complex_cube, small_profile, dop_cfg)
        assert dop_result.complex_cube.shape[0] == small_profile.frame_count
        assert dop_result.complex_cube.shape[1] == 16  # nfft = chirps_per_frame
        assert dop_result.complex_cube.dtype == np.complex64

    def test_doppler_rx_combined_shape(self, small_profile: RadarProfile) -> None:
        cube = _make_noise_cube(small_profile)
        range_cfg = RangeProcessingConfig(nfft=64)
        range_result = compute_range_fft(cube, small_profile, range_cfg)
        dop_cfg = DopplerProcessingConfig(nfft=16)
        dop_result = compute_doppler_fft(range_result.complex_cube, small_profile, dop_cfg)
        # rx_combined: [frame, doppler, range]
        assert dop_result.rx_combined_power.shape[0] == small_profile.frame_count
        assert dop_result.rx_combined_power.ndim == 3

    def test_clutter_removal_in_doppler(self, small_profile: RadarProfile) -> None:
        cube = _make_noise_cube(small_profile)
        range_cfg = RangeProcessingConfig(nfft=64)
        range_result = compute_range_fft(cube, small_profile, range_cfg)

        cfg_no_clutter = DopplerProcessingConfig(nfft=16, clutter_removal=ClutterRemovalMode.NONE)
        cfg_clutter = DopplerProcessingConfig(nfft=16, clutter_removal=ClutterRemovalMode.SLOW_TIME_MEAN)

        res_no = compute_doppler_fft(range_result.complex_cube, small_profile, cfg_no_clutter)
        res_yes = compute_doppler_fft(range_result.complex_cube, small_profile, cfg_clutter)

        # They should differ
        assert not np.allclose(res_no.complex_cube, res_yes.complex_cube)


# ---------------------------------------------------------------------------
# E7: Clutter
# ---------------------------------------------------------------------------

class TestClutter:
    def test_slow_time_mean_removes_static(self) -> None:
        static = np.ones((2, 8, 2, 16), dtype=np.complex64) * (50 + 0j)
        result = remove_clutter(static, ClutterRemovalMode.SLOW_TIME_MEAN)
        np.testing.assert_allclose(result, 0.0, atol=1e-5)

    def test_clutter_none_is_copy(self) -> None:
        cube = np.ones((2, 8, 2, 16), dtype=np.complex64)
        result = remove_clutter(cube, ClutterRemovalMode.NONE)
        np.testing.assert_array_equal(result, cube)
        assert result is not cube


# ---------------------------------------------------------------------------
# E8: CFAR
# ---------------------------------------------------------------------------

class TestCFAR:
    def test_cfar_1d_detects_strong_peak(self) -> None:
        signal = np.full(100, -50.0, dtype=np.float32)
        signal[30] = 0.0  # strong peak
        config = CfarConfig(threshold_factor_db=10.0, minimum_snr_db=5.0)
        dets = cfar_1d(signal, config)
        assert len(dets) > 0
        assert any(d.range_bin == 30 for d in dets)

    def test_cfar_1d_no_detections_in_noise(self) -> None:
        rng = np.random.default_rng(42)
        signal = rng.normal(-50, 1, 100).astype(np.float32)
        config = CfarConfig(threshold_factor_db=20.0, minimum_snr_db=15.0)
        dets = cfar_1d(signal, config)
        # Very high threshold should yield zero or near-zero detections
        assert len(dets) <= 2

    def test_cfar_2d_detects_target(self) -> None:
        rd_map = np.full((64, 64), -50.0, dtype=np.float32)
        rd_map[32, 20] = 0.0  # target
        config = CfarConfig(threshold_factor_db=10.0, minimum_snr_db=5.0)
        dets = cfar_2d(rd_map, config)
        assert len(dets) > 0
        bins = [(d.doppler_bin, d.range_bin) for d in dets]
        assert (32, 20) in bins

    def test_cfar_detection_fields(self) -> None:
        signal = np.full(50, -40.0, dtype=np.float32)
        signal[20] = 10.0
        r_axis = np.linspace(0, 25, 50)
        config = CfarConfig()
        dets = cfar_1d(signal, config, range_axis_m=r_axis)
        for d in dets:
            assert d.snr_db > 0
            assert d.range_m >= 0
            d_dict = d.to_dict()
            assert "snr_db" in d_dict


# ---------------------------------------------------------------------------
# E10: Peaks
# ---------------------------------------------------------------------------

class TestPeaks:
    def test_find_local_maxima(self) -> None:
        spectrum = np.zeros(100, dtype=np.float32) - 50.0
        spectrum[30] = -10.0
        spectrum[70] = -5.0
        peaks = find_local_maxima(spectrum, min_prominence_db=10.0)
        bins = [p.bin_index for p in peaks]
        assert 30 in bins
        assert 70 in bins

    def test_parabolic_interpolation(self) -> None:
        # Create a peak slightly between bins
        spectrum = np.zeros(50, dtype=np.float32) - 50.0
        spectrum[19] = -15.0
        spectrum[20] = -10.0
        spectrum[21] = -12.0
        peaks = find_local_maxima(spectrum, min_prominence_db=5.0)
        if peaks:
            p = [p for p in peaks if p.bin_index == 20][0]
            # Interpolated bin should be slightly left of 20
            assert 19.5 < p.interpolated_bin < 20.5

    def test_cluster_detections(self) -> None:
        dets = [
            CfarDetection(0, 10, 1.0, 5, 0.5, -10, -50, 40, -40),
            CfarDetection(0, 11, 1.1, 5, 0.5, -12, -50, 38, -38),
            CfarDetection(0, 50, 5.0, 30, 3.0, -8, -50, 42, -42),
        ]
        clusters = cluster_detections(dets, range_eps_bins=3, doppler_eps_bins=3)
        assert len(clusters) == 2  # first two close, third separate


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

class TestMetrics:
    def test_noise_floor_median(self) -> None:
        data = np.full(100, -50.0, dtype=np.float32)
        data[10] = 0.0  # one peak
        nf = estimate_noise_floor(data, method="median")
        assert nf.noise_floor_db == pytest.approx(-50.0, abs=1.0)

    def test_processing_comparison(self) -> None:
        orig = np.random.default_rng(42).normal(-40, 5, 100).astype(np.float32)
        proc = orig - 10  # 10 dB improvement
        result = processing_comparison(orig, proc, label="test")
        assert result["label"] == "test"
        assert result["mean_change_db"] == pytest.approx(-10.0, abs=0.1)


# ---------------------------------------------------------------------------
# MATLAB export
# ---------------------------------------------------------------------------

class TestMatlabExport:
    def test_export_creates_file(self, smoke_profile: RadarProfile, tmp_path: Path) -> None:
        cube = np.random.default_rng(42).integers(
            -100, 100, (8, 128, 4, 256), dtype=np.int16
        )
        out = export_to_mat(cube, smoke_profile, tmp_path / "test.mat")
        assert out.exists()
        assert out.stat().st_size > 0

    def test_export_roundtrip(self, smoke_profile: RadarProfile, tmp_path: Path) -> None:
        cube = np.random.default_rng(42).integers(
            -100, 100, (8, 128, 4, 256), dtype=np.int16
        )
        out = export_to_mat(
            cube, smoke_profile, tmp_path / "rt.mat",
            canonical_raw_sha256="abc123",
        )
        loaded = sio.loadmat(str(out))
        np.testing.assert_array_equal(loaded["adc_cube"], cube)
        assert loaded["frame_count"].item() == 8
        assert loaded["canonical_raw_sha256"].item() == "abc123"

    def test_matlab_transpose_correctness(self, smoke_profile: RadarProfile, tmp_path: Path) -> None:
        cube = np.arange(8 * 2 * 4 * 16, dtype=np.int16).reshape(8, 2, 4, 16)
        small_prof = RadarProfile(
            start_frequency_hz=77e9, slope_hz_per_s=29.982e12,
            adc_sample_rate_hz=10e6, adc_samples=16,
            idle_time_s=100e-6, ramp_end_time_s=60e-6,
            chirps_per_frame=2, frame_count=8, frame_period_s=40e-3,
            rx_count=4, tx_mask=3, sample_format="real_int16",
            cube_layout="frame_chirp_rx_sample",
        )
        out = export_to_mat(cube, small_prof, tmp_path / "transpose.mat")
        loaded = sio.loadmat(str(out))

        # adc_cube_matlab should be the transpose
        expected_matlab = cube.transpose(3, 2, 1, 0)
        np.testing.assert_array_equal(loaded["adc_cube_matlab"], expected_matlab)

    def test_axes_in_export(self, smoke_profile: RadarProfile, tmp_path: Path) -> None:
        cube = np.zeros((8, 128, 4, 256), dtype=np.int16)
        out = export_to_mat(cube, smoke_profile, tmp_path / "axes.mat")
        loaded = sio.loadmat(str(out))
        assert "range_axis_m" in loaded
        assert "velocity_axis_mps" in loaded
        r = loaded["range_axis_m"].ravel()
        assert r[0] == pytest.approx(0.0)
        assert len(r) == 256 // 2 + 1


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

class TestPipeline:
    def test_pipeline_runs_end_to_end(self, small_profile: RadarProfile) -> None:
        cube = _make_tone_cube(small_profile, range_bin=8)
        config = PipelineConfig(
            profile=small_profile,
            range_cfg=RangeProcessingConfig(nfft=64),
            doppler_cfg=DopplerProcessingConfig(nfft=16),
        )
        result = run_pipeline(cube, config)

        assert result.range_result is not None
        assert result.doppler_result is not None
        assert result.detections is not None
        assert result.timings["total_s"] > 0

    def test_pipeline_preserves_source(self, small_profile: RadarProfile) -> None:
        cube = _make_noise_cube(small_profile)
        original = cube.copy()
        run_pipeline(cube, PipelineConfig(
            profile=small_profile,
            range_cfg=RangeProcessingConfig(nfft=64),
            doppler_cfg=DopplerProcessingConfig(nfft=16),
        ))
        np.testing.assert_array_equal(cube, original)

    def test_pipeline_config_attached(self, small_profile: RadarProfile) -> None:
        cube = _make_noise_cube(small_profile)
        result = run_pipeline(cube, PipelineConfig(
            profile=small_profile,
            range_cfg=RangeProcessingConfig(nfft=64),
            doppler_cfg=DopplerProcessingConfig(nfft=16),
        ))
        assert "profile" in result.config_dict
        assert "range" in result.config_dict

    def test_pipeline_no_cfar(self, small_profile: RadarProfile) -> None:
        cube = _make_noise_cube(small_profile)
        result = run_pipeline(
            cube,
            PipelineConfig(
                profile=small_profile,
                range_cfg=RangeProcessingConfig(nfft=64),
                doppler_cfg=DopplerProcessingConfig(nfft=16),
            ),
            run_cfar=False,
        )
        assert result.detections is None


# ---------------------------------------------------------------------------
# Guard: Angle processing rejection
# ---------------------------------------------------------------------------

class TestAngleGuard:
    def test_simultaneous_tx_rejects_angle(self, smoke_profile: RadarProfile) -> None:
        """TX0+TX1 simultaneous (tx_mask=3) prevents valid angle FFT.
        No angle processing should be attempted."""
        assert smoke_profile.tx_mask == 3  # both TX active simultaneously
        # The DSP package intentionally has no angle FFT implementation
        # because this dataset uses simultaneous TX, not TDM-MIMO
        import awr2944_dca.dsp as dsp_pkg
        assert not hasattr(dsp_pkg, "compute_angle_fft")
