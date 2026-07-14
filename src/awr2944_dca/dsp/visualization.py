"""Static matplotlib plot generators for radar DSP results.

All plots produce matplotlib Figure objects and support PNG export.
Every plot annotates the processing configuration used.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from awr2944_dca.dsp.axes import range_axis, velocity_axis
from awr2944_dca.dsp.config import RadarProfile


def _save_fig(fig: plt.Figure, path: str | Path | None, dpi: int = 150) -> None:
    if path is not None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(path), dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def plot_raw_adc_traces(
    adc_cube: np.ndarray,
    profile: RadarProfile,
    *,
    frame: int = 0,
    chirp: int = 0,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Plot raw ADC traces for all RX channels."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 8), sharex=True, sharey=True)
    axes_flat = axes.ravel()

    for rx in range(min(profile.rx_count, 4)):
        ax = axes_flat[rx]
        data = adc_cube[frame, chirp, rx, :]
        ax.plot(data, linewidth=0.6, color=f"C{rx}")
        ax.set_title(f"RX{rx}", fontsize=10)
        ax.set_ylabel("ADC (int16)")
        ax.grid(True, alpha=0.3)

    axes_flat[-1].set_xlabel("Sample index")
    axes_flat[-2].set_xlabel("Sample index")
    fig.suptitle(f"Raw ADC Traces — Frame {frame}, Chirp {chirp}", fontsize=12)
    fig.tight_layout()
    _save_fig(fig, save_path)
    return fig


def plot_range_profiles(
    range_power_db: np.ndarray,
    profile: RadarProfile,
    nfft: int = 256,
    *,
    frame: int = 0,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Plot mean range profile for each RX and noncoherent combination."""
    r_axis = range_axis(profile, nfft)
    fig, ax = plt.subplots(figsize=(12, 5))

    for rx in range(profile.rx_count):
        mean_profile = np.mean(range_power_db[frame, :, rx, :], axis=0)
        ax.plot(r_axis, mean_profile, linewidth=0.8, label=f"RX{rx}", alpha=0.7)

    # Noncoherent sum
    all_rx = range_power_db[frame, :, :, :]  # [chirp, rx, range]
    mag = 10 ** (all_rx / 20.0)
    nc_power = np.mean(np.sum(mag ** 2, axis=1), axis=0)
    nc_db = 10.0 * np.log10(np.maximum(nc_power, 1e-30))
    ax.plot(r_axis, nc_db, linewidth=1.2, color="black", label="NC-Sum", linestyle="--")

    ax.set_xlabel("Range (m)")
    ax.set_ylabel("Power (dB)")
    ax.set_title(f"Range Profiles — Frame {frame}")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save_fig(fig, save_path)
    return fig


def plot_range_time_heatmap(
    range_power_db: np.ndarray,
    profile: RadarProfile,
    nfft: int = 256,
    *,
    rx: int = 0,
    dynamic_range_db: float = 60.0,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Plot range-time heatmap (mean across chirps per frame)."""
    r_axis = range_axis(profile, nfft)
    num_frames = range_power_db.shape[0]
    time_axis = np.arange(num_frames) * profile.frame_period_s * 1000  # ms

    # Mean across chirps for each frame
    rt_map = np.mean(range_power_db[:, :, rx, :], axis=1)  # [frame, range]
    vmax = float(np.max(rt_map))
    vmin = vmax - dynamic_range_db

    fig, ax = plt.subplots(figsize=(12, 5))
    im = ax.imshow(
        rt_map, aspect="auto", origin="lower",
        extent=[r_axis[0], r_axis[-1], time_axis[0], time_axis[-1]],
        vmin=vmin, vmax=vmax, cmap="viridis",
    )
    ax.set_xlabel("Range (m)")
    ax.set_ylabel("Time (ms)")
    ax.set_title(f"Range-Time Heatmap — RX{rx}")
    fig.colorbar(im, ax=ax, label="Power (dB)")
    fig.tight_layout()
    _save_fig(fig, save_path)
    return fig


def plot_range_doppler(
    rd_power_db: np.ndarray,
    profile: RadarProfile,
    nfft_range: int = 256,
    nfft_doppler: int = 128,
    *,
    frame: int = 0,
    dynamic_range_db: float = 60.0,
    save_path: str | Path | None = None,
    title_suffix: str = "",
) -> plt.Figure:
    """Plot range-Doppler heatmap for a single frame."""
    r_axis = range_axis(profile, nfft_range)
    v_axis = velocity_axis(profile, nfft_doppler)

    data = rd_power_db[frame]  # [doppler, range] if rx-combined
    if data.ndim == 3:
        data = data[:, 0, :]  # pick RX0 if per-RX

    vmax = float(np.max(data))
    vmin = vmax - dynamic_range_db

    fig, ax = plt.subplots(figsize=(10, 7))
    im = ax.imshow(
        data, aspect="auto", origin="lower",
        extent=[r_axis[0], r_axis[-1], v_axis[0], v_axis[-1]],
        vmin=vmin, vmax=vmax, cmap="viridis",
    )
    ax.set_xlabel("Range (m)")
    ax.set_ylabel("Velocity (m/s)")
    title = f"Range-Doppler — Frame {frame}"
    if title_suffix:
        title += f" — {title_suffix}"
    ax.set_title(title)
    fig.colorbar(im, ax=ax, label="Power (dB)")
    fig.tight_layout()
    _save_fig(fig, save_path)
    return fig


def plot_range_doppler_average(
    rd_power_db: np.ndarray,
    profile: RadarProfile,
    nfft_range: int = 256,
    nfft_doppler: int = 128,
    *,
    dynamic_range_db: float = 60.0,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Plot frame-averaged range-Doppler heatmap."""
    avg = np.mean(rd_power_db, axis=0)
    # Wrap into [1, ...] shape for plot_range_doppler
    return plot_range_doppler(
        avg[np.newaxis], profile, nfft_range, nfft_doppler,
        frame=0, dynamic_range_db=dynamic_range_db,
        save_path=save_path, title_suffix="Frame Average",
    )


def plot_doppler_cut(
    rd_power_db: np.ndarray,
    profile: RadarProfile,
    nfft_doppler: int = 128,
    *,
    frame: int = 0,
    range_bin: int = 10,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Plot Doppler spectrum at a selected range bin."""
    v_axis = velocity_axis(profile, nfft_doppler)
    data = rd_power_db[frame]
    if data.ndim == 3:
        data = data[:, 0, :]
    doppler_cut = data[:, range_bin]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(v_axis, doppler_cut, linewidth=0.8)
    ax.set_xlabel("Velocity (m/s)")
    ax.set_ylabel("Power (dB)")
    ax.set_title(f"Doppler Spectrum — Frame {frame}, Range Bin {range_bin}")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save_fig(fig, save_path)
    return fig


def plot_cfar_overlay(
    rd_power_db: np.ndarray,
    detections: list[dict[str, Any]],
    profile: RadarProfile,
    nfft_range: int = 256,
    nfft_doppler: int = 128,
    *,
    frame: int = 0,
    dynamic_range_db: float = 60.0,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Plot range-Doppler heatmap with CFAR detection overlay."""
    r_axis = range_axis(profile, nfft_range)
    v_axis = velocity_axis(profile, nfft_doppler)

    data = rd_power_db[frame]
    if data.ndim == 3:
        data = data[:, 0, :]

    vmax = float(np.max(data))
    vmin = vmax - dynamic_range_db

    fig, ax = plt.subplots(figsize=(10, 7))
    im = ax.imshow(
        data, aspect="auto", origin="lower",
        extent=[r_axis[0], r_axis[-1], v_axis[0], v_axis[-1]],
        vmin=vmin, vmax=vmax, cmap="viridis",
    )

    # Overlay detections
    frame_dets = [d for d in detections if d.get("frame") == frame]
    if frame_dets:
        det_r = [d["range_m"] for d in frame_dets]
        det_v = [d["velocity_mps"] for d in frame_dets]
        ax.scatter(det_r, det_v, marker="o", s=60, facecolors="none",
                   edgecolors="red", linewidths=1.5, label=f"CFAR ({len(frame_dets)} det)")
        ax.legend(fontsize=8)

    ax.set_xlabel("Range (m)")
    ax.set_ylabel("Velocity (m/s)")
    ax.set_title(f"CFAR Overlay — Frame {frame}")
    fig.colorbar(im, ax=ax, label="Power (dB)")
    fig.tight_layout()
    _save_fig(fig, save_path)
    return fig


def plot_histograms(
    adc_cube: np.ndarray,
    profile: RadarProfile,
    *,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Plot ADC sample histograms for each RX."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes_flat = axes.ravel()

    for rx in range(min(profile.rx_count, 4)):
        ax = axes_flat[rx]
        data = adc_cube[:, :, rx, :].ravel()
        ax.hist(data, bins=200, density=True, alpha=0.7, color=f"C{rx}")
        ax.set_title(f"RX{rx} (mean={np.mean(data):.1f}, std={np.std(data):.1f})")
        ax.set_xlabel("ADC value")
        ax.set_ylabel("Density")
        ax.grid(True, alpha=0.3)

    fig.suptitle("ADC Sample Histograms", fontsize=12)
    fig.tight_layout()
    _save_fig(fig, save_path)
    return fig


def plot_frame_chirp_rx_rms(
    adc_cube: np.ndarray,
    profile: RadarProfile,
    *,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Plot RMS per frame, per RX."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Per-frame RMS
    ax = axes[0]
    for rx in range(profile.rx_count):
        frame_rms = []
        for f in range(adc_cube.shape[0]):
            d = adc_cube[f, :, rx, :].astype(np.float64)
            frame_rms.append(np.sqrt(np.mean(d ** 2)))
        ax.plot(frame_rms, marker="o", label=f"RX{rx}", markersize=4)
    ax.set_xlabel("Frame")
    ax.set_ylabel("RMS")
    ax.set_title("Per-Frame RMS")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Per-sample-index mean
    ax = axes[1]
    for rx in range(profile.rx_count):
        mean_per_idx = np.mean(adc_cube[:, :, rx, :].astype(np.float64), axis=(0, 1))
        ax.plot(mean_per_idx, linewidth=0.5, label=f"RX{rx}", alpha=0.7)
    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Mean ADC")
    ax.set_title("Mean vs Sample Index")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.suptitle("Frame/Chirp/RX Statistics", fontsize=12)
    fig.tight_layout()
    _save_fig(fig, save_path)
    return fig
