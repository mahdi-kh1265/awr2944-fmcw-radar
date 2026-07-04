local run_id = "65f0dda2"
local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/connection_connect_gui_result.json]]
local jsonl_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/connection_connect_gui_progress.jsonl]]
local sequence = "select-set-connect"

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
local c_ret_str = "null"
local c1_ret_str = "null"
local c2_ret_str = "null"
local sop_ret_str = "null"
local dv_ret_str = "null"
local fb_ret_str = "null"
local cv_ret_str = "null"
local gui_ver = "unknown"

local ok, err = pcall(function()
    local lf = io.open(jsonl_path, "w"); if lf then lf:close() end
    progress("script_started")
    progress("sequence", sequence)

    progress("before_startup_lite_v3")
    local lite_ok, lite_err = pcall(function()

local RSTD_PATH = "C:\\\\ti\\\\mmwave_studio_03_01_04_04\\\\mmWaveStudio"
if type(RSTD) == "table" and RSTD.GetRstdPath then RSTD_PATH = RSTD.GetRstdPath() end

-- Startup.lua line 4: RTTT = RSTD (critical alias used by AR1xController)
if type(RSTD) == "table" then
    RTTT = RSTD
end

-- Startup.lua line 16: AR1_GUI = true
AR1_GUI = true

-- Setup package.path to match normal GUI environment
local runtime_path = RSTD_PATH .. "\\\\RunTime"
package.path = ".\\\\?.lua;"
    .. runtime_path .. "\\\\lua\\\\?.lua;"
    .. runtime_path .. "\\\\lua\\\\?\\\\init.lua;"
    .. runtime_path .. "\\\\?.lua;"
    .. runtime_path .. "\\\\?\\\\init.lua;"
    .. runtime_path .. "\\\\LuaScripts\\\\?.lua;"
    .. runtime_path .. "\\\\..\\\\Clients\\\\LuaModules\\\\LuaSocket\\\\?.lua"

local ar1x_controller_path = RSTD_PATH .. "\\\\Clients\\\\AR1xController\\\\AR1xController.dll"
local registers_xml = RSTD_PATH .. "\\\\Clients\\\\AR1xController\\\\AR2944ES1P0_Registers.xml"
local al_path = RSTD_PATH .. "\\\\RunTime\\\\SAL.dll"
local client_path = RSTD_PATH .. "\\\\Clients\\\\LabClient.dll"

if type(RSTD) ~= "table" or not RSTD.UnBuild then
    error("STARTUP_LITE_V3_FAILED: RSTD not available")
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

RSTD.SetAndTransmit("/Settings/Scripter/Display DateTime", "1")
RSTD.SetAndTransmit("/Settings/Scripter/DateTime Format", "HH:mm:ss")

pcall(function() dofile(RSTD_PATH .. "\\\\Scripts\\\\Startup\\\\General_functions.lua") end)
pcall(function() dofile(RSTD_PATH .. "\\\\Scripts\\\\Startup\\\\BinDecHex.lua") end)
pcall(function() dofile(RSTD_PATH .. "\\\\Scripts\\\\Startup\\\\lib_math.lua") end)

RSTD.Build()

RSTD.RegisterDllEx(ar1x_controller_path, false)
RSTD.SetExternalAL(ar1x_controller_path)

-- Startup.lua line 66: RSTD.SetTitle(ar1.GuiVersion())
local gv_ok, gv_ret = pcall(function() return ar1.GuiVersion() end)
if gv_ok and gv_ret then
    RSTD.SetTitle(tostring(gv_ret))
else
    RSTD.SetTitle("AWR-CLI")
end

RSTD.LoadExpose(registers_xml)

    end)
    progress("after_startup_lite_v3", tostring(lite_ok) .. " " .. tostring(lite_err))
    if not lite_ok then status = "STARTUP_LITE_V3_FAILED"; error("STARTUP_LITE_V3_FAILED") end

    progress("check_ar1_type", type(ar1))
    if type(ar1) ~= "table" then
        status = "AR1_MISSING"
        error("AR1_MISSING")
    end

    progress("before_ShowGui")
    local sg_ok, sg_err = pcall(function() ar1.ShowGui() end)
    progress("after_ShowGui", tostring(sg_ok) .. " " .. tostring(sg_err))
    if not sg_ok then status = "SHOWGUI_FAILED"; error("SHOWGUI_FAILED") end

    progress("before_frequencyBandSelection", "77G")
    local fb_ok, fb_ret = pcall(function() return ar1.frequencyBandSelection("77G") end)
    progress("after_frequencyBandSelection", tostring(fb_ret))
    fb_ret_str = esc(fb_ret)

    progress("before_deviceVariantSelection", "XWR2944")
    local dv_ok, dv_ret = pcall(function() return ar1.deviceVariantSelection("XWR2944") end)
    progress("after_deviceVariantSelection", tostring(dv_ret))
    dv_ret_str = esc(dv_ret)

    progress("before_SelectChipVersion", "AWR2944")
    local cv_ok, cv_ret = pcall(function() return ar1.SelectChipVersion("AWR2944") end)
    progress("after_SelectChipVersion", tostring(cv_ret))
    cv_ret_str = esc(cv_ret)

    progress("before_SOPControl", "mode=2")
    local sop_ok, sop_ret = pcall(function() return ar1.SOPControl(2) end)
    if not sop_ok then
        progress("after_SOPControl", "ERROR: " .. tostring(sop_ret))
        sop_ret_str = esc(tostring(sop_ret))
    else
        progress("after_SOPControl", tostring(sop_ret))
        sop_ret_str = esc(sop_ret)
    end

    progress("before_Sleep", "3000 ms")
    RSTD.Sleep(3000)
    progress("after_Sleep")

    progress("before_Connect", "COM6 baud=115200 timeout=1000")
    local c_ok, c_ret = pcall(function() return ar1.Connect(6, 115200, 1000) end)

    if not c_ok then
        status = "CONNECT_EXCEPTION"
        progress("after_Connect", "ERROR: " .. tostring(c_ret))
        c_ret_str = esc(tostring(c_ret))
        error("CONNECT_EXCEPTION: " .. tostring(c_ret))
    end
    progress("after_Connect", tostring(c_ret))
    c_ret_str = esc(c_ret)

    if c_ret == 3 then
        progress("connect_returned_3_retry", "waiting 3000ms then retrying once")
        c1_ret_str = esc(c_ret)
        RSTD.Sleep(3000)
        progress("before_Connect_retry")
        local c2_ok, c2_ret = pcall(function() return ar1.Connect(6, 115200, 1000) end)
        if not c2_ok then
            progress("after_Connect_retry", "ERROR: " .. tostring(c2_ret))
            c2_ret_str = esc(tostring(c2_ret))
            status = "CONNECT_RETRY_EXCEPTION"
        else
            progress("after_Connect_retry", tostring(c2_ret))
            c2_ret_str = esc(c2_ret)
            c_ret = c2_ret
        end
    end

    if c_ret == 0 then
        -- Mark success only if selection and SOP steps (if executed) also passed
        if (fb_ret_str == "null" or fb_ret_str == '"0"') and
           (dv_ret_str == "null" or dv_ret_str == '"0"') and
           (cv_ret_str == "null" or cv_ret_str == '"0"') and
           (sop_ret_str == "null" or sop_ret_str == '"0"') then
            status = "CONNECTION_GUI_SUCCESS"
        else
            status = "CONNECTION_GUI_SELECTION_FAILED"
        end

        -- Retrieve version info
        local gv = nil
        pcall(function() gv = ar1.GuiVersion() end)
        if gv then gui_ver = tostring(gv) end

        -- Post-connect selections (if not already done in sequence)
        if dv_ret_str == "null" then
            progress("before_deviceVariantSelection", "XWR2944")
            local dv_ok2, dv_ret2 = pcall(function() return ar1.deviceVariantSelection("XWR2944") end)
            progress("after_deviceVariantSelection", tostring(dv_ret2))
            dv_ret_str = esc(dv_ret2)
        end
        if fb_ret_str == "null" then
            progress("before_frequencyBandSelection", "77G")
            local fb_ok2, fb_ret2 = pcall(function() return ar1.frequencyBandSelection("77G") end)
            progress("after_frequencyBandSelection", tostring(fb_ret2))
            fb_ret_str = esc(fb_ret2)
        end
        if cv_ret_str == "null" then
            progress("before_SelectChipVersion", "AWR2944")
            local cv_ok2, cv_ret2 = pcall(function() return ar1.SelectChipVersion("AWR2944") end)
            progress("after_SelectChipVersion", tostring(cv_ret2))
            cv_ret_str = esc(cv_ret2)
        end
    elseif c_ret == 3 then
        status = "CONNECT_RETURNED_3"
    else
        status = "CONNECT_RETURNED_ERROR"
    end

    local f = io.open(out_path, "w")
    if f then
        line(f, "{")
        line(f, '  "run_id": ' .. esc(run_id) .. ',')
        line(f, '  "executed": true,')
        line(f, '  "sequence": ' .. esc(sequence) .. ',')
        line(f, '  "status": ' .. esc(status) .. ',')
        line(f, '  "connect_return": ' .. c_ret_str .. ',')
        line(f, '  "connect_return_1": ' .. c1_ret_str .. ',')
        line(f, '  "connect_return_2": ' .. c2_ret_str .. ',')
        line(f, '  "sop_return": ' .. sop_ret_str .. ',')
        line(f, '  "device_variant_selection_return": ' .. dv_ret_str .. ',')
        line(f, '  "frequency_band_selection_return": ' .. fb_ret_str .. ',')
        line(f, '  "chip_version_selection_return": ' .. cv_ret_str .. ',')
        line(f, '  "gui_version": ' .. esc(gui_ver) .. ',')
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
        line(f, '  "sequence": ' .. esc(sequence) .. ',')
        line(f, '  "status": ' .. esc(status) .. ',')
        line(f, '  "connect_return": ' .. c_ret_str .. ',')
        line(f, '  "connect_return_1": ' .. c1_ret_str .. ',')
        line(f, '  "connect_return_2": ' .. c2_ret_str .. ',')
        line(f, '  "sop_return": ' .. sop_ret_str .. ',')
        line(f, '  "error": ' .. esc(tostring(err)))
        line(f, "}")
        f:close()
    end
end
