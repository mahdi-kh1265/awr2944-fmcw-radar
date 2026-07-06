local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/fresh_gui_lua_set_only_result.json]]
local jsonl_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/fresh_gui_lua_set_only_progress.jsonl]]

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

local function call_step(name, fn)
    progress("before_" .. name)
    local ok, ret = pcall(fn)
    if ok then
        progress("after_" .. name, tostring(ret))
        return true, ret
    else
        progress("after_" .. name, "ERROR: " .. tostring(ret))
        return false, ret
    end
end

local status = "NO_START"
local fb_ret, cv_ret, dv_ret, sop_ret = nil, nil, nil, nil

local ok, err = pcall(function()
    local lf = io.open(jsonl_path, "w")
    if lf then lf:close() end

    progress("script_started")
    progress("type_ar1", type(ar1))

    local ok1, r1 = call_step("frequencyBandSelection_77G", function()
        return ar1.frequencyBandSelection("77G")
    end)
    fb_ret = r1

    local ok2, r2 = call_step("SelectChipVersion_AR1642", function()
        return ar1.SelectChipVersion("AR1642")
    end)
    cv_ret = r2

    local ok3, r3 = call_step("deviceVariantSelection_XWR2944", function()
        return ar1.deviceVariantSelection("XWR2944")
    end)
    dv_ret = r3

    local ok4, r4 = call_step("SOPControl_2", function()
        return ar1.SOPControl(2)
    end)
    sop_ret = r4

    if ok1 and ok2 and ok3 and ok4 and r1 == 0 and r2 == 0 and r3 == 0 and r4 == 0 then
        status = "LUA_SET_ONLY_SUCCESS"
    else
        status = "LUA_SET_ONLY_FAILED"
    end
end)

local f = io.open(out_path, "w")
if f then
    line(f, "{")
    line(f, '  "executed": ' .. tostring(ok) .. ',')
    line(f, '  "status": ' .. esc(status) .. ',')
    line(f, '  "frequencyBandSelection_return": ' .. esc(fb_ret) .. ',')
    line(f, '  "SelectChipVersion_return": ' .. esc(cv_ret) .. ',')
    line(f, '  "deviceVariantSelection_return": ' .. esc(dv_ret) .. ',')
    line(f, '  "SOPControl_return": ' .. esc(sop_ret) .. ',')
    if ok then
        line(f, '  "error": null')
    else
        line(f, '  "error": ' .. esc(err))
    end
    line(f, "}")
    f:close()
end
