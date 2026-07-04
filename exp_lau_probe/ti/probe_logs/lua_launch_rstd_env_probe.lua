-- lua-launch rstd-env-probe
local run_id = "3b4aa646"
local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/lua_launch_rstd_env_probe_result.json]]

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

local ok, err = pcall(function()
    local type_rstd = type(RSTD)
    local has_registerdllex = false
    local has_netstart = false
    if type_rstd == "table" then
        if type(RSTD.RegisterDllEx) == "function" or type(RSTD.RegisterDllEx) == "userdata" then has_registerdllex = true end
        if type(RSTD.NetStart) == "function" or type(RSTD.NetStart) == "userdata" then has_netstart = true end
    end
    
    local f = io.open(out_path, "w")
    if not f then error("Cannot open result file") end
    
    line(f, "{")
    line(f, '  "run_id": ' .. esc(run_id) .. ',')
    line(f, '  "executed": true,')
    line(f, '  "type_RSTD": ' .. esc(type_rstd) .. ',')
    line(f, '  "RSTD_RegisterDllEx_exists": ' .. tostring(has_registerdllex) .. ',')
    line(f, '  "RSTD_NetStart_exists": ' .. tostring(has_netstart) .. ',')
    line(f, '  "type_ar1": ' .. esc(type(ar1)) .. ',')
    line(f, '  "type_WriteToLog": ' .. esc(type(WriteToLog)) .. ',')
    line(f, '  "type_writeToLog": ' .. esc(type(writeToLog)))
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
