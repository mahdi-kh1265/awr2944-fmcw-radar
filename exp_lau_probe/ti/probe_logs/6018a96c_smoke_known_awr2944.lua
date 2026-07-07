-- GUI-Derived AWR2944 Smoke Config
-- NOT YET REPLAY-VALIDATED
-- These commands match mmWave Studio GUI emission for AWR2944
-- but have not been verified on a clean session.
-- run_id: 6018a96c

local progress_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/6018a96c_smoke_known_awr2944_progress.jsonl]]

local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/6018a96c_smoke_known_awr2944_result.json]]
local result = {
    run_id = "6018a96c",
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
            return false
        else
            table.insert(result.warnings, funcName .. " failed: " .. tostring(err or ret))
        end
    end
    return true
end

-- WARNING: captured during dirty session; replay validation required
if not safeCall("ChanNAdcConfig", function() return ar1.ChanNAdcConfig(1, 1, 0, 1, 1, 1, 1, 2, 1, 0, 1) end, true) then return end

if not safeCall("LPModConfig", function() return ar1.LPModConfig(0, 1) end, true) then return end

if not safeCall("RfLdoBypassConfig", function() return ar1.RfLdoBypassConfig(0) end, true) then return end

if not safeCall("SetCalMonFreqLimitConfig", function() return ar1.SetCalMonFreqLimitConfig(760, 810, 0) end, true) then return end

if not safeCall("SetRFDeviceConfig", function() return ar1.SetRFDeviceConfig(1, 0, 0, 0, 0, 0, 0) end, true) then return end

if not safeCall("RfSetCalMonFreqTxPowLimitConfig", function() return ar1.RfSetCalMonFreqTxPowLimitConfig(760, 810, 0, 0, 760, 810, 0, 0, 760, 810, 0, 0, 0) end, true) then return end

if not safeCall("SetApllSynthBWCtlConfig", function() return ar1.SetApllSynthBWCtlConfig(0, 1, 1, 0, 1, 1, 0) end, true) then return end

if not safeCall("RfInit", function() return ar1.RfInit() end, true) then return end
RSTD.Sleep(1000)

if not safeCall("DataPathConfig", function() return ar1.DataPathConfig(1, 1, 0) end, true) then return end

if not safeCall("LVDSLaneConfig", function() return ar1.LVDSLaneConfig(0, 1, 1, 0, 0, 1, 0, 0) end, true) then return end

if not safeCall("ProfileConfig", function() return ar1.ProfileConfig(0, 77, 100, 6, 60, 0, 0, 0, 0, 0, 0, 29.982, 0, 256, 10000, 0, 0, 30, 0, 0, 0, 0, 0) end, true) then return end

if not safeCall("ChirpConfig", function() return ar1.ChirpConfig(0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0) end, true) then return end

if not safeCall("FrameConfig", function() return ar1.FrameConfig(0, 0, 8, 128, 40, 0, 0) end, true) then return end

print("GUI-derived AWR2944 smoke config completed successfully.")
result.success = true
saveResult()