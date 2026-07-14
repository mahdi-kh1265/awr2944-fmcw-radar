"""CFAR (Constant False Alarm Rate) detection.

Implements:
    1. 1D CA-CFAR for range profiles
    2. 2D CA-CFAR for range-Doppler maps

Architecture supports future extension to GO-CFAR, SO-CFAR, OS-CFAR.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from awr2944_dca.dsp.config import CfarConfig, CfarMode
from awr2944_dca.dsp.types import CfarDetection


def cfar_1d(
    signal: np.ndarray,
    config: CfarConfig,
    *,
    range_axis_m: np.ndarray | None = None,
) -> list[CfarDetection]:
    """1D CA-CFAR on a range profile.

    Parameters
    ----------
    signal : ndarray, float32
        Power in dB, shape (num_range_bins,).
    config : CfarConfig
    range_axis_m : ndarray, optional
        Physical range axis for detection labeling.

    Returns
    -------
    list of CfarDetection
    """
    n = len(signal)
    guard = config.guard_cells_range
    train = config.training_cells_range
    threshold_db = config.threshold_factor_db
    min_snr = config.minimum_snr_db

    detections: list[CfarDetection] = []
    noise_estimate = np.full(n, np.nan, dtype=np.float32)
    threshold = np.full(n, np.nan, dtype=np.float32)

    for i in range(n):
        # Define training window
        left_start = max(i - guard - train, 0)
        left_end = max(i - guard, 0)
        right_start = min(i + guard + 1, n)
        right_end = min(i + guard + train + 1, n)

        left_cells = signal[left_start:left_end]
        right_cells = signal[right_start:right_end]

        training = np.concatenate([left_cells, right_cells])

        if len(training) == 0:
            continue

        if config.mode == CfarMode.CA:
            noise_level = float(np.mean(training))
        elif config.mode == CfarMode.GO:
            left_mean = float(np.mean(left_cells)) if len(left_cells) > 0 else -np.inf
            right_mean = float(np.mean(right_cells)) if len(right_cells) > 0 else -np.inf
            noise_level = max(left_mean, right_mean)
        elif config.mode == CfarMode.SO:
            left_mean = float(np.mean(left_cells)) if len(left_cells) > 0 else np.inf
            right_mean = float(np.mean(right_cells)) if len(right_cells) > 0 else np.inf
            noise_level = min(left_mean, right_mean)
        else:
            noise_level = float(np.mean(training))

        thresh = noise_level + threshold_db
        noise_estimate[i] = noise_level
        threshold[i] = thresh

        snr = float(signal[i]) - noise_level

        if float(signal[i]) > thresh and snr >= min_snr:
            range_m = float(range_axis_m[i]) if range_axis_m is not None else 0.0
            detections.append(CfarDetection(
                frame=0,
                range_bin=i,
                range_m=range_m,
                doppler_bin=0,
                velocity_mps=0.0,
                signal_power_db=float(signal[i]),
                noise_estimate_db=noise_level,
                snr_db=snr,
                threshold_db=thresh,
            ))

    return detections


def cfar_2d(
    rd_map: np.ndarray,
    config: CfarConfig,
    *,
    range_axis_m: np.ndarray | None = None,
    velocity_axis_mps: np.ndarray | None = None,
    frame: int = 0,
) -> list[CfarDetection]:
    """2D CA-CFAR on a range-Doppler map.

    Parameters
    ----------
    rd_map : ndarray, float32
        Power in dB, shape (num_doppler_bins, num_range_bins).
    config : CfarConfig
    range_axis_m : ndarray, optional
    velocity_axis_mps : ndarray, optional
    frame : int

    Returns
    -------
    list of CfarDetection
    """
    nd, nr = rd_map.shape
    guard_r = config.guard_cells_range
    train_r = config.training_cells_range
    guard_d = config.guard_cells_doppler
    train_d = config.training_cells_doppler
    threshold_db = config.threshold_factor_db
    min_snr = config.minimum_snr_db

    detections: list[CfarDetection] = []

    # Determine CUT range
    r_start = (guard_r + train_r) if config.edge_guard else 0
    r_end = (nr - guard_r - train_r) if config.edge_guard else nr
    d_start = (guard_d + train_d) if config.edge_guard else 0
    d_end = (nd - guard_d - train_d) if config.edge_guard else nd

    for di in range(d_start, d_end):
        for ri in range(r_start, r_end):
            # Build training mask
            training_sum = 0.0
            training_count = 0

            for dj in range(max(di - guard_d - train_d, 0),
                           min(di + guard_d + train_d + 1, nd)):
                for rj in range(max(ri - guard_r - train_r, 0),
                               min(ri + guard_r + train_r + 1, nr)):
                    # Skip guard cells
                    if (abs(dj - di) <= guard_d and abs(rj - ri) <= guard_r):
                        continue
                    training_sum += rd_map[dj, rj]
                    training_count += 1

            if training_count == 0:
                continue

            noise_level = training_sum / training_count
            thresh = noise_level + threshold_db
            cell_val = float(rd_map[di, ri])
            snr = cell_val - noise_level

            if cell_val > thresh and snr >= min_snr:
                range_m = float(range_axis_m[ri]) if range_axis_m is not None else 0.0
                vel_mps = float(velocity_axis_mps[di]) if velocity_axis_mps is not None else 0.0

                detections.append(CfarDetection(
                    frame=frame,
                    range_bin=ri,
                    range_m=range_m,
                    doppler_bin=di,
                    velocity_mps=vel_mps,
                    signal_power_db=cell_val,
                    noise_estimate_db=noise_level,
                    snr_db=snr,
                    threshold_db=thresh,
                ))

    return detections
