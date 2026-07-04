-- lua-launch smoke test
-- Self-contained: no WriteToLog, no ar1, no Startup.lua
-- run_id: 1ea860ca

local run_id = "1ea860ca"
local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/lua_launch_smoke_result.json]]

local function line(f, s)
    f:write(s)
    f:write("\n")
end

local ok, err = pcall(function()
    local f = io.open(out_path, "w")
    if not f then
        error("Cannot open result file: " .. out_path)
    end
    line(f, "{")
    line(f, '  "run_id": "' .. run_id .. '",')
    line(f, '  "executed": true,')
    line(f, '  "write_ok": true,')
    line(f, '  "error": null')
    line(f, "}")
    f:close()
end)

if not ok then
    -- Last-ditch: try to write error result
    local f = io.open(out_path, "w")
    if f then
        line(f, "{")
        line(f, '  "run_id": "' .. run_id .. '",')
        line(f, '  "executed": false,')
        line(f, '  "write_ok": false,')
        line(f, '  "error": "' .. tostring(err):gsub('"', '\\"') .. '"')
        line(f, "}")
        f:close()
    end
end
