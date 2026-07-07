-- Test Lua script
if (ar1.ChanNAdcConfig(1, 15, 0, 2, 0, 0, 1, 2, 1, 0) == 0) then
    WriteToLog("ChanNAdcConfig Success")
end

ar1.DataPathConfig(1, 1, 0)

ar1.LVDSLaneConfig(0, 1, 1, 1, 1, 1, 0, 0)

ar1.ProfileConfig(0, 77, 10, 6, 60, 0, 0, 0, 0, 0, 0, 60.0, 0, 256, 10000, 0, 0, 94)

ar1.ChirpConfig(0, 0, 0, 0, 0, 0, 0, 1, 1, 0)

ar1.FrameConfig(0, 0, 128, 10, 50, 0, 1)
