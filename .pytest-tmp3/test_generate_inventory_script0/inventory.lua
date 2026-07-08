-- AWR2944 DCA Lab - Offline Inventory
local result = {
    probe_id = "test_inv_456",
    inventory_executed = true,
    ar1_exists = false,
    ar1_type = "nil",
    ar1_iterable = false,
    ar1_keys = {},
    g_keys = {}
}

-- Tiny JSON escaper
local function escapeJSON(s)
    if type(s) ~= "string" then return tostring(s) end
    s = s:gsub("\\", "\\\\")
    s = s:gsub('\"', '\\\"')
    s = s:gsub("\n", "\\n")
    s = s:gsub("\r", "\\r")
    s = s:gsub("\t", "\\t")
    -- truncate long strings
    if string.len(s) > 200 then
        s = string.sub(s, 1, 200) .. "..."
    end
    return s
end

local function record_ar1()
    if ar1 == nil then return end
    result.ar1_exists = true
    result.ar1_type = type(ar1)
    
    local status, err = pcall(function()
        local count = 0
        for k, v in pairs(ar1) do
            if count >= 500 then break end
            local key_str = escapeJSON(tostring(k))
            local type_str = type(v)
            local val_str = escapeJSON(tostring(v))
            table.insert(result.ar1_keys, string.format('        \"%s\": {"type": \"%s\", "value": \"%s\"}', key_str, type_str, val_str))
            count = count + 1
        end
        result.ar1_iterable = true
    end)
    
    if not status then
        result.ar1_iterable = false
        result.ar1_error = escapeJSON(err)
    end
end

local function record_G()
    local status, err = pcall(function()
        local count = 0
        for k, v in pairs(_G) do
            if count >= 500 then break end
            local key_str = escapeJSON(tostring(k))
            local type_str = type(v)
            table.insert(result.g_keys, string.format('        \"%s\": \"%s\"', key_str, type_str))
            count = count + 1
        end
    end)
end

record_ar1()
record_G()

-- Construct JSON string manually
local ar1_keys_json = table.concat(result.ar1_keys, ",\n")
local g_keys_json = table.concat(result.g_keys, ",\n")
local ar1_error_json = result.ar1_error and string.format(',\n    "ar1_error": "%s"', result.ar1_error) or ""

local json_str = string.format([[
{
    "probe_id": "%s",
    "inventory_executed": true,
    "ar1_exists": %s,
    "ar1_type": "%s",
    "ar1_iterable": %s%s,
    "ar1_keys": {
%s
    },
    "_G_keys": {
%s
    }
}
]], result.probe_id, tostring(result.ar1_exists), result.ar1_type, tostring(result.ar1_iterable), ar1_error_json, ar1_keys_json, g_keys_json)

local file, err = io.open("C:/Users/khams008/Documents/awr2944-fmcw-radar/.pytest-tmp3/test_generate_inventory_script0/inventory_result.json", "w")
if file then
    file:write(json_str)
    file:close()
end
