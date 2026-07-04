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
        if "dca1000" in name_lower or "dca" in name_lower or (hwid and "VID:PID=0403:6010" in hwid):
            role = "dca_ftdi_candidate"
            conf = "high"
            reason = "Matches DCA1000 FTDI signature. Do not use for AWR RS232."
        elif "ar-devpack" in name_lower or "ftdi" in name_lower or "ftdi" in mfg_lower:
            role = "awr_ftdi_control_candidate"
            conf = "medium"
            reason = "Matches AWR2944 J10 FTDI (radar UART/SPI/I2C/RS232/SOP)."
        elif "application/user" in name_lower or "user uart" in name_lower:
            role = "awr_rs232_candidate"
            conf = "high"
            reason = "Matches standard TI mmWave Application/User UART signature."
        elif "xds110" in name_lower:
            role = "awr_xds_uart_candidate"
            conf = "high"
            reason = "Matches AWR2944 J8 XDS (JTAG/MSS UART). Not typically used for mmWave Studio RS232 on this board."
            
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
