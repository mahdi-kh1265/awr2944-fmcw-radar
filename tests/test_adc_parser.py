"""Tests for ADC parser (Path B).

All tests use synthetic tmp_path files.  No real lab adc_data.bin required.
No FFT tests.
"""

import json
import struct
from pathlib import Path

import numpy as np
import pytest
from typer.testing import CliRunner

from awr2944_dca.adc_parser import (
    AdcParserConfig,
    expected_adc_bytes,
    inspect_adc_file,
    load_adc_int16,
    parse_complex_int16,
)
from awr2944_dca.cli import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_synthetic_adc(path: Path, config: AdcParserConfig | None = None):
    """Write a synthetic ADC binary file with known complex int16 data."""
    if config is None:
        config = AdcParserConfig()
    n_complex = config.frames * config.chirps * config.rx * config.samples
    # Produce repeating pattern: I=idx%1000, Q=-(idx%1000)
    i_vals = np.arange(n_complex, dtype=np.int16) % 1000
    q_vals = -(np.arange(n_complex, dtype=np.int16) % 1000)
    interleaved = np.empty(2 * n_complex, dtype="<i2")
    interleaved[0::2] = i_vals
    interleaved[1::2] = q_vals
    interleaved.tofile(path)
    return i_vals, q_vals


# ---------------------------------------------------------------------------
# expected_adc_bytes
# ---------------------------------------------------------------------------

def test_expected_adc_bytes_default():
    """Default config produces 4,194,304 bytes."""
    assert expected_adc_bytes() == 4_194_304
    assert expected_adc_bytes(AdcParserConfig()) == 4_194_304


def test_expected_adc_bytes_custom():
    cfg = AdcParserConfig(frames=1, chirps=1, rx=1, samples=1)
    assert expected_adc_bytes(cfg) == 4


# ---------------------------------------------------------------------------
# parse_complex_int16 roundtrip
# ---------------------------------------------------------------------------

def test_parse_complex_roundtrip(tmp_path):
    """Synthetic complex cube writes and parses correctly for default layout."""
    path = tmp_path / "adc_data.bin"
    config = AdcParserConfig(frames=2, chirps=4, rx=2, samples=8)
    i_vals, q_vals = _write_synthetic_adc(path, config)

    cube = parse_complex_int16(path, config)
    assert cube.shape == (2, 4, 2, 8)
    assert cube.dtype == np.complex64

    # Verify first complex value
    assert cube.ravel()[0].real == float(i_vals[0])
    assert cube.ravel()[0].imag == float(q_vals[0])


def test_parse_complex_roundtrip_default_size(tmp_path):
    """Full default-size file parses without error."""
    path = tmp_path / "adc_data.bin"
    _write_synthetic_adc(path)
    cube = parse_complex_int16(path)
    assert cube.shape == (8, 128, 4, 256)


# ---------------------------------------------------------------------------
# Size validation
# ---------------------------------------------------------------------------

def test_wrong_file_size_raises(tmp_path):
    """File with wrong size raises ValueError."""
    path = tmp_path / "adc_data.bin"
    path.write_bytes(b"\x00" * 100)
    with pytest.raises(ValueError, match="size mismatch"):
        parse_complex_int16(path)


def test_odd_int16_count_raises(tmp_path):
    """File with odd byte count raises ValueError."""
    path = tmp_path / "adc_data.bin"
    path.write_bytes(b"\x00" * 3)  # 3 bytes = not aligned to int16
    with pytest.raises(ValueError):
        load_adc_int16(path)


def test_empty_file_raises(tmp_path):
    """Empty file raises ValueError."""
    path = tmp_path / "adc_data.bin"
    path.write_bytes(b"")
    with pytest.raises(ValueError, match="empty"):
        load_adc_int16(path)


# ---------------------------------------------------------------------------
# iq_order
# ---------------------------------------------------------------------------

def test_iq_order_iq_vs_qi(tmp_path):
    """iq_order='iq' and 'qi' produce different results."""
    path = tmp_path / "adc_data.bin"
    config_iq = AdcParserConfig(frames=1, chirps=1, rx=1, samples=2, iq_order="iq")
    config_qi = AdcParserConfig(frames=1, chirps=1, rx=1, samples=2, iq_order="qi")

    # Write known data: [10, 20, 30, 40] as int16
    data = np.array([10, 20, 30, 40], dtype="<i2")
    data.tofile(path)

    cube_iq = parse_complex_int16(path, config_iq)
    cube_qi = parse_complex_int16(path, config_qi)

    # iq: complex = I + jQ = 10+20j, 30+40j
    assert cube_iq.ravel()[0] == 10 + 20j
    assert cube_iq.ravel()[1] == 30 + 40j

    # qi: complex = Q + jI = 20+10j, 40+30j
    assert cube_qi.ravel()[0] == 20 + 10j
    assert cube_qi.ravel()[1] == 40 + 30j


# ---------------------------------------------------------------------------
# inspect_adc_file
# ---------------------------------------------------------------------------

def test_inspect_returns_shape_stats_sha256(tmp_path):
    """inspect_adc_file returns shape, stats, and SHA256."""
    path = tmp_path / "adc_data.bin"
    config = AdcParserConfig(frames=1, chirps=2, rx=1, samples=4)
    _write_synthetic_adc(path, config)

    info = inspect_adc_file(path, config)
    assert info["error"] is None
    assert info["shape"] == [1, 2, 1, 4]
    assert info["size_match"] is True
    assert "sha256" in info
    assert len(info["sha256"]) == 64
    assert "real_min" in info
    assert "imag_min" in info
    assert "per_rx_rms" in info
    assert len(info["per_rx_rms"]) == 1


def test_inspect_layout_assumption(tmp_path):
    """inspect output explicitly labels layout as unconfirmed assumption."""
    path = tmp_path / "adc_data.bin"
    config = AdcParserConfig(frames=1, chirps=1, rx=1, samples=1)
    _write_synthetic_adc(path, config)

    info = inspect_adc_file(path, config)
    assert info["layout_assumption"] == "frame_chirp_rx_sample"
    assert info["layout_assumption_confirmed"] is False


def test_inspect_first_values(tmp_path):
    """inspect includes first_16_int16_values and first_8_complex_values."""
    path = tmp_path / "adc_data.bin"
    config = AdcParserConfig(frames=1, chirps=2, rx=2, samples=4)
    _write_synthetic_adc(path, config)

    info = inspect_adc_file(path, config)
    assert "first_16_int16_values" in info
    assert len(info["first_16_int16_values"]) == 16
    assert "first_8_complex_values" in info
    assert len(info["first_8_complex_values"]) == 8
    assert "real" in info["first_8_complex_values"][0]
    assert "imag" in info["first_8_complex_values"][0]


def test_all_zero_detected(tmp_path):
    """All-zero file reports all_zero=True."""
    path = tmp_path / "adc_data.bin"
    config = AdcParserConfig(frames=1, chirps=1, rx=1, samples=2)
    size = expected_adc_bytes(config)
    path.write_bytes(b"\x00" * size)

    info = inspect_adc_file(path, config)
    assert info["error"] is None
    assert info["all_zero"] is True


def test_inspect_wrong_size(tmp_path):
    """inspect returns error dict (not exception) for wrong size."""
    path = tmp_path / "adc_data.bin"
    path.write_bytes(b"\x00" * 100)

    info = inspect_adc_file(path)
    assert info["error"] is not None
    assert "mismatch" in info["error"].lower()


def test_inspect_missing_file(tmp_path):
    """inspect returns error for missing file."""
    path = tmp_path / "nonexistent.bin"
    info = inspect_adc_file(path)
    assert info["error"] is not None
    assert "not found" in info["error"].lower()


# ---------------------------------------------------------------------------
# CLI: awr adc inspect
# ---------------------------------------------------------------------------

def test_cli_text_inspect(tmp_path):
    """CLI text inspection works."""
    path = tmp_path / "adc_data.bin"
    config = AdcParserConfig(frames=1, chirps=2, rx=1, samples=4)
    _write_synthetic_adc(path, config)

    res = runner.invoke(app, [
        "adc", "inspect",
        "--bin", str(path),
        "--frames", "1",
        "--chirps", "2",
        "--rx", "1",
        "--samples", "4",
    ])
    assert res.exit_code == 0
    assert "ADC" in res.stdout
    assert "SHA256" in res.stdout or "sha256" in res.stdout.lower()
    assert "Layout assumption" in res.stdout
    assert "confirmed" in res.stdout.lower()


def test_cli_json_inspect_valid(tmp_path):
    """CLI JSON inspection is valid JSON and includes layout_assumption_confirmed."""
    path = tmp_path / "adc_data.bin"
    config = AdcParserConfig(frames=1, chirps=1, rx=1, samples=2)
    _write_synthetic_adc(path, config)

    res = runner.invoke(app, [
        "adc", "inspect",
        "--bin", str(path),
        "--frames", "1",
        "--chirps", "1",
        "--rx", "1",
        "--samples", "2",
        "--format", "json",
    ])
    assert res.exit_code == 0
    data = json.loads(res.stdout)
    assert data["layout_assumption_confirmed"] is False
    assert "first_16_int16_values" in data
    assert "first_8_complex_values" in data
    assert data["error"] is None


def test_cli_rejects_wrong_size(tmp_path):
    """CLI rejects wrong-size file with clear message."""
    path = tmp_path / "adc_data.bin"
    path.write_bytes(b"\x00" * 100)

    res = runner.invoke(app, [
        "adc", "inspect",
        "--bin", str(path),
    ])
    assert res.exit_code == 1
    assert "mismatch" in res.stdout.lower() or "error" in res.stdout.lower()
