with open('src/awr2944_dca/mmws/lua_builder.py', 'a', encoding='utf-8') as f:
    f.write('''

def build_lua_launch_rstd_env_probe(run_id: str, result_path: str) -> str:
    result_path = result_path.replace("\\\\", "/")
    return f"""\\
-- lua-launch rstd-env-probe
local run_id = "{run_id}"
local out_path = [[{result_path}]]

local function esc(s)
    if s == nil then return "null" end
    s = tostring(s)
    s = s:gsub("\\\\\\\\", "\\\\\\\\\\\\\\\\")
    s = s:gsub('"', '\\\\\\\\"')
    s = s:gsub("\\\\r", "\\\\\\\\r")
    s = s:gsub("\\\\n", "\\\\\\\\n")
    s = s:gsub("\\\\t", "\\\\\\\\t")
    return '"' .. s .. '"'
end
local function line(f, s) f:write(s); f:write("\\\\n") end

local ok, err = pcall(function()
    local type_rstd = type(RSTD)
    local has_registerdllex = false
    local has_netstart = false
    if type_rstd == "table" then
        if type(RSTD.RegisterDllEx) == "function" or type(RSTD.RegisterDllEx) == "userdata" then has_registerdllex = true end
        if type(RSTD.NetStart) == "function" or type(RSTD.NetStart) == "userdata" then has_netstart = true end
    end
    
    local f = io.open(out_path, "w")
    if not f then error("Cannot open result file") end
    
    line(f, "{{\")
    line(f, '  "run_id": ' .. esc(run_id) .. ',')
    line(f, '  "executed": true,')
    line(f, '  "type_RSTD": ' .. esc(type_rstd) .. ',')
    line(f, '  "RSTD_RegisterDllEx_exists": ' .. tostring(has_registerdllex) .. ',')
    line(f, '  "RSTD_NetStart_exists": ' .. tostring(has_netstart) .. ',')
    line(f, '  "type_ar1": ' .. esc(type(ar1)) .. ',')
    line(f, '  "type_WriteToLog": ' .. esc(type(WriteToLog)) .. ',')
    line(f, '  "type_writeToLog": ' .. esc(type(writeToLog)))
    line(f, "}}\")
    f:close()
end)
if not ok then
    local f = io.open(out_path, "w")
    if f then
        line(f, "{{\")
        line(f, '  "run_id": ' .. esc(run_id) .. ',')
        line(f, '  "executed": false,')
        line(f, '  "error": ' .. esc(tostring(err)))
        line(f, "}}\")
        f:close()
    end
end
"""

def build_lua_launch_registerdll_probe(run_id: str, result_path: str) -> str:
    result_path = result_path.replace("\\\\", "/")
    return f"""\\
-- lua-launch registerdll-probe
local run_id = "{run_id}"
local out_path = [[{result_path}]]
local jsonl_path = out_path .. ".jsonl"

local function esc(s)
    if s == nil then return "null" end
    s = tostring(s)
    s = s:gsub("\\\\\\\\", "\\\\\\\\\\\\\\\\")
    s = s:gsub('"', '\\\\\\\\"')
    s = s:gsub("\\\\r", "\\\\\\\\r")
    s = s:gsub("\\\\n", "\\\\\\\\n")
    s = s:gsub("\\\\t", "\\\\\\\\t")
    return '"' .. s .. '"'
end
local function line(f, s) f:write(s); f:write("\\\\n") end

local ok, err = pcall(function()
    local lf = io.open(jsonl_path, "w")
    if lf then 
        line(lf, '{{\\"step\\": \\"start\\", \\"type_RSTD\\": ' .. esc(type(RSTD)) .. '}}')
        lf:close()
    end

    local type_RSTD = type(RSTD)
    local register_ok, register_err = false, "RSTD not found"
    if type_RSTD == "table" and RSTD.GetRstdPath then
        local rstd_path = RSTD.GetRstdPath()
        local ar1x_controller_path = rstd_path .. "\\\\\\\\Clients\\\\\\\\AR1xController\\\\\\\\AR1xController.dll"
        register_ok, register_err = pcall(function()
            RSTD.RegisterDllEx(ar1x_controller_path, false)
        end)
    end
    
    lf = io.open(jsonl_path, "a")
    if lf then 
        line(lf, '{{\\"step\\": \\"after_register\\", \\"ok\\": ' .. tostring(register_ok) .. ', \\"err\\": ' .. esc(register_err) .. '}}')
        lf:close()
    end
    
    local ar1_type = type(ar1)
    local ar1_connect_exists = false
    local ar1_isconnected_exists = false
    local ar1_sopcontrol_exists = false
    if ar1_type == "table" then
        ar1_connect_exists = (ar1.Connect ~= nil)
        ar1_isconnected_exists = (ar1.IsConnected ~= nil)
        ar1_sopcontrol_exists = (ar1.SOPControl ~= nil)
    end
    
    local f = io.open(out_path, "w")
    if not f then error("Cannot open result file") end
    
    line(f, "{{\")
    line(f, '  "run_id": ' .. esc(run_id) .. ',')
    line(f, '  "executed": true,')
    line(f, '  "type_RSTD": ' .. esc(type_RSTD) .. ',')
    line(f, '  "register_ok": ' .. tostring(register_ok) .. ',')
    line(f, '  "register_err": ' .. esc(register_err) .. ',')
    line(f, '  "type_ar1": ' .. esc(ar1_type) .. ',')
    line(f, '  "ar1_connect_exists": ' .. tostring(ar1_connect_exists) .. ',')
    line(f, '  "ar1_isconnected_exists": ' .. tostring(ar1_isconnected_exists) .. ',')
    line(f, '  "ar1_sopcontrol_exists": ' .. tostring(ar1_sopcontrol_exists))
    line(f, "}}\")
    f:close()
end)
if not ok then
    local f = io.open(out_path, "w")
    if f then
        line(f, "{{\")
        line(f, '  "run_id": ' .. esc(run_id) .. ',')
        line(f, '  "executed": false,')
        line(f, '  "error": ' .. esc(tostring(err)))
        line(f, "}}\")
        f:close()
    end
end
"""

def build_lua_launch_startup_lite_probe(run_id: str, result_path: str) -> str:
    result_path = result_path.replace("\\\\", "/")
    return f"""\\
-- lua-launch startup-lite-probe
local run_id = "{run_id}"
local out_path = [[{result_path}]]

local function esc(s)
    if s == nil then return "null" end
    s = tostring(s)
    s = s:gsub("\\\\\\\\", "\\\\\\\\\\\\\\\\")
    s = s:gsub('"', '\\\\\\\\"')
    s = s:gsub("\\\\r", "\\\\\\\\r")
    s = s:gsub("\\\\n", "\\\\\\\\n")
    s = s:gsub("\\\\t", "\\\\\\\\t")
    return '"' .. s .. '"'
end
local function line(f, s) f:write(s); f:write("\\\\n") end

local ok, err = pcall(function()
    local RSTD_PATH = "C:\\\\\\\\ti\\\\\\\\mmwave_studio_03_01_04_04\\\\\\\\mmWaveStudio"
    if type(RSTD) == "table" and RSTD.GetRstdPath then RSTD_PATH = RSTD.GetRstdPath() end
    
    local ar1x_controller_path = RSTD_PATH .. "\\\\\\\\Clients\\\\\\\\AR1xController\\\\\\\\AR1xController.dll"
    local registers_xml = RSTD_PATH .. "\\\\\\\\Clients\\\\\\\\AR1xController\\\\\\\\AR2944ES1P0_Registers.xml"
    local al_path = RSTD_PATH .. "\\\\\\\\RunTime\\\\\\\\SAL.dll"
    local client_path = RSTD_PATH .. "\\\\\\\\Clients\\\\\\\\LabClient.dll"
    
    if type(RSTD) == "table" and RSTD.UnBuild then
        RSTD.UnBuild()
        RSTD.SetClientDll(al_path, client_path, "", 0)
        
        RSTD.SetVar("/Settings/AutoUpdate/Enabled", "TRUE")
        RSTD.SetVar("/Settings/AutoUpdate/Interval", "1")
        RSTD.SetVar("/Settings/Monitors/UpdateDisplay", "TRUE")
        RSTD.SetVar("/Settings/Monitors/OneClickStart", "TRUE")
        RSTD.SetVar("/Settings/Automation/Automation Mode", "false")
        RSTD.Transmit("/")
        RSTD.SaveClientSettings()
        
        pcall(function() dofile(RSTD_PATH .. "\\\\\\\\Scripts\\\\\\\\Startup\\\\\\\\General_functions.lua") end)
        pcall(function() dofile(RSTD_PATH .. "\\\\\\\\Scripts\\\\\\\\Startup\\\\\\\\BinDecHex.lua") end)
        pcall(function() dofile(RSTD_PATH .. "\\\\\\\\Scripts\\\\\\\\Startup\\\\\\\\lib_math.lua") end)
        
        RSTD.Build()
    end
    
    local reg_ok, reg_err = false, "RSTD not table"
    if type(RSTD) == "table" and RSTD.RegisterDllEx then
        reg_ok, reg_err = pcall(function()
            RSTD.RegisterDllEx(ar1x_controller_path, false)
            RSTD.SetExternalAL(ar1x_controller_path)
            RSTD.SetTitle("Startup-Lite")
            RSTD.LoadExpose(registers_xml)
        end)
    end
    
    local f = io.open(out_path, "w")
    if not f then error("Cannot open result file") end
    
    line(f, "{{\")
    line(f, '  "run_id": ' .. esc(run_id) .. ',')
    line(f, '  "executed": true,')
    line(f, '  "lite_ok": ' .. tostring(reg_ok) .. ',')
    line(f, '  "lite_err": ' .. esc(reg_err) .. ',')
    line(f, '  "type_ar1": ' .. esc(type(ar1)))
    line(f, "}}\")
    f:close()
end)
if not ok then
    local f = io.open(out_path, "w")
    if f then
        line(f, "{{\")
        line(f, '  "run_id": ' .. esc(run_id) .. ',')
        line(f, '  "executed": false,')
        line(f, '  "error": ' .. esc(tostring(err)))
        line(f, "}}\")
        f:close()
    end
end
"""
''')
