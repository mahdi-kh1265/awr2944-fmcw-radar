local f = io.open([[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/rstd_runscript_file_result.json]], "w")
if f then
    f:write([[{"executed":true,"method":"runscript-file"}]])
    f:close()
end
