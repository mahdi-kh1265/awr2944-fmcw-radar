"""Peak detection, parabolic interpolation, and clustering.

Peak interpolation:
    Parabolic interpolation around local FFT peaks for sub-bin estimates.
    Clearly distinguish FFT bin spacing, interpolated peak, and physical resolution.

Clustering:
    DBSCAN or connected-component grouping of nearby CFAR detections
    to prevent multiple bins from being reported as separate targets.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from awr2944_dca.dsp.types import CfarDetection


@dataclass
class PeakInfo:
    """A detected peak with optional sub-bin interpolation."""
    bin_index: int
    magnitude: float
    magnitude_db: float
    interpolated_bin: float
    interpolated_magnitude_db: float
    prominence: float


def find_local_maxima(
    spectrum_db: np.ndarray,
    *,
    min_prominence_db: float = 6.0,
    min_distance: int = 2,
) -> list[PeakInfo]:
    """Find local maxima in a 1D spectrum.

    Parameters
    ----------
    spectrum_db : ndarray
        1D power spectrum in dB.
    min_prominence_db : float
        Minimum prominence above neighbors.
    min_distance : int
        Minimum bin separation between peaks.

    Returns
    -------
    list of PeakInfo
    """
    n = len(spectrum_db)
    peaks: list[PeakInfo] = []

    for i in range(1, n - 1):
        if spectrum_db[i] > spectrum_db[i - 1] and spectrum_db[i] > spectrum_db[i + 1]:
            # Check prominence
            left_min = np.min(spectrum_db[max(0, i - 10):i])
            right_min = np.min(spectrum_db[i + 1:min(n, i + 11)])
            prominence = spectrum_db[i] - max(left_min, right_min)

            if prominence >= min_prominence_db:
                interp_bin, interp_db = _parabolic_interpolation(
                    spectrum_db, i
                )
                peaks.append(PeakInfo(
                    bin_index=i,
                    magnitude=10 ** (spectrum_db[i] / 20.0),
                    magnitude_db=float(spectrum_db[i]),
                    interpolated_bin=interp_bin,
                    interpolated_magnitude_db=interp_db,
                    prominence=prominence,
                ))

    # Enforce minimum distance
    if min_distance > 0 and len(peaks) > 1:
        peaks.sort(key=lambda p: p.magnitude_db, reverse=True)
        filtered: list[PeakInfo] = []
        for p in peaks:
            if all(abs(p.bin_index - f.bin_index) >= min_distance for f in filtered):
                filtered.append(p)
        peaks = filtered

    return peaks


def _parabolic_interpolation(
    spectrum_db: np.ndarray,
    peak_idx: int,
) -> tuple[float, float]:
    """Parabolic interpolation around a local peak for sub-bin estimate.

    Uses three points: (peak_idx-1, peak_idx, peak_idx+1).

    Returns
    -------
    (interpolated_bin, interpolated_magnitude_db)
    """
    if peak_idx <= 0 or peak_idx >= len(spectrum_db) - 1:
        return float(peak_idx), float(spectrum_db[peak_idx])

    alpha = float(spectrum_db[peak_idx - 1])
    beta = float(spectrum_db[peak_idx])
    gamma = float(spectrum_db[peak_idx + 1])

    denom = alpha - 2 * beta + gamma
    if abs(denom) < 1e-12:
        return float(peak_idx), beta

    p = 0.5 * (alpha - gamma) / denom
    interpolated_bin = peak_idx + p
    interpolated_db = beta - 0.25 * (alpha - gamma) * p

    return interpolated_bin, interpolated_db


def cluster_detections(
    detections: list[CfarDetection],
    *,
    range_eps_bins: float = 3.0,
    doppler_eps_bins: float = 3.0,
) -> list[list[CfarDetection]]:
    """Simple distance-based clustering of CFAR detections.

    Groups detections that are within (range_eps, doppler_eps) of each other.
    Uses a greedy nearest-neighbor approach (not full DBSCAN).

    Parameters
    ----------
    detections : list of CfarDetection
    range_eps_bins : float
        Maximum range-bin distance for grouping.
    doppler_eps_bins : float
        Maximum Doppler-bin distance for grouping.

    Returns
    -------
    list of list of CfarDetection
        Each inner list is a cluster.
    """
    if not detections:
        return []

    assigned = [False] * len(detections)
    clusters: list[list[CfarDetection]] = []

    for i, det_i in enumerate(detections):
        if assigned[i]:
            continue

        cluster = [det_i]
        assigned[i] = True

        for j, det_j in enumerate(detections):
            if assigned[j]:
                continue
            if (abs(det_i.range_bin - det_j.range_bin) <= range_eps_bins
                    and abs(det_i.doppler_bin - det_j.doppler_bin) <= doppler_eps_bins):
                cluster.append(det_j)
                assigned[j] = True

        clusters.append(cluster)

    return clusters
