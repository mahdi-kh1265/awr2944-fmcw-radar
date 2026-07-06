local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/fresh_gui_human_set_lua_connect_result.json]]
local jsonl_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/fresh_gui_human_set_lua_connect_progress.jsonl]]

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

local status = "NO_START"
local connect_ret = nil

local ok, err = pcall(function()
    local lf = io.open(jsonl_path, "w")
    if lf then lf:close() end

    progress("script_started")
    progress("type_ar1", type(ar1))

    progress("before_Connect_COM6_115200")
    local c_ok, c_ret = pcall(function()
        return ar1.Connect(6, 115200, 1000)
    end)

    if c_ok then
        connect_ret = c_ret
        progress("after_Connect_COM6_115200", tostring(c_ret))
        if c_ret == 0 then
            status = "CONNECT_RETURNED_0"
        else
            status = "CONNECT_RETURNED_NONZERO"
        end
    else
        connect_ret = tostring(c_ret)
        progress("after_Connect_COM6_115200", "ERROR: " .. tostring(c_ret))
        status = "CONNECT_EXCEPTION"
    end
end)

local f = io.open(out_path, "w")
if f then
    line(f, "{")
    line(f, '  "executed": ' .. tostring(ok) .. ',')
    line(f, '  "status": ' .. esc(status) .. ',')
    line(f, '  "Connect_return": ' .. esc(connect_ret) .. ',')
    if ok then
        line(f, '  "error": null')
    else
        line(f, '  "error": ' .. esc(err))
    end
    line(f, "}")
    f:close()
end
