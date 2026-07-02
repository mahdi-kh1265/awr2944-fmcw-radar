"""Experiment context discovery."""

from __future__ import annotations

from pathlib import Path


class ExperimentContext:
    """Represents a discovered experiment context."""

    def __init__(self, root_dir: Path, config_path: Path):
        self.root_dir = root_dir
        self.config_path = config_path


def discover_context(start_path: Path | None = None) -> ExperimentContext | None:
    """Find the nearest enclosing experiment directory.
    
    Searches upward from `start_path` (or current directory) for
    `.awr-experiment` and `capture.yaml`.
    
    Returns ExperimentContext if found, else None.
    """
    current = (start_path or Path.cwd()).resolve()

    while True:
        if (current / ".awr-experiment").exists() and (current / "capture.yaml").exists():
            return ExperimentContext(
                root_dir=current,
                config_path=current / "capture.yaml",
            )
        
        parent = current.parent
        if parent == current:
            break
        current = parent

    return None
