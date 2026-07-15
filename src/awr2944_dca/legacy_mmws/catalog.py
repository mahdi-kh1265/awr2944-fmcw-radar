"""API catalog: scan TI mmWave Studio scripts for ar1 calls.

Scans ``C:\\ti\\mmwave_studio_*\\mmWaveStudio`` directories for Lua, txt,
cfg, and json files containing ar1.* calls.  Builds a catalog that
classifies each call by category and risk level.

Unknown functions are marked ``unknown`` — they are never guessed.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from awr2944_dca.legacy_mmws.stages import ALL_KNOWN_CALLS
from awr2944_dca.ti.classify import classify_key


@dataclass
class CatalogEntry:
    """One ar1 API function discovered in TI scripts."""

    name: str
    category: str = "unknown"
    risk: str = "dangerous_or_unknown"
    known_stage: bool = False
    source_files: list[dict] = field(default_factory=list)
    notes: str = ""


def discover_mmws_installations(base: Path | None = None) -> list[Path]:
    """Find mmWave Studio installation directories under C:\\ti."""
    if base is None:
        base = Path("C:/ti")
    if not base.exists():
        return []
    results = []
    for child in base.iterdir():
        if child.is_dir() and "mmwave_studio" in child.name.lower():
            studio_dir = child / "mmWaveStudio"
            if studio_dir.exists():
                results.append(studio_dir)
    return results


def scan_scripts(search_dirs: list[Path]) -> dict[str, CatalogEntry]:
    """Scan directories for ar1.* calls in script files.

    Returns a dict mapping function name -> CatalogEntry.
    """
    catalog: dict[str, CatalogEntry] = {}
    extensions = {"*.lua", "*.txt", "*.cfg", "*.json"}

    for search_dir in search_dirs:
        for ext in extensions:
            for filepath in search_dir.rglob(ext):
                try:
                    content = filepath.read_text(encoding="utf-8")
                except (UnicodeDecodeError, PermissionError):
                    continue

                for i, line in enumerate(content.splitlines(), start=1):
                    stripped = line.strip()
                    if stripped.startswith("--"):
                        continue

                    for m in re.finditer(r"ar1\.([a-zA-Z0-9_]+)", stripped):
                        func = m.group(1)

                        if func not in catalog:
                            cat, risk = classify_key(func)
                            known = func in ALL_KNOWN_CALLS
                            notes = ""
                            if not known:
                                notes = (
                                    "Unknown function. May require manual inspection "
                                    "in mmWave Studio GUI."
                                )
                            catalog[func] = CatalogEntry(
                                name=func,
                                category=cat,
                                risk=risk,
                                known_stage=known,
                                notes=notes,
                            )

                        catalog[func].source_files.append({
                            "file": str(filepath),
                            "line": i,
                            "text": stripped[:120],  # truncate long lines
                        })

    return catalog


def write_catalog(catalog: dict[str, CatalogEntry], out_dir: Path) -> tuple[Path, Path]:
    """Write the API catalog as JSON and Markdown."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # JSON
    json_path = out_dir / "mmws_api_catalog.json"
    data = {}
    for name, entry in sorted(catalog.items()):
        data[name] = {
            "category": entry.category,
            "risk": entry.risk,
            "known_stage": entry.known_stage,
            "usage_count": len(entry.source_files),
            "notes": entry.notes,
            "source_files": [
                {"file": Path(s["file"]).name, "line": s["line"]}
                for s in entry.source_files[:5]  # limit to 5 examples
            ],
        }
    json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Markdown
    md_path = out_dir / "mmws_api_catalog.md"
    lines = [
        "# mmWave Studio API Catalog\n",
        "Auto-generated from scanning TI mmWave Studio scripts.\n",
        "| Function | Category | Risk | Known Stage | Usages | Notes |",
        "|----------|----------|------|-------------|--------|-------|",
    ]
    for name, entry in sorted(catalog.items()):
        notes = entry.notes or ""
        lines.append(
            f"| `ar1.{name}` | {entry.category} | {entry.risk} "
            f"| {'✓' if entry.known_stage else '✗'} "
            f"| {len(entry.source_files)} | {notes} |"
        )
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    return json_path, md_path
