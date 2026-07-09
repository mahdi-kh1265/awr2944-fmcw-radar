import subprocess
import json
import dataclasses
from typing import List, Optional, Tuple, Dict, Any

@dataclasses.dataclass
class NetworkAdapter:
    interface_alias: str
    interface_index: int
    status: str
    link_speed: str
    mac_address: str
    ipv4_addresses: List[str]
    has_default_gateway: bool
    has_dns: bool
    
    score: int = 0
    reason: str = ""
    is_safe: bool = False

def get_adapters() -> List[NetworkAdapter]:
    """Retrieve non-virtual network adapters and their networking details via PowerShell."""
    ps_script = """
$ErrorActionPreference = 'SilentlyContinue'
$adapters = Get-NetAdapter | Where-Object { $_.Virtual -eq $false -and $_.MacAddress }

$results = @()
foreach ($a in $adapters) {
    $idx = $a.InterfaceIndex
    $ips = (Get-NetIPAddress -InterfaceIndex $idx -AddressFamily IPv4 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty IPAddress)
    $routes = (Get-NetRoute -InterfaceIndex $idx -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue)
    $dns = (Get-DnsClientServerAddress -InterfaceIndex $idx -AddressFamily IPv4 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ServerAddresses)
    
    $ipList = @()
    if ($ips) {
        if ($ips -is [array]) { $ipList = $ips } else { $ipList = @($ips) }
    }
    
    $obj = @{
        InterfaceAlias = $a.Name
        InterfaceIndex = $idx
        Status = $a.Status
        LinkSpeed = $a.LinkSpeed
        MacAddress = $a.MacAddress
        IPv4Addresses = $ipList
        HasDefaultGateway = if ($routes) { $true } else { $false }
        HasDns = if ($dns) { $true } else { $false }
    }
    $results += $obj
}

$results | ConvertTo-Json -Depth 3 -Compress
"""
    try:
        output = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", ps_script], 
            text=True, 
            creationflags=subprocess.CREATE_NO_WINDOW
        ).strip()
        
        if not output:
            return []
            
        data = json.loads(output)
        if isinstance(data, dict):
            data = [data]
            
        adapters = []
        for d in data:
            adapters.append(NetworkAdapter(
                interface_alias=d.get("InterfaceAlias", "Unknown"),
                interface_index=d.get("InterfaceIndex", 0),
                status=d.get("Status", "Unknown"),
                link_speed=d.get("LinkSpeed", "Unknown"),
                mac_address=d.get("MacAddress", ""),
                ipv4_addresses=d.get("IPv4Addresses", []),
                has_default_gateway=d.get("HasDefaultGateway", False),
                has_dns=d.get("HasDns", False)
            ))
        return adapters
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return []

def score_adapter(adapter: NetworkAdapter) -> Tuple[int, str, bool]:
    """
    Score an adapter for its likelihood of being the DCA connection.
    Returns (score, reason, is_safe).
    """
    name_lower = adapter.interface_alias.lower()
    
    if "wi-fi" in name_lower or "wireless" in name_lower:
        return (-100, "Refused: Wi-Fi adapter", False)
        
    if adapter.has_default_gateway:
        # e.g. campus internet
        return (-50, "Refused: Has default gateway", False)
        
    score = 0
    reasons = []
    
    if "192.168.33.30" in adapter.ipv4_addresses:
        score += 100
        reasons.append("Strong PASS: Already configured for DCA1000")
    else:
        # Evaluate standard unconfigured or APIPA link
        if not adapter.has_default_gateway:
            score += 1
            reasons.append("Positive: No default gateway")
            
        has_apipa = any(ip.startswith("169.254.") for ip in adapter.ipv4_addresses)
        if has_apipa:
            score += 1
            reasons.append("Positive: APIPA (169.254.x.x) detected")
            
        if adapter.status.lower() == "disconnected":
            reasons.append("Warning: Disconnected")
            
        if "ethernet" in name_lower:
            score += 1
            reasons.append("Positive: Physical Ethernet")

    reason_str = ", ".join(reasons) if reasons else "Neutral candidate"
    is_safe = score > 0
    return score, reason_str, is_safe

def suggest_dca_adapter(adapters: List[NetworkAdapter] = None) -> Optional[NetworkAdapter]:
    """Find the best safe candidate adapter."""
    if adapters is None:
        adapters = get_adapters()
        
    best_adapter = None
    best_score = 0
    
    for a in adapters:
        score, reason, is_safe = score_adapter(a)
        a.score = score
        a.reason = reason
        a.is_safe = is_safe
        
        if is_safe and score > best_score:
            best_score = score
            best_adapter = a
            
    return best_adapter
