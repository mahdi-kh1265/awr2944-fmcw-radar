"""Synthetic radar cube generation and binary packing for testing.

Provides tools to:
1. Generate synthetic radar cubes with optional simulated point targets.
2. Pack cubes back to raw binary format matching a specific layout.
3. Enable round-trip testing: generate → pack → parse → verify.

For round-trip equality tests, use integer-valued samples (no fractional
components) so that int16 → float32 → int16 conversion is exact.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from awr2944_dca.config.schema import AdcConfig, RadarConfig
from awr2944_dca.formats.layouts import BinaryLayout, get_layout


def generate_radar_cube(
    config: RadarConfig,
    *,
    mode: str = "noise",
    seed: int = 42,
    max_amplitude: int = 1000,
) -> np.ndarray:
    """Generate a synthetic radar cube.

    Args:
        config: Validated radar config.
        mode: Generation mode:
            - "noise": Random integer noise (good for round-trip tests).
            - "zeros": All zeros.
            - "ramp": Deterministic ramp values (sample index mod 32767).
        seed: Random seed for reproducibility.
        max_amplitude: Max absolute sample value for noise mode.

    Returns:
        Radar cube:
            - Real ADC config:    float32 [frames, chirps, rx, samples]
            - Complex ADC config: complex64 [frames, chirps, rx, samples]
    """
    rng = np.random.default_rng(seed)

    shape = (
        config.frame.num_frames,
        config.frame.chirps_per_frame,
        config.hardware.num_rx,
        config.adc.samples_per_chirp,
    )

    if config.adc.is_complex:
        if mode == "noise":
            real = rng.integers(-max_amplitude, max_amplitude + 1, size=shape, dtype=np.int16)
            imag = rng.integers(-max_amplitude, max_amplitude + 1, size=shape, dtype=np.int16)
            cube = real.astype(np.float32) + 1j * imag.astype(np.float32)
        elif mode == "zeros":
            cube = np.zeros(shape, dtype=np.complex64)
        elif mode == "ramp":
            total = int(np.prod(shape))
            ramp = np.arange(total, dtype=np.float32) % 32767
            cube = (ramp + 1j * (-ramp)).reshape(shape)
        else:
            raise ValueError(f"Unknown mode '{mode}'")
        return cube
    else:
        if mode == "noise":
            samples = rng.integers(-max_amplitude, max_amplitude + 1, size=shape, dtype=np.int16)
            cube = samples.astype(np.float32)
        elif mode == "zeros":
            cube = np.zeros(shape, dtype=np.float32)
        elif mode == "ramp":
            total = int(np.prod(shape))
            ramp = np.arange(total, dtype=np.float32) % 32767
            cube = ramp.reshape(shape)
        else:
            raise ValueError(f"Unknown mode '{mode}'")
        return cube


def generate_tone_cube(
    config: RadarConfig,
    *,
    range_bin: int = 10,
    doppler_bin: int = 0,
    amplitude: float = 100.0,
) -> np.ndarray:
    """Generate a synthetic cube with a single-frequency tone for DSP testing.

    Places a sinusoidal tone at a specific range bin (sample frequency) and
    optionally a Doppler bin (chirp-to-chirp phase ramp).

    This produces float-valued data — use np.allclose for comparison, not
    exact equality.

    Args:
        config: Validated radar config.
        range_bin: Target range bin (frequency index in sample axis).
        doppler_bin: Target Doppler bin (phase ramp across chirps).
        amplitude: Tone amplitude.

    Returns:
        float32 cube [frames, chirps, rx, samples] (always real for the
        time-domain signal — complex emerges after FFT).
    """
    num_frames = config.frame.num_frames
    chirps = config.frame.chirps_per_frame
    num_rx = config.hardware.num_rx
    samples = config.adc.samples_per_chirp

    cube = np.zeros((num_frames, chirps, num_rx, samples), dtype=np.float32)

    # Range tone: sinusoid at frequency = range_bin / samples * sample_rate
    sample_idx = np.arange(samples, dtype=np.float32)
    range_tone = amplitude * np.cos(2 * np.pi * range_bin * sample_idx / samples)

    # Doppler phase ramp: phase shift per chirp
    chirp_idx = np.arange(chirps, dtype=np.float32)
    doppler_phase = 2 * np.pi * doppler_bin * chirp_idx / chirps

    for frame in range(num_frames):
        for rx in range(num_rx):
            for chirp in range(chirps):
                # Shift range tone by Doppler phase
                cube[frame, chirp, rx, :] = range_tone * np.cos(doppler_phase[chirp])

    return cube


def pack_cube_to_bin(
    cube: np.ndarray,
    config: RadarConfig,
    layout: BinaryLayout | None = None,
) -> bytes:
    """Pack a radar cube into raw binary bytes matching a layout.

    Args:
        cube: Radar cube [frames, chirps, rx, samples].
        config: Validated radar config.
        layout: Optional layout override.  If None, uses config.adc.layout.

    Returns:
        Raw bytes that can be written to an adc_data.bin file.
    """
    if layout is None:
        layout = get_layout(config.adc.layout)

    flat = layout.pack_cube(cube, config)
    return flat.tobytes()


def write_synthetic_bin(
    path: str | Path,
    config: RadarConfig,
    *,
    mode: str = "noise",
    seed: int = 42,
    layout: BinaryLayout | None = None,
) -> np.ndarray:
    """Generate a synthetic cube and write it as a binary file.

    Args:
        path: Output file path.
        config: Radar config.
        mode: Generation mode (see generate_radar_cube).
        seed: Random seed.
        layout: Optional layout override.

    Returns:
        The generated cube (for test comparison).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    cube = generate_radar_cube(config, mode=mode, seed=seed)
    raw_bytes = pack_cube_to_bin(cube, config, layout)

    with open(path, "wb") as f:
        f.write(raw_bytes)

    return cube
