"""Config presets for AWR2944 + DCA1000 experiments.

Each preset is a plain Python dict matching the RadarConfig schema.
All default to: real ADC, 16-bit, channel_interleave=1,
layout=awr2944_real_2lane_noninterleaved_candidate.

TDM-MIMO presets (corner-reflector, walking-person) are marked
experimental — virtual antenna ordering is NOT validated.
"""

from __future__ import annotations

import copy
from typing import Any

# ---------------------------------------------------------------------------
# Common AWR2944 defaults
# ---------------------------------------------------------------------------

_AWR2944_DEFAULTS: dict[str, Any] = {
    "rig": {
        "name": "awr2944-dca1000",
        "radar": "AWR2944EVM",
        "capture_card": "DCA1000EVM",
    },
    "adc": {
        "samples_per_chirp": 256,
        "bits": 16,
        "is_complex": False,
        "iq_order": "IQ",
        "num_lvds_lanes": 2,
        "channel_interleave": 1,
        "layout": "awr2944_real_2lane_noninterleaved_candidate",
    },
    "profile": {
        "start_freq_ghz": 77.0,
        "slope_mhz_per_us": 60.0,
        "sample_rate_ksps": 10000.0,
        "idle_time_us": 10.0,
        "ramp_end_time_us": 60.0,
    },
    "capture": {
        "output_root": "experiments",
        "packet_delay_us": 25,
        "save_raw_packets": True,
        "raw_files": [],
        "adc_file": "raw/adc_data.bin",
    },
}


def _merge(base: dict, overlay: dict) -> dict:
    """Deep merge overlay into a copy of base."""
    result = copy.deepcopy(base)
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _merge(result[k], v)
        else:
            result[k] = copy.deepcopy(v)
    return result


# ---------------------------------------------------------------------------
# Preset definitions
# ---------------------------------------------------------------------------

PRESETS: dict[str, dict[str, Any]] = {
    "first-capture": _merge(_AWR2944_DEFAULTS, {
        "experiment": {
            "name": "first_capture",
            "operator": "",
            "description": "First AWR2944 + DCA1000 raw ADC capture. Conservative settings.",
        },
        "hardware": {
            "tx_enabled": [0],
            "rx_enabled": [0, 1, 2, 3],
            "antenna_mode": "single_tx",
        },
        "frame": {
            "chirps_per_frame": 128,
            "num_frames": 10,
            "frame_period_ms": 50.0,
        },
    }),

    "parser-validation": _merge(_AWR2944_DEFAULTS, {
        "experiment": {
            "name": "parser_validation",
            "operator": "",
            "description": (
                "Small capture for parser validation. "
                "Use with 'awr compare-layouts' to verify binary layout."
            ),
        },
        "hardware": {
            "tx_enabled": [0],
            "rx_enabled": [0, 1, 2, 3],
            "antenna_mode": "single_tx",
        },
        "adc": {
            "samples_per_chirp": 64,
        },
        "frame": {
            "chirps_per_frame": 32,
            "num_frames": 4,
            "frame_period_ms": 50.0,
        },
    }),

    "corner-reflector": _merge(_AWR2944_DEFAULTS, {
        "experiment": {
            "name": "corner_reflector",
            "operator": "",
            "description": (
                "Corner reflector calibration. "
                "EXPERIMENTAL: TDM-MIMO virtual antenna ordering is NOT validated."
            ),
            "notes": "TDM-MIMO preset — virtual antenna ordering unvalidated.",
        },
        "hardware": {
            "tx_enabled": [0, 1, 2, 3],
            "rx_enabled": [0, 1, 2, 3],
            "antenna_mode": "tdm_mimo",
        },
        "calibration_target": {
            "type": "corner_reflector",
            "range_m": 2.0,
            "azimuth_deg": 0.0,
            "elevation_deg": 0.0,
        },
        "frame": {
            "chirps_per_frame": 128,
            "num_frames": 50,
            "frame_period_ms": 50.0,
        },
    }),

    "walking-person": _merge(_AWR2944_DEFAULTS, {
        "experiment": {
            "name": "walking_person",
            "operator": "",
            "description": (
                "Person walking 1-5 m in front of radar. "
                "EXPERIMENTAL: TDM-MIMO virtual antenna ordering is NOT validated."
            ),
            "notes": "TDM-MIMO preset — virtual antenna ordering unvalidated.",
        },
        "hardware": {
            "tx_enabled": [0, 1, 2, 3],
            "rx_enabled": [0, 1, 2, 3],
            "antenna_mode": "tdm_mimo",
        },
        "frame": {
            "chirps_per_frame": 128,
            "num_frames": 200,
            "frame_period_ms": 50.0,
        },
    }),
}


def get_preset(name: str) -> dict[str, Any]:
    """Return a deep copy of the named preset dict.

    Raises KeyError if the preset name is not recognized.
    """
    if name not in PRESETS:
        raise KeyError(
            f"Unknown preset '{name}'. Available: {list(PRESETS.keys())}"
        )
    return copy.deepcopy(PRESETS[name])


def list_presets() -> list[str]:
    """Return the list of available preset names."""
    return list(PRESETS.keys())
