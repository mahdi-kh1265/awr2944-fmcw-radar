local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/manual_connected_state_snapshot_result.json]]

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

local function safe(fn)
    local ok, ret = pcall(fn)
    if ok then return tostring(ret) else return "ERROR: " .. tostring(ret) end
end

local f = io.open(out_path, "w")
if f then
    f:write("{\n")
    f:write('  "type_ar1": ' .. esc(type(ar1)) .. ',\n')
    f:write('  "GuiVersion": ' .. esc(safe(function() return ar1.GuiVersion() end)) .. ',\n')
    f:write('  "GetVersion": ' .. esc(safe(function() return ar1.GetVersion() end)) .. ',\n')
    f:write('  "Calling_IsConnected": ' .. esc(safe(function() return ar1.Calling_IsConnected() end)) .. ',\n')
    f:write('  "IsConnected": ' .. esc(safe(function() return ar1.IsConnected() end)) .. '\n')
    f:write("}\n")
    f:close()
end
