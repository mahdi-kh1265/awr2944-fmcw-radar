-- lua-launch ar1-readonly-probe
-- run_id: dde88be4
-- mode: method-only

local run_id = "dde88be4"
local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/lua_launch_ar1_readonly_probe_result.json]]
local jsonl_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/lua_launch_ar1_readonly_probe_progress.jsonl]]

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

local function progress(step, detail)
    local lf = io.open(jsonl_path, "a")
    if lf then
        if detail then
            line(lf, '{"step": ' .. esc(step) .. ', "detail": ' .. esc(detail) .. '}')
        else
            line(lf, '{"step": ' .. esc(step) .. '}')
        end
        lf:close()
    end
end

local status = "NO_LUA_START"

local ok, err = pcall(function()
    local lf = io.open(jsonl_path, "w"); if lf then lf:close() end
    progress("script_started")

    progress("before_startup_lite")
    local lite_ok, lite_err = pcall(function()

local RSTD_PATH = "C:\\\\ti\\\\mmwave_studio_03_01_04_04\\\\mmWaveStudio"
if type(RSTD) == "table" and RSTD.GetRstdPath then RSTD_PATH = RSTD.GetRstdPath() end

local ar1x_controller_path = RSTD_PATH .. "\\\\Clients\\\\AR1xController\\\\AR1xController.dll"
local registers_xml = RSTD_PATH .. "\\\\Clients\\\\AR1xController\\\\AR2944ES1P0_Registers.xml"
local al_path = RSTD_PATH .. "\\\\RunTime\\\\SAL.dll"
local client_path = RSTD_PATH .. "\\\\Clients\\\\LabClient.dll"

if type(RSTD) ~= "table" or not RSTD.UnBuild then
    error("STARTUP_LITE_FAILED: RSTD not available")
end

RSTD.UnBuild()
RSTD.SetClientDll(al_path, client_path, "", 0)

RSTD.SetVar("/Settings/AutoUpdate/Enabled", "TRUE")
RSTD.SetVar("/Settings/AutoUpdate/Interval", "1")
RSTD.SetVar("/Settings/Monitors/UpdateDisplay", "TRUE")
RSTD.SetVar("/Settings/Monitors/OneClickStart", "TRUE")
RSTD.SetVar("/Settings/Automation/Automation Mode", "false")
RSTD.Transmit("/")
RSTD.SaveClientSettings()

pcall(function() dofile(RSTD_PATH .. "\\\\Scripts\\\\Startup\\\\General_functions.lua") end)
pcall(function() dofile(RSTD_PATH .. "\\\\Scripts\\\\Startup\\\\BinDecHex.lua") end)
pcall(function() dofile(RSTD_PATH .. "\\\\Scripts\\\\Startup\\\\lib_math.lua") end)

RSTD.Build()

RSTD.RegisterDllEx(ar1x_controller_path, false)
RSTD.SetExternalAL(ar1x_controller_path)
RSTD.SetTitle("AWR-CLI")
RSTD.LoadExpose(registers_xml)

    end)
    progress("after_startup_lite", tostring(lite_ok) .. " " .. tostring(lite_err))

    if not lite_ok then
        status = "STARTUP_LITE_FAILED"
        error("STARTUP_LITE_FAILED: " .. tostring(lite_err))
    end

    progress("check_ar1_type", type(ar1))
    if type(ar1) ~= "table" then
        status = "AR1_MISSING"
        error("AR1_MISSING: type(ar1) = " .. type(ar1))
    end

    local ar1_connect_exists = (ar1.Connect ~= nil)
    local ar1_isconnected_exists = (ar1.IsConnected ~= nil)
    local ar1_sopcontrol_exists = (ar1.SOPControl ~= nil)
    progress("ar1_methods", "Connect=" .. tostring(ar1_connect_exists) .. " IsConnected=" .. tostring(ar1_isconnected_exists) .. " SOPControl=" .. tostring(ar1_sopcontrol_exists))

    local ic_ret_str = "null"

    status = "AR1_READONLY_OK"

    local f = io.open(out_path, "w")
    if not f then error("Cannot open result file") end

    line(f, "{")
    line(f, '  "run_id": ' .. esc(run_id) .. ',')
    line(f, '  "executed": true,')
    line(f, '  "status": ' .. esc(status) .. ',')
    line(f, '  "type_ar1": ' .. esc(type(ar1)) .. ',')
    line(f, '  "ar1_connect_exists": ' .. tostring(ar1_connect_exists) .. ',')
    line(f, '  "ar1_isconnected_exists": ' .. tostring(ar1_isconnected_exists) .. ',')
    line(f, '  "ar1_sopcontrol_exists": ' .. tostring(ar1_sopcontrol_exists) .. ',')
    line(f, '  "is_connected_return": ' .. ic_ret_str .. ',')
    line(f, '  "error": null')
    line(f, "}")
    f:close()
end)

if not ok then
    local f = io.open(out_path, "w")
    if f then
        line(f, "{")
        line(f, '  "run_id": ' .. esc(run_id) .. ',')
        line(f, '  "executed": false,')
        line(f, '  "status": ' .. esc(status) .. ',')
        line(f, '  "error": ' .. esc(tostring(err)))
        line(f, "}")
        f:close()
    end
end
