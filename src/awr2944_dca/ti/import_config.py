"""Import a TI config file into our capture.yaml format.

Conservative import: unknown fields are NOT silently guessed.
Missing fields use defaults and are marked as assumptions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from awr2944_dca.ti.inspect import UNKNOWN, TiExtractedConfig, inspect_ti_file


def _safe_int(val: str, default: int | None = None) -> int | None:
    """Convert string to int, returning default if UNKNOWN or invalid."""
    if val == UNKNOWN:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def _safe_float(val: str, default: float | None = None) -> float | None:
    """Convert string to float, returning default if UNKNOWN or invalid."""
    if val == UNKNOWN:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _rx_bitmask_to_list(mask_str: str) -> list[int] | None:
    """Convert RX channel enable bitmask string to list of channel indices."""
    val = _safe_int(mask_str)
    if val is None:
        return None
    channels = []
    for i in range(4):
        if val & (1 << i):
            channels.append(i)
    return channels


def _tx_bitmask_to_list(mask_str: str) -> list[int] | None:
    """Convert TX channel enable bitmask string to list of channel indices."""
    val = _safe_int(mask_str)
    if val is None:
        return None
    channels = []
    for i in range(4):
        if val & (1 << i):
            channels.append(i)
    return channels


def _adc_bits_lookup(val: str) -> int | None:
    """Convert TI adcBits field value to actual bit count.

    TI convention (from ChanNAdcConfig):
        0 = 12-bit, 1 = 14-bit, 2 = 16-bit
    But some JSON logs may store the actual bit count directly.
    """
    int_val = _safe_int(val)
    if int_val is None:
        return None
    if int_val in (12, 14, 16):
        return int_val
    # TI enum mapping
    mapping = {0: 12, 1: 14, 2: 16}
    return mapping.get(int_val)


def _adc_fmt_to_complex(val: str) -> bool | None:
    """Convert TI adcFmt to is_complex flag.

    TI convention: 0=real, 1=complex1x, 2=complex2x
    """
    int_val = _safe_int(val)
    if int_val is None:
        return None
    return int_val != 0



def import_ti_config(
    ti_file: str | Path,
    *,
    output_path: str | Path | None = None,
) -> tuple[dict[str, Any], list[str], list[str]]:
    """Import a TI config file into our capture.yaml format.

    Returns:
        (config_dict, assumptions, unknown_fields)
        - config_dict: dict suitable for RadarConfig.model_validate()
        - assumptions: list of fields where defaults were assumed
        - unknown_fields: list of fields that could not be extracted
    """
    extracted = inspect_ti_file(ti_file)

    assumptions: list[str] = []
    unknown_fields: list[str] = []

    # --- Build config dict ---
    config: dict[str, Any] = {
        "experiment": {
            "name": f"imported_from_{Path(ti_file).stem}",
            "operator": "",
            "description": f"Imported from TI file: {Path(ti_file).name}",
        },
        "rig": {
            "name": "awr2944-dca1000",
            "radar": "AWR2944EVM",
            "capture_card": "DCA1000EVM",
        },
    }

    # --- Hardware ---
    rx_list = _rx_bitmask_to_list(extracted.rx_channel_en)
    tx_list = _tx_bitmask_to_list(extracted.tx_channel_en)

    hw: dict[str, Any] = {}
    if tx_list is not None:
        hw["tx_enabled"] = tx_list
    else:
        hw["tx_enabled"] = [0]
        assumptions.append("tx_enabled: defaulted to [0] (TI field not found)")
        unknown_fields.append("tx_channel_en")

    if rx_list is not None:
        hw["rx_enabled"] = rx_list
    else:
        hw["rx_enabled"] = [0, 1, 2, 3]
        assumptions.append("rx_enabled: defaulted to [0,1,2,3] (TI field not found)")
        unknown_fields.append("rx_channel_en")

    # Antenna mode — guess from TX count
    if len(hw["tx_enabled"]) > 1:
        hw["antenna_mode"] = "tdm_mimo"
        assumptions.append("antenna_mode: assumed tdm_mimo from multiple TX channels")
    else:
        hw["antenna_mode"] = "single_tx"

    config["hardware"] = hw

    # --- ADC ---
    adc: dict[str, Any] = {}

    is_complex = _adc_fmt_to_complex(extracted.adc_fmt)
    if is_complex is not None:
        adc["is_complex"] = is_complex
    else:
        adc["is_complex"] = False
        assumptions.append("is_complex: defaulted to false (TI field not found)")
        unknown_fields.append("adc_fmt")

    bits = _adc_bits_lookup(extracted.adc_bits)
    if bits is not None:
        adc["bits"] = bits
    else:
        adc["bits"] = 16
        assumptions.append("bits: defaulted to 16 (TI field not found)")
        unknown_fields.append("adc_bits")

    samples = _safe_int(extracted.num_adc_samples)
    if samples is not None:
        adc["samples_per_chirp"] = samples
    else:
        adc["samples_per_chirp"] = 256
        assumptions.append("samples_per_chirp: defaulted to 256 (TI field not found)")
        unknown_fields.append("num_adc_samples")

    ch_interleave = _safe_int(extracted.ch_interleave)
    if ch_interleave is not None:
        adc["channel_interleave"] = ch_interleave
    else:
        adc["channel_interleave"] = 1
        assumptions.append("channel_interleave: defaulted to 1 (TI field not found)")
        unknown_fields.append("ch_interleave")

    adc["num_lvds_lanes"] = 2
    adc["iq_order"] = "IQ"

    # Set layout based on interleave
    ci = adc.get("channel_interleave", 1)
    if adc.get("is_complex", False):
        adc["layout"] = "xwr14xx_complex_4lane"
    elif ci == 0:
        adc["layout"] = "awr2944_real_2lane_interleaved_candidate"
    else:
        adc["layout"] = "awr2944_real_2lane_noninterleaved_candidate"

    config["adc"] = adc

    # --- Profile ---
    profile: dict[str, Any] = {}

    start_freq = _safe_float(extracted.start_freq_ghz)
    if start_freq is not None:
        profile["start_freq_ghz"] = start_freq
    else:
        profile["start_freq_ghz"] = 77.0
        assumptions.append("start_freq_ghz: defaulted to 77.0")
        unknown_fields.append("start_freq_ghz")

    slope = _safe_float(extracted.slope_mhz_per_us)
    if slope is not None:
        profile["slope_mhz_per_us"] = slope
    else:
        profile["slope_mhz_per_us"] = 60.0
        assumptions.append("slope_mhz_per_us: defaulted to 60.0")
        unknown_fields.append("slope_mhz_per_us")

    sample_rate = _safe_float(extracted.sample_rate_ksps)
    if sample_rate is not None:
        profile["sample_rate_ksps"] = sample_rate
    else:
        profile["sample_rate_ksps"] = 10000.0
        assumptions.append("sample_rate_ksps: defaulted to 10000.0")
        unknown_fields.append("sample_rate_ksps")

    idle = _safe_float(extracted.idle_time_us)
    if idle is not None:
        profile["idle_time_us"] = idle
    else:
        profile["idle_time_us"] = 10.0
        assumptions.append("idle_time_us: defaulted to 10.0")
        unknown_fields.append("idle_time_us")

    ramp = _safe_float(extracted.ramp_end_time_us)
    if ramp is not None:
        profile["ramp_end_time_us"] = ramp
    else:
        profile["ramp_end_time_us"] = 60.0
        assumptions.append("ramp_end_time_us: defaulted to 60.0")
        unknown_fields.append("ramp_end_time_us")

    config["profile"] = profile

    # --- Frame ---
    frame: dict[str, Any] = {}

    chirps = _safe_int(extracted.chirps_per_frame)
    if chirps is not None:
        frame["chirps_per_frame"] = chirps
    else:
        frame["chirps_per_frame"] = 128
        assumptions.append("chirps_per_frame: defaulted to 128")
        unknown_fields.append("chirps_per_frame")

    n_frames = _safe_int(extracted.num_frames)
    if n_frames is not None:
        frame["num_frames"] = n_frames
    else:
        frame["num_frames"] = 10
        assumptions.append("num_frames: defaulted to 10")
        unknown_fields.append("num_frames")

    fp = _safe_float(extracted.frame_period_ms)
    if fp is not None:
        frame["frame_period_ms"] = fp
    else:
        frame["frame_period_ms"] = 50.0
        assumptions.append("frame_period_ms: defaulted to 50.0")
        unknown_fields.append("frame_period_ms")

    config["frame"] = frame

    # --- Capture defaults ---
    config["capture"] = {
        "output_root": "experiments",
        "packet_delay_us": 25,
        "save_raw_packets": True,
        "raw_files": [],
        "adc_file": "raw/adc_data.bin",
    }

    # --- Write to file if requested ---
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build YAML with comments
        lines = [
            f"# Imported from: {Path(ti_file).name}",
            "# Review all fields before using for a real capture.",
            "",
        ]
        if assumptions:
            lines.append("# === ASSUMPTIONS (fields defaulted due to missing TI data) ===")
            for a in assumptions:
                lines.append(f"#   {a}")
            lines.append("")
        if unknown_fields:
            lines.append("# === UNKNOWN FIELDS (could not extract from TI file) ===")
            for f in unknown_fields:
                lines.append(f"#   {f}")
            lines.append("")

        yaml_str = yaml.dump(config, default_flow_style=False, sort_keys=False)
        lines.append(yaml_str)

        output_path.write_text("\n".join(lines), encoding="utf-8")

    return config, assumptions, unknown_fields
