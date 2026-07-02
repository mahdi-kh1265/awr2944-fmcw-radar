import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

try:
    import serial.tools.list_ports
    HAVE_PYSERIAL = True
except ImportError:
    HAVE_PYSERIAL = False

@dataclass
class PortInfo:
    com: str
    friendly_name: str
    manufacturer: str
    hwid: str
    likely_role: str
    confidence: str
    reason: str

def scan_ports() -> list[PortInfo]:
    if not HAVE_PYSERIAL:
        raise RuntimeError("pyserial is required to scan ports.")
        
    ports = serial.tools.list_ports.comports()
    results = []
    
    for p in ports:
        name = p.description or ""
        mfg = p.manufacturer or ""
        hwid = p.hwid or ""
        
        name_lower = name.lower()
        mfg_lower = mfg.lower()
        
        role = "unknown"
        conf = "low"
        reason = "No matches"
        
        # Heuristics
        if "application/user" in name_lower or "user uart" in name_lower:
            role = "awr-rs232"
            conf = "high"
            reason = "Matches standard TI mmWave Application/User UART signature."
        elif "xds110" in name_lower:
            role = "ti-debug-uart"
            conf = "medium"
            reason = "Matches XDS110 debugger, might be Application or Data port."
        elif "ftdi" in name_lower or "ftdi" in mfg_lower:
            role = "possible_ftdi"
            conf = "low"
            reason = "FTDI chip found, could be DCA1000 or DevPack."
        elif any(x in name_lower for x in ["dca", "devpack", "capture", "dca1000", "ar-devpack"]):
            role = "capture_control"
            conf = "medium"
            reason = "Name indicates capture or DevPack control port."
            
        results.append(PortInfo(
            com=p.device,
            friendly_name=name,
            manufacturer=mfg,
            hwid=hwid,
            likely_role=role,
            confidence=conf,
            reason=reason
        ))
        
    return results

def resolve_port(role: str) -> list[PortInfo]:
    ports = scan_ports()
    
    def rank(p: PortInfo) -> int:
        if p.likely_role == role and p.confidence == "high": return 3
        if p.likely_role == role and p.confidence == "medium": return 2
        if p.likely_role == role: return 1
        return 0
        
    return sorted(ports, key=rank, reverse=True)

def get_local_hardware_config(exp_root: Path) -> dict:
    cfg = exp_root / "local_hardware.yaml"
    if not cfg.exists():
        return {}
    try:
        return yaml.safe_load(cfg.read_text()) or {}
    except Exception:
        return {}

def save_local_hardware(exp_root: Path, role: str, com_port: str) -> Path:
    cfg = exp_root / "local_hardware.yaml"
    data = get_local_hardware_config(exp_root)
    
    if "hardware" not in data:
        data["hardware"] = {}
        
    role_key = role.replace("-", "_") + "_com"
    data["hardware"][role_key] = com_port
    
    cfg.write_text(yaml.dump(data, default_flow_style=False))
    return cfg
