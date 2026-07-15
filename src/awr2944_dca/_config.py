import dataclasses
import json
import logging
from pathlib import Path
from typing import Any, Dict

import tomli
import tomli_w

logger = logging.getLogger(__name__)

class ConfigMismatchError(Exception):
    """Raised when cf.json settings conflict with TOML configuration."""
    pass


@dataclasses.dataclass
class PortableConfig:
    """Portable project configuration (awr2944.toml)"""
    project_name: str = "unnamed_project"
    project_id: str = ""
    schema_version: int = 2
    
    # Defaults
    frames: int = 9
    guard_frames: int = 1
    profile: str = "smoke_v1"
    
    # Network
    dca_ip: str = "192.168.33.180"
    config_port: int = 4096
    data_port: int = 4098

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)


@dataclasses.dataclass
class LocalConfig:
    """Machine-local project configuration (.awr2944/local.toml)"""
    # Serial
    com_port: str = ""
    aux_com_port: str = ""
    baud_rate: int = 115200

    # Network
    host_ip: str = ""

    # DCA Tools
    dca_control_exe: str = ""
    dca_record_exe: str = ""
    rf_api_dll: str = ""
    cf_json_path: str = ""

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)


class ProjectConfig:
    """Combines portable and local configurations."""
    
    def __init__(self, project_root: Path):
        self.root = Path(project_root)
        self.portable = PortableConfig()
        self.local = LocalConfig()
        
        self.portable_path = self.root / "awr2944.toml"
        self.local_dir = self.root / ".awr2944"
        self.local_path = self.local_dir / "local.toml"
        
        self.load()

    def load(self) -> None:
        """Load configurations from disk if they exist."""
        if self.portable_path.exists():
            with open(self.portable_path, "rb") as f:
                p_data = tomli.load(f)
                
            proj = p_data.get("project", {})
            defaults = p_data.get("defaults", {})
            net = p_data.get("network", {})
            
            self.portable.update(
                project_name=proj.get("name", self.portable.project_name),
                project_id=proj.get("id", self.portable.project_id),
                schema_version=proj.get("schema_version", self.portable.schema_version),
                frames=defaults.get("frames", self.portable.frames),
                guard_frames=defaults.get("guard_frames", self.portable.guard_frames),
                profile=defaults.get("profile", self.portable.profile),
                dca_ip=net.get("dca_ip", self.portable.dca_ip),
                config_port=net.get("config_port", self.portable.config_port),
                data_port=net.get("data_port", self.portable.data_port),
            )
            
            # Legacy host_ip fallback
            if "host_ip" in net and not self.local_path.exists():
                self.local.host_ip = net["host_ip"]
            
        if self.local_path.exists():
            with open(self.local_path, "rb") as f:
                l_data = tomli.load(f)
                
            serial = l_data.get("serial", {})
            net = l_data.get("network", {})
            tools = l_data.get("dca_tools", {})
            
            self.local.update(
                com_port=serial.get("com_port", self.local.com_port),
                aux_com_port=serial.get("aux_com_port", self.local.aux_com_port),
                baud_rate=serial.get("baud_rate", self.local.baud_rate),
                host_ip=net.get("host_ip", self.local.host_ip),
                dca_control_exe=tools.get("control_exe", self.local.dca_control_exe),
                dca_record_exe=tools.get("record_exe", self.local.dca_record_exe),
                rf_api_dll=tools.get("rf_api_dll", self.local.rf_api_dll),
                cf_json_path=tools.get("cf_json", self.local.cf_json_path),
            )

    def save(self) -> None:
        """Save configurations to disk."""
        p_data = {
            "project": {
                "name": self.portable.project_name,
                "id": self.portable.project_id,
                "schema_version": self.portable.schema_version,
            },
            "defaults": {
                "frames": self.portable.frames,
                "guard_frames": self.portable.guard_frames,
                "profile": self.portable.profile,
            },
            "network": {
                "dca_ip": self.portable.dca_ip,
                "config_port": self.portable.config_port,
                "data_port": self.portable.data_port,
            }
        }
        
        l_data = {
            "serial": {
                "com_port": self.local.com_port,
                "aux_com_port": self.local.aux_com_port,
                "baud_rate": self.local.baud_rate,
            },
            "network": {
                "host_ip": self.local.host_ip,
            },
            "dca_tools": {
                "control_exe": self.local.dca_control_exe,
                "record_exe": self.local.dca_record_exe,
                "rf_api_dll": self.local.rf_api_dll,
                "cf_json": self.local.cf_json_path,
            }
        }
        
        with open(self.portable_path, "wb") as f:
            tomli_w.dump(p_data, f)
            
        self.local_dir.mkdir(parents=True, exist_ok=True)
        with open(self.local_path, "wb") as f:
            tomli_w.dump(l_data, f)

    def show(self) -> Dict[str, Any]:
        """Return merged configuration representation."""
        return {
            "portable": dataclasses.asdict(self.portable),
            "local": dataclasses.asdict(self.local),
        }
        
    def validate_cf_json(self) -> None:
        """Ensure the specified cf.json matches the project configuration."""
        cf_path = Path(self.local.cf_json_path)
        if not cf_path.exists():
            # If it doesn't exist, we can't validate it. It might be missing.
            raise ConfigMismatchError(f"cf.json not found at {cf_path}")
            
        with open(cf_path, "r", encoding="utf-8") as f:
            try:
                cf_data = json.load(f)
            except json.JSONDecodeError as e:
                raise ConfigMismatchError(f"Failed to parse cf.json: {e}")
                
        dca_cfg = cf_data.get("DCA1000Config", {})
        net_update = dca_cfg.get("ethernetConfigUpdate", {})
        net_base = dca_cfg.get("ethernetConfig", {})
        
        errors = []
        
        # Check System IP (Host IP)
        sys_ip = net_update.get("systemIPAddress")
        if sys_ip and sys_ip != self.local.host_ip:
            errors.append(f"Host IP mismatch: TOML={self.local.host_ip}, cf.json={sys_ip}")
            
        # Check DCA IP
        dca_ip = net_update.get("DCA1000IPAddress") or net_base.get("DCA1000IPAddress")
        if dca_ip and dca_ip != self.portable.dca_ip:
            errors.append(f"DCA IP mismatch: TOML={self.portable.dca_ip}, cf.json={dca_ip}")
            
        # Check Command Port
        cmd_port = net_update.get("DCA1000ConfigPort") or net_base.get("DCA1000ConfigPort")
        if cmd_port and cmd_port != self.portable.config_port:
            errors.append(f"Command Port mismatch: TOML={self.portable.config_port}, cf.json={cmd_port}")
            
        # Check Data Port
        data_port = net_update.get("DCA1000DataPort") or net_base.get("DCA1000DataPort")
        if data_port and data_port != self.portable.data_port:
            errors.append(f"Data Port mismatch: TOML={self.portable.data_port}, cf.json={data_port}")
            
        if errors:
            raise ConfigMismatchError("cf.json validation failed:\n  - " + "\n  - ".join(errors))
