-- GUI-Derived AWR2944 Smoke Config (FROZEN LITERAL REPLAY)
-- These are exact GUI-emitted commands. DO NOT modify arguments.
-- source: frozen_gui_derived_awr2944
-- replay_validated: true
-- run_id: 62d8a837

local run_id = "62d8a837"
local run_stage = "smoke_config"
local progress_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/62d8a837_smoke_config_progress.jsonl]]

local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/62d8a837_smoke_config_result.json]]
local result = {
    run_id = "62d8a837",
    executed = true,
    success = false,
    error = "",
    warnings = {}
}

local function saveResult()
    local f = io.open(out_path, "w")
    if f then
        local w_str = "["
        for i, w in ipairs(result.warnings) do
            w_str = w_str .. '"' .. string.gsub(w, '"', '\\"') .. '"'
            if i < #result.warnings then w_str = w_str .. ", " end
        end
        w_str = w_str .. "]"
        f:write(string.format('{"run_id": "%s", "executed": %s, "success": %s, "error": "%s", "warnings": %s}\n',
            result.run_id, tostring(result.executed), tostring(result.success), string.gsub(result.error, '"', '\\"'), w_str))
        f:close()
    end
end

local function logProgress(func, ret, ok, err)
    local f = io.open(progress_path, "a")
    if f then
        local ret_str
        if ret == nil then
            ret_str = "null"
        elseif type(ret) == "number" then
            ret_str = tostring(ret)
        else
            ret_str = '"' .. tostring(ret):gsub('\\', '\\\\'):gsub('"', '\\"') .. '"'
        end
        local err_str = ""
        if err ~= nil then
            err_str = string.format(', "err": "%s"', tostring(err):gsub('\\', '\\\\'):gsub('"', '\\"'))
        end
        f:write('{"ts": "' .. os.date('%X') .. '", "cmd": "' .. func .. '", "ret": ' .. ret_str .. ', "ok": ' .. tostring(ok) .. err_str .. '}\n')
        f:close()
    end
end

local function safeCall(funcName, func, critical)
    local ok, ret = pcall(func)
    local err = nil
    if not ok then err = ret; ret = nil end
    logProgress(funcName, ret, ok, err)
    if not ok or (type(ret) == "number" and ret ~= 0) then
        if funcName == "DisableTestSource" and ret == -1 then
            table.insert(result.warnings, "DisableTestSource returned -1; likely benign if Test Source Already Disabled.")
            return true
        end
        if critical then
            result.error = funcName .. " failed: " .. tostring(err or ret)
            saveResult()
            print("AWR_RUN_END run_id=" .. run_id .. " stage=" .. run_stage .. " success=false")
            return false
        else
            table.insert(result.warnings, funcName .. " failed: " .. tostring(err or ret))
        end
    end
    return true
end

print("AWR_RUN_BEGIN run_id=" .. run_id .. " stage=" .. run_stage)

if not safeCall("ChanNAdcConfig", function() return ar1.ChanNAdcConfig(1, 1, 0, 0, 1, 1, 0, 0, 2, 0, 0) end, true) then return end

if not safeCall("LPModConfig", function() return ar1.LPModConfig(0, 0) end, true) then return end

if not safeCall("RfLdoBypassConfig", function() return ar1.RfLdoBypassConfig(0x0) end, true) then return end

if not safeCall("SetCalMonFreqLimitConfig", function() return ar1.SetCalMonFreqLimitConfig(76,81,0) end, true) then return end

if not safeCall("SetRFDeviceConfig", function() return ar1.SetRFDeviceConfig(5, 0, 0, 0, 0, 0, 0) end, true) then return end

if not safeCall("RfSetCalMonFreqTxPowLimitConfig", function() return ar1.RfSetCalMonFreqTxPowLimitConfig(76, 76, 76, 76, 81, 81, 81, 81, 0, 0, 0, 0,0) end, true) then return end

if not safeCall("SetApllSynthBWCtlConfig", function() return ar1.SetApllSynthBWCtlConfig(1, 4, 3, 9, 18, 1, 4) end, true) then return end

if not safeCall("RfInit", function() return ar1.RfInit() end, true) then return end
RSTD.Sleep(1000)

if not safeCall("DataPathConfig", function() return ar1.DataPathConfig(513, 1216644097, 0) end, true) then return end

if not safeCall("LVDSLaneConfig", function() return ar1.LVDSLaneConfig(0, 1, 0, 0, 0, 1, 0, 0) end, true) then return end

if not safeCall("ProfileConfig", function() return ar1.ProfileConfig(0, 77, 100, 6, 60, 0, 0, 0, 0, 0, 0, 0, 0, 29.982, 0, 256, 10000, 2216755200, 0, 30, 0, 0, 0) end, true) then return end

if not safeCall("ChirpConfig", function() return ar1.ChirpConfig(0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0) end, true) then return end

if not safeCall("FrameConfig", function() return ar1.FrameConfig(0, 0, 8, 128, 40, 0, 1) end, true) then return end

print("GUI-derived AWR2944 smoke config completed successfully.")
result.success = true
saveResult()
print("AWR_RUN_END run_id=" .. run_id .. " stage=" .. run_stage .. " success=true")