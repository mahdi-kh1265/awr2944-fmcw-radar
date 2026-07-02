-- AWR2944 DCA Lab - Offline Probe

local probe_executed = true
local ar1_available = false
local write_to_log_available = false

-- Safe logging function
local function SafeLog(msg, color)
    local status, err = pcall(function()
        WriteToLog(msg, color)
    end)
    if status then
        write_to_log_available = true
    end
end

SafeLog("=========================================\n", "green")
SafeLog("PROBE SUCCESS: mmWave Studio Lua execution works!\n", "green")
SafeLog("=========================================\n", "green")

-- Try a harmless ar1 command if available (just getting version/help)
if ar1 then
    ar1_available = true
    SafeLog("ar1 API is available.\n", "blue")
else
    SafeLog("ar1 API is NOT available.\n", "red")
end

-- Write result to JSON manually
local json_str = string.format([[
{
    "probe_executed": %s,
    "ar1_available": %s,
    "write_to_log_available": %s
}
]], tostring(probe_executed), tostring(ar1_available), tostring(write_to_log_available))

local file, err = io.open("C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/probe_result.json", "w")
if file then
    file:write(json_str)
    file:close()
else
    SafeLog("ERROR writing JSON: " .. tostring(err) .. "\n", "red")
end
