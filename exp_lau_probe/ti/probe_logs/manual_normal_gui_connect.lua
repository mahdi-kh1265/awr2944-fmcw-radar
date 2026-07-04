local run_id = "manual_gui_connect"
local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/manual_normal_gui_connect_result.json]]
local jsonl_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/manual_normal_gui_connect_progress.jsonl]]

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

local function progress(step, detail)
    local lf = io.open(jsonl_path, "a")
    if lf then
        if detail then
            line(lf, '{"step": ' .. esc(step) .. ', "detail": ' .. esc(detail) .. '}')
        else
            line(lf, '{"step": ' .. esc(step) .. '}')
        end
        lf:close()
    end
end

local status = "NO_LUA_START"
local connect_ret = nil

local ok, err = pcall(function()
    local lf = io.open(jsonl_path, "w")
    if lf then lf:close() end

    progress("script_started")
    progress("check_ar1_type", type(ar1))

    if type(ar1) ~= "table" then
        status = "AR1_MISSING"
        error("AR1_MISSING: type(ar1)=" .. type(ar1))
    end

    progress("check_connect_exists", tostring(ar1.Connect ~= nil))

    if ar1.Connect == nil then
        status = "CONNECT_MISSING"
        error("CONNECT_MISSING")
    end

    progress("before_Connect", "COM6 baud=115200 timeout=1000")
    local c_ok, c_ret = pcall(function()
        return ar1.Connect(6, 115200, 1000)
    end)

    if not c_ok then
        status = "CONNECT_EXCEPTION"
        progress("after_Connect", "ERROR: " .. tostring(c_ret))
        error(tostring(c_ret))
    end

    connect_ret = c_ret
    progress("after_Connect", tostring(connect_ret))

    if connect_ret == 0 then
        status = "CONNECT_SUCCESS"
    else
        status = "CONNECT_RETURNED_ERROR"
    end
end)

local f = io.open(out_path, "w")
if f then
    line(f, "{")
    line(f, '  "run_id": ' .. esc(run_id) .. ',')
    line(f, '  "executed": ' .. tostring(ok) .. ',')
    line(f, '  "status": ' .. esc(status) .. ',')
    line(f, '  "type_ar1": ' .. esc(type(ar1)) .. ',')
    line(f, '  "connect_return": ' .. esc(connect_ret) .. ',')
    if ok then
        line(f, '  "error": null')
    else
        line(f, '  "error": ' .. esc(err))
    end
    line(f, "}")
    f:close()
end
