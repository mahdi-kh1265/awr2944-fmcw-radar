import re
from pathlib import Path
from dataclasses import dataclass, field
import json

@dataclass
class APIKey:
    name: str
    lua_type: str
    value_summary: str
    category: str = "unknown"
    risk: str = "dangerous_or_unknown"
    used_by_ti_script: bool = False
    used_in_files: list[str] = field(default_factory=list)

def classify_key(name: str) -> tuple[str, str]:
    """Heuristic classification returning (category, risk)."""
    n = name.lower()
    if n.startswith("ar1."):
        n = n[4:]
        
    # Risk overwrites
    if "poweron" in n:
        return ("connection/setup", "state_changing")
    if any(x in n for x in ["rfinit", "rfenable", "sensorstart", "framestart", "calib"]):
        return ("RF/hardware action", "capture_triggering")
        
    # Categories
    if any(n.startswith(x) for x in ["get", "version", "status", "info"]):
        return ("harmless/read-only", "safe_offline")
        
    if any(x in n for x in ["connect", "disconnect", "sopcontrol"]):
        return ("connection/setup", "state_changing")
        
    if "download" in n:
        return ("firmware/loading", "state_changing")
        
    if any(x in n for x in ["chan", "adc", "lp", "ldo", "pll", "mon", "testsource"]):
        return ("static config", "safe_with_board_no_rf")
        
    if any(x in n for x in ["profile", "chirp", "frame"]):
        return ("profile/chirp/frame config", "safe_with_board_no_rf")
        
    if any(x in n for x in ["capture", "record", "dca"]):
        return ("DCA/capture", "state_changing")
        
    # Default
    return ("unknown", "dangerous_or_unknown")

def scan_ti_scripts(search_dir: Path) -> dict[str, list[dict]]:
    """Scan Lua files in directory for ar1 calls.
    Returns dict mapping ar1 API name to list of usage instances.
    """
    results = {}
    if not search_dir.exists():
        return results
        
    # Find all Lua files recursively
    for filepath in search_dir.rglob("*.lua"):
        try:
            content = filepath.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
            
        for i, line in enumerate(content.splitlines(), start=1):
            line_str = line.strip()
            # Ignore comments
            if line_str.startswith("--"):
                continue
                
            # Find ar1.XYZ calls
            matches = re.finditer(r"ar1\.([a-zA-Z0-9_]+)", line_str)
            for m in matches:
                func_name = m.group(1)
                if func_name not in results:
                    results[func_name] = []
                    
                results[func_name].append({
                    "file": str(filepath.resolve()),
                    "line": i,
                    "text": line_str
                })
                
    return results

def generate_classification(inventory_json: dict, ti_scripts_dir: Path | None = None) -> list[APIKey]:
    keys = []
    
    usage_map = {}
    if ti_scripts_dir:
        usage_map = scan_ti_scripts(ti_scripts_dir)
        
    for k, v in inventory_json.get("ar1_keys", {}).items():
        cat, risk = classify_key(k)
        
        used_by = k in usage_map
        files_used = list(set([x["file"] for x in usage_map.get(k, [])]))
        
        key_obj = APIKey(
            name=k,
            lua_type=v.get("type", "unknown"),
            value_summary=v.get("value", ""),
            category=cat,
            risk=risk,
            used_by_ti_script=used_by,
            used_in_files=files_used
        )
        keys.append(key_obj)
        
    return sorted(keys, key=lambda x: (x.risk, x.category, x.name))

def write_outputs(keys: list[APIKey], usage_map: dict[str, list[dict]], out_dir: Path):
    # JSON
    json_path = out_dir / "ar1_inventory_classified.json"
    data = [k.__dict__ for k in keys]
    json_path.write_text(json.dumps(data, indent=2))
    
    # MD
    md_path = out_dir / "ar1_inventory_classified.md"
    md_lines = ["# ar1 API Classification\n", "## Heuristic Map\n"]
    for k in keys:
        md_lines.append(f"### {k.name}")
        md_lines.append(f"- **Category:** {k.category}")
        md_lines.append(f"- **Risk:** {k.risk}")
        md_lines.append(f"- **Type:** {k.lua_type}")
        md_lines.append(f"- **Used by TI Script:** {k.used_by_ti_script}")
        if k.used_in_files:
            md_lines.append("- **Files:**")
            for f in k.used_in_files:
                md_lines.append(f"  - `{Path(f).name}`")
        md_lines.append("")
    md_path.write_text("\n".join(md_lines))
    
    # Workflow static
    flow_path = out_dir / "ti_lua_workflow_static.md"
    flow_lines = ["# Static TI Lua Workflow Analysis\n"]
    flow_lines.append("This document shows static calls found in TI Lua scripts. These were **not** executed.\n")
    
    for func, usages in usage_map.items():
        flow_lines.append(f"## {func}")
        for u in usages:
            name = Path(u["file"]).name
            flow_lines.append(f"- `{name}:{u['line']}` : `{u['text']}`")
        flow_lines.append("")
        
    flow_path.write_text("\n".join(flow_lines))
