"""Profile collection management for AWR2944 projects."""

from __future__ import annotations
from pathlib import Path
import dataclasses
from typing import Any
import re

from awr2944_dca.api.profile import RadarProfile

_WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
}

def is_valid_profile_name(name: str) -> bool:
    """Validate profile name prevents path traversal and reserved names."""
    if not name or not isinstance(name, str):
        return False
    if "/" in name or "\\" in name:
        return False
    if name.startswith("."):
        return False
    if name.upper() in _WINDOWS_RESERVED:
        return False
    # Only allow word characters, hyphens, and spaces
    if not re.match(r"^[\w\-\s]+$", name):
        return False
    return True

@dataclasses.dataclass
class ProfileEntry:
    name: str
    origin: str  # "project" or "built_in"
    path: Path | None
    shadows_built_in: bool

class ProfileCollection:
    """Manages reading and writing structured profiles in a RadarProject."""
    
    def __init__(self, profiles_dir: Path):
        self._dir = Path(profiles_dir).resolve()
        self._built_ins = {
            "smoke_v1": RadarProfile.smoke_v1()
        }
        
    def _get_path(self, name: str) -> Path:
        if not is_valid_profile_name(name):
            raise ValueError(f"Invalid profile name: {name}")
        return self._dir / f"{name}.toml"

    def list(self) -> list[ProfileEntry]:
        """List all available profiles."""
        entries = {}
        
        # Add built-ins
        for name in self._built_ins:
            entries[name] = ProfileEntry(
                name=name,
                origin="built_in",
                path=None,
                shadows_built_in=False
            )
            
        # Add local project profiles
        if self._dir.exists():
            for p in self._dir.glob("*.toml"):
                name = p.stem
                if not is_valid_profile_name(name):
                    continue
                if name in entries:
                    entries[name].origin = "project"
                    entries[name].path = p
                    entries[name].shadows_built_in = True
                else:
                    entries[name] = ProfileEntry(
                        name=name,
                        origin="project",
                        path=p,
                        shadows_built_in=False
                    )
                    
        return list(entries.values())

    def get(self, name: str) -> RadarProfile:
        """Load a profile by name."""
        path = self._get_path(name)
        if path.exists():
            return RadarProfile.from_toml(path.read_text(encoding="utf-8"))
            
        if name in self._built_ins:
            return self._built_ins[name]
            
        raise FileNotFoundError(f"Profile not found: {name}")

    def load(self, name: str) -> RadarProfile:
        """Alias for get()."""
        return self.get(name)

    def save(self, profile: RadarProfile, overwrite: bool = False) -> None:
        """Save a profile to the project."""
        if not is_valid_profile_name(profile.name):
            raise ValueError(f"Invalid profile name: {profile.name}")
            
        path = self._get_path(profile.name)
        if path.exists() and not overwrite:
            raise FileExistsError(f"Profile {profile.name} already exists. Use overwrite=True to replace.")
            
        self._dir.mkdir(parents=True, exist_ok=True)
        path.write_text(profile.to_toml(), encoding="utf-8")

    def delete(self, name: str) -> None:
        """Delete a profile from the project."""
        if not is_valid_profile_name(name):
            raise ValueError(f"Invalid profile name: {name}")
            
        path = self._get_path(name)
        if not path.exists():
            if name in self._built_ins:
                raise ValueError(f"Cannot delete built-in profile: {name}")
            raise FileNotFoundError(f"Profile not found: {name}")
            
        path.unlink()
