"""Offline probe and automation utilities for TI mmWave Studio."""

from __future__ import annotations

import os
from pathlib import Path

# Common mmWave Studio install paths on Windows
_TI_PATHS = [
    Path("C:/ti"),
    # For CI or non-Windows, we also allow the local repo if it has mock paths
]

class StudioInstallation:
    def __init__(self, path: Path):
        self.path = path
        self.exe_path = path / "mmWaveStudio" / "RunTime" / "mmWaveStudio.exe"
        
    @property
    def is_valid(self) -> bool:
        return self.exe_path.exists()

def find_studio() -> list[StudioInstallation]:
    """Find all mmWave Studio installations."""
    installs = []
    
    for base in _TI_PATHS:
        if not base.exists() or not base.is_dir():
            continue
            
        for child in base.iterdir():
            if child.is_dir() and "mmwave_studio" in child.name.lower():
                installs.append(StudioInstallation(child))
                
    # Keep it simple for now, return valid installs
    return [i for i in installs if i.is_valid]

def generate_probe_script(out_path: Path, probe_id: str = "") -> Path:
    """Generate a harmless Lua script that prints a log and saves JSON results."""
    # Convert path to forward slashes for Lua
    result_path = str(out_path.parent / "probe_result.json").replace("\\", "/")
    
    script = f"""-- AWR2944 DCA Lab - Offline Probe

local probe_executed = true
local ar1_available = false
local write_to_log_available = false

-- Safe logging function
local function SafeLog(msg, color)
    local status, err = pcall(function()
        WriteToLog(msg, color)
    end)
    if status then
        write_to_log_available = true
    end
end

SafeLog("=========================================\\n", "green")
SafeLog("PROBE SUCCESS: mmWave Studio Lua execution works!\\n", "green")
SafeLog("=========================================\\n", "green")

-- Try a harmless ar1 command if available (just getting version/help)
if ar1 then
    ar1_available = true
    SafeLog("ar1 API is available.\\n", "blue")
else
    SafeLog("ar1 API is NOT available.\\n", "red")
end

-- Write result to JSON manually
local json_str = string.format([[
{{
    "probe_id": "%s",
    "probe_executed": %s,
    "ar1_available": %s,
    "write_to_log_available": %s
}}
]], "{probe_id}", tostring(probe_executed), tostring(ar1_available), tostring(write_to_log_available))

local file, err = io.open("{result_path}", "w")
if file then
    file:write(json_str)
    file:close()
else
    SafeLog("ERROR writing JSON: " .. tostring(err) .. "\\n", "red")
end
"""
    out_path.write_text(script, encoding="utf-8")
    return out_path


def generate_inventory_script(out_path: Path, probe_id: str) -> Path:
    """Generate a read-only Lua script that dumps ar1 APIs and globals."""
    result_path = str(out_path.parent / "inventory_result.json").replace("\\", "/")

    script = f"""-- AWR2944 DCA Lab - Offline Inventory
local result = {{
    probe_id = "{probe_id}",
    inventory_executed = true,
    ar1_exists = false,
    ar1_type = "nil",
    ar1_iterable = false,
    ar1_keys = {{}},
    g_keys = {{}}
}}

-- Tiny JSON escaper
local function escapeJSON(s)
    if type(s) ~= "string" then return tostring(s) end
    s = s:gsub("\\\\", "\\\\\\\\")
    s = s:gsub('\\"', '\\\\\\"')
    s = s:gsub("\\n", "\\\\n")
    s = s:gsub("\\r", "\\\\r")
    s = s:gsub("\\t", "\\\\t")
    -- truncate long strings
    if string.len(s) > 200 then
        s = string.sub(s, 1, 200) .. "..."
    end
    return s
end

local function record_ar1()
    if ar1 == nil then return end
    result.ar1_exists = true
    result.ar1_type = type(ar1)
    
    local status, err = pcall(function()
        local count = 0
        for k, v in pairs(ar1) do
            if count >= 500 then break end
            local key_str = escapeJSON(tostring(k))
            local type_str = type(v)
            local val_str = escapeJSON(tostring(v))
            table.insert(result.ar1_keys, string.format('        \\"%s\\": {{"type": \\"%s\\", "value": \\"%s\\"}}', key_str, type_str, val_str))
            count = count + 1
        end
        result.ar1_iterable = true
    end)
    
    if not status then
        result.ar1_iterable = false
        result.ar1_error = escapeJSON(err)
    end
end

local function record_G()
    local status, err = pcall(function()
        local count = 0
        for k, v in pairs(_G) do
            if count >= 500 then break end
            local key_str = escapeJSON(tostring(k))
            local type_str = type(v)
            table.insert(result.g_keys, string.format('        \\"%s\\": \\"%s\\"', key_str, type_str))
            count = count + 1
        end
    end)
end

record_ar1()
record_G()

-- Construct JSON string manually
local ar1_keys_json = table.concat(result.ar1_keys, ",\\n")
local g_keys_json = table.concat(result.g_keys, ",\\n")
local ar1_error_json = result.ar1_error and string.format(',\\n    "ar1_error": "%s"', result.ar1_error) or ""

local json_str = string.format([[
{{
    "probe_id": "%s",
    "inventory_executed": true,
    "ar1_exists": %s,
    "ar1_type": "%s",
    "ar1_iterable": %s%s,
    "ar1_keys": {{
%s
    }},
    "_G_keys": {{
%s
    }}
}}
]], result.probe_id, tostring(result.ar1_exists), result.ar1_type, tostring(result.ar1_iterable), ar1_error_json, ar1_keys_json, g_keys_json)

local file, err = io.open("{result_path}", "w")
if file then
    file:write(json_str)
    file:close()
end
"""
    out_path.write_text(script, encoding="utf-8")
    return out_path


def static_scan_for_hardware_actions(script_path: Path) -> list[str]:
    """Scan a Lua script for commands that interact with hardware.
    
    Returns a list of matched dangerous patterns.
    """
    dangerous_patterns = [
        "ar1.Connect",
        "ar1.SOPControl",
        "ar1.PowerOn",
        "ar1.RfEnable",
        "ar1.StartFrame",
        "ar1.CaptureCardConfig_StartRecord",
        "ar1.DownloadBSSFw",
        "ar1.DownloadMSSFw",
    ]
    
    content = script_path.read_text(encoding="utf-8")
    found = []
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("--"):
            continue  # ignore comments
        for pattern in dangerous_patterns:
            if pattern in line:
                found.append(line)
                
    return found

def generate_connection_probe_script(out_path: Path, run_id: str, com_num: int, baud: int = 921600, timeout_ms: int = 1000) -> None:
    """Generate a connection-only Lua script."""
    
    script = f"""-- Connection-Only Hardware Probe
-- Generated by awr2944_dca

local run_id = "{run_id}"
local out_path = "{str(out_path.parent.resolve()).replace('\\', '/')}/connection_result.json"

local function escapeJSON(s)
    if s == nil then return "null" end
    s = tostring(s)
    s = string.gsub(s, '\\\\', '\\\\\\\\')
    s = string.gsub(s, '"', '\\\\"')
    s = string.gsub(s, '\\n', '\\\\n')
    s = string.gsub(s, '\\r', '\\\\r')
    return s
end

local result = {{
    run_id = run_id,
    executed = true,
    com_display = "COM" .. tostring({com_num}),
    com_number = {com_num},
    baud = {baud},
    timeout_ms = {timeout_ms},
    sop_control_called = false,
    sop_control_return = nil,
    connect_called = false,
    connect_return = nil,
    is_connected_called = false,
    is_connected_return = nil,
    error = nil
}}

local function writeResult()
    local f, err = io.open(out_path, "w")
    if f then
        f:write('{{\\n')
        f:write('  "run_id": "' .. result.run_id .. '",\\n')
        f:write('  "executed": ' .. tostring(result.executed) .. ',\\n')
        f:write('  "com_display": "' .. result.com_display .. '",\\n')
        f:write('  "com_number": ' .. tostring(result.com_number) .. ',\\n')
        f:write('  "baud": ' .. tostring(result.baud) .. ',\\n')
        f:write('  "timeout_ms": ' .. tostring(result.timeout_ms) .. ',\\n')
        f:write('  "sop_control_called": ' .. tostring(result.sop_control_called) .. ',\\n')
        f:write('  "sop_control_return": ' .. escapeJSON(result.sop_control_return) .. ',\\n')
        f:write('  "connect_called": ' .. tostring(result.connect_called) .. ',\\n')
        f:write('  "connect_return": ' .. escapeJSON(result.connect_return) .. ',\\n')
        f:write('  "is_connected_called": ' .. tostring(result.is_connected_called) .. ',\\n')
        f:write('  "is_connected_return": ' .. escapeJSON(result.is_connected_return) .. ',\\n')
        if result.error then
            f:write('  "error": "' .. escapeJSON(result.error) .. '"\\n')
        else
            f:write('  "error": null\\n')
        end
        f:write('}}\\n')
        f:close()
    end
end

local function safeLog(msg)
    if ar1 and ar1.WriteToLog then
        pcall(function() ar1.WriteToLog(msg .. "\\n") end)
    end
end

local function run()
    if not ar1 then
        result.error = "ar1 API not available"
        return
    end
    
    -- SOP Control
    if ar1.SOPControl then
        result.sop_control_called = true
        local status, ret = pcall(function() return ar1.SOPControl(2) end)
        if status then
            result.sop_control_return = ret
            safeLog("SOPControl(2) returned: " .. tostring(ret))
        else
            result.error = "SOPControl crashed: " .. tostring(ret)
            return
        end
    end
    
    -- Connect
    if ar1.Connect then
        result.connect_called = true
        local status, ret = pcall(function() return ar1.Connect({com_num}, {baud}, {timeout_ms}) end)
        if status then
            result.connect_return = ret
            safeLog("Connect({com_num}, {baud}, {timeout_ms}) returned: " .. tostring(ret))
        else
            result.error = "Connect crashed: " .. tostring(ret)
            return
        end
    end
    
    -- IsConnected
    if ar1.IsConnected then
        result.is_connected_called = true
        local status, ret = pcall(function() return ar1.IsConnected() end)
        if status then
            result.is_connected_return = ret
            safeLog("IsConnected() returned: " .. tostring(ret))
        else
            -- Ignore crash in IsConnected, not as critical
            result.error = (result.error or "") .. " | IsConnected crashed"
        end
    end
end

pcall(run)
writeResult()
"""
    out_path.write_text(script, encoding="utf-8")
