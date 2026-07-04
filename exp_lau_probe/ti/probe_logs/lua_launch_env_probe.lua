-- lua-launch env-probe
-- Self-contained: no WriteToLog, no ar1, no Startup.lua
-- run_id: 2ee8c951

local run_id = "2ee8c951"
local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/lua_launch_env_probe_result.json]]

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

local function line(f, s)
    f:write(s)
    f:write("\n")
end

local ok, err = pcall(function()
    local lua_version = _VERSION or "unknown"
    local ar1_type = type(ar1)
    local ar1_connect_exists = false
    if type(ar1) == "table" and ar1.Connect then
        ar1_connect_exists = true
    end
    local write_to_log_type = type(WriteToLog)
    local write_to_log_lower_type = type(writeToLog)

    local f = io.open(out_path, "w")
    if not f then
        error("Cannot open result file: " .. out_path)
    end
    
    line(f, "{")
    line(f, '  "run_id": ' .. esc(run_id) .. ',')
    line(f, '  "executed": true,')
    line(f, '  "_VERSION": ' .. esc(lua_version) .. ',')
    line(f, '  "type_ar1": ' .. esc(ar1_type) .. ',')
    line(f, '  "ar1_connect_exists": ' .. tostring(ar1_connect_exists) .. ',')
    line(f, '  "type_WriteToLog": ' .. esc(write_to_log_type) .. ',')
    line(f, '  "type_writeToLog": ' .. esc(write_to_log_lower_type) .. ',')
    line(f, '  "io_open_works": true,')
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
        line(f, '  "error": ' .. esc(tostring(err)))
        line(f, "}")
        f:close()
    end
end
