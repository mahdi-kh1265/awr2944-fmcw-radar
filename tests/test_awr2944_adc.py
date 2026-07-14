"""Regression tests for AWR2944 real-format two-lane ADC parser.

All tests use synthetic data.  No real captures required.
"""

from pathlib import Path

import numpy as np
import pytest

from awr2944_dca.awr2944_adc import (
    AWR2944AdcLayout,
    DEFAULT_LAYOUT,
    active_payload_bytes,
    depad_dca_2lane,
    expected_raw_dca_bytes,
    inactive_slot_stats,
    inspect_awr2944,
    parse_awr2944_real,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_dca_raw(
    active_i16: np.ndarray,
    slot2_fill: int = -1,
    slot3_fill: int | None = None,
    slot3_garbage: np.ndarray | None = None,
) -> np.ndarray:
    """Build a DCA 4-word-slot raw stream from active (2-lane) data.

    At each clock, DCA stores [slot0, slot1, slot2, slot3].
    active_i16 has 2 values per clock (lanes 0 and 1).
    """
    assert active_i16.size % 2 == 0, "active must have even length"
    n_clocks = active_i16.size // 2
    groups = active_i16.reshape(n_clocks, 2)

    raw = np.empty((n_clocks, 4), dtype=np.int16)
    raw[:, 0] = groups[:, 0]
    raw[:, 1] = groups[:, 1]
    raw[:, 2] = slot2_fill

    if slot3_garbage is not None:
        assert slot3_garbage.size == n_clocks
        raw[:, 3] = slot3_garbage
    elif slot3_fill is not None:
        raw[:, 3] = slot3_fill
    else:
        raw[:, 3] = -1

    return raw.reshape(-1)


def _write_dca_file(
    path: Path,
    frames: int,
    chirps: int,
    rx: int,
    samples: int,
    pattern: str = "sequential",
) -> np.ndarray:
    """Write a synthetic DCA raw file and return the expected active data."""
    n_active = frames * chirps * rx * samples
    if pattern == "sequential":
        active = np.arange(n_active, dtype=np.int16)
    elif pattern == "random":
        rng = np.random.default_rng(42)
        active = rng.integers(-10000, 10000, size=n_active, dtype=np.int16)
    else:
        active = np.zeros(n_active, dtype=np.int16)

    raw = _make_dca_raw(active)
    raw.tofile(path)
    return active


# ---------------------------------------------------------------------------
# 1. Synthetic two-active-lane/four-slot depadding
# ---------------------------------------------------------------------------

class TestDepadding:
    def test_basic_depad_roundtrip(self):
        """Construct known data, embed in 4-word DCA frame, verify round-trip."""
        active = np.array([10, 20, 30, 40, 50, 60], dtype=np.int16)
        raw = _make_dca_raw(active)
        assert raw.size == 12  # 3 clocks × 4 slots
        result = depad_dca_2lane(raw)
        np.testing.assert_array_equal(result, active)

    def test_depad_large(self):
        """Round-trip with 560-sample realistic data."""
        n = 4 * 560  # 4 RX × 560 samples = one chirp
        active = np.arange(n, dtype=np.int16)
        raw = _make_dca_raw(active)
        result = depad_dca_2lane(raw)
        np.testing.assert_array_equal(result, active)

    def test_depad_rejects_non_divisible(self):
        """File not divisible by dca_word_slots raises ValueError."""
        bad = np.zeros(7, dtype=np.int16)
        with pytest.raises(ValueError, match="not divisible"):
            depad_dca_2lane(bad)


# ---------------------------------------------------------------------------
# 2. Clock-order preservation
# ---------------------------------------------------------------------------

class TestClockOrder:
    def test_clock_order_preserved(self):
        """groups[:, [0,1]].reshape(-1) preserves L0,L1 interleaving."""
        # Clock 0: L0=100, L1=200
        # Clock 1: L0=300, L1=400
        active = np.array([100, 200, 300, 400], dtype=np.int16)
        raw = _make_dca_raw(active)
        # raw is [100, 200, -1, -1, 300, 400, -1, -1]
        result = depad_dca_2lane(raw)
        expected = np.array([100, 200, 300, 400], dtype=np.int16)
        np.testing.assert_array_equal(result, expected)

    def test_not_lane_concatenated(self):
        """Depad must NOT produce all-L0 then all-L1 (lane concatenation)."""
        active = np.array([100, 200, 300, 400], dtype=np.int16)
        raw = _make_dca_raw(active)
        result = depad_dca_2lane(raw)
        # Lane-concat would be [100, 300, 200, 400] — wrong
        wrong_concat = np.array([100, 300, 200, 400], dtype=np.int16)
        assert not np.array_equal(result, wrong_concat)


# ---------------------------------------------------------------------------
# 3. Four sequential RX blocks
# ---------------------------------------------------------------------------

class TestRXBlocks:
    def test_sequential_rx_blocks(self):
        """After depadding, contiguous sample-chunks map to sequential RX."""
        frames, chirps, rx, samples = 1, 1, 4, 8
        # RX0=[0..7], RX1=[8..15], RX2=[16..23], RX3=[24..31]
        active = np.arange(frames * chirps * rx * samples, dtype=np.int16)
        raw = _make_dca_raw(active)
        cube = depad_dca_2lane(raw).reshape(frames, chirps, rx, samples)
        for r in range(rx):
            expected_start = r * samples
            np.testing.assert_array_equal(
                cube[0, 0, r, :],
                np.arange(expected_start, expected_start + samples,
                          dtype=np.int16),
            )

    def test_multi_chirp_rx_continuity(self):
        """RX blocks repeat correctly across chirps."""
        frames, chirps, rx, samples = 1, 3, 4, 4
        active = np.arange(frames * chirps * rx * samples, dtype=np.int16)
        raw = _make_dca_raw(active)
        cube = depad_dca_2lane(raw).reshape(frames, chirps, rx, samples)
        # Chirp 1, RX2 should start at 1*4*4 + 2*4 = 24
        np.testing.assert_array_equal(
            cube[0, 1, 2, :],
            np.array([24, 25, 26, 27], dtype=np.int16),
        )


# ---------------------------------------------------------------------------
# 4. Inactive-slot garbage not mistaken for ADC
# ---------------------------------------------------------------------------

class TestInactiveSlotGarbage:
    def test_garbage_in_slot3_not_in_active(self):
        """Non-0xFFFF garbage in slots 2/3 must not appear in active data."""
        active = np.array([10, 20, 30, 40], dtype=np.int16)
        garbage = np.array([9999, 8888], dtype=np.int16)
        raw = _make_dca_raw(active, slot3_garbage=garbage)
        result = depad_dca_2lane(raw)
        np.testing.assert_array_equal(result, active)
        assert 9999 not in result
        assert 8888 not in result

    def test_inactive_stats_reports_garbage(self):
        """inactive_slot_stats correctly reports non-0xFFFF values."""
        active = np.array([10, 20, 30, 40], dtype=np.int16)
        garbage = np.array([9999, -5], dtype=np.int16)
        raw = _make_dca_raw(active, slot3_garbage=garbage)
        stats = inactive_slot_stats(raw)
        assert "slot_2" in stats
        assert "slot_3" in stats
        assert stats["slot_2"]["pct_0xFFFF"] == 100.0
        assert stats["slot_3"]["n_other"] == 2
        assert stats["slot_3"]["pct_0xFFFF"] == 0.0


# ---------------------------------------------------------------------------
# 5. TI sample file dimensions
# ---------------------------------------------------------------------------

class TestTISampleDimensions:
    def test_ti_sample_raw_size(self):
        """TI sample: 8,601,600 bytes raw → [20,48,4,560]."""
        expected_raw = expected_raw_dca_bytes(20, 48, 4, 560)
        assert expected_raw == 8_601_600

    def test_ti_sample_active_size(self):
        expected_active = active_payload_bytes(20, 48, 4, 560)
        assert expected_active == 4_300_800

    def test_ti_sample_parse(self, tmp_path):
        """Full round-trip at TI sample dimensions."""
        path = tmp_path / "ti_sample.bin"
        active = _write_dca_file(path, 20, 48, 4, 560, pattern="random")
        cube = parse_awr2944_real(path, 20, 48, 4, 560)
        assert cube.shape == (20, 48, 4, 560)
        assert cube.dtype == np.int16
        np.testing.assert_array_equal(
            cube.reshape(-1), active,
        )


# ---------------------------------------------------------------------------
# 6. smoke_v1 expected raw and depadded sizes
# ---------------------------------------------------------------------------

class TestSmokeV1Sizes:
    def test_smoke_active_payload(self):
        """smoke_v1: 8×128×4×256×2 = 2,097,152 bytes."""
        assert active_payload_bytes(8, 128, 4, 256) == 2_097_152

    def test_smoke_raw_dca(self):
        """smoke_v1: 2,097,152 × 4/2 = 4,194,304 bytes."""
        assert expected_raw_dca_bytes(8, 128, 4, 256) == 4_194_304

    def test_smoke_parse(self, tmp_path):
        """Full round-trip at smoke_v1 dimensions."""
        path = tmp_path / "smoke.bin"
        active = _write_dca_file(path, 8, 128, 4, 256, pattern="random")
        cube = parse_awr2944_real(path, 8, 128, 4, 256)
        assert cube.shape == (8, 128, 4, 256)
        assert cube.dtype == np.int16
        np.testing.assert_array_equal(cube.reshape(-1), active)


# ---------------------------------------------------------------------------
# 7. No complex/IQ interpretation for AWR2944
# ---------------------------------------------------------------------------

class TestNoComplexInterpretation:
    def test_parser_returns_real_int16(self, tmp_path):
        """parse_awr2944_real returns int16, not complex64."""
        path = tmp_path / "real_test.bin"
        _write_dca_file(path, 1, 2, 4, 8)
        cube = parse_awr2944_real(path, 1, 2, 4, 8)
        assert cube.dtype == np.int16
        assert not np.iscomplexobj(cube)

    def test_layout_says_real(self):
        """Layout metadata explicitly states real_int16."""
        assert DEFAULT_LAYOUT.sample_format == "real_int16"
        assert DEFAULT_LAYOUT.device == "AWR2944"


# ---------------------------------------------------------------------------
# 8. Old parser cannot silently accept AWR2944 raw as complex
# ---------------------------------------------------------------------------

class TestOldParserGuard:
    def test_old_parser_size_mismatch_on_awr2944_raw(self, tmp_path):
        """parse_complex_int16 should reject AWR2944 DCA raw by size."""
        from awr2944_dca.adc_parser import AdcParserConfig, parse_complex_int16

        path = tmp_path / "awr2944.bin"
        # Write a TI-sample-sized file (8,601,600 bytes)
        data = np.zeros(8_601_600 // 2, dtype=np.int16)
        data.tofile(path)
        # Default smoke config expects 4,194,304 bytes
        with pytest.raises(ValueError, match="size mismatch"):
            parse_complex_int16(path)

    def test_old_parser_wrong_interpretation_on_smoke_size(self, tmp_path):
        """Even if sizes match, complex parse of DCA raw is wrong:
        the old parser treats it as [I,Q,I,Q,...] which is incorrect
        for AWR2944 real + DCA 4-slot data."""
        # This test documents that the old parser WOULD accept a
        # 4,194,304-byte file without error, but the result is
        # meaningless for AWR2944.  The guard must come from metadata.
        from awr2944_dca.adc_parser import AdcParserConfig, parse_complex_int16

        path = tmp_path / "ambiguous.bin"
        data = np.zeros(4_194_304 // 2, dtype=np.int16)
        data.tofile(path)
        # Old parser accepts this size — documents the metadata-guard need
        cube = parse_complex_int16(path)
        assert cube.shape == (8, 128, 4, 256)
        assert cube.dtype == np.complex64
        # But interpretation is wrong — all zeros so we can't detect it
        # from data alone.  Guard must be metadata-based.


# ---------------------------------------------------------------------------
# 9. File-size divisibility
# ---------------------------------------------------------------------------

class TestFileSizeDivisibility:
    def test_reject_not_divisible_by_8(self, tmp_path):
        """Raw file not divisible by 8 bytes (4 slots × 2 bytes) is rejected."""
        path = tmp_path / "bad.bin"
        # 10 bytes = 5 int16, not divisible by 4 slots
        np.zeros(5, dtype=np.int16).tofile(path)
        with pytest.raises(ValueError):
            parse_awr2944_real(path, 1, 1, 1, 1)

    def test_reject_odd_bytes(self, tmp_path):
        """Odd byte count is rejected."""
        path = tmp_path / "odd.bin"
        path.write_bytes(b"\x00" * 9)
        with pytest.raises(ValueError):
            parse_awr2944_real(path, 1, 1, 1, 1)


# ---------------------------------------------------------------------------
# 10. Incompatible layout refused
# ---------------------------------------------------------------------------

class TestIncompatibleLayout:
    def test_wrong_slot_count_raises(self, tmp_path):
        """A layout with 3 slots on 2-lane 4-slot data raises."""
        path = tmp_path / "test.bin"
        _write_dca_file(path, 1, 1, 4, 8)
        weird_layout = AWR2944AdcLayout(
            dca_word_slots=3,
            active_slot_indices=(0, 1),
        )
        with pytest.raises(ValueError):
            parse_awr2944_real(path, 1, 1, 4, 8, layout=weird_layout)

    def test_size_mismatch_raises(self, tmp_path):
        """Wrong dimensions for file size raises ValueError."""
        path = tmp_path / "test.bin"
        _write_dca_file(path, 1, 1, 4, 8)
        with pytest.raises(ValueError, match="size mismatch"):
            parse_awr2944_real(path, 2, 1, 4, 8)  # wrong frame count


# ---------------------------------------------------------------------------
# Layout metadata
# ---------------------------------------------------------------------------

class TestLayoutMetadata:
    def test_default_layout_fields(self):
        layout = DEFAULT_LAYOUT
        assert layout.device == "AWR2944"
        assert layout.sample_format == "real_int16"
        assert layout.byte_order == "little"
        assert layout.physical_lvds_lanes == 2
        assert layout.dca_word_slots == 4
        assert layout.active_slot_indices == (0, 1)
        assert layout.rx_order == "cbuff_sequential"
        assert layout.cube_layout == "frame_chirp_rx_sample"
        assert layout.layout_version == "awr2944_real_2lane_dca4slot_v1"

    def test_layout_is_frozen(self):
        with pytest.raises(AttributeError):
            DEFAULT_LAYOUT.device = "other"


# ---------------------------------------------------------------------------
# Inspect function
# ---------------------------------------------------------------------------

class TestInspect:
    def test_inspect_returns_per_rx(self, tmp_path):
        path = tmp_path / "test.bin"
        _write_dca_file(path, 2, 4, 4, 16, pattern="random")
        result = inspect_awr2944(path, 2, 4, 4, 16)
        assert result["error"] is None
        assert result["compatibility"] == "OK"
        assert result["shape"] == [2, 4, 4, 16]
        assert "RX0" in result["per_rx_stats"]
        assert "sha256" in result

    def test_inspect_missing_file(self, tmp_path):
        result = inspect_awr2944(tmp_path / "nope.bin", 1, 1, 1, 1)
        assert result["error"] is not None
