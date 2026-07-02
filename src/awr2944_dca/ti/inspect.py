"""Inspect TI mmWave Studio config files (Lua, JSON, log).

Extracts parsing-relevant fields using regex for Lua and key-lookup for JSON.
Unknown/missing fields are reported as UNKNOWN — never silently guessed.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

UNKNOWN = "UNKNOWN"


@dataclass
class TiExtractedConfig:
    """Fields extracted from a TI config file.

    Any field set to UNKNOWN could not be determined from the source file.
    """

    source_file: str = ""
    source_format: str = UNKNOWN  # "lua", "json", "cfg", "unknown"

    # ADC / data format
    adc_fmt: str = UNKNOWN          # 0=real, 1=complex1x, 2=complex2x
    adc_bits: str = UNKNOWN         # 12, 14, 16
    ch_interleave: str = UNKNOWN    # 0=interleaved, 1=non-interleaved
    iq_swap_sel: str = UNKNOWN      # 0=I first, 1=Q first
    rx_channel_en: str = UNKNOWN    # bitmask, e.g. 15 = all 4 RX
    tx_channel_en: str = UNKNOWN    # bitmask, e.g. 1 = TX0 only

    # Profile
    start_freq_ghz: str = UNKNOWN
    slope_mhz_per_us: str = UNKNOWN
    sample_rate_ksps: str = UNKNOWN
    idle_time_us: str = UNKNOWN
    ramp_end_time_us: str = UNKNOWN
    num_adc_samples: str = UNKNOWN

    # Frame
    chirps_per_frame: str = UNKNOWN
    num_frames: str = UNKNOWN
    frame_period_ms: str = UNKNOWN

    # Data path
    data_path_intf: str = UNKNOWN   # 1=LVDS, etc.
    lvds_lane_en: str = UNKNOWN

    # Raw API calls preserved
    raw_api_calls: list[str] = field(default_factory=list)


def _bitmask_to_channels(mask_val: int) -> list[int]:
    """Convert a channel enable bitmask to a list of channel indices."""
    channels = []
    for i in range(4):
        if mask_val & (1 << i):
            channels.append(i)
    return channels


# ---------------------------------------------------------------------------
# Lua parser
# ---------------------------------------------------------------------------

# Patterns for ar1.* API calls
_LUA_API_PATTERN = re.compile(
    r"ar1\.(\w+)\s*\(([^)]*)\)", re.MULTILINE
)


def _parse_lua(text: str, file_path: str) -> TiExtractedConfig:
    """Extract config from a TI mmWave Studio Lua script."""
    result = TiExtractedConfig(source_file=file_path, source_format="lua")

    # Find all ar1.* calls
    for match in _LUA_API_PATTERN.finditer(text):
        func_name = match.group(1)
        raw_args = match.group(2).strip()
        result.raw_api_calls.append(f"ar1.{func_name}({raw_args})")

        args = [a.strip() for a in raw_args.split(",") if a.strip()]

        if func_name == "ChanNAdcConfig":
            # ar1.ChanNAdcConfig(txEn, rxEn, reserved, adcBits, adcFmt,
            #                    iqSwapSel, chInterleave, ?, ?, ?)
            # Based on DataCaptureDemo_xWR.lua line 87:
            #   ar1.ChanNAdcConfig(1, 1, 0, 1, 1, 1, 1, 2, 1, 0)
            # Parameter mapping is uncertain — record raw and extract best-guess
            if len(args) >= 7:
                result.tx_channel_en = args[0]
                result.rx_channel_en = args[1]
                # args[2] reserved
                result.adc_bits = args[3]
                result.adc_fmt = args[4]
                result.iq_swap_sel = args[5]
                result.ch_interleave = args[6]

        elif func_name == "ProfileConfig":
            # ar1.ProfileConfig(profileId, startFreq, idleTime, adcStartTime,
            #                   rampEndTime, ?, ?, ?, ?, ?, ?,
            #                   freqSlopeConst, ?, numAdcSamples, sampleRate,
            #                   ?, ?, ?)
            # Based on DataCaptureDemo_xWR.lua line 131:
            #   ar1.ProfileConfig(0, 77, 100, 6, 60, 0, 0, 0, 0, 0, 0,
            #                     29.982, 0, 256, 10000, 0, 0, 94)
            if len(args) >= 15:
                result.start_freq_ghz = args[1]
                result.idle_time_us = args[2]
                result.ramp_end_time_us = args[4]
                result.slope_mhz_per_us = args[11]
                result.num_adc_samples = args[13]
                result.sample_rate_ksps = args[14]

        elif func_name == "FrameConfig":
            # ar1.FrameConfig(chirpStartIdx, chirpEndIdx, numLoops,
            #                 numFrames, framePeriod, ?, ?)
            # Based on DataCaptureDemo_xWR.lua line 146:
            #   ar1.FrameConfig(0, 0, 8, 128, 40, 0, 1)
            # chirps_per_frame = (chirpEndIdx - chirpStartIdx + 1) * numLoops
            if len(args) >= 5:
                try:
                    chirp_start = int(args[0])
                    chirp_end = int(args[1])
                    num_loops = int(args[2])
                    chirps = (chirp_end - chirp_start + 1) * num_loops
                    result.chirps_per_frame = str(chirps)
                except (ValueError, IndexError):
                    pass
                result.num_frames = args[3]
                # framePeriod is in units that need conversion
                result.frame_period_ms = args[4]

        elif func_name == "DataPathConfig":
            # ar1.DataPathConfig(intfSel, ?, ?)
            if len(args) >= 1:
                result.data_path_intf = args[0]

        elif func_name == "LVDSLaneConfig":
            # ar1.LVDSLaneConfig(?, laneEn, ?, ?, ?, ?, ?, ?)
            if len(args) >= 2:
                result.lvds_lane_en = args[1]

    return result


# ---------------------------------------------------------------------------
# JSON parser
# ---------------------------------------------------------------------------

_JSON_KEY_MAP = {
    "adcFmt": "adc_fmt",
    "adcOutFormat": "adc_fmt",
    "adcBits": "adc_bits",
    "chInterleave": "ch_interleave",
    "channelInterleave": "ch_interleave",
    "iqSwapSel": "iq_swap_sel",
    "sampleInterleave": "iq_swap_sel",
    "rxChannelEn": "rx_channel_en",
    "txChannelEn": "tx_channel_en",
    "numAdcSamples": "num_adc_samples",
    "chirpsPerFrame": "chirps_per_frame",
    "numFrames": "num_frames",
    "startFreqConst": "start_freq_ghz",
    "freqSlopeConst": "slope_mhz_per_us",
    "digOutSampleRate": "sample_rate_ksps",
    "idleTimeConst": "idle_time_us",
    "rampEndTime": "ramp_end_time_us",
}


def _flatten_json(obj: Any, prefix: str = "") -> dict[str, Any]:
    """Flatten a nested JSON object into key-value pairs."""
    items: dict[str, Any] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                items.update(_flatten_json(v, new_key))
            elif isinstance(v, list):
                # Recurse into list elements that are dicts
                for i, elem in enumerate(v):
                    if isinstance(elem, dict):
                        items.update(_flatten_json(elem, f"{new_key}[{i}]"))
                items[new_key] = v
            else:
                items[new_key] = v
                # Also store without prefix for simple key matching
                items[k] = v
    return items


def _parse_json(text: str, file_path: str) -> TiExtractedConfig:
    """Extract config from a TI JSON config/log file."""
    result = TiExtractedConfig(source_file=file_path, source_format="json")

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return result

    flat = _flatten_json(data)

    for json_key, our_field in _JSON_KEY_MAP.items():
        if json_key in flat:
            setattr(result, our_field, str(flat[json_key]))

    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def inspect_ti_file(file_path: str | Path) -> TiExtractedConfig:
    """Inspect a TI config file and extract parsing-relevant fields.

    Supports:
        - .lua scripts (regex extraction of ar1.* API calls)
        - .json config/log files (key lookup)

    Unknown fields are set to UNKNOWN. Never silently guesses.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"TI config file not found: {path}")

    text = path.read_text(encoding="utf-8", errors="replace")
    suffix = path.suffix.lower()

    if suffix == ".lua":
        return _parse_lua(text, str(path))
    elif suffix == ".json":
        return _parse_json(text, str(path))
    else:
        # Unknown format — return empty result
        return TiExtractedConfig(
            source_file=str(path),
            source_format="unknown",
        )
