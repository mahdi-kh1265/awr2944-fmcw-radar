local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/manual_normal_gui_paths_result.json]]

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

local function safe_call(name, fn)
    local ok, ret = pcall(fn)
    if ok then return tostring(ret) else return "ERROR: " .. tostring(ret) end
end

local f = io.open(out_path, "w")
if f then
    line(f, "{")
    line(f, '  "RSTD_GetRstdPath": ' .. esc(safe_call("GetRstdPath", function() return RSTD.GetRstdPath() end)) .. ',')
    line(f, '  "RSTD_GetApplicationDir": ' .. esc(safe_call("GetApplicationDir", function() return RSTD.GetApplicationDir() end)) .. ',')
    line(f, '  "RSTD_GetWorkingDirectory": ' .. esc(safe_call("GetWorkingDirectory", function() return RSTD.GetWorkingDirectory() end)) .. ',')
    line(f, '  "RSTD_GetInputPath": ' .. esc(safe_call("GetInputPath", function() return RSTD.GetInputPath() end)) .. ',')
    line(f, '  "RSTD_GetOutputPath": ' .. esc(safe_call("GetOutputPath", function() return RSTD.GetOutputPath() end)) .. ',')
    line(f, '  "RSTD_GetSettingsPath": ' .. esc(safe_call("GetSettingsPath", function() return RSTD.GetSettingsPath() end)) .. ',')
    line(f, '  "type_RSTD": ' .. esc(type(RSTD)) .. ',')
    line(f, '  "type_RTTT": ' .. esc(type(RTTT)) .. ',')
    line(f, '  "type_ar1": ' .. esc(type(ar1)) .. ',')
    line(f, '  "package_path": ' .. esc(package.path))
    line(f, "}")
    f:close()
end
