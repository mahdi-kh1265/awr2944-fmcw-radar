"""mmWave Studio installation discovery.

Wraps existing ``ti.probe`` installation finding and adds helpers for
locating scripts and firmware directories within an installation.
"""

from __future__ import annotations

from pathlib import Path


class StudioInstallation:
    """Represents a discovered mmWave Studio installation."""

    def __init__(self, path: Path):
        self.path = path
        self.exe_path = path / "mmWaveStudio" / "RunTime" / "mmWaveStudio.exe"

    @property
    def is_valid(self) -> bool:
        return self.exe_path.exists()

    @property
    def version_dir(self) -> str:
        """e.g. 'mmwave_studio_03_01_04_04'."""
        return self.path.name

    @property
    def scripts_dir(self) -> Path:
        return self.path / "mmWaveStudio" / "Scripts"

    @property
    def firmware_dir(self) -> Path:
        return self.path / "mmWaveStudio" / "rf_eval_firmware"

    def __repr__(self) -> str:
        return f"StudioInstallation({self.path})"


_TI_BASE = Path("C:/ti")


def discover_installations(base: Path | None = None) -> list[StudioInstallation]:
    """Find all mmWave Studio installations under ``C:\\ti``."""
    search = base if base is not None else _TI_BASE
    if not search.exists() or not search.is_dir():
        return []

    installs = []
    for child in search.iterdir():
        if child.is_dir() and "mmwave_studio" in child.name.lower():
            inst = StudioInstallation(child)
            if inst.is_valid:
                installs.append(inst)
    return installs
