"""CaptureRawData — typed access to raw capture files.

Delegates to the existing proven parser (parse_awr2944_real) only.
Never invokes DSP, FFT, windowing, clutter removal, or MATLAB.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CaptureRawData:
    """Typed accessor for raw binary capture data.

    Provides paths, SHA256 hashes (from manifest), disk-verified hashes,
    and cube parsing via the existing AWR2944 parser.
    """

    def __init__(self, capture_dir: Path, manifest: dict | None):
        self._dir = capture_dir
        self._manifest = manifest or {}

    # -----------------------------------------------------------------------
    # Path accessors
    # -----------------------------------------------------------------------

    @property
    def native_path(self) -> Path | None:
        p = self._dir / "adc_data.bin"
        return p if p.exists() else None

    @property
    def canonical_path(self) -> Path | None:
        p = self._dir / "adc_data_canonical.bin"
        return p if p.exists() else None

    @property
    def packet_metadata_path(self) -> Path | None:
        rel = self._manifest.get("packet_metadata_path")
        if rel:
            p = self._dir / rel
            return p if p.exists() else None
        return None

    # -----------------------------------------------------------------------
    # Hash properties (from manifest, no disk I/O)
    # -----------------------------------------------------------------------

    @property
    def native_sha256(self) -> str | None:
        return self._manifest.get("native_sha256") or None

    @property
    def canonical_sha256(self) -> str | None:
        return self._manifest.get("canonical_sha256") or None

    @property
    def native_bytes(self) -> int | None:
        """Size of the native capture file in bytes."""
        p = self.native_path
        return p.stat().st_size if p else None

    @property
    def canonical_bytes(self) -> int | None:
        """Size of the canonical capture file in bytes."""
        p = self.canonical_path
        return p.stat().st_size if p else None

    # -----------------------------------------------------------------------
    # Disk-verified hash
    # -----------------------------------------------------------------------

    def compute_sha256(self, kind: str = "canonical") -> str:
        """Read the file from disk and compute its SHA256 hex digest."""
        if kind == "canonical":
            path = self.canonical_path
        elif kind == "native":
            path = self.native_path
        else:
            raise ValueError(f"Unknown kind: {kind!r}. Use 'canonical' or 'native'.")
        if path is None or not path.exists():
            raise FileNotFoundError(f"No {kind} data file found in {self._dir}")
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while True:
                chunk = f.read(1 << 20)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()

    # -----------------------------------------------------------------------
    # Cube parsing — uses existing proven parser ONLY
    # -----------------------------------------------------------------------

    def _resolve_dimensions(self, kind: str) -> tuple[Path, int, int, int, int]:
        """Resolve file path and cube dimensions from manifest."""
        m = self._manifest

        if kind == "canonical":
            path = self.canonical_path
            frames = m.get("canonical_frame_count", 0)
        elif kind == "native":
            path = self.native_path
            frames = m.get("total_frames", 0)
        else:
            raise ValueError(f"Unknown kind: {kind!r}. Use 'canonical' or 'native'.")

        if path is None or not path.exists():
            raise FileNotFoundError(f"No {kind} data file found in {self._dir}")

        # Get chirps, rx, samples from manifest profile or cube shape
        cube_shape = m.get("logical_cube_shape")
        if cube_shape and len(cube_shape) == 4:
            _, chirps, rx, samples = cube_shape
        else:
            # Fallback: try profile dict
            profile = m.get("profile", {})
            chirps = profile.get("chirps_per_frame", 0)
            rx = profile.get("rx_count", 0)
            samples = profile.get("adc_samples", 0)

        if not all([frames, chirps, rx, samples]):
            raise ValueError(
                f"Cannot determine cube dimensions from manifest. "
                f"frames={frames}, chirps={chirps}, rx={rx}, samples={samples}"
            )

        return path, frames, chirps, rx, samples

    def to_cube(self, kind: str = "canonical") -> Any:
        """Parse raw data into int16 cube using the existing AWR2944 parser.

        Returns numpy ndarray of shape (frames, chirps, rx, samples).
        Does NOT invoke DSP, FFT, windowing, or MATLAB.
        """
        from awr2944_dca.awr2944_adc import parse_awr2944_real
        path, frames, chirps, rx, samples = self._resolve_dimensions(kind)
        return parse_awr2944_real(path, frames, chirps, rx, samples)

    def iter_frames(self, kind: str = "canonical") -> Any:
        """Yield each frame of the raw data as a numpy array.
        
        Yields ndarray of shape (chirps, rx, samples).
        Does NOT invoke DSP, FFT, windowing, or MATLAB.
        """
        cube = self.to_cube(kind)
        for i in range(cube.shape[0]):
            yield cube[i]

    def memmap(self, kind: str = "canonical") -> Any:
        """Memory-map the raw data file as int16.

        Returns a flat numpy memmap. Use to_cube() for shaped access.
        """
        import numpy as np
        if kind == "canonical":
            path = self.canonical_path
        elif kind == "native":
            path = self.native_path
        else:
            raise ValueError(f"Unknown kind: {kind!r}")
        if path is None or not path.exists():
            raise FileNotFoundError(f"No {kind} data file found in {self._dir}")
        return np.memmap(path, dtype="<i2", mode="r")

    # -----------------------------------------------------------------------
    # Packet metadata
    # -----------------------------------------------------------------------

    def packet_metadata(self) -> list[dict] | None:
        """Load packet metadata records from JSONL file."""
        path = self.packet_metadata_path
        if path is None:
            return None
        records = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records
