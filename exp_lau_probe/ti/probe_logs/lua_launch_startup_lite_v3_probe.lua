local run_id = "a55ccf71"
local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/lua_launch_startup_lite_v3_probe_result.json]]
local jsonl_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/lua_launch_startup_lite_v3_probe_progress.jsonl]]

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

local status = "NO_START"
local gv_ret = nil

local ok, err = pcall(function()
    local lf = io.open(jsonl_path, "w"); if lf then lf:close() end
    progress("script_started")

    local RSTD_PATH = RSTD.GetRstdPath()
    progress("rstd_path", RSTD_PATH)

    progress("before_RTTT_alias")
    if type(RSTD) == "table" then RTTT = RSTD end
    progress("after_RTTT_alias", "type(RTTT)=" .. type(RTTT))

    progress("before_AR1_GUI")
    AR1_GUI = true
    progress("after_AR1_GUI", tostring(AR1_GUI))

    local runtime_path = RSTD_PATH .. "\\RunTime"
    package.path = ".\\?.lua;"
        .. runtime_path .. "\\lua\\?.lua;"
        .. runtime_path .. "\\lua\\?\\init.lua;"
        .. runtime_path .. "\\?.lua;"
        .. runtime_path .. "\\?\\init.lua;"
        .. runtime_path .. "\\LuaScripts\\?.lua;"
        .. runtime_path .. "\\..\\Clients\\LuaModules\\LuaSocket\\?.lua"
    progress("package_path_set", package.path)

    local ar1x_controller_path = RSTD_PATH .. "\\Clients\\AR1xController\\AR1xController.dll"
    local registers_xml = RSTD_PATH .. "\\Clients\\AR1xController\\AR2944ES1P0_Registers.xml"
    local al_path = RSTD_PATH .. "\\RunTime\\SAL.dll"
    local client_path = RSTD_PATH .. "\\Clients\\LabClient.dll"

    RSTD.UnBuild()
    RSTD.SetClientDll(al_path, client_path, "", 0)
    RSTD.SetVar("/Settings/AutoUpdate/Enabled", "TRUE")
    RSTD.SetVar("/Settings/AutoUpdate/Interval", "1")
    RSTD.SetVar("/Settings/Monitors/UpdateDisplay", "TRUE")
    RSTD.SetVar("/Settings/Monitors/OneClickStart", "TRUE")
    RSTD.SetVar("/Settings/Automation/Automation Mode", "false")
    RSTD.Transmit("/")
    RSTD.SaveClientSettings()
    RSTD.SetAndTransmit("/Settings/Scripter/Display DateTime", "1")
    RSTD.SetAndTransmit("/Settings/Scripter/DateTime Format", "HH:mm:ss")

    pcall(function() dofile(RSTD_PATH .. "\\Scripts\\Startup\\General_functions.lua") end)
    pcall(function() dofile(RSTD_PATH .. "\\Scripts\\Startup\\BinDecHex.lua") end)
    pcall(function() dofile(RSTD_PATH .. "\\Scripts\\Startup\\lib_math.lua") end)

    progress("before_Build")
    RSTD.Build()
    progress("after_Build")

    progress("before_RegisterDllEx")
    RSTD.RegisterDllEx(ar1x_controller_path, false)
    RSTD.SetExternalAL(ar1x_controller_path)
    progress("after_RegisterDllEx", "type(ar1)=" .. type(ar1))

    progress("before_GuiVersion")
    local gv_ok2
    gv_ok2, gv_ret = pcall(function() return ar1.GuiVersion() end)
    progress("after_GuiVersion", tostring(gv_ok2) .. " " .. tostring(gv_ret))
    if gv_ok2 and gv_ret then
        RSTD.SetTitle(tostring(gv_ret))
    else
        RSTD.SetTitle("AWR-CLI")
    end

    progress("before_LoadExpose")
    RSTD.LoadExpose(registers_xml)
    progress("after_LoadExpose")

    status = "STARTUP_LITE_V3_OK"

    local f = io.open(out_path, "w")
    if f then
        line(f, "{")
        line(f, '  "run_id": ' .. esc(run_id) .. ',')
        line(f, '  "executed": true,')
        line(f, '  "status": ' .. esc(status) .. ',')
        line(f, '  "type_ar1": ' .. esc(type(ar1)) .. ',')
        line(f, '  "type_RTTT": ' .. esc(type(RTTT)) .. ',')
        line(f, '  "AR1_GUI": ' .. tostring(AR1_GUI) .. ',')
        line(f, '  "gui_version": ' .. esc(gv_ret) .. ',')
        line(f, '  "error": null')
        line(f, "}")
        f:close()
    end
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
