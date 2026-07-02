"""DSP processing pipeline for radar cubes.

Pipeline stages (Milestone 1 implemented stages marked with ✓):
    ✓ DC offset removal — subtract per-chirp mean
    ✓ Range windowing + FFT — windowed FFT along sample axis
    ✓ Static clutter removal — subtract mean across chirps per range bin
    ✓ Doppler windowing + FFT — windowed FFT along chirp axis
    ○ Angle FFT / beamforming — placeholder (requires validated virtual array)
    ○ CFAR detection — placeholder
    ○ Point cloud export — placeholder
    ○ Corner reflector calibration — placeholder

All functions operate on the canonical cube shape: [frame, chirp, rx, sample].

Note on real vs. complex ADC:
    Real-valued time-domain ADC samples produce complex-valued FFT outputs.
    After range FFT, each range bin has complex amplitude and phase.  This
    supports Doppler and angle processing.  The parser correctly represents
    real ADC samples as float32; after range FFT the cube becomes complex64.
"""

from __future__ import annotations

import warnings

import numpy as np
from scipy.signal.windows import hann as hann_window


def remove_dc_offset(cube: np.ndarray) -> np.ndarray:
    """Remove DC offset by subtracting the per-chirp mean along the sample axis.

    Args:
        cube: [frame, chirp, rx, sample] float32 or complex64.

    Returns:
        DC-removed cube (same shape and dtype).
    """
    mean = cube.mean(axis=-1, keepdims=True)
    return cube - mean


def apply_range_fft(
    cube: np.ndarray,
    *,
    window: str = "hann",
    n_fft: int | None = None,
) -> np.ndarray:
    """Apply windowed FFT along the sample (range) axis.

    The output is complex64 regardless of whether input is real or complex.
    For real ADC data, this is correct: the FFT of real signals produces
    complex frequency-domain components with phase information.

    Args:
        cube: [frame, chirp, rx, sample] float32 or complex64.
        window: Window function name ("hann" or "none").
        n_fft: FFT length.  If None, uses samples_per_chirp.

    Returns:
        Complex64 cube [frame, chirp, rx, range_bin].
    """
    num_samples = cube.shape[-1]
    n = n_fft or num_samples

    # Apply window
    if window == "hann":
        w = hann_window(num_samples, sym=False).astype(np.float32)
        # Broadcast window across all dimensions except the last
        cube_windowed = cube * w
    elif window == "none":
        cube_windowed = cube
    else:
        raise ValueError(f"Unknown window '{window}'. Use 'hann' or 'none'.")

    # FFT along sample axis (last axis)
    result = np.fft.fft(cube_windowed, n=n, axis=-1)
    return result.astype(np.complex64)


def remove_static_clutter(cube: np.ndarray) -> np.ndarray:
    """Remove static clutter by subtracting the mean across chirps per range bin.

    This removes zero-Doppler (stationary) components, making moving targets
    more visible.

    Args:
        cube: [frame, chirp, rx, range_bin] complex64 (post range-FFT).

    Returns:
        Clutter-removed cube (same shape).
    """
    # Mean across chirp axis (axis=1)
    mean = cube.mean(axis=1, keepdims=True)
    return cube - mean


def apply_doppler_fft(
    cube: np.ndarray,
    *,
    window: str = "hann",
    n_fft: int | None = None,
    fft_shift: bool = True,
) -> np.ndarray:
    """Apply windowed FFT along the chirp (Doppler) axis.

    Args:
        cube: [frame, chirp, rx, range_bin] complex64.
        window: Window function name ("hann" or "none").
        n_fft: FFT length.  If None, uses chirps_per_frame.
        fft_shift: If True (default), shift zero-Doppler to center.

    Returns:
        Complex64 cube [frame, doppler_bin, rx, range_bin].
    """
    num_chirps = cube.shape[1]
    n = n_fft or num_chirps

    # Apply window along chirp axis
    if window == "hann":
        w = hann_window(num_chirps, sym=False).astype(np.float32)
        # Reshape for broadcasting: [1, chirps, 1, 1]
        w = w.reshape(1, -1, 1, 1)
        cube_windowed = cube * w
    elif window == "none":
        cube_windowed = cube
    else:
        raise ValueError(f"Unknown window '{window}'. Use 'hann' or 'none'.")

    # FFT along chirp axis (axis=1)
    result = np.fft.fft(cube_windowed, n=n, axis=1)

    if fft_shift:
        result = np.fft.fftshift(result, axes=1)

    return result.astype(np.complex64)


def process_cube(
    cube: np.ndarray,
    *,
    range_window: str = "hann",
    doppler_window: str = "hann",
    remove_clutter: bool = True,
    fft_shift_doppler: bool = True,
) -> dict[str, np.ndarray]:
    """Run the full M1 DSP pipeline on a radar cube.

    Pipeline: DC removal → range FFT → (optional) clutter removal → Doppler FFT.

    Args:
        cube: [frame, chirp, rx, sample] float32 or complex64.
        range_window: Window for range FFT.
        doppler_window: Window for Doppler FFT.
        remove_clutter: If True, apply static clutter removal.
        fft_shift_doppler: If True, shift Doppler FFT.

    Returns:
        Dict with intermediate and final results:
            "dc_removed": cube after DC removal
            "range_fft": cube after range FFT
            "clutter_removed": cube after clutter removal (if applied)
            "range_doppler": final range-Doppler cube
    """
    results: dict[str, np.ndarray] = {}

    # 1. DC offset removal
    dc_removed = remove_dc_offset(cube)
    results["dc_removed"] = dc_removed

    # 2. Range FFT
    range_cube = apply_range_fft(dc_removed, window=range_window)
    results["range_fft"] = range_cube

    # 3. Static clutter removal (optional)
    if remove_clutter:
        clutter_removed = remove_static_clutter(range_cube)
        results["clutter_removed"] = clutter_removed
        doppler_input = clutter_removed
    else:
        doppler_input = range_cube

    # 4. Doppler FFT
    rd_cube = apply_doppler_fft(
        doppler_input,
        window=doppler_window,
        fft_shift=fft_shift_doppler,
    )
    results["range_doppler"] = rd_cube

    return results


# ---------------------------------------------------------------------------
# Placeholder stubs for future pipeline stages
# ---------------------------------------------------------------------------


def apply_angle_fft(cube: np.ndarray, **kwargs) -> np.ndarray:
    """Placeholder for angle FFT / beamforming.

    TODO (Milestone 4): Implement after virtual antenna array geometry
    is validated and antenna spacing is known.

    Ref: TI FMCW deck — θ = asin(λω / (2πd))
    θ_res = λ / (N·d·cosθ)
    Requires: validated virtual array ordering, antenna spacing d.
    """
    raise NotImplementedError(
        "Angle FFT is not implemented in M1.  Requires validated "
        "virtual antenna array geometry.  See docs/ROADMAP.md Milestone 4."
    )


def apply_cfar(cube: np.ndarray, **kwargs) -> np.ndarray:
    """Placeholder for CFAR (Constant False Alarm Rate) detection.

    TODO (Milestone 4): Implement CA-CFAR and OS-CFAR.
    """
    raise NotImplementedError(
        "CFAR detection is not implemented in M1.  See docs/ROADMAP.md Milestone 4."
    )


def export_point_cloud(cube: np.ndarray, **kwargs) -> None:
    """Placeholder for point cloud export.

    TODO (Milestone 4): Export detected targets as a point cloud.
    """
    raise NotImplementedError(
        "Point cloud export is not implemented in M1.  See docs/ROADMAP.md Milestone 4."
    )


def calibrate_corner_reflector(cube: np.ndarray, **kwargs) -> None:
    """Placeholder for corner reflector calibration.

    TODO (Milestone 6): Implement range bias and RX gain/phase calibration.
    """
    raise NotImplementedError(
        "Corner reflector calibration is not implemented in M1.  "
        "See docs/ROADMAP.md Milestone 6."
    )
