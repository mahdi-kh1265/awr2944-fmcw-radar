-- run_id: cd76100b
-- stage: postproc
-- Output paths:
--   lua: C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/cd76100b_postproc.lua
--   prog: C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/cd76100b_postproc_progress.jsonl
--   res: C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/cd76100b_postproc_result.json
--   adc_data_path: C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc\adc_data.bin

local run_id = "cd76100b"
local run_stage = "postproc"
local progress_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/cd76100b_postproc_progress.jsonl]]

local function jsonEscape(s)
    if type(s) ~= "string" then s = tostring(s) end
    s = s:gsub('\\', '\\\\')
    s = s:gsub("\"", "\\\"")
    s = s:gsub('\n', '\\n')
    s = s:gsub('\r', '\\r')
    s = s:gsub('\t', '\\t')
    return s
end
local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/cd76100b_postproc_result.json]]
local result = {
    run_id = "cd76100b",
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
            w_str = w_str .. '"' .. jsonEscape(w) .. '"'
            if i < #result.warnings then w_str = w_str .. ", " end
        end
        w_str = w_str .. "]"
        f:write(string.format('{"run_id": "%s", "executed": %s, "success": %s, "error": "%s", "warnings": %s}\n',
            result.run_id, tostring(result.executed), tostring(result.success), jsonEscape(result.error), w_str))
        f:close()
    end
end

local function jsonEscape(s)
    if type(s) ~= "string" then s = tostring(s) end
    s = s:gsub('\\', '\\\\')
    s = s:gsub("\"", "\\\"")
    s = s:gsub('\n', '\\n')
    s = s:gsub('\r', '\\r')
    s = s:gsub('\t', '\\t')
    return s
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
            ret_str = "\"" .. jsonEscape(ret) .. "\""
        end
        local err_str = ""
        if err ~= nil then
            err_str = string.format(', "err": "%s"', jsonEscape(err))
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

local adc_data_path = [[C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc\adc_data.bin]]
if not safeCall("StartMatlabPostProc", function() return ar1.StartMatlabPostProc(adc_data_path) end, true) then return end

print("Post-processing trigger completed successfully.")
result.success = true
saveResult()
print("AWR_RUN_END run_id=" .. run_id .. " stage=" .. run_stage .. " success=true")