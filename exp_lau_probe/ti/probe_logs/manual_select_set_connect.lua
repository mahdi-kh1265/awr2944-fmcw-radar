local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/manual_select_set_connect_result.json]]
local jsonl_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/manual_select_set_connect_progress.jsonl]]

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
local dv_ret, fb_ret, cv_ret, sop_ret, connect_ret = nil, nil, nil, nil, nil

local ok, err = pcall(function()
    local lf = io.open(jsonl_path, "w")
    if lf then lf:close() end

    progress("script_started")
    progress("check_ar1_type", type(ar1))

    if type(ar1) ~= "table" then
        status = "AR1_MISSING"
        error("AR1_MISSING")
    end

    local ok1, r1 = call_step("frequencyBandSelection_77G", function()
        return ar1.frequencyBandSelection("77G")
    end)
    fb_ret = r1

    local ok2, r2 = call_step("deviceVariantSelection_XWR2944", function()
        return ar1.deviceVariantSelection("XWR2944")
    end)
    dv_ret = r2

    local ok3, r3 = call_step("SelectChipVersion_AWR2944", function()
        return ar1.SelectChipVersion("AWR2944")
    end)
    cv_ret = r3

    local ok4, r4 = call_step("SOPControl_2_Set", function()
        return ar1.SOPControl(2)
    end)
    sop_ret = r4

    progress("before_Sleep_after_Set", "3000 ms")
    if type(RSTD) == "table" and RSTD.Sleep then
        RSTD.Sleep(3000)
    end
    progress("after_Sleep_after_Set")

    local ok5, r5 = call_step("Connect_COM6_115200", function()
        return ar1.Connect(6, 115200, 1000)
    end)
    connect_ret = r5

    if not ok5 then
        status = "CONNECT_EXCEPTION"
        error(tostring(r5))
    elseif connect_ret == 0 then
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
    line(f, '  "frequency_band_selection_return": ' .. esc(fb_ret) .. ',')
    line(f, '  "device_variant_selection_return": ' .. esc(dv_ret) .. ',')
    line(f, '  "chip_version_selection_return": ' .. esc(cv_ret) .. ',')
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
