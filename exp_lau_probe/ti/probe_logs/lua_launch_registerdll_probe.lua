-- lua-launch registerdll-probe
local run_id = "ee34430b"
local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/lua_launch_registerdll_probe_result.json]]
local jsonl_path = out_path .. ".jsonl"

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
    local lf = io.open(jsonl_path, "w")
    if lf then 
        line(lf, '{"step": "start", "type_RSTD": ' .. esc(type(RSTD)) .. '}')
        lf:close()
    end

    local type_RSTD = type(RSTD)
    local register_ok, register_err = false, "RSTD not found"
    if type_RSTD == "table" and RSTD.GetRstdPath then
        local rstd_path = RSTD.GetRstdPath()
        local ar1x_controller_path = rstd_path .. "\\Clients\\AR1xController\\AR1xController.dll"
        register_ok, register_err = pcall(function()
            RSTD.RegisterDllEx(ar1x_controller_path, false)
        end)
    end
    
    lf = io.open(jsonl_path, "a")
    if lf then 
        line(lf, '{"step": "after_register", "ok": ' .. tostring(register_ok) .. ', "err": ' .. esc(register_err) .. '}')
        lf:close()
    end
    
    local ar1_type = type(ar1)
    local ar1_connect_exists = false
    local ar1_isconnected_exists = false
    local ar1_sopcontrol_exists = false
    if ar1_type == "table" then
        ar1_connect_exists = (ar1.Connect ~= nil)
        ar1_isconnected_exists = (ar1.IsConnected ~= nil)
        ar1_sopcontrol_exists = (ar1.SOPControl ~= nil)
    end
    
    local f = io.open(out_path, "w")
    if not f then error("Cannot open result file") end
    
    line(f, "{")
    line(f, '  "run_id": ' .. esc(run_id) .. ',')
    line(f, '  "executed": true,')
    line(f, '  "type_RSTD": ' .. esc(type_RSTD) .. ',')
    line(f, '  "register_ok": ' .. tostring(register_ok) .. ',')
    line(f, '  "register_err": ' .. esc(register_err) .. ',')
    line(f, '  "type_ar1": ' .. esc(ar1_type) .. ',')
    line(f, '  "ar1_connect_exists": ' .. tostring(ar1_connect_exists) .. ',')
    line(f, '  "ar1_isconnected_exists": ' .. tostring(ar1_isconnected_exists) .. ',')
    line(f, '  "ar1_sopcontrol_exists": ' .. tostring(ar1_sopcontrol_exists))
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
