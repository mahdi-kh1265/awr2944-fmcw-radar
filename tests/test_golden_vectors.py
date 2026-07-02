"""Golden-vector tests for AWR2944 candidate layouts.

These tests are NON-CIRCULAR: the flat int16 binary stream is constructed
by hand according to the assumed TI interleave patterns, not by using
pack_cube_to_bin.  The parser is then run on this hand-constructed binary
and the output cube is asserted against the expected RX/sample values.

Candidate A (Interleaved):
    [RX0_s0, RX1_s0, RX2_s0, RX3_s0, RX0_s1, RX1_s1, ...]

Candidate B (Non-Interleaved):
    [RX0_s0, RX0_s1, ..., RX0_sN, RX1_s0, RX1_s1, ...]

STATUS: ASSUMED LAYOUTS — must be validated against a real AWR2944 capture.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pytest

from awr2944_dca.config.schema import RadarConfig
from awr2944_dca.formats.adc_parser import parse_adc_bin
from awr2944_dca.formats.layouts import (
    Awr2944Real2LaneInterleavedCandidate,
    Awr2944Real2LaneNoninterleavedCandidate,
)


def _make_config(*, frames: int, chirps: int, rx: int, samples: int, layout_name: str) -> RadarConfig:
    """Create a minimal RadarConfig for golden-vector tests."""
    rx_list = list(range(rx))
    ch_interleave = 0 if "interleaved" in layout_name and "non" not in layout_name else 1
    return RadarConfig.model_validate({
        "experiment": {"name": "golden_vector_test", "operator": "test"},
        "hardware": {
            "tx_enabled": [0],
            "rx_enabled": rx_list,
            "antenna_mode": "single_tx",
        },
        "adc": {
            "samples_per_chirp": samples,
            "bits": 16,
            "is_complex": False,
            "num_lvds_lanes": 2,
            "channel_interleave": ch_interleave,
            "layout": layout_name,
        },
        "frame": {
            "chirps_per_frame": chirps,
            "num_frames": frames,
        },
    })


def _build_flat_stream_interleaved(rx_data_per_chirp: list[list[list[int]]]) -> np.ndarray:
    """Build a flat int16 stream for interleaved layout.

    [RX0_s0, RX1_s0, RX2_s0, RX3_s0, RX0_s1, ...]
    """
    flat = []
    for chirp_data in rx_data_per_chirp:
        num_rx = len(chirp_data)
        num_samples = len(chirp_data[0])
        for s in range(num_samples):
            for rx in range(num_rx):
                flat.append(chirp_data[rx][s])
    return np.array(flat, dtype=np.int16)


def _build_flat_stream_noninterleaved(rx_data_per_chirp: list[list[list[int]]]) -> np.ndarray:
    """Build a flat int16 stream for non-interleaved layout.

    [RX0_s0, RX0_s1, ..., RX0_sN, RX1_s0, ...]
    """
    flat = []
    for chirp_data in rx_data_per_chirp:
        num_rx = len(chirp_data)
        num_samples = len(chirp_data[0])
        for rx in range(num_rx):
            for s in range(num_samples):
                flat.append(chirp_data[rx][s])
    return np.array(flat, dtype=np.int16)


def _write_and_parse(
    flat: np.ndarray,
    config: RadarConfig,
    tmp_path: Path,
) -> np.ndarray:
    """Write flat int16 data to a temp file and parse it."""
    bin_path = tmp_path / "adc_data.bin"
    flat.tofile(bin_path)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cube = parse_adc_bin(bin_path, config)

    return cube


@pytest.fixture(params=[
    ("awr2944_real_2lane_interleaved_candidate", _build_flat_stream_interleaved),
    ("awr2944_real_2lane_noninterleaved_candidate", _build_flat_stream_noninterleaved)
])
def layout_info(request):
    """Fixture to test both candidate layouts."""
    return request.param


class TestGoldenVectorSingleChirp:
    """Test 1: 1 frame, 1 chirp, 4 RX, 4 samples."""

    def test_single_chirp_golden(self, tmp_path: Path, layout_info) -> None:
        layout_name, build_func = layout_info
        config = _make_config(frames=1, chirps=1, rx=4, samples=4, layout_name=layout_name)

        rx0 = [1000, 1001, 1002, 1003]
        rx1 = [2000, 2001, 2002, 2003]
        rx2 = [3000, 3001, 3002, 3003]
        rx3 = [4000, 4001, 4002, 4003]

        flat = build_func([[rx0, rx1, rx2, rx3]])

        cube = _write_and_parse(flat, config, tmp_path)

        assert cube.shape == (1, 1, 4, 4)
        assert cube.dtype == np.float32

        np.testing.assert_array_equal(cube[0, 0, 0, :], rx0)
        np.testing.assert_array_equal(cube[0, 0, 1, :], rx1)
        np.testing.assert_array_equal(cube[0, 0, 2, :], rx2)
        np.testing.assert_array_equal(cube[0, 0, 3, :], rx3)

    def test_single_chirp_file_size(self, tmp_path: Path, layout_info) -> None:
        layout_name, _ = layout_info
        config = _make_config(frames=1, chirps=1, rx=4, samples=4, layout_name=layout_name)
        
        if "noninterleaved" in layout_name:
            layout = Awr2944Real2LaneNoninterleavedCandidate()
        else:
            layout = Awr2944Real2LaneInterleavedCandidate()

        expected_bytes = 4 * 4 * 1 * 1 * 2  # = 32 bytes
        assert layout.expected_file_size(config) == expected_bytes
        assert expected_bytes == 32


class TestGoldenVectorTwoChirps:
    """Test 2: 1 frame, 2 chirps, 4 RX, 4 samples."""

    def test_two_chirps_golden(self, tmp_path: Path, layout_info) -> None:
        layout_name, build_func = layout_info
        config = _make_config(frames=1, chirps=2, rx=4, samples=4, layout_name=layout_name)

        c0_rx0 = [1000, 1001, 1002, 1003]
        c0_rx1 = [2000, 2001, 2002, 2003]
        c0_rx2 = [3000, 3001, 3002, 3003]
        c0_rx3 = [4000, 4001, 4002, 4003]

        c1_rx0 = [5000, 5001, 5002, 5003]
        c1_rx1 = [6000, 6001, 6002, 6003]
        c1_rx2 = [7000, 7001, 7002, 7003]
        c1_rx3 = [8000, 8001, 8002, 8003]

        flat = build_func([
            [c0_rx0, c0_rx1, c0_rx2, c0_rx3],
            [c1_rx0, c1_rx1, c1_rx2, c1_rx3],
        ])

        assert len(flat) == 4 * 4 * 2

        cube = _write_and_parse(flat, config, tmp_path)

        assert cube.shape == (1, 2, 4, 4)
        assert cube.dtype == np.float32

        np.testing.assert_array_equal(cube[0, 0, 0, :], c0_rx0)
        np.testing.assert_array_equal(cube[0, 0, 1, :], c0_rx1)
        np.testing.assert_array_equal(cube[0, 0, 2, :], c0_rx2)
        np.testing.assert_array_equal(cube[0, 0, 3, :], c0_rx3)

        np.testing.assert_array_equal(cube[0, 1, 0, :], c1_rx0)
        np.testing.assert_array_equal(cube[0, 1, 1, :], c1_rx1)
        np.testing.assert_array_equal(cube[0, 1, 2, :], c1_rx2)
        np.testing.assert_array_equal(cube[0, 1, 3, :], c1_rx3)

    def test_two_chirps_file_size(self, tmp_path: Path, layout_info) -> None:
        layout_name, _ = layout_info
        config = _make_config(frames=1, chirps=2, rx=4, samples=4, layout_name=layout_name)
        
        if "noninterleaved" in layout_name:
            layout = Awr2944Real2LaneNoninterleavedCandidate()
        else:
            layout = Awr2944Real2LaneInterleavedCandidate()

        expected_bytes = 4 * 4 * 2 * 1 * 2
        assert layout.expected_file_size(config) == expected_bytes


class TestGoldenVectorTwoFrames:
    """Test 3: 2 frames, 2 chirps, 4 RX, 4 samples."""

    def test_two_frames_golden(self, tmp_path: Path, layout_info) -> None:
        layout_name, build_func = layout_info
        config = _make_config(frames=2, chirps=2, rx=4, samples=4, layout_name=layout_name)

        f0c0_rx0 = [100, 101, 102, 103]
        f0c0_rx1 = [200, 201, 202, 203]
        f0c0_rx2 = [300, 301, 302, 303]
        f0c0_rx3 = [400, 401, 402, 403]

        f0c1_rx0 = [110, 111, 112, 113]
        f0c1_rx1 = [210, 211, 212, 213]
        f0c1_rx2 = [310, 311, 312, 313]
        f0c1_rx3 = [410, 411, 412, 413]

        f1c0_rx0 = [500, 501, 502, 503]
        f1c0_rx1 = [600, 601, 602, 603]
        f1c0_rx2 = [700, 701, 702, 703]
        f1c0_rx3 = [800, 801, 802, 803]

        f1c1_rx0 = [510, 511, 512, 513]
        f1c1_rx1 = [610, 611, 612, 613]
        f1c1_rx2 = [710, 711, 712, 713]
        f1c1_rx3 = [810, 811, 812, 813]

        flat = build_func([
            [f0c0_rx0, f0c0_rx1, f0c0_rx2, f0c0_rx3],
            [f0c1_rx0, f0c1_rx1, f0c1_rx2, f0c1_rx3],
            [f1c0_rx0, f1c0_rx1, f1c0_rx2, f1c0_rx3],
            [f1c1_rx0, f1c1_rx1, f1c1_rx2, f1c1_rx3],
        ])

        assert len(flat) == 4 * 4 * 2 * 2

        cube = _write_and_parse(flat, config, tmp_path)

        assert cube.shape == (2, 2, 4, 4)
        assert cube.dtype == np.float32

        np.testing.assert_array_equal(cube[0, 0, 0, :], f0c0_rx0)
        np.testing.assert_array_equal(cube[0, 0, 1, :], f0c0_rx1)
        np.testing.assert_array_equal(cube[0, 0, 2, :], f0c0_rx2)
        np.testing.assert_array_equal(cube[0, 0, 3, :], f0c0_rx3)

        np.testing.assert_array_equal(cube[0, 1, 0, :], f0c1_rx0)
        np.testing.assert_array_equal(cube[0, 1, 1, :], f0c1_rx1)
        np.testing.assert_array_equal(cube[0, 1, 2, :], f0c1_rx2)
        np.testing.assert_array_equal(cube[0, 1, 3, :], f0c1_rx3)

        np.testing.assert_array_equal(cube[1, 0, 0, :], f1c0_rx0)
        np.testing.assert_array_equal(cube[1, 0, 1, :], f1c0_rx1)
        np.testing.assert_array_equal(cube[1, 0, 2, :], f1c0_rx2)
        np.testing.assert_array_equal(cube[1, 0, 3, :], f1c0_rx3)

        np.testing.assert_array_equal(cube[1, 1, 0, :], f1c1_rx0)
        np.testing.assert_array_equal(cube[1, 1, 1, :], f1c1_rx1)
        np.testing.assert_array_equal(cube[1, 1, 2, :], f1c1_rx2)
        np.testing.assert_array_equal(cube[1, 1, 3, :], f1c1_rx3)

    def test_two_frames_file_size(self, tmp_path: Path, layout_info) -> None:
        layout_name, _ = layout_info
        config = _make_config(frames=2, chirps=2, rx=4, samples=4, layout_name=layout_name)
        
        if "noninterleaved" in layout_name:
            layout = Awr2944Real2LaneNoninterleavedCandidate()
        else:
            layout = Awr2944Real2LaneInterleavedCandidate()

        expected_bytes = 4 * 4 * 2 * 2 * 2
        assert layout.expected_file_size(config) == expected_bytes


class TestOutputDtype:
    """Confirm real ADC parser returns float32, not complex64."""

    def test_real_adc_returns_float32(self, tmp_path: Path, layout_info) -> None:
        layout_name, build_func = layout_info
        config = _make_config(frames=1, chirps=1, rx=4, samples=4, layout_name=layout_name)
        flat = build_func([[[1, 2, 3, 4]] * 4])
        cube = _write_and_parse(flat, config, tmp_path)

        assert cube.dtype == np.float32
        assert not np.iscomplexobj(cube)
