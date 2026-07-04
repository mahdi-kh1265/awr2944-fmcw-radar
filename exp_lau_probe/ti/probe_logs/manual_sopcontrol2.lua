local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/manual_sopcontrol2_result.json]]
local jsonl_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/manual_sopcontrol2_progress.jsonl]]

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
    local sop_ok, ret = pcall(function()
        return ar1.SOPControl(2)
    end)

    if not sop_ok then
        status = "SOP_EXCEPTION"
        progress("after_SOPControl", "ERROR: " .. tostring(ret))
        error(tostring(ret))
    end

    sop_ret = ret
    progress("after_SOPControl", tostring(sop_ret))

    if sop_ret == 0 then
        status = "SOP_SET_SUCCESS"
    else
        status = "SOP_RETURNED_ERROR"
    end
end)

local f = io.open(out_path, "w")
if f then
    line(f, "{")
    line(f, '  "executed": ' .. tostring(ok) .. ',')
    line(f, '  "status": ' .. esc(status) .. ',')
    line(f, '  "type_ar1": ' .. esc(type(ar1)) .. ',')
    line(f, '  "sop_return": ' .. esc(sop_ret) .. ',')
    if ok then
        line(f, '  "error": null')
    else
        line(f, '  "error": ' .. esc(err))
    end
    line(f, "}")
    f:close()
end
