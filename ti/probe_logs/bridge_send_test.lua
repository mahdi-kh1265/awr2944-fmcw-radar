-- Bridge send-command test: write a result JSON file
local out_path = "C:/Users/khams008/Documents/awr2944-fmcw-radar/ti/probe_logs/bridge_send_test_result.json"
local f = io.open(out_path, "w")
if f then
    f:write('{"executed":true,"source":"bridge_send_command"}')
    f:close()
end
