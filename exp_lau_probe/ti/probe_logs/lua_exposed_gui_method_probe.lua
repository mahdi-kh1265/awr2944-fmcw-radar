local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/lua_exposed_gui_method_probe_result.json]]

local names = {
    "Connect",
    "Connect_Gui",
    "Connect_Ext",
    "ConnectEx",
    "iConnect",
    "iConnectSeq",
    "iConnect_Invoke",
    "iRs232ConnectDisconnect",
    "iRs232ConnectDisconnect_internal",
    "m_btnRS232Conct_Click",
    "m_btnRS232",
    "m_btnConnect_Click",
    "m_btnSetSop_Click",
    "iSopChangeInvoke",
    "setCOMport",
    "setBaudRate",
    "UpdateGuiFrRs232",
    "UpdateGuiFrSopCmd",
    "iPostConnect",
    "ConnectBegin",
    "ConnectEnd",
    "SetRS232ConnectReadyState",
    "GetBoardInfo",
    "GetBoardInfoAsLuaTable",
    "GetDeviceVariant",
    "GetSelectChipVersion",
    "GetPortNames",
    "SetSOPModeinGui"
}

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

local f = io.open(out_path, "w")
if f then
    f:write("{\n")
    f:write('  "type_ar1": ' .. esc(type(ar1)) .. ',\n')
    f:write('  "methods": {\n')
    for i, name in ipairs(names) do
        local t = "nil"
        if type(ar1) == "table" then
            t = type(ar1[name])
        end
        f:write('    ' .. esc(name) .. ': ' .. esc(t))
        if i < #names then f:write(",") end
        f:write("\n")
    end
    f:write("  }\n")
    f:write("}\n")
    f:close()
end
