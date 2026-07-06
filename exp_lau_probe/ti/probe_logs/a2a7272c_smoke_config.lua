-- Smoke Config Script (Static/Data/Sensor)
-- config_source: ti_baseline
-- yaml_path: none
-- run_id: a2a7272c

local progress_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/a2a7272c_smoke_config_progress.jsonl]]

local function logProgress(func, args, ret, ok, err)
    local f = io.open(progress_path, 'a')
    if f then
        local e = err and string.format(', "err": "%s"', tostring(err):gsub('"', '\\"')) or ''
        f:write(string.format('{"ts": "%s", "cmd": "%s", "args": "%s", "ret": %s, "ok": %s%s}\n', os.date("%X"), func, args:gsub('"', '\\"'), tostring(ret), tostring(ok), e))
        f:close()
    end
end

local function safeCall(funcName, argStr, func)
    local ok, ret = pcall(func)
    local err = nil
    if not ok then err = ret; ret = nil end
    logProgress(funcName, argStr, ret, ok, err)
    if not ok or (type(ret) == 'number' and ret ~= 0) then
        print("Critical failure in " .. funcName .. ": " .. tostring(err or ret))
        return false
    end
    return true
end

-- 1. Static Config
if not safeCall("ChanNAdcConfig", "1, 1, 1, 1, 1, 1, 1, 2, 1, 0", function() return ar1.ChanNAdcConfig(1, 1, 1, 1, 1, 1, 1, 2, 1, 0) end) then return end
if not safeCall("LPModConfig", "0, 0", function() return ar1.LPModConfig(0, 0) end) then return end
if not safeCall("RfInit", "", function() return ar1.RfInit() end) then return end
RSTD.Sleep(1000)

-- 2. Data Config
if not safeCall("DataPathConfig", "1, 1, 0", function() return ar1.DataPathConfig(1, 1, 0) end) then return end
if not safeCall("LvdsClkConfig", "1, 1", function() return ar1.LvdsClkConfig(1, 1) end) then return end
if not safeCall("LVDSLaneConfig", "1, 1, 1, 1, 0, 0, 0, 0", function() return ar1.LVDSLaneConfig(1, 1, 1, 1, 0, 0, 0, 0) end) then return end

-- 3. Sensor Config
if not safeCall("ProfileConfig", "0, 77.0, 100, 7.0, 60.0, 0, 0, 0, 0, 0, 0, 29.982, 0, 256, 10000, 0, 0, 30", function() return ar1.ProfileConfig(0, 77.0, 100, 7.0, 60.0, 0, 0, 0, 0, 0, 0, 29.982, 0, 256, 10000, 0, 0, 30) end) then return end
if not safeCall("ChirpConfig", "0, 0, 0, 0, 0, 0, 0, 1, 1, 0", function() return ar1.ChirpConfig(0, 0, 0, 0, 0, 0, 0, 1, 1, 0) end) then return end
if not safeCall("FrameConfig", "0, 0, 10, 128, 40.0, 0, 0, 1", function() return ar1.FrameConfig(0, 0, 10, 128, 40.0, 0, 0, 1) end) then return end

print("Smoke config applied successfully.")
