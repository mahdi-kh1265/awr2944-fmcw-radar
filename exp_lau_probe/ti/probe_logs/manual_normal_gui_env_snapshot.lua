local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/manual_normal_gui_env_snapshot_result.json]]

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

local function keys_of(t)
    if type(t) ~= "table" then return "" end
    local keys = {}
    for k, v in pairs(t) do
        table.insert(keys, tostring(k) .. ":" .. type(v))
    end
    table.sort(keys)
    return table.concat(keys, ", ")
end

local f = io.open(out_path, "w")
if f then
    line(f, "{")
    line(f, '  "type_ar1": ' .. esc(type(ar1)) .. ',')
    line(f, '  "type_RSTD": ' .. esc(type(RSTD)) .. ',')
    line(f, '  "type_RTTT": ' .. esc(type(RTTT)) .. ',')
    line(f, '  "type_WriteToLog": ' .. esc(type(WriteToLog)) .. ',')
    line(f, '  "type_writeToLog": ' .. esc(type(writeToLog)) .. ',')
    line(f, '  "type_ar1_ShowGui": ' .. esc(type(ar1 and ar1.ShowGui)) .. ',')
    line(f, '  "type_ar1_Connect": ' .. esc(type(ar1 and ar1.Connect)) .. ',')
    line(f, '  "RTTT_keys": ' .. esc(keys_of(RTTT)))
    line(f, "}")
    f:close()
end
