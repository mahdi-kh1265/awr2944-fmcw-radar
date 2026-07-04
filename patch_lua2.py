import re

with open("src/awr2944_dca/mmws/lua_builder.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add manual_connect_script
manual_connect_script = """
def build_lua_manual_connect_script(run_id: str, result_path: str, com_num: int, baud: int) -> str:
    result_path = result_path.replace("\\\\", "/")
    return f\"\"\"\\
-- manual connect-script
-- run_id: {run_id}
local run_id = "{run_id}"
local out_path = [[{result_path}]]
local function esc(s)
    if s == nil then return "null" end
    s = tostring(s)
    s = s:gsub("\\\\\\\\", "\\\\\\\\\\\\\\\\")
    s = s:gsub('"', '\\\\\\\\"')
    s = s:gsub("\\\\r", "\\\\\\\\r")
    s = s:gsub("\\\\n", "\\\\\\\\n")
    s = s:gsub("\\\\t", "\\\\\\\\t")
    return '"' .. s .. '"'
end
local function line(f, s) f:write(s); f:write("\\\\n") end

local status = "NO_START"
local c_ret_str = "null"

local ok, err = pcall(function()
    status = "CHECKING_AR1"
    if type(ar1) ~= "table" then
        status = "AR1_MISSING"
        error("AR1_MISSING")
    end
    if ar1.Connect == nil then
        status = "CONNECT_METHOD_MISSING"
        error("CONNECT_METHOD_MISSING")
    end
    
    status = "BEFORE_CONNECT"
    WriteToLog("Attempting ar1.Connect({com_num}, {baud}, 1000)...\\\\n", "blue")
    
    local c_ok, c_ret = pcall(function() return ar1.Connect({com_num}, {baud}, 1000) end)
    
    if not c_ok then
        status = "CONNECT_EXCEPTION_NULLREF"
        error("CONNECT_EXCEPTION: " .. tostring(c_ret))
    end
    c_ret_str = esc(c_ret)
    if c_ret == 0 then
        status = "CONNECT_SUCCESS"
    else
        status = "CONNECT_RETURNED_ERROR"
    end
    
    local f = io.open(out_path, "w")
    if f then
        line(f, "{{")
        line(f, '  "run_id": ' .. esc(run_id) .. ',')
        line(f, '  "executed": true,')
        line(f, '  "status": ' .. esc(status) .. ',')
        line(f, '  "connect_return": ' .. c_ret_str .. ',')
        line(f, '  "error": null')
        line(f, "}}")
        f:close()
    end
end)

if not ok then
    local f = io.open(out_path, "w")
    if f then
        line(f, "{{")
        line(f, '  "run_id": ' .. esc(run_id) .. ',')
        line(f, '  "executed": false,')
        line(f, '  "status": ' .. esc(status) .. ',')
        line(f, '  "error": ' .. esc(tostring(err)))
        line(f, "}}")
        f:close()
    end
end
\"\"\"
"""

# Add ar1_methods script
ar1_methods_script = """
def build_lua_launch_ar1_methods(run_id: str, result_path: str, filter_str: str) -> str:
    result_path = result_path.replace("\\\\", "/")
    snippet = _STARTUP_LITE_SNIPPET.replace("\\\\", "\\\\\\\\")
    return f\"\"\"\\
local run_id = "{run_id}"
local out_path = [[{result_path}]]
local filter_str = "{filter_str}"

local function esc(s)
    if s == nil then return "null" end
    s = tostring(s)
    s = s:gsub("\\\\\\\\", "\\\\\\\\\\\\\\\\")
    s = s:gsub('"', '\\\\\\\\"')
    s = s:gsub("\\\\r", "\\\\\\\\r")
    s = s:gsub("\\\\n", "\\\\\\\\n")
    s = s:gsub("\\\\t", "\\\\\\\\t")
    return '"' .. s .. '"'
end
local function line(f, s) f:write(s); f:write("\\\\n") end

local ok, err = pcall(function()
{snippet}
    
    local methods = {{}}
    if type(ar1) == "table" then
        for k, v in pairs(ar1) do
            if type(v) == "function" or type(v) == "userdata" then
                if filter_str == "" or string.find(string.lower(k), string.lower(filter_str)) then
                    table.insert(methods, k)
                end
            end
        end
    end
    
    table.sort(methods)
    
    local f = io.open(out_path, "w")
    if f then
        line(f, "{{")
        line(f, '  "run_id": ' .. esc(run_id) .. ',')
        line(f, '  "executed": true,')
        line(f, '  "methods": [')
        for i, m in ipairs(methods) do
            if i < #methods then
                line(f, '    ' .. esc(m) .. ',')
            else
                line(f, '    ' .. esc(m))
            end
        end
        line(f, '  ]')
        line(f, "}}")
        f:close()
    end
end)

if not ok then
    local f = io.open(out_path, "w")
    if f then
        line(f, "{{")
        line(f, '  "run_id": ' .. esc(run_id) .. ',')
        line(f, '  "executed": false,')
        line(f, '  "error": ' .. esc(tostring(err)))
        line(f, "}}")
        f:close()
    end
end
\"\"\"
"""

# Modify connect-only
connect_only_target = 'status = "HUNG_AT_CONNECT"'
content = content.replace(connect_only_target, 'status = "CONNECT_EXCEPTION_NULLREF"')

with open("src/awr2944_dca/mmws/lua_builder.py", "w", encoding="utf-8") as f:
    f.write(content + "\n" + manual_connect_script + "\n" + ar1_methods_script)

print("lua_builder updated.")
