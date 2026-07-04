local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/manual_sop_then_connect_result.json]]
local jsonl_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/manual_sop_then_connect_progress.jsonl]]

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

local status = "NO_START"
local sop_ret = nil
local connect_ret = nil

local ok, err = pcall(function()
    local lf = io.open(jsonl_path, "w")
    if lf then lf:close() end

    progress("script_started")
    progress("check_ar1_type", type(ar1))

    if type(ar1) ~= "table" then
        status = "AR1_MISSING"
        error("AR1_MISSING")
    end

    progress("before_SOPControl", "mode=2")
    local sop_ok, sret = pcall(function()
        return ar1.SOPControl(2)
    end)
    if not sop_ok then
        status = "SOP_EXCEPTION"
        progress("after_SOPControl", "ERROR: " .. tostring(sret))
        error(tostring(sret))
    end

    sop_ret = sret
    progress("after_SOPControl", tostring(sop_ret))

    progress("before_Sleep", "2000 ms")
    if type(RSTD) == "table" and RSTD.Sleep then
        RSTD.Sleep(2000)
    end
    progress("after_Sleep")

    progress("before_Connect", "COM6 baud=115200 timeout=1000")
    local c_ok, cret = pcall(function()
        return ar1.Connect(6, 115200, 1000)
    end)
    if not c_ok then
        status = "CONNECT_EXCEPTION"
        progress("after_Connect", "ERROR: " .. tostring(cret))
        error(tostring(cret))
    end

    connect_ret = cret
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
    line(f, '  "executed": ' .. tostring(ok) .. ',')
    line(f, '  "status": ' .. esc(status) .. ',')
    line(f, '  "sop_return": ' .. esc(sop_ret) .. ',')
    line(f, '  "connect_return": ' .. esc(connect_ret) .. ',')
    if ok then
        line(f, '  "error": null')
    else
        line(f, '  "error": ' .. esc(err))
    end
    line(f, "}")
    f:close()
end
