"""CaptureCollection — iterable collection of RadarCapture objects.

Accessible as ``project.captures``.  Provides ``.list()``, ``.get()``,
``.latest()``, iteration, and a deprecated ``__call__`` for backward
compatibility with the old ``project.captures()`` method.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterator

if TYPE_CHECKING:
    from awr2944_dca.lab import RadarCapture


class AmbiguousCaptureError(ValueError):
    """Raised when a fuzzy query matches multiple captures."""
    pass


class CaptureCollection:
    """Collection of RadarCapture objects for a project."""

    def __init__(self, project_root: Path):
        self._root = Path(project_root).resolve()

    def _load_status(self) -> dict:
        try:
            from awr2944_dca.project import project_status
            return project_status(self._root)
        except FileNotFoundError:
            # Project may use awr2944.toml without legacy project.json
            return self._build_status_from_disk()

    def _build_status_from_disk(self) -> dict:
        """Build minimal status from captures directory when project.json missing."""
        import json
        from awr2944_dca.api._status_resolver import resolve_capture_status
        captures_dir = self._root / "captures"
        managed: list[dict] = []
        if captures_dir.exists():
            for manifest_path in sorted(captures_dir.glob("*/capture_manifest.json")):
                try:
                    m = json.loads(manifest_path.read_text(encoding="utf-8"))
                    prod_path = manifest_path.parent / "manifest.json"
                    prod = None
                    if prod_path.exists():
                        try:
                            prod = json.loads(prod_path.read_text(encoding="utf-8"))
                        except (json.JSONDecodeError, IOError):
                            pass
                    resolved = resolve_capture_status(m, prod)
                    managed.append(resolved)
                except (json.JSONDecodeError, IOError):
                    pass
        newest = managed[-1] if managed else None
        return {
            "capture_count": len(managed),
            "captures": managed,
            "newest_capture": newest,
        }

    def _make_capture(self, capture_id: str) -> RadarCapture:
        from awr2944_dca.lab import RadarCapture
        return RadarCapture(self._root, capture_id)

    def list(self) -> list[RadarCapture]:
        """Return all managed captures as RadarCapture objects."""
        st = self._load_status()
        return [self._make_capture(c['capture_id']) for c in st.get('captures', [])]

    def get(self, query: str) -> RadarCapture:
        """Fuzzy lookup by capture_id prefix, name substring, or date.

        Raises AmbiguousCaptureError if multiple matches found.
        Raises ValueError if no match found.
        """
        st = self._load_status()
        all_captures = st.get('captures', [])
        matches = []
        for c in all_captures:
            cid = c.get('capture_id', '')
            cname = c.get('capture_name', '')
            if cid == query or cid.startswith(query) or query.lower() in cname.lower():
                matches.append(c)

        if len(matches) == 0:
            available = [c.get('capture_id', '') for c in all_captures]
            raise ValueError(f"No capture matching '{query}'. Available: {available}")
        if len(matches) > 1:
            listing = [
                f"  {c['capture_id']}  ({c.get('capture_name', '')})"
                for c in matches
            ]
            raise AmbiguousCaptureError(
                f"Ambiguous: '{query}' matches {len(matches)} captures. "
                f"Use the full capture_id:\n" + '\n'.join(listing)
            )
        return self._make_capture(matches[0]['capture_id'])

    def latest(self) -> RadarCapture:
        """Return the newest managed capture."""
        st = self._load_status()
        newest = st.get('newest_capture')
        if newest is None:
            raise ValueError('No captures in this project.')
        return self._make_capture(newest['capture_id'])

    @property
    def count(self) -> int:
        st = self._load_status()
        return st.get('capture_count', 0)

    def __iter__(self) -> Iterator[RadarCapture]:
        return iter(self.list())

    def __len__(self) -> int:
        return self.count

    def __call__(self) -> list[RadarCapture]:
        """DEPRECATED: Use .list() instead."""
        warnings.warn(
            "project.captures() is deprecated. Use project.captures.list() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.list()

    def __repr__(self) -> str:
        return f"CaptureCollection(count={self.count})"
