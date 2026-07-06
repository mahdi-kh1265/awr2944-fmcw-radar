-- AR1 Replay Script (run_id: 99eb5ab1)
local result_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/99eb5ab1_extracted_replay_progress.jsonl]]
local function logProgress(func, args, ret, ok, err)
    local f = io.open(result_path, 'a')
    if f then
        local e = err and string.format(', "err": "%s"', tostring(err):gsub('"', '\\"')) or ''
        f:write(string.format('{"cmd": "%s", "args": "%s", "ret": %s, "ok": %s%s}\n', func, args:gsub('"', '\\"'), tostring(ret), tostring(ok), e))
        f:close()
    end
end

local ok, ret, err
-- line 81: [13:08:51]
ok, ret = pcall(function() return ar1.DownloadBSSFw("C:\\ti\\mmwave_studio_03_01_04_04\\rf_eval_firmware\\radarss\\xwr29xx_radarss_rprc.bin") end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("DownloadBSSFw", "\"C:\\\\ti\\\\mmwave_studio_03_01_04_04\\\\rf_eval_firmware\\\\radarss\\\\xwr29xx_radarss_rprc.bin\"", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in DownloadBSSFw: ' .. tostring(err or ret))
    -- return
end

-- line 82: [13:08:56]
ok, ret = pcall(function() return ar1.GetBSSFwVersion() end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("GetBSSFwVersion", "", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in GetBSSFwVersion: ' .. tostring(err or ret))
    -- return
end

-- line 84: [13:08:57]
ok, ret = pcall(function() return ar1.GetBSSPatchFwVersion() end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("GetBSSPatchFwVersion", "", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in GetBSSPatchFwVersion: ' .. tostring(err or ret))
    -- return
end

-- line 86: [13:08:58]
ok, ret = pcall(function() return ar1.DownloadMSSFw("C:\\ti\\mmwave_studio_03_01_04_04\\rf_eval_firmware\\masterss\\awr2xxx_mmwave_full_mss_rprc.bin") end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("DownloadMSSFw", "\"C:\\\\ti\\\\mmwave_studio_03_01_04_04\\\\rf_eval_firmware\\\\masterss\\\\awr2xxx_mmwave_full_mss_rprc.bin\"", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in DownloadMSSFw: ' .. tostring(err or ret))
    -- return
end

-- line 88: [13:09:32]
ok, ret = pcall(function() return ar1.GetMSSFwVersion() end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("GetMSSFwVersion", "", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in GetMSSFwVersion: ' .. tostring(err or ret))
    -- return
end

-- line 90: [13:09:35]
ok, ret = pcall(function() return ar1.PowerOn(0, 1000, 0, 0) end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("PowerOn", "0, 1000, 0, 0", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in PowerOn: ' .. tostring(err or ret))
    -- return
end

-- line 93: [13:09:36]
ok, ret = pcall(function() return ar1.RfEnable() end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("RfEnable", "", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in RfEnable: ' .. tostring(err or ret))
    -- return
end

-- line 96: [13:09:37]
ok, ret = pcall(function() return ar1.GetMSSFwVersion() end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("GetMSSFwVersion", "", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in GetMSSFwVersion: ' .. tostring(err or ret))
    -- return
end

-- line 98: [13:09:37]
ok, ret = pcall(function() return ar1.GetBSSFwVersion() end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("GetBSSFwVersion", "", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in GetBSSFwVersion: ' .. tostring(err or ret))
    -- return
end

-- line 100: [13:09:38]
ok, ret = pcall(function() return ar1.GetBSSPatchFwVersion() end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("GetBSSPatchFwVersion", "", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in GetBSSPatchFwVersion: ' .. tostring(err or ret))
    -- return
end
