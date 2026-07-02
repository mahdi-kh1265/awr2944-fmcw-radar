"""Plotting functions for radar DSP results.

Produces publication-quality static figures with:
- dB scaling
- Physical axes (meters, m/s) when config metadata is sufficient
- Fallback to bin indices otherwise
- Metadata in titles
- Warnings for unvalidated layouts or file-size issues
- Save to PNG and SVG

All plot functions return matplotlib Figure objects.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from awr2944_dca.config.derived import C_MPS, DerivedParams, compute_derived
from awr2944_dca.config.schema import RadarConfig
from awr2944_dca.formats.layouts import get_layout


def _db_scale(data: np.ndarray, ref: float | None = None) -> np.ndarray:
    """Convert magnitude to dB scale: 20*log10(|data|/ref).

    Args:
        data: Complex or real array.
        ref: Reference value.  If None, uses max(|data|).

    Returns:
        dB-scaled array.
    """
    mag = np.abs(data).astype(np.float64)
    mag = np.maximum(mag, 1e-12)  # Avoid log(0)
    if ref is None:
        ref = mag.max()
    ref = max(ref, 1e-12)
    return 20.0 * np.log10(mag / ref)


def _layout_warning_text(config: RadarConfig) -> str:
    """Generate a warning annotation if the layout is unvalidated."""
    try:
        layout = get_layout(config.adc.layout)
        if not layout.lab_validated:
            return f"[!] Layout '{layout.name}' is UNVALIDATED"
    except KeyError:
        return f"[!] Unknown layout '{config.adc.layout}'"
    return ""


def _range_axis(config: RadarConfig, num_bins: int) -> tuple[np.ndarray, str]:
    """Compute range axis in meters if possible, else bin indices.

    Range axis: bin_index × d_max / num_bins
    Ref: TI FMCW deck — d_max = Fs·c / (2S)
    """
    try:
        derived = compute_derived(config)
        axis = np.linspace(0, derived.max_range_m, num_bins, endpoint=False)
        return axis, "Range (m)"
    except Exception:
        return np.arange(num_bins, dtype=np.float64), "Range bin"


def _doppler_axis(config: RadarConfig, num_bins: int) -> tuple[np.ndarray, str]:
    """Compute Doppler/velocity axis in m/s if possible, else bin indices.

    Ref: TI FMCW deck — v_max = λ / (4Tc)
    Velocity axis is centered (fftshift assumed).
    """
    try:
        derived = compute_derived(config)
        v_max = derived.max_velocity_mps
        axis = np.linspace(-v_max, v_max, num_bins, endpoint=False)
        return axis, "Velocity (m/s) [estimate]"
    except Exception:
        return np.arange(num_bins, dtype=np.float64), "Doppler bin"


def plot_range_profile(
    range_cube: np.ndarray,
    config: RadarConfig,
    *,
    frame: int = 0,
    rx: int = 0,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Plot the average range profile (magnitude in dB vs range).

    Averages across all chirps in the selected frame.

    Args:
        range_cube: [frame, chirp, rx, range_bin] complex64 (post range-FFT).
        config: Radar config for axis labeling.
        frame: Frame index to plot.
        rx: RX channel index to plot.
        save_path: If provided, save to this path (adds .png and .svg).

    Returns:
        matplotlib Figure.
    """
    # Extract and average across chirps
    data = range_cube[frame, :, rx, :]  # [chirps, range_bins]
    avg_profile = np.mean(np.abs(data), axis=0)

    num_bins = avg_profile.shape[0]
    range_axis, range_label = _range_axis(config, num_bins)
    profile_db = _db_scale(avg_profile)

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(range_axis, profile_db, linewidth=0.8, color="#2196F3")
    ax.set_xlabel(range_label, fontsize=11)
    ax.set_ylabel("Magnitude (dB)", fontsize=11)

    title = (
        f"Range Profile — {config.experiment.name}\n"
        f"Frame {frame}, RX {rx}, "
        f"{config.adc.samples_per_chirp} samples, "
        f"{config.frame.chirps_per_frame} chirps averaged"
    )
    ax.set_title(title, fontsize=12)
    ax.grid(True, alpha=0.3)

    # Add warning annotation if layout is unvalidated
    warning = _layout_warning_text(config)
    if warning:
        ax.annotate(
            warning,
            xy=(0.02, 0.02),
            xycoords="axes fraction",
            fontsize=8,
            color="red",
            fontweight="bold",
        )

    fig.tight_layout()

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path.with_suffix(".png"), dpi=150, bbox_inches="tight")
        fig.savefig(save_path.with_suffix(".svg"), bbox_inches="tight")

    return fig


def plot_range_doppler(
    rd_cube: np.ndarray,
    config: RadarConfig,
    *,
    frame: int = 0,
    rx: int = 0,
    dynamic_range_db: float = 60.0,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Plot a range-Doppler heatmap (magnitude in dB).

    Args:
        rd_cube: [frame, doppler_bin, rx, range_bin] complex64 (post Doppler-FFT).
        config: Radar config for axis labeling.
        frame: Frame index to plot.
        rx: RX channel index to plot.
        dynamic_range_db: Dynamic range for colorbar clipping.
        save_path: If provided, save to this path (adds .png and .svg).

    Returns:
        matplotlib Figure.
    """
    # Extract [doppler, range]
    data = rd_cube[frame, :, rx, :]  # [doppler_bins, range_bins]
    data_db = _db_scale(data)

    # Clip dynamic range
    vmax = 0.0
    vmin = -dynamic_range_db

    num_range_bins = data.shape[1]
    num_doppler_bins = data.shape[0]

    range_axis, range_label = _range_axis(config, num_range_bins)
    doppler_axis, doppler_label = _doppler_axis(config, num_doppler_bins)

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 7))

    im = ax.imshow(
        data_db,
        aspect="auto",
        origin="lower",
        cmap="viridis",
        vmin=vmin,
        vmax=vmax,
        extent=[
            range_axis[0],
            range_axis[-1],
            doppler_axis[0],
            doppler_axis[-1],
        ],
    )

    ax.set_xlabel(range_label, fontsize=11)
    ax.set_ylabel(doppler_label, fontsize=11)

    title = (
        f"Range-Doppler Map — {config.experiment.name}\n"
        f"Frame {frame}, RX {rx}, "
        f"{config.adc.samples_per_chirp} range bins, "
        f"{config.frame.chirps_per_frame} Doppler bins"
    )
    ax.set_title(title, fontsize=12)

    cbar = fig.colorbar(im, ax=ax, label="Magnitude (dB)", shrink=0.8)

    # Add warning annotation if layout is unvalidated
    warning = _layout_warning_text(config)
    if warning:
        ax.annotate(
            warning,
            xy=(0.02, 0.02),
            xycoords="axes fraction",
            fontsize=8,
            color="red",
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8),
        )

    fig.tight_layout()

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path.with_suffix(".png"), dpi=150, bbox_inches="tight")
        fig.savefig(save_path.with_suffix(".svg"), bbox_inches="tight")

    return fig
