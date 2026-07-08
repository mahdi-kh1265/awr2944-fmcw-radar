-- Firmware & Power Sequence
-- run_id: 645cdf51
-- WARNING: Do NOT run this script twice in the same session.

local run_id = "645cdf51"
local run_stage = "firmware_power"
local progress_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/645cdf51_firmware_power_progress.jsonl]]

local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/645cdf51_firmware_power_result.json]]
local result = {
    run_id = "645cdf51",
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
print("AWR_RUN_END run_id=" .. run_id .. " stage=" .. run_stage .. " success=true")
