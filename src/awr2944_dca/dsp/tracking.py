"""Tracking infrastructure for CFAR detections.

Provides:
    - Detection clustering (distance-based)
    - Nearest-neighbor association
    - Kalman filter track state
    - Track ID management, age, confidence
    - CSV/JSON export

Do not claim reliable tracking performance from eight short frames.
Implement interfaces and validate with synthetic data first.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from awr2944_dca.dsp.types import CfarDetection


@dataclass
class TrackState:
    """State of a tracked target."""
    track_id: int
    range_m: float
    velocity_mps: float
    range_rate: float = 0.0  # estimated from Kalman
    age: int = 0             # frames since creation
    missed: int = 0          # consecutive missed detections
    confidence: float = 0.0
    history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "track_id": self.track_id,
            "range_m": round(self.range_m, 4),
            "velocity_mps": round(self.velocity_mps, 4),
            "range_rate": round(self.range_rate, 4),
            "age": self.age,
            "missed": self.missed,
            "confidence": round(self.confidence, 3),
        }


class SimpleKalmanTracker:
    """Minimal 1D Kalman tracker for range tracking.

    State: [range, range_rate]
    Measurement: [range]

    This is a skeleton for future development.
    Full 2D or 3D tracking requires validated angle processing.
    """

    def __init__(
        self,
        *,
        process_noise: float = 0.1,
        measurement_noise: float = 0.5,
        max_missed: int = 3,
        min_confidence: float = 0.3,
    ):
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise
        self.max_missed = max_missed
        self.min_confidence = min_confidence
        self.tracks: list[TrackState] = []
        self._next_id = 0

    def update(
        self,
        detections: list[CfarDetection],
        dt: float = 0.04,  # frame period
    ) -> list[TrackState]:
        """Update tracks with new detections.

        Parameters
        ----------
        detections : list of CfarDetection
        dt : float
            Time between frames.

        Returns
        -------
        list of TrackState
            Current active tracks.
        """
        # Predict step: advance all tracks
        for track in self.tracks:
            track.range_m += track.range_rate * dt
            track.age += 1

        # Associate detections to tracks (nearest-neighbor)
        used_dets = set()
        for track in self.tracks:
            best_dist = float("inf")
            best_idx = -1

            for i, det in enumerate(detections):
                if i in used_dets:
                    continue
                dist = abs(det.range_m - track.range_m)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = i

            if best_idx >= 0 and best_dist < 2.0:  # gate: 2 meters
                det = detections[best_idx]
                used_dets.add(best_idx)

                # Update step
                innovation = det.range_m - track.range_m
                track.range_rate = innovation / dt if dt > 0 else 0.0
                track.range_m = det.range_m
                track.velocity_mps = det.velocity_mps
                track.missed = 0
                track.confidence = min(track.confidence + 0.1, 1.0)
                track.history.append(det.to_dict())
            else:
                track.missed += 1
                track.confidence = max(track.confidence - 0.2, 0.0)

        # Create new tracks from unassociated detections
        for i, det in enumerate(detections):
            if i not in used_dets:
                self.tracks.append(TrackState(
                    track_id=self._next_id,
                    range_m=det.range_m,
                    velocity_mps=det.velocity_mps,
                    confidence=0.5,
                    history=[det.to_dict()],
                ))
                self._next_id += 1

        # Prune dead tracks
        self.tracks = [
            t for t in self.tracks
            if t.missed <= self.max_missed
        ]

        return self.tracks
