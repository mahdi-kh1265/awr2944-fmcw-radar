-- AR1 Replay Script (run_id: 4890c210)
local result_path = [[C:/Users/khams008/Documents/awr2944-fmcw-radar/exp_lau_probe/ti/probe_logs/4890c210_extracted_replay_progress.jsonl]]
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
    return -- abort replay script on error
end

-- line 82: [13:08:56]
ok, ret = pcall(function() return ar1.GetBSSFwVersion() end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("GetBSSFwVersion", "", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in GetBSSFwVersion: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 84: [13:08:57]
ok, ret = pcall(function() return ar1.GetBSSPatchFwVersion() end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("GetBSSPatchFwVersion", "", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in GetBSSPatchFwVersion: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 86: [13:08:58]
ok, ret = pcall(function() return ar1.DownloadMSSFw("C:\\ti\\mmwave_studio_03_01_04_04\\rf_eval_firmware\\masterss\\awr2xxx_mmwave_full_mss_rprc.bin") end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("DownloadMSSFw", "\"C:\\\\ti\\\\mmwave_studio_03_01_04_04\\\\rf_eval_firmware\\\\masterss\\\\awr2xxx_mmwave_full_mss_rprc.bin\"", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in DownloadMSSFw: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 88: [13:09:32]
ok, ret = pcall(function() return ar1.GetMSSFwVersion() end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("GetMSSFwVersion", "", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in GetMSSFwVersion: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 90: [13:09:35]
ok, ret = pcall(function() return ar1.PowerOn(0, 1000, 0, 0) end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("PowerOn", "0, 1000, 0, 0", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in PowerOn: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 93: [13:09:36]
ok, ret = pcall(function() return ar1.RfEnable() end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("RfEnable", "", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in RfEnable: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 96: [13:09:37]
ok, ret = pcall(function() return ar1.GetMSSFwVersion() end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("GetMSSFwVersion", "", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in GetMSSFwVersion: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 98: [13:09:37]
ok, ret = pcall(function() return ar1.GetBSSFwVersion() end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("GetBSSFwVersion", "", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in GetBSSFwVersion: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 100: [13:09:38]
ok, ret = pcall(function() return ar1.GetBSSPatchFwVersion() end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("GetBSSPatchFwVersion", "", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in GetBSSPatchFwVersion: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 138: [15:05:30]
ok, ret = pcall(function() return ar1.DataPathConfig(513, 1216644097, 0) end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("DataPathConfig", "513, 1216644097, 0", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in DataPathConfig: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 140: [15:05:38]
ok, ret = pcall(function() return ar1.LVDSLaneConfig(0, 1, 0, 0, 0, 1, 0, 0) end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("LVDSLaneConfig", "0, 1, 0, 0, 0, 1, 0, 0", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in LVDSLaneConfig: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 142: [15:05:40]
ok, ret = pcall(function() return ar1.LVDSLaneConfig(0, 1, 0, 0, 0, 1, 0, 0) end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("LVDSLaneConfig", "0, 1, 0, 0, 0, 1, 0, 0", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in LVDSLaneConfig: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 144: [15:05:54]
ok, ret = pcall(function() return ar1.LPModConfig(0, 0) end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("LPModConfig", "0, 0", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in LPModConfig: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 146: [15:05:56]
ok, ret = pcall(function() return ar1.RfLdoBypassConfig(0x0) end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("RfLdoBypassConfig", "0x0", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in RfLdoBypassConfig: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 148: [15:05:57]
ok, ret = pcall(function() return ar1.SetCalMonFreqLimitConfig(76,81,0) end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("SetCalMonFreqLimitConfig", "76,81,0", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in SetCalMonFreqLimitConfig: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 150: [15:05:58]
ok, ret = pcall(function() return ar1.SetRFDeviceConfig(5, 0, 0, 0, 0, 0, 0) end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("SetRFDeviceConfig", "5, 0, 0, 0, 0, 0, 0", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in SetRFDeviceConfig: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 152: [15:05:59]
ok, ret = pcall(function() return ar1.RfSetCalMonFreqTxPowLimitConfig(76, 76, 76, 76, 81, 81, 81, 81, 0, 0, 0, 0,0) end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("RfSetCalMonFreqTxPowLimitConfig", "76, 76, 76, 76, 81, 81, 81, 81, 0, 0, 0, 0,0", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in RfSetCalMonFreqTxPowLimitConfig: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 154: [15:05:59]
ok, ret = pcall(function() return ar1.SetApllSynthBWCtlConfig(1, 4, 3, 9, 18, 1, 4) end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("SetApllSynthBWCtlConfig", "1, 4, 3, 9, 18, 1, 4", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in SetApllSynthBWCtlConfig: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 156: [15:06:00]
ok, ret = pcall(function() return ar1.RfInit() end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("RfInit", "", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in RfInit: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 160: [15:06:19]
ok, ret = pcall(function() return ar1.RfInit() end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("RfInit", "", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in RfInit: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 164: [15:06:31]
ok, ret = pcall(function() return ar1.ProfileConfig(0, 77, 100, 6, 60, 0, 0, 0, 0, 0, 0, 0, 0, 29.982, 0, 256, 10000, 2216755200, 0, 30, 0, 0, 0) end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("ProfileConfig", "0, 77, 100, 6, 60, 0, 0, 0, 0, 0, 0, 0, 0, 29.982, 0, 256, 10000, 2216755200, 0, 30, 0, 0, 0", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in ProfileConfig: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 166: [15:06:34]
ok, ret = pcall(function() return ar1.ChirpConfig(0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0) end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("ChirpConfig", "0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in ChirpConfig: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 169: [15:06:39]
ok, ret = pcall(function() return ar1.DisableTestSource(0) end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("DisableTestSource", "0", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in DisableTestSource: ' .. tostring(err or ret))
    return -- abort replay script on error
end

-- line 171: [15:06:39]
ok, ret = pcall(function() return ar1.FrameConfig(0, 0, 8, 128, 40, 0, 1) end)
if not ok then err = ret; ret = nil else err = nil end
logProgress("FrameConfig", "0, 0, 8, 128, 40, 0, 1", ret, ok, err)
if not ok or (ret and type(ret) == 'number' and ret ~= 0) then
    print('Error in FrameConfig: ' .. tostring(err or ret))
    return -- abort replay script on error
end
