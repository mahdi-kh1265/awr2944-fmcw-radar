"""AWR2944 real-format two-lane ADC parser.

Parses DCA1000 raw captures from the AWR2944 radar into real int16 cubes.

The AWR2944 outputs Real int16 ADC data (not complex I/Q) over 2 physical
LVDS data lanes.  The DCA1000 in lvdsMode=1 captures 4 int16 words per LVDS
clock (4-slot mode), but only slots 0 and 1 carry active data.  Slots 2 and 3
are inactive-lane filler (stale register values, predominantly 0xFFFF) and
must be discarded.

The accepted canonical capture (9-frame guard, 8-frame canonical prefix)
was received with zero packet gaps, zero byte-counter gaps, and no
terminal shortfall.  The guard-frame strategy is recommended but terminal
data loss is not inevitable when the capture parameters and receiver are
correctly configured.

Decode pipeline:
    Raw file (N bytes, N divisible by 8)
      |  groups = raw_i16.reshape(-1, 4)
      |  active = groups[:, [0, 1]].reshape(-1)
      v
    Active int16 stream (N/2 int16)
      |  cube = active.reshape(frames, chirps, rx, samples)
      v
    Real int16 cube [F, C, R, S]

Per chirp, CBUFF iterates active RX channels sequentially
(CBUFF_setupNonInterleaved_ADC, cbuff_transfer.c L639-705).  Each RX
block is striped across L0/L1 simultaneously.  After clock-order
depadding, sequential chunks of ``samples`` values correspond to
RX0, RX1, RX2, RX3.

Source citations:
    adcCfg 2 0          → Real, 16-bit          (rl_sensor.h L348-378)
    adcbufCfg -1 1 1 1  → adcFmt=1(Real)        (mss_main.c L2154 assertion)
    lvdsLaneEnable=0x3  → 2 lanes               (mmw_lvds_stream.c L232)
    CBUFF_DataType_REAL  → adcTransferSize=N     (cbuff.c L1930-1933)
    EDMA aCnt=2*N bytes  → 560 int16/RX/chirp    (cbuff_edma.c L229)
    profileCfg argv[10]  → authoritative samples (cli_mmwave.c L751)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import numpy as np


# ---------------------------------------------------------------------------
# Layout metadata
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AWR2944AdcLayout:
    """Describes the AWR2944 DCA1000 raw-file layout."""

    device: str = "AWR2944"
    sample_format: str = "real_int16"
    byte_order: str = "little"
    physical_lvds_lanes: int = 2
    dca_word_slots: int = 4
    active_slot_indices: tuple[int, ...] = (0, 1)
    rx_order: str = "cbuff_sequential"
    cube_layout: str = "frame_chirp_rx_sample"
    layout_version: str = "awr2944_real_2lane_dca4slot_v1"


DEFAULT_LAYOUT = AWR2944AdcLayout()


# ---------------------------------------------------------------------------
# Size calculation
# ---------------------------------------------------------------------------

def active_payload_bytes(
    frames: int, chirps: int, rx: int, samples: int,
) -> int:
    """Return active ADC payload size in bytes.

    ``frames × chirps × rx × samples × 2``
    """
    return frames * chirps * rx * samples * 2


def expected_raw_dca_bytes(
    frames: int, chirps: int, rx: int, samples: int,
    layout: AWR2944AdcLayout | None = None,
) -> int:
    """Return expected DCA raw file size in bytes.

    ``active_payload_bytes × dca_word_slots / physical_lvds_lanes``
    """
    if layout is None:
        layout = DEFAULT_LAYOUT
    apb = active_payload_bytes(frames, chirps, rx, samples)
    return apb * layout.dca_word_slots // layout.physical_lvds_lanes


# ---------------------------------------------------------------------------
# Depadding
# ---------------------------------------------------------------------------

def depad_dca_2lane(
    raw_i16: np.ndarray,
    layout: AWR2944AdcLayout | None = None,
) -> np.ndarray:
    """Extract active-lane data from a DCA 4-word-slot raw capture.

    Preserves clock ordering:  at each LVDS clock the DCA stores
    ``[slot0, slot1, slot2, slot3]``.  Only ``slot0`` and ``slot1``
    carry data from the two active lanes.

    Parameters
    ----------
    raw_i16 : ndarray of int16
        Flat array loaded from the DCA raw file.
    layout : AWR2944AdcLayout, optional
        Layout descriptor (default: 2-lane, 4-slot).

    Returns
    -------
    ndarray of int16
        Active data with inactive slots removed.  Length = len(raw_i16) / 2.

    Raises
    ------
    ValueError
        If ``raw_i16`` length is not divisible by ``dca_word_slots``.
    """
    if layout is None:
        layout = DEFAULT_LAYOUT

    if raw_i16.size % layout.dca_word_slots != 0:
        raise ValueError(
            f"Raw int16 count {raw_i16.size} is not divisible by "
            f"dca_word_slots={layout.dca_word_slots}. "
            f"Cannot depad."
        )

    groups = raw_i16.reshape(-1, layout.dca_word_slots)
    active = groups[:, list(layout.active_slot_indices)].reshape(-1)
    return active


def inactive_slot_stats(
    raw_i16: np.ndarray,
    layout: AWR2944AdcLayout | None = None,
) -> dict[str, Any]:
    """Characterize the inactive DCA slots.

    Reports per-slot statistics for slots not in ``active_slot_indices``.
    These contain stale LVDS register values / filler since
    ``lvdsLaneEnable=0x3`` only activates lanes 0 and 1.

    Returns a dict with per-slot entries.
    """
    if layout is None:
        layout = DEFAULT_LAYOUT

    if raw_i16.size % layout.dca_word_slots != 0:
        raise ValueError(
            f"Raw int16 count {raw_i16.size} is not divisible by "
            f"dca_word_slots={layout.dca_word_slots}."
        )

    active_set = set(layout.active_slot_indices)
    stats: dict[str, Any] = {}

    for slot_idx in range(layout.dca_word_slots):
        if slot_idx in active_set:
            continue

        slot_data = raw_i16[slot_idx :: layout.dca_word_slots]
        total = int(slot_data.size)
        n_ffff = int(np.sum(slot_data == -1))
        n_other = total - n_ffff
        non_ff = slot_data[slot_data != -1]

        slot_info: dict[str, Any] = {
            "total": total,
            "n_0xFFFF": n_ffff,
            "pct_0xFFFF": round(n_ffff / total * 100, 2) if total > 0 else 0.0,
            "n_other": n_other,
            "description": (
                "inactive-lane filler/stale values, discarded "
                "because lvdsLaneEnable=0x3"
            ),
        }
        if n_other > 0:
            vals, counts = np.unique(non_ff, return_counts=True)
            top_k = min(5, len(vals))
            top_indices = np.argsort(counts)[::-1][:top_k]
            slot_info["non_0xFFFF_min"] = int(np.min(non_ff))
            slot_info["non_0xFFFF_max"] = int(np.max(non_ff))
            slot_info["non_0xFFFF_mean"] = round(float(np.mean(non_ff)), 2)
            slot_info["top_values"] = [
                {"value": int(vals[i]), "count": int(counts[i])}
                for i in top_indices
            ]
        stats[f"slot_{slot_idx}"] = slot_info

    return stats


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_awr2944_real(
    path: str | Path,
    frames: int,
    chirps: int,
    rx: int,
    samples: int,
    layout: AWR2944AdcLayout | None = None,
) -> np.ndarray:
    """Parse a DCA1000 raw file into a real int16 cube.

    Parameters
    ----------
    path : str or Path
        Path to the DCA raw binary file.
    frames, chirps, rx, samples : int
        Expected cube dimensions.
    layout : AWR2944AdcLayout, optional

    Returns
    -------
    ndarray of int16, shape (frames, chirps, rx, samples)

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If file size does not match expected, or if the data cannot
        reshape to the requested dimensions.
    """
    if layout is None:
        layout = DEFAULT_LAYOUT

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"ADC file not found: {path}")

    file_size = path.stat().st_size
    expected_raw = expected_raw_dca_bytes(frames, chirps, rx, samples, layout)

    if file_size != expected_raw:
        raise ValueError(
            f"Raw file size mismatch: got {file_size:,} bytes, "
            f"expected {expected_raw:,} bytes "
            f"({frames}F x {chirps}C x {rx}RX x {samples}S, "
            f"layout={layout.layout_version}). "
            f"File: {path}"
        )

    if file_size % 2 != 0:
        raise ValueError(
            f"Raw file has odd byte count ({file_size}), "
            f"not aligned to int16: {path}"
        )

    raw_i16 = np.fromfile(path, dtype="<i2")  # little-endian int16

    if raw_i16.size == 0:
        raise ValueError(f"ADC file is empty: {path}")

    active = depad_dca_2lane(raw_i16, layout)

    expected_active = frames * chirps * rx * samples
    if active.size != expected_active:
        raise ValueError(
            f"Depadded int16 count {active.size} does not match "
            f"expected {expected_active} "
            f"({frames}F x {chirps}C x {rx}RX x {samples}S)"
        )

    cube = active.reshape(frames, chirps, rx, samples)
    return cube


# ---------------------------------------------------------------------------
# Inspection
# ---------------------------------------------------------------------------

def inspect_awr2944(
    path: str | Path,
    frames: int,
    chirps: int,
    rx: int,
    samples: int,
    layout: AWR2944AdcLayout | None = None,
) -> dict[str, Any]:
    """Inspect a DCA1000 raw file and return structured metadata + statistics.

    Does NOT raise on errors — returns error info in the dict instead.
    """
    if layout is None:
        layout = DEFAULT_LAYOUT

    path = Path(path)
    result: dict[str, Any] = {
        "file_path": str(path.resolve()),
        "file_size": 0,
        "expected_raw_bytes": expected_raw_dca_bytes(
            frames, chirps, rx, samples, layout
        ),
        "expected_active_bytes": active_payload_bytes(
            frames, chirps, rx, samples
        ),
        "layout": asdict(layout),
        "dimensions": {
            "frames": frames,
            "chirps": chirps,
            "rx": rx,
            "samples": samples,
        },
        "error": None,
    }

    if not path.exists():
        result["error"] = f"File not found: {path}"
        return result

    file_size = path.stat().st_size
    result["file_size"] = file_size

    # SHA256
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    result["sha256"] = sha.hexdigest()
    result["raw_size_match"] = file_size == result["expected_raw_bytes"]

    if file_size % 2 != 0:
        result["error"] = f"Odd byte count: {file_size}"
        return result

    raw_i16 = np.fromfile(path, dtype="<i2")

    if raw_i16.size == 0:
        result["error"] = "File is empty"
        return result

    # Inactive-slot stats
    try:
        result["inactive_slot_stats"] = inactive_slot_stats(raw_i16, layout)
    except ValueError as e:
        result["error"] = str(e)
        return result

    # Depad
    try:
        active = depad_dca_2lane(raw_i16, layout)
    except ValueError as e:
        result["error"] = str(e)
        return result

    result["depadded_int16_count"] = int(active.size)
    result["depadded_bytes"] = int(active.size * 2)

    # Try reshape
    expected_active = frames * chirps * rx * samples
    result["active_size_match"] = active.size == expected_active

    if active.size != expected_active:
        result["error"] = (
            f"Depadded size {active.size} != expected {expected_active}"
        )
        # Still report global stats
        result["global_min"] = int(np.min(active))
        result["global_max"] = int(np.max(active))
        result["global_rms"] = round(
            float(np.sqrt(np.mean(active.astype(np.float64) ** 2))), 2
        )
        return result

    cube = active.reshape(frames, chirps, rx, samples)
    result["shape"] = list(cube.shape)
    result["dtype"] = str(cube.dtype)

    # Per-RX stats
    per_rx = {}
    for r in range(rx):
        rd = cube[:, :, r, :].astype(np.float64)
        per_rx[f"RX{r}"] = {
            "rms": round(float(np.sqrt(np.mean(rd ** 2))), 2),
            "mean": round(float(np.mean(rd)), 2),
            "std": round(float(np.std(rd)), 2),
            "min": int(np.min(cube[:, :, r, :])),
            "max": int(np.max(cube[:, :, r, :])),
            "clip_pos_32767": int(np.sum(cube[:, :, r, :] == 32767)),
            "clip_neg_32768": int(np.sum(cube[:, :, r, :] == -32768)),
            "value_neg1": int(np.sum(cube[:, :, r, :] == -1)),
            "nonzero_pct": round(
                float(np.sum(cube[:, :, r, :] != 0)
                      / cube[:, :, r, :].size * 100), 2
            ),
        }
    result["per_rx_stats"] = per_rx
    result["compatibility"] = "OK"

    return result
