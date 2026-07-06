local out_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/manual_com_sweep_after_set_result.json]]
local jsonl_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/manual_com_sweep_after_set_progress.jsonl]]

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
        line(lf, '{"step": ' .. esc(step) .. ', "detail": ' .. esc(detail) .. '}')
        lf:close()
    end
end

local ports = {3, 4, 5, 6}
local winner = nil
local returns = {}

local lf = io.open(jsonl_path, "w")
if lf then lf:close() end

for _, p in ipairs(ports) do
    progress("before_Connect", "COM" .. tostring(p))
    local ok, ret = pcall(function()
        return ar1.Connect(p, 115200, 1000)
    end)
    if ok then
        progress("after_Connect", "COM" .. tostring(p) .. " ret=" .. tostring(ret))
        returns[p] = tostring(ret)
        if ret == 0 then
            winner = p
            break
        end
    else
        progress("after_Connect", "COM" .. tostring(p) .. " ERROR=" .. tostring(ret))
        returns[p] = "ERROR: " .. tostring(ret)
    end
    RSTD.Sleep(1000)
end

local f = io.open(out_path, "w")
if f then
    line(f, "{")
    line(f, '  "winner": ' .. esc(winner) .. ',')
    line(f, '  "COM3": ' .. esc(returns[3]) .. ',')
    line(f, '  "COM4": ' .. esc(returns[4]) .. ',')
    line(f, '  "COM5": ' .. esc(returns[5]) .. ',')
    line(f, '  "COM6": ' .. esc(returns[6]))
    line(f, "}")
    f:close()
end
