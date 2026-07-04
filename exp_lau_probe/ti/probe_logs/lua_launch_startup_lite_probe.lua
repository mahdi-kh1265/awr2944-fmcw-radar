-- lua-launch startup-lite-probe
local run_id = "cf7b6c2a"
local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/lua_launch_startup_lite_probe_result.json]]

local function esc(s)
    if s == nil then return "null" end
    s = tostring(s)
    s = s:gsub("\\", "\\\\")
    s = s:gsub('"', '\\"')
    s = s:gsub("\r", "\\r")
    s = s:gsub("\n", "\\n")
    s = s:gsub("\t", "\\t")
    return '"' .. s .. '"'
end
local function line(f, s) f:write(s); f:write("\n") end

local ok, err = pcall(function()
    local RSTD_PATH = "C:\\ti\\mmwave_studio_03_01_04_04\\mmWaveStudio"
    if type(RSTD) == "table" and RSTD.GetRstdPath then RSTD_PATH = RSTD.GetRstdPath() end
    
    local ar1x_controller_path = RSTD_PATH .. "\\Clients\\AR1xController\\AR1xController.dll"
    local registers_xml = RSTD_PATH .. "\\Clients\\AR1xController\\AR2944ES1P0_Registers.xml"
    local al_path = RSTD_PATH .. "\\RunTime\\SAL.dll"
    local client_path = RSTD_PATH .. "\\Clients\\LabClient.dll"
    
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
        
        pcall(function() dofile(RSTD_PATH .. "\\Scripts\\Startup\\General_functions.lua") end)
        pcall(function() dofile(RSTD_PATH .. "\\Scripts\\Startup\\BinDecHex.lua") end)
        pcall(function() dofile(RSTD_PATH .. "\\Scripts\\Startup\\lib_math.lua") end)
        
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
    
    line(f, "{")
    line(f, '  "run_id": ' .. esc(run_id) .. ',')
    line(f, '  "executed": true,')
    line(f, '  "lite_ok": ' .. tostring(reg_ok) .. ',')
    line(f, '  "lite_err": ' .. esc(reg_err) .. ',')
    line(f, '  "type_ar1": ' .. esc(type(ar1)))
    line(f, "}")
    f:close()
end)
if not ok then
    local f = io.open(out_path, "w")
    if f then
        line(f, "{")
        line(f, '  "run_id": ' .. esc(run_id) .. ',')
        line(f, '  "executed": false,')
        line(f, '  "error": ' .. esc(tostring(err)))
        line(f, "}")
        f:close()
    end
end
