-- Firmware & Power Sequence
-- run_id: 701a5f04

local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/701a5f04_firmware_power_result.json]]
local progress_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/701a5f04_firmware_power_result_progress.jsonl]]

local result = {
    run_id = "701a5f04",
    executed = true,
    success = false,
    error = ""
}

local function saveResult()
    local f = io.open(out_path, "w")
    if f then
        f:write(string.format('{"run_id": "%s", "executed": %s, "success": %s, "error": "%s"}\n',
            result.run_id, tostring(result.executed), tostring(result.success), result.error))
        f:close()
    end
end

local function logProgress(func, ret, ok, err)
    local f = io.open(progress_path, 'a')
    if f then
        local e = err and string.format(', "err": "%s"', tostring(err):gsub('"', '\\"')) or ''
        f:write(string.format('{"ts": "%s", "cmd": "%s", "ret": %s, "ok": %s%s}\n', os.date("%X"), func, tostring(ret), tostring(ok), e))
        f:close()
    end
end

local function safeCall(funcName, func, critical)
    local ok, ret = pcall(func)
    local err = nil
    if not ok then err = ret; ret = nil end
    logProgress(funcName, ret, ok, err)
    if critical and (not ok or (type(ret) == 'number' and ret ~= 0)) then
        result.error = funcName .. " failed: " .. tostring(err or ret)
        saveResult()
        return false
    end
    return true
end

-- 1. BSS Firmware
local bss_path = [[C:\ti\mmwave_studio_03_01_04_04\rf_eval_firmware\radarss\xwr29xx_radarss_rprc.bin]]
if not safeCall("DownloadBSSFw", function() return ar1.DownloadBSSFw(bss_path) end, true) then return end
RSTD.Sleep(1000)

safeCall("GetBSSFwVersion", function() return ar1.GetBSSFwVersion() end, false)
safeCall("GetBSSPatchFwVersion", function() return ar1.GetBSSPatchFwVersion() end, false)

-- 2. MSS Firmware
local mss_path = [[C:\ti\mmwave_studio_03_01_04_04\rf_eval_firmware\masterss\awr2xxx_mmwave_full_mss_rprc.bin]]
if not safeCall("DownloadMSSFw", function() return ar1.DownloadMSSFw(mss_path) end, true) then return end
RSTD.Sleep(1000)

safeCall("GetMSSFwVersion", function() return ar1.GetMSSFwVersion() end, false)

-- 3. Power On
if not safeCall("PowerOn", function() return ar1.PowerOn(0, 1000, 0, 0) end, true) then return end
RSTD.Sleep(2000)

-- 4. RF Enable
if not safeCall("RfEnable", function() return ar1.RfEnable() end, true) then return end
RSTD.Sleep(1000)

-- Final verifications
safeCall("GetMSSFwVersion", function() return ar1.GetMSSFwVersion() end, false)
safeCall("GetBSSFwVersion", function() return ar1.GetBSSFwVersion() end, false)
safeCall("GetBSSPatchFwVersion", function() return ar1.GetBSSPatchFwVersion() end, false)

result.success = true
saveResult()
