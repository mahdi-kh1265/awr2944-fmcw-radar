"""Tests for ADC parser: round-trip, file-size validation, synthetic data."""

from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pytest

from awr2944_dca.config.schema import RadarConfig
from awr2944_dca.formats.adc_parser import parse_adc_bin, validate_file_size
from awr2944_dca.formats.layouts import (
    Awr2944RealInterleaved2Lane,
    Xwr14xxComplex4Lane,
    get_layout,
)
from awr2944_dca.formats.synthetic import (
    generate_radar_cube,
    pack_cube_to_bin,
    write_synthetic_bin,
)


class TestFileSizeValidation:
    """Test file-size validation logic."""

    def test_correct_size_passes(self, small_real_config: RadarConfig, tmp_path: Path) -> None:
        layout = get_layout(small_real_config.adc.layout)
        expected = layout.expected_file_size(small_real_config)

        # Create file with correct size
        bin_path = tmp_path / "adc_data.bin"
        bin_path.write_bytes(b"\x00" * expected)

        result = validate_file_size(bin_path, small_real_config)
        assert result.ok is True

    def test_wrong_size_fails(self, small_real_config: RadarConfig, tmp_path: Path) -> None:
        # Create file with wrong size
        bin_path = tmp_path / "adc_data.bin"
        bin_path.write_bytes(b"\x00" * 100)

        result = validate_file_size(bin_path, small_real_config)
        assert result.ok is False
        assert "MISMATCH" in result.message

    def test_too_large_file_diagnostic(self, small_real_config: RadarConfig, tmp_path: Path) -> None:
        layout = get_layout(small_real_config.adc.layout)
        expected = layout.expected_file_size(small_real_config)

        bin_path = tmp_path / "adc_data.bin"
        bin_path.write_bytes(b"\x00" * (expected * 2))

        result = validate_file_size(bin_path, small_real_config)
        assert result.ok is False
        assert "LARGER" in result.message


class TestRoundTripReal:
    """Round-trip tests for real-ADC AWR2944 layout.

    Uses integer-valued samples for exact equality (no float rounding).
    """

    def test_round_trip_noise(self, small_real_config: RadarConfig, tmp_path: Path) -> None:
        """Generate noise cube → pack to binary → parse back → exact equality."""
        cfg = small_real_config
        cube_original = generate_radar_cube(cfg, mode="noise", seed=123)

        # Pack and write
        bin_path = tmp_path / "adc_data.bin"
        raw_bytes = pack_cube_to_bin(cube_original, cfg)
        bin_path.write_bytes(raw_bytes)

        # Parse back
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cube_parsed = parse_adc_bin(bin_path, cfg)

        # Exact equality (integer-valued samples)
        np.testing.assert_array_equal(cube_original, cube_parsed)

    def test_round_trip_ramp(self, small_real_config: RadarConfig, tmp_path: Path) -> None:
        """Ramp pattern round-trip."""
        cfg = small_real_config
        cube_original = generate_radar_cube(cfg, mode="ramp")

        bin_path = tmp_path / "adc_data.bin"
        raw_bytes = pack_cube_to_bin(cube_original, cfg)
        bin_path.write_bytes(raw_bytes)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cube_parsed = parse_adc_bin(bin_path, cfg)

        np.testing.assert_array_equal(cube_original, cube_parsed)

    def test_round_trip_zeros(self, small_real_config: RadarConfig, tmp_path: Path) -> None:
        """Zero-filled round-trip."""
        cfg = small_real_config
        cube_original = generate_radar_cube(cfg, mode="zeros")

        bin_path = tmp_path / "adc_data.bin"
        raw_bytes = pack_cube_to_bin(cube_original, cfg)
        bin_path.write_bytes(raw_bytes)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cube_parsed = parse_adc_bin(bin_path, cfg)

        np.testing.assert_array_equal(cube_original, cube_parsed)

    def test_write_synthetic_bin_helper(self, small_real_config: RadarConfig, tmp_path: Path) -> None:
        """Test the write_synthetic_bin convenience function."""
        cfg = small_real_config
        bin_path = tmp_path / "adc_data.bin"

        cube_original = write_synthetic_bin(bin_path, cfg, mode="noise", seed=99)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cube_parsed = parse_adc_bin(bin_path, cfg)

        np.testing.assert_array_equal(cube_original, cube_parsed)


class TestRoundTripComplex:
    """Round-trip tests for complex-ADC xWR14xx layout."""

    def test_round_trip_complex_noise(self, small_complex_config: RadarConfig, tmp_path: Path) -> None:
        """Complex ADC round-trip with integer I+Q values."""
        cfg = small_complex_config
        cube_original = generate_radar_cube(cfg, mode="noise", seed=456)

        bin_path = tmp_path / "adc_data.bin"
        raw_bytes = pack_cube_to_bin(cube_original, cfg)
        bin_path.write_bytes(raw_bytes)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cube_parsed = parse_adc_bin(bin_path, cfg)

        # Exact equality for integer-valued I and Q
        np.testing.assert_array_equal(cube_original.real, cube_parsed.real)
        np.testing.assert_array_equal(cube_original.imag, cube_parsed.imag)


class TestParserErrors:
    """Test parser error handling."""

    def test_file_not_found(self, small_real_config: RadarConfig) -> None:
        with pytest.raises(FileNotFoundError):
            parse_adc_bin(Path("/nonexistent/adc_data.bin"), small_real_config)

    def test_strict_size_mismatch_raises(self, small_real_config: RadarConfig, tmp_path: Path) -> None:
        bin_path = tmp_path / "adc_data.bin"
        bin_path.write_bytes(b"\x00" * 100)

        with pytest.raises(ValueError, match="MISMATCH"):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                parse_adc_bin(bin_path, small_real_config, strict_size=True)

    def test_unvalidated_layout_warns(self, small_real_config: RadarConfig, tmp_path: Path) -> None:
        cfg = small_real_config
        cube = generate_radar_cube(cfg, mode="zeros")
        bin_path = tmp_path / "adc_data.bin"
        bin_path.write_bytes(pack_cube_to_bin(cube, cfg))

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            parse_adc_bin(bin_path, cfg)

        warning_messages = [str(x.message) for x in w]
        assert any("unvalidated" in msg.lower() or "NOT been validated" in msg for msg in warning_messages)
