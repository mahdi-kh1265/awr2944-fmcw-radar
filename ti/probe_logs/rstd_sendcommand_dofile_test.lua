local f = io.open([[C:/Users/khams008/Documents/awr2944-fmcw-radar/ti/probe_logs/rstd_sendcommand_dofile_result.json]], "w")
if f then
    f:write([[{"executed":true,"method":"sendcommand-dofile"}]])
    f:close()
end
