# Static TI Lua Workflow Analysis

This document shows static calls found in TI Lua scripts. These were **not** executed.

## CaptureImport
- `json.lua:6` : `ar1.CaptureImport("C:\\ti\\mmwave_studio_03_00_00_14\\mmWaveStudio\\JSONSampleFiles\\22xx\\22xx.setup.json")`

## ConfigureSetup
- `json.lua:8` : `ar1.ConfigureSetup()`

## JsonImport
- `json.lua:13` : `ar1.JsonImport("C:\\ti\\mmwave_studio_03_00_00_14\\mmWaveStudio\\JSONSampleFiles\\22xx\\22xx.mmwave.json")`

## JsonLoad
- `json.lua:16` : `ar1.JsonLoad(0)`

## JsonExecute
- `json.lua:19` : `ar1.JsonExecute(0)`

## JsonExport
- `json.lua:22` : `ar1.JsonExport("C:\\ti\\mmwave_studio_03_00_00_14\\mmWaveStudio\\JSONSampleFiles\\22xx\\22xx_export.setup.json", "C:\\ti\\mmwave_studio_03_00_00_14\\mmWaveStudio\\JSONSampleFiles\\22xx\\22xx_export.mmwave.json")`

## FullReset
- `125cLoop.lua:3` : `ar1.FullReset()`

## SOPControl
- `125cLoop.lua:5` : `ar1.SOPControl(2)`
- `RadarStudioAPIsTest.lua:5` : `if (0 == ar1.SOPControl(2)) then`

## Connect
- `125cLoop.lua:7` : `ar1.Connect(100,921600,1000)`
- `RadarStudioAPIsTest.lua:13` : `if (0 == ar1.Connect(24,921600,1000)) then`

## DownloadBSSFw
- `125cLoop.lua:10` : `ar1.DownloadBSSFw("C:\\Users\\a0393390\\Desktop\\ar1xxx_bss.bin")`
- `Advanced_Chirp_Example.lua:90` : `if (ar1.DownloadBSSFw(BSS_FW) == 0) then`
- `DataCaptureDemo_xWR.lua:56` : `if (ar1.DownloadBSSFw(BSS_FW) == 0) then`
- `loop.lua:1` : `ar1.DownloadBSSFw("C:\\Users\\a0393390\\Desktop\\ar1xxx_bss.bin")`
- `RadarStudioAPIsTest.lua:21` : `if (ar1.DownloadBSSFw("\\\\ar04\\c$\\WakeUp_SW\\Firmware\\BSS_1.0.0.16\\ar1xxx_bss.bin")) then`

## DownloadMSSFw
- `125cLoop.lua:12` : `ar1.DownloadMSSFw("C:\\Users\\a0393390\\Desktop\\ar1xxx_mss.bin")`
- `Advanced_Chirp_Example.lua:98` : `if (ar1.DownloadMSSFw(MSS_FW) == 0) then`
- `DataCaptureDemo_xWR.lua:64` : `if (ar1.DownloadMSSFw(MSS_FW) == 0) then`
- `loop.lua:3` : `ar1.DownloadMSSFw("C:\\Users\\a0393390\\Desktop\\ar1xxx_mss.bin")`
- `RadarStudioAPIsTest.lua:29` : `if (0 == ar1.DownloadMSSFw("\\\\ar04\\c$\\WakeUp_SW\\Firmware\\MSS_1.0.0.13\\ar1xxx_mss.bin")) then`

## PowerOn
- `125cLoop.lua:14` : `ar1.PowerOn(0, 0, 0, 0)`
- `Advanced_Chirp_Example.lua:106` : `apiReturn = ar1.PowerOn(0, 1000, 0, 0)`
- `DataCaptureDemo_xWR.lua:72` : `if (ar1.PowerOn(1, 1000, 0, 0) == 0) then`
- `RadarStudioAPIsTest.lua:37` : `if (0 == ar1.PowerOn(0, 0, 0, 0)) then`

## RfEnable
- `125cLoop.lua:15` : `ar1.RfEnable()`
- `Advanced_Chirp_Example.lua:114` : `apiReturn = ar1.RfEnable()`
- `DataCaptureDemo_xWR.lua:80` : `if (ar1.RfEnable() == 0) then`
- `RadarStudioAPIsTest.lua:46` : `if (0 == ar1.RfEnable()) then`

## ChanNAdcConfig
- `125cLoop.lua:18` : `ar1.ChanNAdcConfig(1, 1, 0, 1, 1, 1, 1, 2, 2, 0)`
- `Advanced_Chirp_Example.lua:121` : `apiReturn = ar1.ChanNAdcConfig(1, 1, 1, 1, 1, 1, 1, 0, 3, 0)`
- `DataCaptureDemo_xWR.lua:87` : `if (ar1.ChanNAdcConfig(1, 1, 0, 1, 1, 1, 1, 2, 1, 0) == 0) then`
- `RadarStudioAPIsTest.lua:55` : `if (0 == ar1.ChanNAdcConfig(1, 1, 0, 1, 1, 1, 1, 2, 1, 0)) then`

## LPModConfig
- `125cLoop.lua:19` : `ar1.LPModConfig(0, 0)`
- `Advanced_Chirp_Example.lua:132` : `if (0 ~= ar1.LPModConfig(0, 0)) then`
- `DataCaptureDemo_xWR.lua:94` : `if (ar1.LPModConfig(0, 0) == 0) then`
- `RadarStudioAPIsTest.lua:63` : `if (0 == ar1.LPModConfig(0, 0)) then`

## RfInit
- `125cLoop.lua:20` : `ar1.RfInit()`
- `Advanced_Chirp_Example.lua:137` : `if (0 ~= ar1.RfInit()) then`
- `DataCaptureDemo_xWR.lua:101` : `if (ar1.RfInit() == 0) then`
- `RadarStudioAPIsTest.lua:71` : `if (0 == ar1.RfInit()) then`

## DataPathConfig
- `125cLoop.lua:23` : `ar1.DataPathConfig(1, 0, 0)`
- `Advanced_Chirp_Example.lua:148` : `if (0 ~= ar1.DataPathConfig(513, 1216644097, 0)) then`
- `DataCaptureDemo_xWR.lua:109` : `if (ar1.DataPathConfig(1, 1, 0) == 0) then`
- `RadarStudioAPIsTest.lua:79` : `if (0 == ar1.DataPathConfig(1, 0, 0)) then`

## LvdsClkConfig
- `125cLoop.lua:24` : `ar1.LvdsClkConfig(1, 0)`
- `Advanced_Chirp_Example.lua:153` : `if (0 ~= ar1.LvdsClkConfig(1, 1)) then`
- `DataCaptureDemo_xWR.lua:116` : `if (ar1.LvdsClkConfig(1, 1) == 0) then`
- `RadarStudioAPIsTest.lua:87` : `if (0 == ar1.LvdsClkConfig(1, 0)) then`

## LVDSLaneConfig
- `125cLoop.lua:25` : `ar1.LVDSLaneConfig(0, 1, 1, 1, 1, 1, 0, 0)`
- `Advanced_Chirp_Example.lua:158` : `if (0 ~= ar1.LVDSLaneConfig(0, 1, 1, 1, 1, 1, 0, 0)) then`
- `DataCaptureDemo_xWR.lua:123` : `if (ar1.LVDSLaneConfig(0, 1, 1, 1, 1, 1, 0, 0) == 0) then`
- `RadarStudioAPIsTest.lua:95` : `if (0 == ar1.LVDSLaneConfig(0, 1, 1, 1, 1, 1, 0, 0, 0)) then`

## ProfileConfig
- `125cLoop.lua:28` : `ar1.ProfileConfig(0, 77, 100, 6, 60, 0, 0, 0, 0, 0, 0, 30, 1, 256, 10000, 0, 0, 30)`
- `Advanced_Chirp_Example.lua:164` : `if (0 ~= ar1.ProfileConfig(0, SENSOR_CFG.PROFILE_CONFIG.START_FREQ_0, SENSOR_CFG.PROFILE_CONFIG.IDLE_TIME_0,`
- `DataCaptureDemo_xWR.lua:131` : `if(ar1.ProfileConfig(0, 77, 100, 6, 60, 0, 0, 0, 0, 0, 0, 29.982, 0, 256, 10000, 0, 0, 94) == 0) then`
- `RadarStudioAPIsTest.lua:101` : `if (0 == ar1.ProfileConfig(0, 76, 100, 3, 60, 0, 0, 0, 0, 0, 0, 30, 1, 256, 10000, 0, 0, 30)) then`

## ChirpConfig
- `125cLoop.lua:29` : `ar1.ChirpConfig(0, 0, 0, 0, 0, 0, 0, 1, 1, 0)`
- `DataCaptureDemo_xWR.lua:137` : `if (ar1.ChirpConfig(0, 0, 0, 0, 0, 0, 0, 1, 1, 0) == 0) then`
- `RadarStudioAPIsTest.lua:109` : `if (0 == ar1.ChirpConfig(0, 0, 0, 0, 0, 0, 0, 1, 1, 0)) then`

## FrameConfig
- `125cLoop.lua:30` : `ar1.FrameConfig(0, 0, 0, 8, 2, 0)`
- `DataCaptureDemo_xWR.lua:146` : `if (ar1.FrameConfig(0, 0, 8, 128, 40, 0, 1) == 0) then`
- `RadarStudioAPIsTest.lua:133` : `if (0 == ar1.FrameConfig(0, 0, 0, 8, 2, 0)) then`

## StartFrame
- `125cLoop.lua:31` : `ar1.StartFrame()`
- `Advanced_Chirp_Example.lua:354` : `if (0 ~= ar1.StartFrame()) then`
- `DataCaptureDemo_xWR.lua:193` : `ar1.StartFrame()`
- `RadarStudioAPIsTest.lua:142` : `ar1.StartFrame()`

## StopFrame
- `125cLoop.lua:32` : `ar1.StopFrame()`
- `RadarStudioAPIsTest.lua:146` : `ar1.StopFrame()`

## ReadRegister
- `Advanced_Chirp_Example.lua:18` : `res, efusedevice = ar1.ReadRegister(0xFFFFE214, 0, 31)`
- `Advanced_Chirp_Example.lua:31` : `res, ESVersion = ar1.ReadRegister(0xFFFFE218, 0, 31)`
- `DataCaptureDemo_xWR.lua:23` : `res, efusedevice = ar1.ReadRegister(0xFFFFE214, 0, 31)`
- `DataCaptureDemo_xWR.lua:36` : `res, ESVersion = ar1.ReadRegister(0xFFFFE218, 0, 31)`

## RfLdoBypassConfig
- `Advanced_Chirp_Example.lua:127` : `if (0 ~= ar1.RfLdoBypassConfig(0x3)) then`

## SetRFDeviceConfig
- `Advanced_Chirp_Example.lua:143` : `if (0 ~= ar1.SetRFDeviceConfig(5, 0, STATIC_CFG.DIS_POWER_SAVE, STATIC_CFG.EN_WDT, 0, 0, 0)) then`

## SetMiscConfig
- `Advanced_Chirp_Example.lua:177` : `apiReturn = ar1.SetMiscConfig(1, 1, 0, 0)`

## ClearAdvChirpLUTConfig
- `Advanced_Chirp_Example.lua:182` : `apiReturn = ar1.ClearAdvChirpLUTConfig()`

## SetProfileAdvChirpConfigLUT
- `Advanced_Chirp_Example.lua:187` : `apiReturn = ar1.SetProfileAdvChirpConfigLUT(0, 4, 0, 0, 0, 0)`

## SetStartFreqAdvChirpConfigLUT
- `Advanced_Chirp_Example.lua:192` : `apiReturn = ar1.SetStartFreqAdvChirpConfigLUT(16, 4, 0, 0, 0, 0.01, 0.02, 0.03)`

## SetTxEnAdvChirpConfigLUT
- `Advanced_Chirp_Example.lua:197` : `apiReturn = ar1.SetTxEnAdvChirpConfigLUT(32, 4, 3, 7, 3, 7)`

## SetTx0PhShiftAdvChirpConfigLUT
- `Advanced_Chirp_Example.lua:202` : `apiReturn = ar1.SetTx0PhShiftAdvChirpConfigLUT(48, 4, 5.625, 11.25, 16.875, 22.5)`

## AdvChirpLUTConfig
- `Advanced_Chirp_Example.lua:207` : `apiReturn = ar1.AdvChirpLUTConfig(0, 64)`

## AdvChirpConfig
- `Advanced_Chirp_Example.lua:217` : `apiReturn = ar1.AdvChirpConfig(0, 0, 0, 0, 0, 0, 0, 0, 4, 1, 0,  4, 0, 0, 0, 0, 0)`
- `Advanced_Chirp_Example.lua:225` : `apiReturn = ar1.AdvChirpConfig(1, 0, 8, 1, 18641, 18641, 18641, 18641, 4, 1, 16, 4, 0, 0, 0, 0, 0)`
- `Advanced_Chirp_Example.lua:233` : `apiReturn = ar1.AdvChirpConfig(2, 0, 0, 0, 0, 0, 0, 0, 4, 1, 0,  4, 0, 0, 0, 0, 0)`
- `Advanced_Chirp_Example.lua:241` : `apiReturn = ar1.AdvChirpConfig(3, 0, 0, 0, 0, 0, 0, 0, 4, 1, 0,  4, 0, 0, 0, 0, 0)`
- `Advanced_Chirp_Example.lua:249` : `apiReturn = ar1.AdvChirpConfig(4, 0, 0, 0, 0, 0, 0, 0, 4, 1, 0,  4, 0, 0, 0, 0, 0)`
- `Advanced_Chirp_Example.lua:257` : `apiReturn = ar1.AdvChirpConfig(5, 0, 0, 0, 0, 0, 0, 0, 4, 1, 32, 4, 0, 0, 0, 0, 0)`
- `Advanced_Chirp_Example.lua:265` : `apiReturn = ar1.AdvChirpConfig(6, 0, 0, 0, 0, 0, 0, 0, 4, 1, 0,  4, 0, 0, 0, 0, 0)`
- `Advanced_Chirp_Example.lua:273` : `apiReturn = ar1.AdvChirpConfig(7, 0, 0, 0, 0, 0, 0, 0, 4, 1, 48,  4, 0, 0, 0, 0, 0)`
- `Advanced_Chirp_Example.lua:281` : `apiReturn = ar1.AdvChirpConfig(8, 0, 0, 0, 0, 0, 0, 0, 4, 1, 48,  4, 0, 0, 0, 0, 0)`
- `Advanced_Chirp_Example.lua:289` : `apiReturn = ar1.AdvChirpConfig(9, 0, 0, 0, 0, 0, 0, 0, 4, 1, 48,  4, 0, 0, 0, 0, 0)`

## AdvanceFrameConfig
- `Advanced_Chirp_Example.lua:317` : `res = ar1.AdvanceFrameConfig(SENSOR_CFG.ADV_FRAME_CONFIG.NUM_SUB_FRAMES, 1536, 0, 0, 1, 96, 540000, 0, 10, 2, 10809000, 0, 0, 1, 96, 540000, 0,10, 2, 10809000, 0, 0, 1, 96, 540000, 0, 10, 2, 10809000, 0, 0, 1, 96,540000, 0, 10, 2, 22000000, SENSOR_CFG.ADV_FRAME_CONFIG.NUM_FRAMES, 1, 0, 4, 1920, 256, 1, 1920, 256, 1, 1920,256, 1, 1920, 256, 1)`
- `DataCaptureDemo_xWR.lua:152` : `if (ar1.AdvanceFrameConfig(4, 1536, 0, 0, 1, 128, 8000000, 0, 1, 1, 8000000, 0, 0, 1, 128, 8000000, 0,1, 1, 8000000, 0, 0, 1, 128, 8000000, 0, 1, 1, 8000000, 0, 0, 1, 128,8000000, 0, 1, 1, 8000000, 8, 1, 0, 1, 128, 0, 1, 128, 1, 1, 128,1, 1, 128, 1, 1) == 0) then`

## SelectCaptureDevice
- `Advanced_Chirp_Example.lua:324` : `if (ar1.SelectCaptureDevice("DCA1000") == 0) then`
- `DataCaptureDemo_xWR.lua:161` : `if (ar1.SelectCaptureDevice("DCA1000") == 0) then`

## CaptureCardConfig_EthInit
- `Advanced_Chirp_Example.lua:331` : `if (ar1.CaptureCardConfig_EthInit("192.168.33.30", "192.168.33.180", "12:34:56:78:90:12", 4096, 4098) == 0) then`
- `DataCaptureDemo_xWR.lua:168` : `if (ar1.CaptureCardConfig_EthInit("192.168.33.30", "192.168.33.180", "12:34:56:78:90:12", 4096, 4098) == 0) then`

## CaptureCardConfig_Mode
- `Advanced_Chirp_Example.lua:337` : `if (ar1.CaptureCardConfig_Mode(1, 1, 1, 2, 3, 30) == 0) then`
- `DataCaptureDemo_xWR.lua:174` : `if (ar1.CaptureCardConfig_Mode(1, 1, 1, 2, 3, 30) == 0) then`

## CaptureCardConfig_PacketDelay
- `Advanced_Chirp_Example.lua:343` : `if (ar1.CaptureCardConfig_PacketDelay(25) == 0) then`
- `DataCaptureDemo_xWR.lua:180` : `if (ar1.CaptureCardConfig_PacketDelay(25) == 0) then`

## CaptureCardConfig_StartRecord
- `Advanced_Chirp_Example.lua:350` : `ar1.CaptureCardConfig_StartRecord(adc_data_path, 1)`
- `DataCaptureDemo_xWR.lua:189` : `ar1.CaptureCardConfig_StartRecord(adc_data_path, 1)`

## StartMatlabPostProc
- `Advanced_Chirp_Example.lua:362` : `ar1.StartMatlabPostProc(adc_data_path)`
- `DataCaptureDemo_xWR.lua:197` : `ar1.StartMatlabPostProc(adc_data_path)`

## ReadRegisterByName
- `ar1.lua:18` : `res, val = ar1.ReadRegisterByName (full_path, tonumber(start_bit), tonumber(end_bit))`
- `ar1.lua:74` : `res, val = ar1.ReadRegisterByName (full_path, tonumber(start_bit), tonumber(end_bit))`

## ReadByName
- `ar1.lua:20` : `res, val = ar1.ReadByName (full_path)`
- `ar1.lua:76` : `res, val = ar1.ReadByName (full_path)`

## WriteRegisterByName
- `ar1.lua:48` : `res = ar1.WriteRegisterByName (full_path, tonumber(start_bit), tonumber(end_bit), value)`
- `ar1.lua:104` : `res = ar1.WriteRegisterByName (full_path, tonumber(start_bit), tonumber(end_bit), value)`

## WriteByName
- `ar1.lua:50` : `res = ar1.WriteByName (full_path, value)`
- `ar1.lua:106` : `res = ar1.WriteByName (full_path, value)`

## lua
- `AR1xFunctions.lua:76` : `dofile(RSTD_PATH .. "\\Scripts\\ar1.lua")`

## ShowGui
- `AR1xFunctions.lua:79` : `ar1.ShowGui()`

## Calling_ReadAddr_Single
- `bitoperations.lua:245` : `local ret, regVal = ar1.Calling_ReadAddr_Single(addr)`
- `bitoperations.lua:260` : `local regVal = ar1.Calling_ReadAddr_Single(addr)`
- `ar1.lua:13` : `res, val = ar1.Calling_ReadAddr_Single(abs_address)`
- `ar1.lua:46` : `res, reg_val = ar1.Calling_ReadAddr_Single(abs_address)`

## Calling_WriteAddr_Single
- `bitoperations.lua:269` : `ar1.Calling_WriteAddr_Single(addr, regVal)`
- `ar1.lua:43` : `res = ar1.Calling_WriteAddr_Single(abs_address, value)`
- `ar1.lua:51` : `res = ar1.Calling_WriteAddr_Single(abs_address, reg_val)`

## ContStrConfig
- `DataCaptureDemo_xWR.lua:203` : `if(ar1.ContStrConfig(77, 9000, 94, 0, 0, 0, 0, 0, 0, 0, 0) == 0) then`

## ContStrModEnable
- `DataCaptureDemo_xWR.lua:210` : `ar1.ContStrModEnable()`

## BasicConfigurationForAnalysis
- `DataCaptureDemo_xWR.lua:213` : `ar1.BasicConfigurationForAnalysis(16384, 16384, 1, 0, 0, 0, 1)`
- `Meas_Gain.lua:14` : `Success = ar1.BasicConfigurationForAnalysis(Num_Samples_per_Channel, Num_FFT_Points, 1, 1, 1, 1, 2)`
- `Meas_NF.lua:16` : `Success = ar1.BasicConfigurationForAnalysis(Num_Samples_per_Channel, Num_FFT_Points, 1, 1, 1, 1, 2)`
- `Cascade_Capture_ContStream.lua:115` : `if (0 == ar1.BasicConfigurationForAnalysis(numSamples, numSamples, 1, 0, 0, 0, 1)) then`

## CaptureCardConfig_StartRecord_ContinuousStreamData
- `DataCaptureDemo_xWR.lua:216` : `ar1.CaptureCardConfig_StartRecord_ContinuousStreamData(adc_data_path, 0)`

## ContStrModDisable
- `DataCaptureDemo_xWR.lua:220` : `ar1.ContStrModDisable()`

## ProcessContStreamADCData
- `DataCaptureDemo_xWR.lua:223` : `ar1.ProcessContStreamADCData(adc_data_path)`
- `Meas_Gain.lua:24` : `Success = ar1.ProcessContStreamADCData(ADC_File_Path)--TBD remove the extra parameter`
- `Meas_NF.lua:29` : `Success = ar1.ProcessContStreamADCData(ADC_File_Path)`

## ContStrConfig_mult
- `DataCapture_CascadeCW.lua:63` : `status 			= ar1.ContStrConfig_mult(1,Test_freq, Sample_Rate, Rx_Gain, HPF1_Corner_Freq, HPF2_Corner_Freq, Tx_Backoff,Tx_Backoff,Tx_Backoff, 0, 0, 0)`
- `DataCapture_CascadeCW.lua:67` : `status		=	status + ar1.ContStrConfig_mult(dev_list[CW_Test_Dev],Test_freq, Sample_Rate, Rx_Gain, HPF1_Corner_Freq, HPF2_Corner_Freq, Tx_Backoff, Tx_Backoff, Tx_Backoff, 0, 0, 0)`
- `Cascade_Capture_ContStream.lua:34` : `if (0 == ar1.ContStrConfig_mult(deviceMapOverall, start_freq, sample_freq, rx_gain, hpfCornerFreq1,`

## RFTemperatureGet_mult
- `DemoConfig_Cascade.lua:138` : `ErrStatus,Time_ms,Rx1_Temp,Rx2_Temp,Rx3_Temp,Rx4_Temp,Tx1_Temp,Tx2_Temp,Tx3_Temp,PM_Temp,Dig_Temp = ar1.RFTemperatureGet_mult(dev_list[CW_Test_Dev])`
- `Cascade_Configuration_TXBF_AngleSweep.lua:612` : `dummy1, Timestamp, Rx1TempVal[devIdx], Rx2TempVal[devIdx], Rx3TempVal[devIdx], Rx4TempVal[devIdx], Tx1TempVal[devIdx], Tx2TempVal[devIdx], Tx3TempVal[devIdx], PMTempVal[devIdx], Dig1TempVal[devIdx], Dig2TempVal[devIdx] = ar1.RFTemperatureGet_mult(dev_list[devIdx])`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:955` : `dummy1, Timestamp, Rx1TempVal[devIdx], Rx2TempVal[devIdx], Rx3TempVal[devIdx], Rx4TempVal[devIdx], Tx1TempVal[devIdx], Tx2TempVal[devIdx], Tx3TempVal[devIdx], PMTempVal[devIdx], Dig1TempVal[devIdx], Dig2TempVal[devIdx] = ar1.RFTemperatureGet_mult(dev_list[devIdx])`

## CustomCommand_mult
- `DemoConfig_Cascade.lua:155` : `status = ar1.CustomCommand_mult(dev_list[Device_ID], 0x1, 0x0, 0x8, 0x1, 0x104, 0x4,"0"..En1_Dis0.."000000") --Enable/disable Continuous Stream`
- `DemoConfig_Cascade.lua:156` : `status = status + ar1.CustomCommand_mult(dev_list[Device_ID], 0x5, 0x0, 0x202, 0x1, 0x4046, 0x4,"0"..En1_Dis0.."000000") --Enable the continuous mode data transfer`

## StartFrame_mult
- `DemoConfig_Cascade.lua:162` : `status = ar1.StartFrame_mult(dev_list[Device_ID]) --Start Trigger Frame`
- `Cascade_Capture.lua:56` : `status = ar1.StartFrame_mult(dev_list[Device_ID]) --Start Trigger Frame`
- `Cascade_Configuration_TXBF_AngleSweep.lua:187` : `status = ar1.StartFrame_mult(dev_list[Device_ID]) --Start Trigger Frame`
- `Cascade_Configuration_TXBF_Simple.lua:217` : `status = ar1.StartFrame_mult(dev_list[Device_ID]) --Start Trigger Frame`
- `Cascade_Monitoring_Example.lua:30` : `status = ar1.StartFrame_mult(dev_list[Device_ID]) --Start Trigger Frame`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:537` : `status = ar1.StartFrame_mult(dev_list[Device_ID]) --Start Trigger Frame`

## SOPControl_mult
- `DemoConfig_Cascade.lua:309` : `if (0 == ar1.SOPControl_mult(dev_list[1],sop_mode)) then`
- `DemoConfig_Cascade.lua:343` : `if (0 == ar1.SOPControl_mult(dev_list[i],sop_mode)) then`
- `Cascade_Configuration_Basic.lua:83` : `if (0 == ar1.SOPControl_mult(dev_list[i], 4)) then`
- `Cascade_Configuration_ContStream.lua:72` : `if (0 == ar1.SOPControl_mult(1, 4)) then`
- `Cascade_Configuration_ContStream.lua:118` : `if (0 == ar1.SOPControl_mult(dev_list[i], 4)) then`
- `Cascade_Configuration_MIMO.lua:540` : `if (0 == ar1.SOPControl_mult(1, 4)) then`
- `Cascade_Configuration_MIMO.lua:586` : `if (0 == ar1.SOPControl_mult(dev_list[i], 4)) then`
- `Cascade_Configuration_TestSource.lua:116` : `if (0 == ar1.SOPControl_mult(1, 4)) then`
- `Cascade_Configuration_TestSource.lua:162` : `if (0 == ar1.SOPControl_mult(dev_list[i], 4)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:348` : `if (0 == ar1.SOPControl_mult(1, 4)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:395` : `if (0 == ar1.SOPControl_mult(dev_list[i], 4)) then`
- `Cascade_Configuration_TXBF_Simple.lua:378` : `if (0 == ar1.SOPControl_mult(1, 4)) then`
- `Cascade_Configuration_TXBF_Simple.lua:425` : `if (0 == ar1.SOPControl_mult(dev_list[i], 4)) then`
- `Cascade_Flashing_example.lua:63` : `if (0 == ar1.SOPControl_mult(1, 4)) then`
- `Cascade_Flashing_example.lua:91` : `if (0 == ar1.SOPControl_mult(1, 4)) then`
- `Cascade_Flashing_example.lua:131` : `if (0 == ar1.SOPControl_mult(dev_list[i], 4)) then`
- `Cascade_Flashing_example.lua:164` : `if (0 == ar1.SOPControl_mult(1, 4)) then`
- `Cascade_Flashing_example.lua:204` : `if (0 == ar1.SOPControl_mult(dev_list[i], 4)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:584` : `if (0 == ar1.SOPControl_mult(1, 4)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:630` : `if (0 == ar1.SOPControl_mult(dev_list[i], 4)) then`

## Connect_mult
- `DemoConfig_Cascade.lua:316` : `if (0 == ar1.Connect_mult(1,com_list[1],921600,1000)) then`
- `DemoConfig_Cascade.lua:353` : `if (0 == ar1.Connect_mult(1,com_list[i],921600,1000)) then`

## Disconnect
- `DemoConfig_Cascade.lua:323` : `if (0 == ar1.Disconnect()) then`
- `DemoConfig_Cascade.lua:507` : `if (0 == ar1.Disconnect()) then`

## DownloadBSSFw_mult
- `DemoConfig_Cascade.lua:363` : `if (0 == ar1.DownloadBSSFw_mult(dev_list[i],BSS_firmware)) then`
- `Cascade_Flashing_example.lua:81` : `if (0 == ar1.DownloadBSSFw_mult(1, metaImagePath)) then`
- `Cascade_Flashing_example.lua:152` : `if (0 == ar1.DownloadBSSFw_mult(deviceMapSlaves, metaImagePath)) then`

## DownloadMSSFw_mult
- `DemoConfig_Cascade.lua:373` : `if (0 == ar1.DownloadMSSFw_mult(dev_list[i],MSS_firmware)) then`

## PowerOn_mult
- `DemoConfig_Cascade.lua:385` : `status	=	ar1.PowerOn_mult(dev_list[i],0, 1000, 0, 0)`
- `Cascade_Configuration_Basic.lua:92` : `status    =    ar1.PowerOn_mult(dev_list[i], 0, 1000, 0, 0)`
- `Cascade_Configuration_ContStream.lua:80` : `if (0 == ar1.PowerOn_mult(1, 0, 1000, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:548` : `if (0 == ar1.PowerOn_mult(1, 0, 1000, 0, 0)) then`
- `Cascade_Configuration_TestSource.lua:124` : `if (0 == ar1.PowerOn_mult(1, 0, 1000, 0, 0)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:356` : `if (0 == ar1.PowerOn_mult(1, 0, 1000, 0, 0)) then`
- `Cascade_Configuration_TXBF_Simple.lua:386` : `if (0 == ar1.PowerOn_mult(1, 0, 1000, 0, 0)) then`
- `Cascade_Flashing_example.lua:71` : `if (0 == ar1.PowerOn_mult(1, 0, 1000, 0, 0)) then`
- `Cascade_Flashing_example.lua:99` : `if (0 == ar1.PowerOn_mult(1, 0, 1000, 0, 0)) then`
- `Cascade_Flashing_example.lua:172` : `if (0 == ar1.PowerOn_mult(1, 0, 1000, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:592` : `if (0 == ar1.PowerOn_mult(1, 0, 1000, 0, 0)) then`

## AddDevice
- `DemoConfig_Cascade.lua:387` : `status	=	ar1.AddDevice(dev_list[i])`
- `Cascade_Configuration_Basic.lua:94` : `status    =    ar1.AddDevice(dev_list[i])`
- `Cascade_Configuration_ContStream.lua:126` : `if (0 == ar1.AddDevice(dev_list[i])) then`
- `Cascade_Configuration_MIMO.lua:594` : `if (0 == ar1.AddDevice(dev_list[i])) then`
- `Cascade_Configuration_TestSource.lua:170` : `if (0 == ar1.AddDevice(dev_list[i])) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:403` : `if (0 == ar1.AddDevice(dev_list[i])) then`
- `Cascade_Configuration_TXBF_Simple.lua:433` : `if (0 == ar1.AddDevice(dev_list[i])) then`
- `Cascade_Flashing_example.lua:139` : `if (0 == ar1.AddDevice(dev_list[i])) then`
- `Cascade_Flashing_example.lua:212` : `if (0 == ar1.AddDevice(dev_list[i])) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:638` : `if (0 == ar1.AddDevice(dev_list[i])) then`

## RfEnable_mult
- `DemoConfig_Cascade.lua:399` : `if (0 == ar1.RfEnable_mult(dev_list[i])) then`
- `Cascade_Configuration_Basic.lua:113` : `if (0 == ar1.RfEnable_mult(dev_list[i])) then`
- `Cascade_Configuration_ContStream.lua:96` : `if (0 == ar1.RfEnable_mult(1)) then`
- `Cascade_Configuration_ContStream.lua:145` : `if (0 == ar1.RfEnable_mult(deviceMapSlaves)) then`
- `Cascade_Configuration_MIMO.lua:564` : `if (0 == ar1.RfEnable_mult(1)) then`
- `Cascade_Configuration_MIMO.lua:613` : `if (0 == ar1.RfEnable_mult(deviceMapSlaves)) then`
- `Cascade_Configuration_TestSource.lua:140` : `if (0 == ar1.RfEnable_mult(1)) then`
- `Cascade_Configuration_TestSource.lua:189` : `if (0 == ar1.RfEnable_mult(deviceMapSlaves)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:373` : `if (0 == ar1.RfEnable_mult(1)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:422` : `if (0 == ar1.RfEnable_mult(deviceMapSlaves)) then`
- `Cascade_Configuration_TXBF_Simple.lua:403` : `if (0 == ar1.RfEnable_mult(1)) then`
- `Cascade_Configuration_TXBF_Simple.lua:452` : `if (0 == ar1.RfEnable_mult(deviceMapSlaves)) then`
- `Cascade_Flashing_example.lua:109` : `if (0 == ar1.RfEnable_mult(1)) then`
- `Cascade_Flashing_example.lua:182` : `if (0 == ar1.RfEnable_mult(1)) then`
- `Cascade_Flashing_example.lua:225` : `if (0 == ar1.RfEnable_mult(deviceMapSlaves)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:608` : `if (0 == ar1.RfEnable_mult(1)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:657` : `if (0 == ar1.RfEnable_mult(deviceMapSlaves)) then`

## ChanNAdcConfig_mult
- `DemoConfig_Cascade.lua:409` : `if (0 == ar1.ChanNAdcConfig_mult(dev_list[i],Tx1[i],Tx2[i],Tx3[i],Rx1,Rx2,Rx3,Rx4,nbits,data_format,IQ_swap,cascade_mode_list[i])) then`
- `Cascade_Configuration_Basic.lua:123` : `if (0 == ar1.ChanNAdcConfig_mult(dev_list[i], 1, 1, 1, 1, 1, 1, 1, 2, 1, 0, cascade_mode_list[i])) then`
- `Cascade_Configuration_ContStream.lua:104` : `if (0 == ar1.ChanNAdcConfig_mult(1,1,1,1,1,1,1,1,2,1,0,1)) then`
- `Cascade_Configuration_ContStream.lua:153` : `if (0 == ar1.ChanNAdcConfig_mult(deviceMapSlaves,1,1,1,1,1,1,1,2,1,0,2)) then`
- `Cascade_Configuration_MIMO.lua:572` : `if (0 == ar1.ChanNAdcConfig_mult(1,1,1,1,1,1,1,1,2,1,0,1)) then`
- `Cascade_Configuration_MIMO.lua:621` : `if (0 == ar1.ChanNAdcConfig_mult(deviceMapSlaves,1,1,1,1,1,1,1,2,1,0,2)) then`
- `Cascade_Configuration_TestSource.lua:148` : `if (0 == ar1.ChanNAdcConfig_mult(1,1,1,1,1,1,1,1,2,1,0,1)) then`
- `Cascade_Configuration_TestSource.lua:197` : `if (0 == ar1.ChanNAdcConfig_mult(deviceMapSlaves,1,1,1,1,1,1,1,2,1,0,2)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:381` : `if (0 == ar1.ChanNAdcConfig_mult(1,1,1,1,1,1,1,1,2,1,0,1)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:430` : `if (0 == ar1.ChanNAdcConfig_mult(deviceMapSlaves,1,1,1,1,1,1,1,2,1,0,2)) then`
- `Cascade_Configuration_TXBF_Simple.lua:411` : `if (0 == ar1.ChanNAdcConfig_mult(1,1,1,1,1,1,1,1,2,1,0,1)) then`
- `Cascade_Configuration_TXBF_Simple.lua:460` : `if (0 == ar1.ChanNAdcConfig_mult(deviceMapSlaves,1,1,1,1,1,1,1,2,1,0,2)) then`
- `Cascade_Flashing_example.lua:117` : `if (0 == ar1.ChanNAdcConfig_mult(1,1,1,1,1,1,1,1,2,1,0,1)) then`
- `Cascade_Flashing_example.lua:190` : `if (0 == ar1.ChanNAdcConfig_mult(1,1,1,1,1,1,1,1,2,1,0,1)) then`
- `Cascade_Flashing_example.lua:233` : `if (0 == ar1.ChanNAdcConfig_mult(deviceMapSlaves,1,1,1,1,1,1,1,2,1,0,2)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:616` : `if (0 == ar1.ChanNAdcConfig_mult(1,1,1,1,1,1,1,1,2,1,0,1)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:665` : `if (0 == ar1.ChanNAdcConfig_mult(deviceMapSlaves,1,1,1,1,1,1,1,2,1,0,2)) then`

## RfLdoBypassConfig_mult
- `DemoConfig_Cascade.lua:418` : `if (0 == ar1.RfLdoBypassConfig_mult(dev_list[i], LDO_en)) then`
- `Cascade_Configuration_Basic.lua:132` : `if (0 == ar1.RfLdoBypassConfig_mult(dev_list[i], 3)) then`
- `Cascade_Configuration_ContStream.lua:164` : `if (0 == ar1.RfLdoBypassConfig_mult(deviceMapOverall, 3)) then`
- `Cascade_Configuration_MIMO.lua:632` : `if (0 == ar1.RfLdoBypassConfig_mult(deviceMapOverall, 3)) then`
- `Cascade_Configuration_TestSource.lua:208` : `if (0 == ar1.RfLdoBypassConfig_mult(deviceMapOverall, 3)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:441` : `if (0 == ar1.RfLdoBypassConfig_mult(deviceMapOverall, 3)) then`
- `Cascade_Configuration_TXBF_Simple.lua:471` : `if (0 == ar1.RfLdoBypassConfig_mult(deviceMapOverall, 3)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:676` : `if (0 == ar1.RfLdoBypassConfig_mult(deviceMapOverall, 3)) then`

## LPModConfig_mult
- `DemoConfig_Cascade.lua:427` : `if (0 == ar1.LPModConfig_mult(dev_list[i],0, ADC_Mode)) then`
- `Cascade_Configuration_Basic.lua:140` : `if (0 == ar1.LPModConfig_mult(dev_list[i],0, 0)) then`
- `Cascade_Configuration_ContStream.lua:172` : `if (0 == ar1.LPModConfig_mult(deviceMapOverall,0, 0)) then`
- `Cascade_Configuration_MIMO.lua:640` : `if (0 == ar1.LPModConfig_mult(deviceMapOverall,0, 0)) then`
- `Cascade_Configuration_TestSource.lua:216` : `if (0 == ar1.LPModConfig_mult(deviceMapOverall,0, 0)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:449` : `if (0 == ar1.LPModConfig_mult(deviceMapOverall,0, 0)) then`
- `Cascade_Configuration_TXBF_Simple.lua:479` : `if (0 == ar1.LPModConfig_mult(deviceMapOverall,0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:684` : `if (0 == ar1.LPModConfig_mult(deviceMapOverall,0, 0)) then`

## RfInit_mult
- `DemoConfig_Cascade.lua:436` : `if (0 == ar1.RfInit_mult(dev_list[i])) then`
- `Cascade_Configuration_Basic.lua:165` : `if (0 == ar1.RfInit_mult(dev_list[i])) then`
- `Cascade_Configuration_ContStream.lua:197` : `if (0 == ar1.RfInit_mult(deviceMapOverall)) then`
- `Cascade_Configuration_MIMO.lua:665` : `if (0 == ar1.RfInit_mult(deviceMapOverall)) then`
- `Cascade_Configuration_TestSource.lua:241` : `if (0 == ar1.RfInit_mult(deviceMapOverall)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:474` : `if (0 == ar1.RfInit_mult(deviceMapOverall)) then`
- `Cascade_Configuration_TXBF_Simple.lua:504` : `if (0 == ar1.RfInit_mult(deviceMapOverall)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:709` : `if (0 == ar1.RfInit_mult(deviceMapOverall)) then`

## DataPathConfig_mult
- `DemoConfig_Cascade.lua:447` : `if (0 == ar1.DataPathConfig_mult(dev_list[i],1,1,0)) then`
- `Cascade_Configuration_Basic.lua:194` : `if (0 == ar1.DataPathConfig_mult(dev_list[i], 0, 1, 0)) then`
- `Cascade_Configuration_ContStream.lua:207` : `if (0 == ar1.DataPathConfig_mult(deviceMapOverall, 0, 1, 0)) then`
- `Cascade_Configuration_MIMO.lua:675` : `if (0 == ar1.DataPathConfig_mult(deviceMapOverall, 0, 1, 0)) then`
- `Cascade_Configuration_TestSource.lua:251` : `if (0 == ar1.DataPathConfig_mult(deviceMapOverall, 0, 1, 0)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:484` : `if (0 == ar1.DataPathConfig_mult(deviceMapOverall, 0, 1, 0)) then`
- `Cascade_Configuration_TXBF_Simple.lua:514` : `if (0 == ar1.DataPathConfig_mult(deviceMapOverall, 0, 1, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:719` : `if (0 == ar1.DataPathConfig_mult(deviceMapOverall, 0, 1, 0)) then`

## LvdsClkConfig_mult
- `DemoConfig_Cascade.lua:456` : `if (0 == ar1.LvdsClkConfig_mult(dev_list[i],1,lvds_data_rate)) then`
- `Cascade_Configuration_Basic.lua:202` : `if (0 == ar1.LvdsClkConfig_mult(dev_list[i], 1, 1)) then`
- `Cascade_Configuration_ContStream.lua:215` : `if (0 == ar1.LvdsClkConfig_mult(deviceMapOverall, 1, 1)) then`
- `Cascade_Configuration_MIMO.lua:683` : `if (0 == ar1.LvdsClkConfig_mult(deviceMapOverall, 1, 1)) then`
- `Cascade_Configuration_TestSource.lua:259` : `if (0 == ar1.LvdsClkConfig_mult(deviceMapOverall, 1, 1)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:492` : `if (0 == ar1.LvdsClkConfig_mult(deviceMapOverall, 1, 1)) then`
- `Cascade_Configuration_TXBF_Simple.lua:522` : `if (0 == ar1.LvdsClkConfig_mult(deviceMapOverall, 1, 1)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:727` : `if (0 == ar1.LvdsClkConfig_mult(deviceMapOverall, 1, 1)) then`

## LVDSLaneConfig_mult
- `DemoConfig_Cascade.lua:465` : `if (0 == ar1.LVDSLaneConfig_mult(dev_list[i],0, lane1, lane2, lane3, lane4, MSB_on, 0, 0)) then`

## ProfileConfig_mult
- `DemoConfig_Cascade.lua:477` : `if (0 == ar1.ProfileConfig_mult(dev_list[i],0, start_freq, idle_time, adc_start_time, ramp_end_time, 0, 0, 0, 0, 0, 0, slope, 0, adc_samples, sample_freq, 0, 0, rx_gain)) then`
- `Cascade_Configuration_MIMO.lua:753` : `if (0 == ar1.ProfileConfig_mult(deviceMapOverall, 0, start_freq, idle_time, adc_start_time, ramp_end_time,`
- `Cascade_Configuration_TestSource.lua:329` : `if (0 == ar1.ProfileConfig_mult(deviceMapOverall, 0, start_freq, idle_time, adc_start_time, ramp_end_time,`
- `Cascade_Configuration_TXBF.lua:2` : `ar1.ProfileConfig_mult(1, 0, 77, 5, 6, 40, 0, 0, 0, 0, 0, 0, 78.986, 0, 256, 8000, 2, 1, 40)`
- `Cascade_Configuration_TXBF.lua:247` : `ar1.ProfileConfig_mult(2, 0, 77, 5, 6, 40, 0, 0, 0, 0, 0, 0, 78.986, 0, 256, 8000, 2, 1, 40)`
- `Cascade_Configuration_TXBF.lua:492` : `ar1.ProfileConfig_mult(4, 0, 77, 5, 6, 40, 0, 0, 0, 0, 0, 0, 78.986, 0, 256, 8000, 2, 1, 40)`
- `Cascade_Configuration_TXBF.lua:737` : `ar1.ProfileConfig_mult(8, 0, 77, 5, 6, 40, 0, 0, 0, 0, 0, 0, 78.986, 0, 256, 8000, 2, 1, 40)`
- `Cascade_Configuration_TXBF_AngleSweep.lua:575` : `if (0 == ar1.ProfileConfig_mult(dev_list[devIdx], 0, start_freq, idle_time, adc_start_time, ramp_end_time, 0, 0, 0, psSettings[devIdx][1], psSettings[devIdx][2], psSettings[devIdx][3], slope, 0, adc_samples, sample_freq, 0, 0, rx_gain)) then`
- `Cascade_Configuration_TXBF_Simple.lua:547` : `if (0 == ar1.ProfileConfig_mult(dev_list[devIdx], 0, start_freq, idle_time, adc_start_time, ramp_end_time, 0, 0, 0, psSettings[devIdx][1], psSettings[devIdx][2], psSettings[devIdx][3], slope, 0, adc_samples, sample_freq, 0, 0, rx_gain)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:848` : `if (0 == ar1.ProfileConfig_mult(deviceMapOverall, 0, start_freq, idle_time, adc_start_time, ramp_end_time, 0, 0, 0, phaseShiftValue*phaseShifterStepinDeg, phaseShiftValue*phaseShifterStepinDeg, phaseShiftValue*phaseShifterStepinDeg, slope, 0, adc_samples, sample_freq, 0, 0, rx_gain)) then`

## ChirpConfig_mult
- `DemoConfig_Cascade.lua:486` : `if (0 == ar1.ChirpConfig_mult(dev_list[i],0, 0, 0, 0, 0, 0, 0,Tx1_Enable[i],Tx2_Enable[i],Tx3_Enable[i])) then`
- `Cascade_Configuration_MIMO.lua:122` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:130` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 1, 1, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:138` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 2, 2, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:146` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 3, 3, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:154` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 4, 4, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:162` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 5, 5, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:170` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 6, 6, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:178` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 7, 7, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:186` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 8, 8, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:194` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 9, 9, 0, 0, 0, 0, 0, 0, 0, 1)) then`
- `Cascade_Configuration_MIMO.lua:202` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 10, 10, 0, 0, 0, 0, 0, 0, 1, 0)) then`
- `Cascade_Configuration_MIMO.lua:210` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 11, 11, 0, 0, 0, 0, 0, 1, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:220` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:228` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 1, 1, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:236` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 2, 2, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:244` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 3, 3, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:252` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 4, 4, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:260` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 5, 5, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:268` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 6, 6, 0, 0, 0, 0, 0, 0, 0, 1)) then`
- `Cascade_Configuration_MIMO.lua:276` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 7, 7, 0, 0, 0, 0, 0, 0, 1, 0)) then`
- `Cascade_Configuration_MIMO.lua:284` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 8, 8, 0, 0, 0, 0, 0, 1, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:292` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 9, 9, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:300` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 10, 10, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:308` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 11, 11, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:318` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:326` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 1, 1, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:334` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 2, 2, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:342` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 3, 3, 0, 0, 0, 0, 0, 0, 0, 1)) then`
- `Cascade_Configuration_MIMO.lua:350` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 4, 4, 0, 0, 0, 0, 0, 0, 1, 0)) then`
- `Cascade_Configuration_MIMO.lua:358` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 5, 5, 0, 0, 0, 0, 0, 1, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:366` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 6, 6, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:374` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 7, 7, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:382` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 8, 8, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:390` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 9, 9, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:398` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 10, 10, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:406` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 11, 11, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:416` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)) then`
- `Cascade_Configuration_MIMO.lua:424` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 1, 1, 0, 0, 0, 0, 0, 0, 1, 0)) then`
- `Cascade_Configuration_MIMO.lua:432` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 2, 2, 0, 0, 0, 0, 0, 1, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:440` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 3, 3, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:448` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 4, 4, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:456` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 5, 5, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:464` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 6, 6, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:472` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 7, 7, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:480` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 8, 8, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:488` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 9, 9, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:496` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 10, 10, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:504` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 11, 11, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_TestSource.lua:339` : `if (0 == ar1.ChirpConfig_mult(deviceMapOverall, start_chirp_tx, end_chirp_tx, 0, 0, 0, 0, 0, 1, 1, 0)) then`
- `Cascade_Configuration_TXBF.lua:3` : `ar1.ChirpConfig_mult(1, 0, 0, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:5` : `ar1.ChirpConfig_mult(1, 1, 1, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:7` : `ar1.ChirpConfig_mult(1, 2, 2, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:9` : `ar1.ChirpConfig_mult(1, 3, 3, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:11` : `ar1.ChirpConfig_mult(1, 4, 4, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:13` : `ar1.ChirpConfig_mult(1, 5, 5, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:15` : `ar1.ChirpConfig_mult(1, 6, 6, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:17` : `ar1.ChirpConfig_mult(1, 7, 7, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:19` : `ar1.ChirpConfig_mult(1, 8, 8, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:21` : `ar1.ChirpConfig_mult(1, 9, 9, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:23` : `ar1.ChirpConfig_mult(1, 10, 10, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:25` : `ar1.ChirpConfig_mult(1, 11, 11, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:27` : `ar1.ChirpConfig_mult(1, 12, 12, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:29` : `ar1.ChirpConfig_mult(1, 13, 13, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:31` : `ar1.ChirpConfig_mult(1, 14, 14, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:33` : `ar1.ChirpConfig_mult(1, 15, 15, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:35` : `ar1.ChirpConfig_mult(1, 16, 16, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:37` : `ar1.ChirpConfig_mult(1, 17, 17, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:39` : `ar1.ChirpConfig_mult(1, 18, 18, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:41` : `ar1.ChirpConfig_mult(1, 19, 19, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:43` : `ar1.ChirpConfig_mult(1, 20, 20, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:45` : `ar1.ChirpConfig_mult(1, 21, 21, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:47` : `ar1.ChirpConfig_mult(1, 22, 22, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:49` : `ar1.ChirpConfig_mult(1, 23, 23, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:51` : `ar1.ChirpConfig_mult(1, 24, 24, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:53` : `ar1.ChirpConfig_mult(1, 25, 25, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:55` : `ar1.ChirpConfig_mult(1, 26, 26, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:57` : `ar1.ChirpConfig_mult(1, 27, 27, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:59` : `ar1.ChirpConfig_mult(1, 28, 28, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:61` : `ar1.ChirpConfig_mult(1, 29, 29, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:63` : `ar1.ChirpConfig_mult(1, 30, 30, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:65` : `ar1.ChirpConfig_mult(1, 31, 31, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:67` : `ar1.ChirpConfig_mult(1, 32, 32, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:69` : `ar1.ChirpConfig_mult(1, 33, 33, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:71` : `ar1.ChirpConfig_mult(1, 34, 34, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:73` : `ar1.ChirpConfig_mult(1, 35, 35, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:75` : `ar1.ChirpConfig_mult(1, 36, 36, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:77` : `ar1.ChirpConfig_mult(1, 37, 37, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:79` : `ar1.ChirpConfig_mult(1, 38, 38, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:81` : `ar1.ChirpConfig_mult(1, 39, 39, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:83` : `ar1.ChirpConfig_mult(1, 40, 40, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:85` : `ar1.ChirpConfig_mult(1, 41, 41, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:87` : `ar1.ChirpConfig_mult(1, 42, 42, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:89` : `ar1.ChirpConfig_mult(1, 43, 43, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:91` : `ar1.ChirpConfig_mult(1, 44, 44, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:93` : `ar1.ChirpConfig_mult(1, 45, 45, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:95` : `ar1.ChirpConfig_mult(1, 46, 46, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:97` : `ar1.ChirpConfig_mult(1, 47, 47, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:99` : `ar1.ChirpConfig_mult(1, 48, 48, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:101` : `ar1.ChirpConfig_mult(1, 49, 49, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:103` : `ar1.ChirpConfig_mult(1, 50, 50, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:105` : `ar1.ChirpConfig_mult(1, 51, 51, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:107` : `ar1.ChirpConfig_mult(1, 52, 52, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:109` : `ar1.ChirpConfig_mult(1, 53, 53, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:111` : `ar1.ChirpConfig_mult(1, 54, 54, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:113` : `ar1.ChirpConfig_mult(1, 55, 55, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:115` : `ar1.ChirpConfig_mult(1, 56, 56, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:117` : `ar1.ChirpConfig_mult(1, 57, 57, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:119` : `ar1.ChirpConfig_mult(1, 58, 58, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:121` : `ar1.ChirpConfig_mult(1, 59, 59, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:123` : `ar1.ChirpConfig_mult(1, 60, 60, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:125` : `ar1.ChirpConfig_mult(1, 61, 61, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:127` : `ar1.ChirpConfig_mult(1, 62, 62, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:129` : `ar1.ChirpConfig_mult(1, 63, 63, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:131` : `ar1.ChirpConfig_mult(1, 64, 64, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:133` : `ar1.ChirpConfig_mult(1, 65, 65, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:135` : `ar1.ChirpConfig_mult(1, 66, 66, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:137` : `ar1.ChirpConfig_mult(1, 67, 67, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:139` : `ar1.ChirpConfig_mult(1, 68, 68, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:141` : `ar1.ChirpConfig_mult(1, 69, 69, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:143` : `ar1.ChirpConfig_mult(1, 70, 70, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:145` : `ar1.ChirpConfig_mult(1, 71, 71, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:147` : `ar1.ChirpConfig_mult(1, 72, 72, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:149` : `ar1.ChirpConfig_mult(1, 73, 73, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:151` : `ar1.ChirpConfig_mult(1, 74, 74, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:153` : `ar1.ChirpConfig_mult(1, 75, 75, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:155` : `ar1.ChirpConfig_mult(1, 76, 76, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:157` : `ar1.ChirpConfig_mult(1, 77, 77, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:159` : `ar1.ChirpConfig_mult(1, 78, 78, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:161` : `ar1.ChirpConfig_mult(1, 79, 79, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:163` : `ar1.ChirpConfig_mult(1, 80, 80, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:165` : `ar1.ChirpConfig_mult(1, 81, 81, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:167` : `ar1.ChirpConfig_mult(1, 82, 82, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:169` : `ar1.ChirpConfig_mult(1, 83, 83, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:171` : `ar1.ChirpConfig_mult(1, 84, 84, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:173` : `ar1.ChirpConfig_mult(1, 85, 85, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:175` : `ar1.ChirpConfig_mult(1, 86, 86, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:177` : `ar1.ChirpConfig_mult(1, 87, 87, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:179` : `ar1.ChirpConfig_mult(1, 88, 88, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:181` : `ar1.ChirpConfig_mult(1, 89, 89, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:183` : `ar1.ChirpConfig_mult(1, 90, 90, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:185` : `ar1.ChirpConfig_mult(1, 91, 91, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:187` : `ar1.ChirpConfig_mult(1, 92, 92, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:189` : `ar1.ChirpConfig_mult(1, 93, 93, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:191` : `ar1.ChirpConfig_mult(1, 94, 94, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:193` : `ar1.ChirpConfig_mult(1, 95, 95, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:195` : `ar1.ChirpConfig_mult(1, 96, 96, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:197` : `ar1.ChirpConfig_mult(1, 97, 97, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:199` : `ar1.ChirpConfig_mult(1, 98, 98, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:201` : `ar1.ChirpConfig_mult(1, 99, 99, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:203` : `ar1.ChirpConfig_mult(1, 100, 100, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:205` : `ar1.ChirpConfig_mult(1, 101, 101, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:207` : `ar1.ChirpConfig_mult(1, 102, 102, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:209` : `ar1.ChirpConfig_mult(1, 103, 103, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:211` : `ar1.ChirpConfig_mult(1, 104, 104, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:213` : `ar1.ChirpConfig_mult(1, 105, 105, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:215` : `ar1.ChirpConfig_mult(1, 106, 106, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:217` : `ar1.ChirpConfig_mult(1, 107, 107, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:219` : `ar1.ChirpConfig_mult(1, 108, 108, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:221` : `ar1.ChirpConfig_mult(1, 109, 109, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:223` : `ar1.ChirpConfig_mult(1, 110, 110, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:225` : `ar1.ChirpConfig_mult(1, 111, 111, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:227` : `ar1.ChirpConfig_mult(1, 112, 112, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:229` : `ar1.ChirpConfig_mult(1, 113, 113, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:231` : `ar1.ChirpConfig_mult(1, 114, 114, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:233` : `ar1.ChirpConfig_mult(1, 115, 115, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:235` : `ar1.ChirpConfig_mult(1, 116, 116, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:237` : `ar1.ChirpConfig_mult(1, 117, 117, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:239` : `ar1.ChirpConfig_mult(1, 118, 118, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:241` : `ar1.ChirpConfig_mult(1, 119, 119, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:243` : `ar1.ChirpConfig_mult(1, 120, 120, 0, 0, 0, 0, 0, 0, 0,0)`
- `Cascade_Configuration_TXBF.lua:248` : `ar1.ChirpConfig_mult(2, 0, 0, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:250` : `ar1.ChirpConfig_mult(2, 1, 1, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:252` : `ar1.ChirpConfig_mult(2, 2, 2, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:254` : `ar1.ChirpConfig_mult(2, 3, 3, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:256` : `ar1.ChirpConfig_mult(2, 4, 4, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:258` : `ar1.ChirpConfig_mult(2, 5, 5, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:260` : `ar1.ChirpConfig_mult(2, 6, 6, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:262` : `ar1.ChirpConfig_mult(2, 7, 7, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:264` : `ar1.ChirpConfig_mult(2, 8, 8, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:266` : `ar1.ChirpConfig_mult(2, 9, 9, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:268` : `ar1.ChirpConfig_mult(2, 10, 10, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:270` : `ar1.ChirpConfig_mult(2, 11, 11, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:272` : `ar1.ChirpConfig_mult(2, 12, 12, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:274` : `ar1.ChirpConfig_mult(2, 13, 13, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:276` : `ar1.ChirpConfig_mult(2, 14, 14, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:278` : `ar1.ChirpConfig_mult(2, 15, 15, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:280` : `ar1.ChirpConfig_mult(2, 16, 16, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:282` : `ar1.ChirpConfig_mult(2, 17, 17, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:284` : `ar1.ChirpConfig_mult(2, 18, 18, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:286` : `ar1.ChirpConfig_mult(2, 19, 19, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:288` : `ar1.ChirpConfig_mult(2, 20, 20, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:290` : `ar1.ChirpConfig_mult(2, 21, 21, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:292` : `ar1.ChirpConfig_mult(2, 22, 22, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:294` : `ar1.ChirpConfig_mult(2, 23, 23, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:296` : `ar1.ChirpConfig_mult(2, 24, 24, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:298` : `ar1.ChirpConfig_mult(2, 25, 25, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:300` : `ar1.ChirpConfig_mult(2, 26, 26, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:302` : `ar1.ChirpConfig_mult(2, 27, 27, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:304` : `ar1.ChirpConfig_mult(2, 28, 28, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:306` : `ar1.ChirpConfig_mult(2, 29, 29, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:308` : `ar1.ChirpConfig_mult(2, 30, 30, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:310` : `ar1.ChirpConfig_mult(2, 31, 31, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:312` : `ar1.ChirpConfig_mult(2, 32, 32, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:314` : `ar1.ChirpConfig_mult(2, 33, 33, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:316` : `ar1.ChirpConfig_mult(2, 34, 34, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:318` : `ar1.ChirpConfig_mult(2, 35, 35, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:320` : `ar1.ChirpConfig_mult(2, 36, 36, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:322` : `ar1.ChirpConfig_mult(2, 37, 37, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:324` : `ar1.ChirpConfig_mult(2, 38, 38, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:326` : `ar1.ChirpConfig_mult(2, 39, 39, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:328` : `ar1.ChirpConfig_mult(2, 40, 40, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:330` : `ar1.ChirpConfig_mult(2, 41, 41, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:332` : `ar1.ChirpConfig_mult(2, 42, 42, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:334` : `ar1.ChirpConfig_mult(2, 43, 43, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:336` : `ar1.ChirpConfig_mult(2, 44, 44, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:338` : `ar1.ChirpConfig_mult(2, 45, 45, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:340` : `ar1.ChirpConfig_mult(2, 46, 46, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:342` : `ar1.ChirpConfig_mult(2, 47, 47, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:344` : `ar1.ChirpConfig_mult(2, 48, 48, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:346` : `ar1.ChirpConfig_mult(2, 49, 49, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:348` : `ar1.ChirpConfig_mult(2, 50, 50, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:350` : `ar1.ChirpConfig_mult(2, 51, 51, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:352` : `ar1.ChirpConfig_mult(2, 52, 52, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:354` : `ar1.ChirpConfig_mult(2, 53, 53, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:356` : `ar1.ChirpConfig_mult(2, 54, 54, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:358` : `ar1.ChirpConfig_mult(2, 55, 55, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:360` : `ar1.ChirpConfig_mult(2, 56, 56, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:362` : `ar1.ChirpConfig_mult(2, 57, 57, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:364` : `ar1.ChirpConfig_mult(2, 58, 58, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:366` : `ar1.ChirpConfig_mult(2, 59, 59, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:368` : `ar1.ChirpConfig_mult(2, 60, 60, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:370` : `ar1.ChirpConfig_mult(2, 61, 61, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:372` : `ar1.ChirpConfig_mult(2, 62, 62, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:374` : `ar1.ChirpConfig_mult(2, 63, 63, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:376` : `ar1.ChirpConfig_mult(2, 64, 64, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:378` : `ar1.ChirpConfig_mult(2, 65, 65, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:380` : `ar1.ChirpConfig_mult(2, 66, 66, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:382` : `ar1.ChirpConfig_mult(2, 67, 67, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:384` : `ar1.ChirpConfig_mult(2, 68, 68, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:386` : `ar1.ChirpConfig_mult(2, 69, 69, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:388` : `ar1.ChirpConfig_mult(2, 70, 70, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:390` : `ar1.ChirpConfig_mult(2, 71, 71, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:392` : `ar1.ChirpConfig_mult(2, 72, 72, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:394` : `ar1.ChirpConfig_mult(2, 73, 73, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:396` : `ar1.ChirpConfig_mult(2, 74, 74, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:398` : `ar1.ChirpConfig_mult(2, 75, 75, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:400` : `ar1.ChirpConfig_mult(2, 76, 76, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:402` : `ar1.ChirpConfig_mult(2, 77, 77, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:404` : `ar1.ChirpConfig_mult(2, 78, 78, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:406` : `ar1.ChirpConfig_mult(2, 79, 79, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:408` : `ar1.ChirpConfig_mult(2, 80, 80, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:410` : `ar1.ChirpConfig_mult(2, 81, 81, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:412` : `ar1.ChirpConfig_mult(2, 82, 82, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:414` : `ar1.ChirpConfig_mult(2, 83, 83, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:416` : `ar1.ChirpConfig_mult(2, 84, 84, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:418` : `ar1.ChirpConfig_mult(2, 85, 85, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:420` : `ar1.ChirpConfig_mult(2, 86, 86, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:422` : `ar1.ChirpConfig_mult(2, 87, 87, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:424` : `ar1.ChirpConfig_mult(2, 88, 88, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:426` : `ar1.ChirpConfig_mult(2, 89, 89, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:428` : `ar1.ChirpConfig_mult(2, 90, 90, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:430` : `ar1.ChirpConfig_mult(2, 91, 91, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:432` : `ar1.ChirpConfig_mult(2, 92, 92, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:434` : `ar1.ChirpConfig_mult(2, 93, 93, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:436` : `ar1.ChirpConfig_mult(2, 94, 94, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:438` : `ar1.ChirpConfig_mult(2, 95, 95, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:440` : `ar1.ChirpConfig_mult(2, 96, 96, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:442` : `ar1.ChirpConfig_mult(2, 97, 97, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:444` : `ar1.ChirpConfig_mult(2, 98, 98, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:446` : `ar1.ChirpConfig_mult(2, 99, 99, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:448` : `ar1.ChirpConfig_mult(2, 100, 100, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:450` : `ar1.ChirpConfig_mult(2, 101, 101, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:452` : `ar1.ChirpConfig_mult(2, 102, 102, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:454` : `ar1.ChirpConfig_mult(2, 103, 103, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:456` : `ar1.ChirpConfig_mult(2, 104, 104, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:458` : `ar1.ChirpConfig_mult(2, 105, 105, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:460` : `ar1.ChirpConfig_mult(2, 106, 106, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:462` : `ar1.ChirpConfig_mult(2, 107, 107, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:464` : `ar1.ChirpConfig_mult(2, 108, 108, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:466` : `ar1.ChirpConfig_mult(2, 109, 109, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:468` : `ar1.ChirpConfig_mult(2, 110, 110, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:470` : `ar1.ChirpConfig_mult(2, 111, 111, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:472` : `ar1.ChirpConfig_mult(2, 112, 112, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:474` : `ar1.ChirpConfig_mult(2, 113, 113, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:476` : `ar1.ChirpConfig_mult(2, 114, 114, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:478` : `ar1.ChirpConfig_mult(2, 115, 115, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:480` : `ar1.ChirpConfig_mult(2, 116, 116, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:482` : `ar1.ChirpConfig_mult(2, 117, 117, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:484` : `ar1.ChirpConfig_mult(2, 118, 118, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:486` : `ar1.ChirpConfig_mult(2, 119, 119, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:488` : `ar1.ChirpConfig_mult(2, 120, 120, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:493` : `ar1.ChirpConfig_mult(4, 0, 0, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:495` : `ar1.ChirpConfig_mult(4, 1, 1, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:497` : `ar1.ChirpConfig_mult(4, 2, 2, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:499` : `ar1.ChirpConfig_mult(4, 3, 3, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:501` : `ar1.ChirpConfig_mult(4, 4, 4, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:503` : `ar1.ChirpConfig_mult(4, 5, 5, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:505` : `ar1.ChirpConfig_mult(4, 6, 6, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:507` : `ar1.ChirpConfig_mult(4, 7, 7, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:509` : `ar1.ChirpConfig_mult(4, 8, 8, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:511` : `ar1.ChirpConfig_mult(4, 9, 9, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:513` : `ar1.ChirpConfig_mult(4, 10, 10, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:515` : `ar1.ChirpConfig_mult(4, 11, 11, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:517` : `ar1.ChirpConfig_mult(4, 12, 12, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:519` : `ar1.ChirpConfig_mult(4, 13, 13, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:521` : `ar1.ChirpConfig_mult(4, 14, 14, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:523` : `ar1.ChirpConfig_mult(4, 15, 15, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:525` : `ar1.ChirpConfig_mult(4, 16, 16, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:527` : `ar1.ChirpConfig_mult(4, 17, 17, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:529` : `ar1.ChirpConfig_mult(4, 18, 18, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:531` : `ar1.ChirpConfig_mult(4, 19, 19, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:533` : `ar1.ChirpConfig_mult(4, 20, 20, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:535` : `ar1.ChirpConfig_mult(4, 21, 21, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:537` : `ar1.ChirpConfig_mult(4, 22, 22, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:539` : `ar1.ChirpConfig_mult(4, 23, 23, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:541` : `ar1.ChirpConfig_mult(4, 24, 24, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:543` : `ar1.ChirpConfig_mult(4, 25, 25, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:545` : `ar1.ChirpConfig_mult(4, 26, 26, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:547` : `ar1.ChirpConfig_mult(4, 27, 27, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:549` : `ar1.ChirpConfig_mult(4, 28, 28, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:551` : `ar1.ChirpConfig_mult(4, 29, 29, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:553` : `ar1.ChirpConfig_mult(4, 30, 30, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:555` : `ar1.ChirpConfig_mult(4, 31, 31, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:557` : `ar1.ChirpConfig_mult(4, 32, 32, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:559` : `ar1.ChirpConfig_mult(4, 33, 33, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:561` : `ar1.ChirpConfig_mult(4, 34, 34, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:563` : `ar1.ChirpConfig_mult(4, 35, 35, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:565` : `ar1.ChirpConfig_mult(4, 36, 36, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:567` : `ar1.ChirpConfig_mult(4, 37, 37, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:569` : `ar1.ChirpConfig_mult(4, 38, 38, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:571` : `ar1.ChirpConfig_mult(4, 39, 39, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:573` : `ar1.ChirpConfig_mult(4, 40, 40, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:575` : `ar1.ChirpConfig_mult(4, 41, 41, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:577` : `ar1.ChirpConfig_mult(4, 42, 42, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:579` : `ar1.ChirpConfig_mult(4, 43, 43, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:581` : `ar1.ChirpConfig_mult(4, 44, 44, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:583` : `ar1.ChirpConfig_mult(4, 45, 45, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:585` : `ar1.ChirpConfig_mult(4, 46, 46, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:587` : `ar1.ChirpConfig_mult(4, 47, 47, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:589` : `ar1.ChirpConfig_mult(4, 48, 48, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:591` : `ar1.ChirpConfig_mult(4, 49, 49, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:593` : `ar1.ChirpConfig_mult(4, 50, 50, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:595` : `ar1.ChirpConfig_mult(4, 51, 51, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:597` : `ar1.ChirpConfig_mult(4, 52, 52, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:599` : `ar1.ChirpConfig_mult(4, 53, 53, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:601` : `ar1.ChirpConfig_mult(4, 54, 54, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:603` : `ar1.ChirpConfig_mult(4, 55, 55, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:605` : `ar1.ChirpConfig_mult(4, 56, 56, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:607` : `ar1.ChirpConfig_mult(4, 57, 57, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:609` : `ar1.ChirpConfig_mult(4, 58, 58, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:611` : `ar1.ChirpConfig_mult(4, 59, 59, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:613` : `ar1.ChirpConfig_mult(4, 60, 60, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:615` : `ar1.ChirpConfig_mult(4, 61, 61, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:617` : `ar1.ChirpConfig_mult(4, 62, 62, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:619` : `ar1.ChirpConfig_mult(4, 63, 63, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:621` : `ar1.ChirpConfig_mult(4, 64, 64, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:623` : `ar1.ChirpConfig_mult(4, 65, 65, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:625` : `ar1.ChirpConfig_mult(4, 66, 66, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:627` : `ar1.ChirpConfig_mult(4, 67, 67, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:629` : `ar1.ChirpConfig_mult(4, 68, 68, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:631` : `ar1.ChirpConfig_mult(4, 69, 69, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:633` : `ar1.ChirpConfig_mult(4, 70, 70, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:635` : `ar1.ChirpConfig_mult(4, 71, 71, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:637` : `ar1.ChirpConfig_mult(4, 72, 72, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:639` : `ar1.ChirpConfig_mult(4, 73, 73, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:641` : `ar1.ChirpConfig_mult(4, 74, 74, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:643` : `ar1.ChirpConfig_mult(4, 75, 75, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:645` : `ar1.ChirpConfig_mult(4, 76, 76, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:647` : `ar1.ChirpConfig_mult(4, 77, 77, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:649` : `ar1.ChirpConfig_mult(4, 78, 78, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:651` : `ar1.ChirpConfig_mult(4, 79, 79, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:653` : `ar1.ChirpConfig_mult(4, 80, 80, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:655` : `ar1.ChirpConfig_mult(4, 81, 81, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:657` : `ar1.ChirpConfig_mult(4, 82, 82, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:659` : `ar1.ChirpConfig_mult(4, 83, 83, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:661` : `ar1.ChirpConfig_mult(4, 84, 84, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:663` : `ar1.ChirpConfig_mult(4, 85, 85, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:665` : `ar1.ChirpConfig_mult(4, 86, 86, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:667` : `ar1.ChirpConfig_mult(4, 87, 87, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:669` : `ar1.ChirpConfig_mult(4, 88, 88, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:671` : `ar1.ChirpConfig_mult(4, 89, 89, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:673` : `ar1.ChirpConfig_mult(4, 90, 90, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:675` : `ar1.ChirpConfig_mult(4, 91, 91, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:677` : `ar1.ChirpConfig_mult(4, 92, 92, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:679` : `ar1.ChirpConfig_mult(4, 93, 93, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:681` : `ar1.ChirpConfig_mult(4, 94, 94, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:683` : `ar1.ChirpConfig_mult(4, 95, 95, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:685` : `ar1.ChirpConfig_mult(4, 96, 96, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:687` : `ar1.ChirpConfig_mult(4, 97, 97, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:689` : `ar1.ChirpConfig_mult(4, 98, 98, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:691` : `ar1.ChirpConfig_mult(4, 99, 99, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:693` : `ar1.ChirpConfig_mult(4, 100, 100, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:695` : `ar1.ChirpConfig_mult(4, 101, 101, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:697` : `ar1.ChirpConfig_mult(4, 102, 102, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:699` : `ar1.ChirpConfig_mult(4, 103, 103, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:701` : `ar1.ChirpConfig_mult(4, 104, 104, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:703` : `ar1.ChirpConfig_mult(4, 105, 105, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:705` : `ar1.ChirpConfig_mult(4, 106, 106, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:707` : `ar1.ChirpConfig_mult(4, 107, 107, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:709` : `ar1.ChirpConfig_mult(4, 108, 108, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:711` : `ar1.ChirpConfig_mult(4, 109, 109, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:713` : `ar1.ChirpConfig_mult(4, 110, 110, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:715` : `ar1.ChirpConfig_mult(4, 111, 111, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:717` : `ar1.ChirpConfig_mult(4, 112, 112, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:719` : `ar1.ChirpConfig_mult(4, 113, 113, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:721` : `ar1.ChirpConfig_mult(4, 114, 114, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:723` : `ar1.ChirpConfig_mult(4, 115, 115, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:725` : `ar1.ChirpConfig_mult(4, 116, 116, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:727` : `ar1.ChirpConfig_mult(4, 117, 117, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:729` : `ar1.ChirpConfig_mult(4, 118, 118, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:731` : `ar1.ChirpConfig_mult(4, 119, 119, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:733` : `ar1.ChirpConfig_mult(4, 120, 120, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:738` : `ar1.ChirpConfig_mult(8, 0, 0, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:740` : `ar1.ChirpConfig_mult(8, 1, 1, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:742` : `ar1.ChirpConfig_mult(8, 2, 2, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:744` : `ar1.ChirpConfig_mult(8, 3, 3, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:746` : `ar1.ChirpConfig_mult(8, 4, 4, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:748` : `ar1.ChirpConfig_mult(8, 5, 5, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:750` : `ar1.ChirpConfig_mult(8, 6, 6, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:752` : `ar1.ChirpConfig_mult(8, 7, 7, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:754` : `ar1.ChirpConfig_mult(8, 8, 8, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:756` : `ar1.ChirpConfig_mult(8, 9, 9, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:758` : `ar1.ChirpConfig_mult(8, 10, 10, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:760` : `ar1.ChirpConfig_mult(8, 11, 11, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:762` : `ar1.ChirpConfig_mult(8, 12, 12, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:764` : `ar1.ChirpConfig_mult(8, 13, 13, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:766` : `ar1.ChirpConfig_mult(8, 14, 14, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:768` : `ar1.ChirpConfig_mult(8, 15, 15, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:770` : `ar1.ChirpConfig_mult(8, 16, 16, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:772` : `ar1.ChirpConfig_mult(8, 17, 17, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:774` : `ar1.ChirpConfig_mult(8, 18, 18, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:776` : `ar1.ChirpConfig_mult(8, 19, 19, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:778` : `ar1.ChirpConfig_mult(8, 20, 20, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:780` : `ar1.ChirpConfig_mult(8, 21, 21, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:782` : `ar1.ChirpConfig_mult(8, 22, 22, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:784` : `ar1.ChirpConfig_mult(8, 23, 23, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:786` : `ar1.ChirpConfig_mult(8, 24, 24, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:788` : `ar1.ChirpConfig_mult(8, 25, 25, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:790` : `ar1.ChirpConfig_mult(8, 26, 26, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:792` : `ar1.ChirpConfig_mult(8, 27, 27, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:794` : `ar1.ChirpConfig_mult(8, 28, 28, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:796` : `ar1.ChirpConfig_mult(8, 29, 29, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:798` : `ar1.ChirpConfig_mult(8, 30, 30, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:800` : `ar1.ChirpConfig_mult(8, 31, 31, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:802` : `ar1.ChirpConfig_mult(8, 32, 32, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:804` : `ar1.ChirpConfig_mult(8, 33, 33, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:806` : `ar1.ChirpConfig_mult(8, 34, 34, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:808` : `ar1.ChirpConfig_mult(8, 35, 35, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:810` : `ar1.ChirpConfig_mult(8, 36, 36, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:812` : `ar1.ChirpConfig_mult(8, 37, 37, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:814` : `ar1.ChirpConfig_mult(8, 38, 38, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:816` : `ar1.ChirpConfig_mult(8, 39, 39, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:818` : `ar1.ChirpConfig_mult(8, 40, 40, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:820` : `ar1.ChirpConfig_mult(8, 41, 41, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:822` : `ar1.ChirpConfig_mult(8, 42, 42, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:824` : `ar1.ChirpConfig_mult(8, 43, 43, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:826` : `ar1.ChirpConfig_mult(8, 44, 44, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:828` : `ar1.ChirpConfig_mult(8, 45, 45, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:830` : `ar1.ChirpConfig_mult(8, 46, 46, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:832` : `ar1.ChirpConfig_mult(8, 47, 47, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:834` : `ar1.ChirpConfig_mult(8, 48, 48, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:836` : `ar1.ChirpConfig_mult(8, 49, 49, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:838` : `ar1.ChirpConfig_mult(8, 50, 50, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:840` : `ar1.ChirpConfig_mult(8, 51, 51, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:842` : `ar1.ChirpConfig_mult(8, 52, 52, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:844` : `ar1.ChirpConfig_mult(8, 53, 53, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:846` : `ar1.ChirpConfig_mult(8, 54, 54, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:848` : `ar1.ChirpConfig_mult(8, 55, 55, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:850` : `ar1.ChirpConfig_mult(8, 56, 56, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:852` : `ar1.ChirpConfig_mult(8, 57, 57, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:854` : `ar1.ChirpConfig_mult(8, 58, 58, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:856` : `ar1.ChirpConfig_mult(8, 59, 59, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:858` : `ar1.ChirpConfig_mult(8, 60, 60, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:860` : `ar1.ChirpConfig_mult(8, 61, 61, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:862` : `ar1.ChirpConfig_mult(8, 62, 62, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:864` : `ar1.ChirpConfig_mult(8, 63, 63, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:866` : `ar1.ChirpConfig_mult(8, 64, 64, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:868` : `ar1.ChirpConfig_mult(8, 65, 65, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:870` : `ar1.ChirpConfig_mult(8, 66, 66, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:872` : `ar1.ChirpConfig_mult(8, 67, 67, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:874` : `ar1.ChirpConfig_mult(8, 68, 68, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:876` : `ar1.ChirpConfig_mult(8, 69, 69, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:878` : `ar1.ChirpConfig_mult(8, 70, 70, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:880` : `ar1.ChirpConfig_mult(8, 71, 71, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:882` : `ar1.ChirpConfig_mult(8, 72, 72, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:884` : `ar1.ChirpConfig_mult(8, 73, 73, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:886` : `ar1.ChirpConfig_mult(8, 74, 74, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:888` : `ar1.ChirpConfig_mult(8, 75, 75, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:890` : `ar1.ChirpConfig_mult(8, 76, 76, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:892` : `ar1.ChirpConfig_mult(8, 77, 77, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:894` : `ar1.ChirpConfig_mult(8, 78, 78, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:896` : `ar1.ChirpConfig_mult(8, 79, 79, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:898` : `ar1.ChirpConfig_mult(8, 80, 80, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:900` : `ar1.ChirpConfig_mult(8, 81, 81, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:902` : `ar1.ChirpConfig_mult(8, 82, 82, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:904` : `ar1.ChirpConfig_mult(8, 83, 83, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:906` : `ar1.ChirpConfig_mult(8, 84, 84, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:908` : `ar1.ChirpConfig_mult(8, 85, 85, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:910` : `ar1.ChirpConfig_mult(8, 86, 86, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:912` : `ar1.ChirpConfig_mult(8, 87, 87, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:914` : `ar1.ChirpConfig_mult(8, 88, 88, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:916` : `ar1.ChirpConfig_mult(8, 89, 89, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:918` : `ar1.ChirpConfig_mult(8, 90, 90, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:920` : `ar1.ChirpConfig_mult(8, 91, 91, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:922` : `ar1.ChirpConfig_mult(8, 92, 92, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:924` : `ar1.ChirpConfig_mult(8, 93, 93, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:926` : `ar1.ChirpConfig_mult(8, 94, 94, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:928` : `ar1.ChirpConfig_mult(8, 95, 95, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:930` : `ar1.ChirpConfig_mult(8, 96, 96, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:932` : `ar1.ChirpConfig_mult(8, 97, 97, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:934` : `ar1.ChirpConfig_mult(8, 98, 98, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:936` : `ar1.ChirpConfig_mult(8, 99, 99, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:938` : `ar1.ChirpConfig_mult(8, 100, 100, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:940` : `ar1.ChirpConfig_mult(8, 101, 101, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:942` : `ar1.ChirpConfig_mult(8, 102, 102, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:944` : `ar1.ChirpConfig_mult(8, 103, 103, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:946` : `ar1.ChirpConfig_mult(8, 104, 104, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:948` : `ar1.ChirpConfig_mult(8, 105, 105, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:950` : `ar1.ChirpConfig_mult(8, 106, 106, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:952` : `ar1.ChirpConfig_mult(8, 107, 107, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:954` : `ar1.ChirpConfig_mult(8, 108, 108, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:956` : `ar1.ChirpConfig_mult(8, 109, 109, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:958` : `ar1.ChirpConfig_mult(8, 110, 110, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:960` : `ar1.ChirpConfig_mult(8, 111, 111, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:962` : `ar1.ChirpConfig_mult(8, 112, 112, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:964` : `ar1.ChirpConfig_mult(8, 113, 113, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:966` : `ar1.ChirpConfig_mult(8, 114, 114, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:968` : `ar1.ChirpConfig_mult(8, 115, 115, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:970` : `ar1.ChirpConfig_mult(8, 116, 116, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:972` : `ar1.ChirpConfig_mult(8, 117, 117, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:974` : `ar1.ChirpConfig_mult(8, 118, 118, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:976` : `ar1.ChirpConfig_mult(8, 119, 119, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF.lua:978` : `ar1.ChirpConfig_mult(8, 120, 120, 0, 0, 0, 0, 0, 1, 1,1)`
- `Cascade_Configuration_TXBF_AngleSweep.lua:278` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:289` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 0, 0, 0, 0, 0, 0, 0, 1, 1, 1)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:300` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 0, 0, 0, 0, 0, 0, 0, 1, 1, 1)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:311` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 0, 0, 0, 0, 0, 0, 0, 1, 1, 1)) then`
- `Cascade_Configuration_TXBF_Simple.lua:307` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Configuration_TXBF_Simple.lua:318` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 0, 0, 0, 0, 0, 0, 0, 1, 1, 1)) then`
- `Cascade_Configuration_TXBF_Simple.lua:329` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 0, 0, 0, 0, 0, 0, 0, 1, 1, 1)) then`
- `Cascade_Configuration_TXBF_Simple.lua:340` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 0, 0, 0, 0, 0, 0, 0, 1, 1, 1)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:139` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:147` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 1, 1, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:155` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 2, 2, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:163` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 3, 3, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:171` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 4, 4, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:179` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 5, 5, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:187` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 6, 6, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:195` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 7, 7, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:203` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 8, 8, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:211` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 9, 9, 0, 0, 0, 0, 0, 0, 0, 1)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:219` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 10, 10, 0, 0, 0, 0, 0, 0, 1, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:227` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 11, 11, 0, 0, 0, 0, 0, 1, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:237` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:245` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 1, 1, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:253` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 2, 2, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:261` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 3, 3, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:269` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 4, 4, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:277` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 5, 5, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:285` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 6, 6, 0, 0, 0, 0, 0, 0, 0, 1)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:293` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 7, 7, 0, 0, 0, 0, 0, 0, 1, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:301` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 8, 8, 0, 0, 0, 0, 0, 1, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:309` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 9, 9, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:317` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 10, 10, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:325` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 11, 11, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:335` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:343` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 1, 1, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:351` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 2, 2, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:359` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 3, 3, 0, 0, 0, 0, 0, 0, 0, 1)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:367` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 4, 4, 0, 0, 0, 0, 0, 0, 1, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:375` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 5, 5, 0, 0, 0, 0, 0, 1, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:383` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 6, 6, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:391` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 7, 7, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:399` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 8, 8, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:407` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 9, 9, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:415` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 10, 10, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:423` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 11, 11, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:433` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:441` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 1, 1, 0, 0, 0, 0, 0, 0, 1, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:449` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 2, 2, 0, 0, 0, 0, 0, 1, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:457` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 3, 3, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:465` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 4, 4, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:473` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 5, 5, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:481` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 6, 6, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:489` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 7, 7, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:497` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 8, 8, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:505` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 9, 9, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:513` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 10, 10, 0, 0, 0, 0, 0, 0, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:521` : `if (0 == ar1.ChirpConfig_mult(dev_list[i], 11, 11, 0, 0, 0, 0, 0, 0, 0, 0)) then`

## FrameConfig_mult
- `DemoConfig_Cascade.lua:495` : `if (0 == ar1.FrameConfig_mult(dev_list[i],start_chirp_tx,end_chirp_tx,nframes, nchirp_loops, Inter_Frame_Interval, 0, trig_list[i])) then --n*2 for the work around to handle an issue in the TSW14J56 FW`
- `Cascade_Configuration_MIMO.lua:776` : `if (0 == ar1.FrameConfig_mult(1,start_chirp_tx,end_chirp_tx,nframes_master, nchirp_loops,`
- `Cascade_Configuration_MIMO.lua:783` : `if (0 == ar1.FrameConfig_mult(deviceMapSlaves,start_chirp_tx,end_chirp_tx,nframes_slave, nchirp_loops,`
- `Cascade_Configuration_TestSource.lua:354` : `if (0 == ar1.FrameConfig_mult(1,start_chirp_tx,end_chirp_tx,nframes_master, nchirp_loops,`
- `Cascade_Configuration_TestSource.lua:361` : `if (0 == ar1.FrameConfig_mult(deviceMapSlaves,start_chirp_tx,end_chirp_tx,nframes_slave, nchirp_loops,`
- `Cascade_Configuration_TXBF_AngleSweep.lua:593` : `if (0 == ar1.FrameConfig_mult(1,start_chirp_tx,end_chirp_tx,nframes_master, nchirp_loops, Inter_Frame_Interval, 0, 1)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:599` : `if (0 == ar1.FrameConfig_mult(deviceMapSlaves,start_chirp_tx,end_chirp_tx,nframes_slave, nchirp_loops, Inter_Frame_Interval, 0, 2)) then`
- `Cascade_Configuration_TXBF_Simple.lua:565` : `if (0 == ar1.FrameConfig_mult(1,start_chirp_tx,end_chirp_tx,nframes_master, nchirp_loops, Inter_Frame_Interval, 0, 1)) then`
- `Cascade_Configuration_TXBF_Simple.lua:571` : `if (0 == ar1.FrameConfig_mult(deviceMapSlaves,start_chirp_tx,end_chirp_tx,nframes_slave, nchirp_loops, Inter_Frame_Interval, 0, 2)) then`
- `Cascade_Monitoring_Example.lua:52` : `if (0 == ar1.FrameConfig_mult(1, start_chirp_tx, end_chirp_tx, nframes_master, nchirp_loops,`
- `Cascade_Monitoring_Example.lua:59` : `if (0 == ar1.FrameConfig_mult(14, start_chirp_tx, end_chirp_tx, nframes_slave, nchirp_loops,`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:866` : `if (0 == ar1.FrameConfig_mult(1,start_chirp_tx,end_chirp_tx,nframes_master, nchirp_loops,`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:873` : `if (0 == ar1.FrameConfig_mult(deviceMapSlaves,start_chirp_tx,end_chirp_tx,nframes_slave, nchirp_loops,`

## CaptureContStreamADCData
- `Meas_Gain.lua:19` : `Success = ar1.CaptureContStreamADCData(ADC_File_Path, Num_Samples_per_Channel)`
- `Meas_NF.lua:24` : `Success = ar1.CaptureContStreamADCData(ADC_File_Path, Num_Samples_per_Channel)`

## MeasureFundPower
- `Meas_Gain.lua:30` : `Success, Signal_Output_Power_dBFs, Meas_Peak_IF_Freq_Hz =  ar1.MeasureFundPower(ADC_File_Path, Signal_Meas_RBW_Hz,  RxChain, 0)`

## MeasurePowerSpectralDensity
- `Meas_NF.lua:34` : `Success, Noise_dBFsperHz =  ar1.MeasurePowerSpectralDensity(ADC_File_Path,IF_Freq_MHz*1e6-Noise_IntegBW_Hz/2,Noise_IntegBW_Hz,RxChain, 0)`

## SetTestSource
- `RadarStudioAPIsTest.lua:117` : `if (0 == ar1.SetTestSource(4, 3, 0, 0, 0, 0, -327, 0, -327, 327, 327, 327, -2, 327, 327, 0, 0, 0, 0, -327, 0, -327, 327, 327, 327, -237, 0, 0, 4, 0, 8, 0, 12, 0, 0, 0, 0, 0, 0, 0)) then`

## EnableTestSource
- `RadarStudioAPIsTest.lua:125` : `if (0 == ar1.EnableTestSource(1)) then`

## PowerOff
- `RadarStudioAPIsTest.lua:152` : `ar1.PowerOff()`

## ReadRegAbs
- `ar1.lua:7` : `Example 		: val = ar1.ReadRegAbs(0xFFFFE254, "5:0")`
- `ar1.lua:9` : `function ar1.ReadRegAbs(abs_address, field_mask)`

## WriteRegAbs
- `ar1.lua:31` : `Example 		: res = ar1.WriteRegAbs(0xFFFFE254, "5:0", 0x1F)`
- `ar1.lua:33` : `function ar1.WriteRegAbs(abs_address, field_mask, value)`

## rbn
- `ar1.lua:65` : `Examples 		: res = ar1.rbn("/Registers/MSS_QSPI/SPI_DATA1")`
- `ar1.lua:66` : `res = ar1.rbn("/Registers/MSS_QSPI/SPI_DATA1", "31:0")`
- `ar1.lua:68` : `function ar1.rbn(full_path, field_mask)`

## wbn
- `ar1.lua:94` : `Example 		: res = ar1.wbn("/Registers/MSS_QSPI/SPI_DATA1", 0xABCDEFAB)`
- `ar1.lua:95` : `res = ar1.wbn("/Registers/MSS_QSPI/SPI_DATA1", 0xABCDEFAB,"31:0")`
- `ar1.lua:98` : `function ar1.wbn(full_path, value, field_mask)`

## StopFrame_mult
- `Cascade_Capture.lua:64` : `status = ar1.StopFrame_mult(dev_list[Device_ID], stop_frame_mode) --Stop Trigger Frame`
- `Cascade_Configuration_TXBF_AngleSweep.lua:195` : `status = ar1.StopFrame_mult(dev_list[Device_ID]) --Stop Trigger Frame`
- `Cascade_Configuration_TXBF_Simple.lua:225` : `status = ar1.StopFrame_mult(dev_list[Device_ID]) --Stop Trigger Frame`
- `Cascade_Monitoring_Example.lua:38` : `status = ar1.StopFrame_mult(dev_list[Device_ID], stop_frame_mode) --Stop Trigger Frame`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:545` : `status = ar1.StopFrame_mult(dev_list[Device_ID]) --Stop Trigger Frame`

## TDACaptureCard_StartRecord_mult
- `Cascade_Capture.lua:84` : `status = ar1.TDACaptureCard_StartRecord_mult(1, n_files_allocation, data_packaging, capture_directory, num_frames_to_capture)`
- `Cascade_Configuration_TXBF_AngleSweep.lua:223` : `status = ar1.TDACaptureCard_StartRecord_mult(1, n_files_allocation, data_packaging, capture_directory, num_frames_to_capture)`
- `Cascade_Configuration_TXBF_Simple.lua:253` : `status = ar1.TDACaptureCard_StartRecord_mult(1, n_files_allocation, data_packaging, capture_directory, num_frames_to_capture)`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:914` : `status = ar1.TDACaptureCard_StartRecord_mult(1, n_files_allocation, data_packaging, capture_directory, num_frames_to_capture)`

## TransferFilesUsingWinSCP_mult
- `Cascade_Capture.lua:142` : `status = ar1.TransferFilesUsingWinSCP_mult(1)`
- `Cascade_Configuration_TXBF_AngleSweep.lua:255` : `status = ar1.TransferFilesUsingWinSCP_mult(1)`
- `Cascade_Configuration_TXBF_Simple.lua:285` : `status = ar1.TransferFilesUsingWinSCP_mult(1)`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:946` : `status = ar1.TransferFilesUsingWinSCP_mult(1)`

## ContStrModEnable_mult
- `Cascade_Capture_ContStream.lua:69` : `status = ar1.ContStrModEnable_mult(dev_list[Device_ID]) --Start Streaming`

## ContStrModDisable_mult
- `Cascade_Capture_ContStream.lua:77` : `status = ar1.ContStrModDisable_mult(dev_list[Device_ID]) --Stop Streaming`

## TDAContStream_StartRecord_mult
- `Cascade_Capture_ContStream.lua:127` : `status = ar1.TDAContStream_StartRecord_mult(15, capture_directory)`

## TransferFilesUsingWinSCPContStream_mult
- `Cascade_Capture_ContStream.lua:163` : `status = ar1.TransferFilesUsingWinSCPContStream_mult(1)`

## ConnectTDA
- `Cascade_Configuration_Basic.lua:53` : `if (0 == ar1.ConnectTDA(TDA_IPAddress, 5001, deviceMapTDA)) then`
- `Cascade_Configuration_ContStream.lua:53` : `if(0 == ar1.ConnectTDA(TDA_IPAddress, 5001, deviceMapOverall)) then`
- `Cascade_Configuration_MIMO.lua:521` : `if(0 == ar1.ConnectTDA(TDA_IPAddress, 5001, deviceMapOverall)) then`
- `Cascade_Configuration_TestSource.lua:97` : `if(0 == ar1.ConnectTDA(TDA_IPAddress, 5001, deviceMapOverall)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:329` : `if(0 == ar1.ConnectTDA(TDA_IPAddress, 5001, deviceMapOverall)) then`
- `Cascade_Configuration_TXBF_Simple.lua:359` : `if(0 == ar1.ConnectTDA(TDA_IPAddress, 5001, deviceMapOverall)) then`
- `Cascade_Flashing_example.lua:44` : `if(0 == ar1.ConnectTDA(TDA_IPAddress, 5001, deviceMapOverall)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:565` : `if(0 == ar1.ConnectTDA(TDA_IPAddress, 5001, deviceMapOverall)) then`

## selectCascadeMode
- `Cascade_Configuration_Basic.lua:60` : `if (0 == ar1.selectCascadeMode(1)) then`
- `Cascade_Configuration_ContStream.lua:60` : `if(0 == ar1.selectCascadeMode(1)) then`
- `Cascade_Configuration_MIMO.lua:528` : `if(0 == ar1.selectCascadeMode(1)) then`
- `Cascade_Configuration_TestSource.lua:104` : `if(0 == ar1.selectCascadeMode(1)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:336` : `if(0 == ar1.selectCascadeMode(1)) then`
- `Cascade_Configuration_TXBF_Simple.lua:366` : `if(0 == ar1.selectCascadeMode(1)) then`
- `Cascade_Flashing_example.lua:51` : `if(0 == ar1.selectCascadeMode(1)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:572` : `if(0 == ar1.selectCascadeMode(1)) then`

## DownloadBssFwOvSPI_mult
- `Cascade_Configuration_Basic.lua:104` : `if (0 == ar1.DownloadBssFwOvSPI_mult(dev_list[i], metaImagePath)) then`
- `Cascade_Configuration_ContStream.lua:88` : `if (0 == ar1.DownloadBssFwOvSPI_mult(1, metaImagePath)) then`
- `Cascade_Configuration_ContStream.lua:137` : `if (0 == ar1.DownloadBssFwOvSPI_mult(deviceMapSlaves, metaImagePath)) then`
- `Cascade_Configuration_MIMO.lua:556` : `if (0 == ar1.DownloadBssFwOvSPI_mult(1, metaImagePath)) then`
- `Cascade_Configuration_MIMO.lua:605` : `if (0 == ar1.DownloadBssFwOvSPI_mult(deviceMapSlaves, metaImagePath)) then`
- `Cascade_Configuration_TestSource.lua:132` : `if (0 == ar1.DownloadBssFwOvSPI_mult(1, metaImagePath)) then`
- `Cascade_Configuration_TestSource.lua:181` : `if (0 == ar1.DownloadBssFwOvSPI_mult(deviceMapSlaves, metaImagePath)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:364` : `if (0 == ar1.DownloadBssFwOvSPI_mult(1, metaImagePath)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:414` : `if (0 == ar1.DownloadBssFwOvSPI_mult(deviceMapSlaves, metaImagePath)) then`
- `Cascade_Configuration_TXBF_Simple.lua:394` : `if (0 == ar1.DownloadBssFwOvSPI_mult(1, metaImagePath)) then`
- `Cascade_Configuration_TXBF_Simple.lua:444` : `if (0 == ar1.DownloadBssFwOvSPI_mult(deviceMapSlaves, metaImagePath)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:600` : `if (0 == ar1.DownloadBssFwOvSPI_mult(1, metaImagePath)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:649` : `if (0 == ar1.DownloadBssFwOvSPI_mult(deviceMapSlaves, metaImagePath)) then`

## SetMiscConfig_mult
- `Cascade_Configuration_Basic.lua:148` : `if (0 == ar1.SetMiscConfig_mult(dev_list[i], 1, 0, 0, 0)) then`
- `Cascade_Configuration_ContStream.lua:180` : `if (0 == ar1.SetMiscConfig_mult(deviceMapOverall, 1, 0, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:648` : `if (0 == ar1.SetMiscConfig_mult(deviceMapOverall, 1, 0, 0, 0)) then`
- `Cascade_Configuration_TestSource.lua:224` : `if (0 == ar1.SetMiscConfig_mult(deviceMapOverall, 1, 0, 0, 0)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:457` : `if (0 == ar1.SetMiscConfig_mult(deviceMapOverall, 0, 0, 0, 0)) then -- enables the per chirp phase shifter enable`
- `Cascade_Configuration_TXBF_Simple.lua:487` : `if (0 == ar1.SetMiscConfig_mult(deviceMapOverall, 0, 0, 0, 0)) then -- enables the per chirp phase shifter enable`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:692` : `if (0 == ar1.SetMiscConfig_mult(deviceMapOverall, 1, 0, 0, 0)) then`

## RfInitCalibConfig_mult
- `Cascade_Configuration_Basic.lua:157` : `if (0 == ar1.RfInitCalibConfig_mult(dev_list[i], 1, 1, 1, 1, 1, 1, 1, 65537)) then`
- `Cascade_Configuration_ContStream.lua:189` : `if (0 == ar1.RfInitCalibConfig_mult(deviceMapOverall, 1, 1, 1, 1, 1, 1, 1, 65537)) then`
- `Cascade_Configuration_MIMO.lua:657` : `if (0 == ar1.RfInitCalibConfig_mult(deviceMapOverall, 1, 1, 1, 1, 1, 1, 1, 65537)) then`
- `Cascade_Configuration_TestSource.lua:233` : `if (0 == ar1.RfInitCalibConfig_mult(deviceMapOverall, 1, 1, 1, 1, 1, 1, 1, 65537)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:466` : `if (0 == ar1.RfInitCalibConfig_mult(deviceMapOverall, 1, 1, 1, 1, 1, 1, 1, 65537)) then`
- `Cascade_Configuration_TXBF_Simple.lua:496` : `if (0 == ar1.RfInitCalibConfig_mult(deviceMapOverall, 1, 1, 1, 1, 1, 1, 1, 65537)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:701` : `if (0 == ar1.RfInitCalibConfig_mult(deviceMapOverall, 1, 1, 1, 1, 1, 1, 1, 65537)) then`

## CSI2LaneConfig_mult
- `Cascade_Configuration_Basic.lua:210` : `if (0 == ar1.CSI2LaneConfig_mult(dev_list[i], 1, 0, 2, 0, 4, 0, 5, 0, 3, 0, 0)) then`
- `Cascade_Configuration_ContStream.lua:223` : `if (0 == ar1.CSI2LaneConfig_mult(deviceMapOverall, 1, 0, 2, 0, 4, 0, 5, 0, 3, 0, 0)) then`
- `Cascade_Configuration_MIMO.lua:691` : `if (0 == ar1.CSI2LaneConfig_mult(deviceMapOverall, 1, 0, 2, 0, 4, 0, 5, 0, 3, 0, 0)) then`
- `Cascade_Configuration_TestSource.lua:267` : `if (0 == ar1.CSI2LaneConfig_mult(deviceMapOverall, 1, 0, 2, 0, 4, 0, 5, 0, 3, 0, 0)) then`
- `Cascade_Configuration_TXBF_AngleSweep.lua:500` : `if (0 == ar1.CSI2LaneConfig_mult(deviceMapOverall, 1, 0, 2, 0, 4, 0, 5, 0, 3, 0, 0)) then`
- `Cascade_Configuration_TXBF_Simple.lua:530` : `if (0 == ar1.CSI2LaneConfig_mult(deviceMapOverall, 1, 0, 2, 0, 4, 0, 5, 0, 3, 0, 0)) then`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:735` : `if (0 == ar1.CSI2LaneConfig_mult(deviceMapOverall, 1, 0, 2, 0, 4, 0, 5, 0, 3, 0, 0)) then`

## SetTestSource_mult
- `Cascade_Configuration_MIMO.lua:706` : `if (0 == ar1.SetTestSource_mult(1, 4, 3, 0, 0, 0, 0, -327, 0, -327, 327, 327, 327, -2.5, 327, 327, 0,`
- `Cascade_Configuration_MIMO.lua:717` : `if (0 == ar1.SetTestSource_mult(2, 3, 4, 0, 0, 0, 0, -327, 0, -327, 327, 327, 327, -2.5, 327, 327, 0,`
- `Cascade_Configuration_MIMO.lua:728` : `if (0 == ar1.SetTestSource_mult(4, 12, 5, 0, 0, 0, 0, -327, 0, -327, 327, 327, 327, -2.5, 327, 327, 0,`
- `Cascade_Configuration_MIMO.lua:739` : `if (0 == ar1.SetTestSource_mult(8, 5, 12, 0, 0, 0, 0, -327, 0, -327, 327, 327, 327, -2.5, 327, 327, 0,`
- `Cascade_Configuration_TestSource.lua:282` : `if (0 == ar1.SetTestSource_mult(1, 4, 3, 0, 0, 0, 0, -327, 0, -327, 327, 327, 327, -2.5, 327, 327, 0,`
- `Cascade_Configuration_TestSource.lua:293` : `if (0 == ar1.SetTestSource_mult(2, 3, 4, 0, 0, 0, 0, -327, 0, -327, 327, 327, 327, -2.5, 327, 327, 0,`
- `Cascade_Configuration_TestSource.lua:304` : `if (0 == ar1.SetTestSource_mult(4, 12, 5, 0, 0, 0, 0, -327, 0, -327, 327, 327, 327, -2.5, 327, 327, 0,`
- `Cascade_Configuration_TestSource.lua:315` : `if (0 == ar1.SetTestSource_mult(8, 5, 12, 0, 0, 0, 0, -327, 0, -327, 327, 327, 327, -2.5, 327, 327, 0,`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:750` : `if (0 == ar1.SetTestSource_mult(1, 4, 3, 0, 0, 0, 0, -327, 0, -327, 327, 327, 327, -2.5, 327, 327, 0,`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:761` : `if (0 == ar1.SetTestSource_mult(2, 3, 4, 0, 0, 0, 0, -327, 0, -327, 327, 327, 327, -2.5, 327, 327, 0,`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:772` : `if (0 == ar1.SetTestSource_mult(4, 12, 5, 0, 0, 0, 0, -327, 0, -327, 327, 327, 327, -2.5, 327, 327, 0,`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:783` : `if (0 == ar1.SetTestSource_mult(8, 5, 12, 0, 0, 0, 0, -327, 0, -327, 327, 327, 327, -2.5, 327, 327, 0,`

## EnableTestSource_mult
- `Cascade_Configuration_MIMO.lua:770` : `ar1.EnableTestSource_mult(deviceMapOverall, 1)`
- `Cascade_Configuration_TestSource.lua:348` : `ar1.EnableTestSource_mult(deviceMapOverall, 1)`

## SetPerChirpPhaseShifterConfig_mult
- `Cascade_Configuration_TXBF.lua:4` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 0, 0, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:6` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 1, 1, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:8` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 2, 2, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:10` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 3, 3, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:12` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 4, 4, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:14` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 5, 5, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:16` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 6, 6, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:18` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 7, 7, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:20` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 8, 8, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:22` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 9, 9, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:24` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 10, 10, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:26` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 11, 11, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:28` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 12, 12, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:30` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 13, 13, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:32` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 14, 14, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:34` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 15, 15, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:36` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 16, 16, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:38` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 17, 17, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:40` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 18, 18, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:42` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 19, 19, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:44` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 20, 20, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:46` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 21, 21, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:48` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 22, 22, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:50` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 23, 23, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:52` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 24, 24, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:54` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 25, 25, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:56` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 26, 26, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:58` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 27, 27, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:60` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 28, 28, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:62` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 29, 29, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:64` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 30, 30, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:66` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 31, 31, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:68` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 32, 32, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:70` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 33, 33, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:72` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 34, 34, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:74` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 35, 35, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:76` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 36, 36, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:78` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 37, 37, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:80` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 38, 38, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:82` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 39, 39, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:84` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 40, 40, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:86` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 41, 41, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:88` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 42, 42, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:90` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 43, 43, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:92` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 44, 44, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:94` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 45, 45, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:96` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 46, 46, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:98` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 47, 47, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:100` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 48, 48, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:102` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 49, 49, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:104` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 50, 50, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:106` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 51, 51, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:108` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 52, 52, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:110` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 53, 53, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:112` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 54, 54, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:114` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 55, 55, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:116` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 56, 56, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:118` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 57, 57, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:120` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 58, 58, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:122` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 59, 59, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:124` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 60, 60, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:126` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 61, 61, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:128` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 62, 62, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:130` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 63, 63, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:132` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 64, 64, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:134` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 65, 65, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:136` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 66, 66, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:138` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 67, 67, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:140` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 68, 68, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:142` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 69, 69, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:144` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 70, 70, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:146` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 71, 71, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:148` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 72, 72, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:150` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 73, 73, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:152` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 74, 74, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:154` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 75, 75, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:156` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 76, 76, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:158` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 77, 77, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:160` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 78, 78, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:162` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 79, 79, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:164` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 80, 80, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:166` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 81, 81, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:168` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 82, 82, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:170` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 83, 83, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:172` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 84, 84, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:174` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 85, 85, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:176` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 86, 86, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:178` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 87, 87, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:180` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 88, 88, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:182` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 89, 89, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:184` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 90, 90, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:186` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 91, 91, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:188` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 92, 92, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:190` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 93, 93, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:192` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 94, 94, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:194` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 95, 95, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:196` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 96, 96, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:198` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 97, 97, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:200` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 98, 98, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:202` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 99, 99, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:204` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 100, 100, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:206` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 101, 101, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:208` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 102, 102, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:210` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 103, 103, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:212` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 104, 104, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:214` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 105, 105, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:216` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 106, 106, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:218` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 107, 107, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:220` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 108, 108, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:222` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 109, 109, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:224` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 110, 110, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:226` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 111, 111, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:228` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 112, 112, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:230` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 113, 113, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:232` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 114, 114, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:234` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 115, 115, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:236` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 116, 116, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:238` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 117, 117, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:240` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 118, 118, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:242` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 119, 119, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:244` : `ar1.SetPerChirpPhaseShifterConfig_mult(1, 120, 120, 42, 44, 47)`
- `Cascade_Configuration_TXBF.lua:249` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 0, 0, 0, 54, 49)`
- `Cascade_Configuration_TXBF.lua:251` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 1, 1, 8, 62, 55)`
- `Cascade_Configuration_TXBF.lua:253` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 2, 2, 18, 6, 62)`
- `Cascade_Configuration_TXBF.lua:255` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 3, 3, 27, 14, 5)`
- `Cascade_Configuration_TXBF.lua:257` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 4, 4, 37, 23, 13)`
- `Cascade_Configuration_TXBF.lua:259` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 5, 5, 47, 31, 20)`
- `Cascade_Configuration_TXBF.lua:261` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 6, 6, 58, 40, 28)`
- `Cascade_Configuration_TXBF.lua:263` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 7, 7, 4, 50, 36)`
- `Cascade_Configuration_TXBF.lua:265` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 8, 8, 15, 59, 44)`
- `Cascade_Configuration_TXBF.lua:267` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 9, 9, 26, 5, 52)`
- `Cascade_Configuration_TXBF.lua:269` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 10, 10, 37, 15, 61)`
- `Cascade_Configuration_TXBF.lua:271` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 11, 11, 49, 25, 6)`
- `Cascade_Configuration_TXBF.lua:273` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 12, 12, 61, 35, 15)`
- `Cascade_Configuration_TXBF.lua:275` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 13, 13, 9, 46, 24)`
- `Cascade_Configuration_TXBF.lua:277` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 14, 14, 21, 57, 33)`
- `Cascade_Configuration_TXBF.lua:279` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 15, 15, 34, 4, 42)`
- `Cascade_Configuration_TXBF.lua:281` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 16, 16, 47, 15, 52)`
- `Cascade_Configuration_TXBF.lua:283` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 17, 17, 60, 26, 62)`
- `Cascade_Configuration_TXBF.lua:285` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 18, 18, 9, 38, 8)`
- `Cascade_Configuration_TXBF.lua:287` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 19, 19, 22, 50, 18)`
- `Cascade_Configuration_TXBF.lua:289` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 20, 20, 36, 61, 28)`
- `Cascade_Configuration_TXBF.lua:291` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 21, 21, 50, 9, 38)`
- `Cascade_Configuration_TXBF.lua:293` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 22, 22, 0, 22, 49)`
- `Cascade_Configuration_TXBF.lua:295` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 23, 23, 14, 35, 60)`
- `Cascade_Configuration_TXBF.lua:297` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 24, 24, 29, 47, 7)`
- `Cascade_Configuration_TXBF.lua:299` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 25, 25, 44, 60, 18)`
- `Cascade_Configuration_TXBF.lua:301` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 26, 26, 59, 9, 29)`
- `Cascade_Configuration_TXBF.lua:303` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 27, 27, 9, 22, 40)`
- `Cascade_Configuration_TXBF.lua:305` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 28, 28, 25, 36, 51)`
- `Cascade_Configuration_TXBF.lua:307` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 29, 29, 40, 49, 63)`
- `Cascade_Configuration_TXBF.lua:309` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 30, 30, 56, 63, 11)`
- `Cascade_Configuration_TXBF.lua:311` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 31, 31, 7, 12, 23)`
- `Cascade_Configuration_TXBF.lua:313` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 32, 32, 23, 27, 35)`
- `Cascade_Configuration_TXBF.lua:315` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 33, 33, 39, 41, 47)`
- `Cascade_Configuration_TXBF.lua:317` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 34, 34, 56, 55, 59)`
- `Cascade_Configuration_TXBF.lua:319` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 35, 35, 8, 5, 7)`
- `Cascade_Configuration_TXBF.lua:321` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 36, 36, 25, 20, 19)`
- `Cascade_Configuration_TXBF.lua:323` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 37, 37, 41, 34, 32)`
- `Cascade_Configuration_TXBF.lua:325` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 38, 38, 58, 49, 45)`
- `Cascade_Configuration_TXBF.lua:327` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 39, 39, 11, 0, 57)`
- `Cascade_Configuration_TXBF.lua:329` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 40, 40, 28, 14, 6)`
- `Cascade_Configuration_TXBF.lua:331` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 41, 41, 45, 29, 19)`
- `Cascade_Configuration_TXBF.lua:333` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 42, 42, 62, 44, 32)`
- `Cascade_Configuration_TXBF.lua:335` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 43, 43, 16, 60, 45)`
- `Cascade_Configuration_TXBF.lua:337` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 44, 44, 33, 11, 58)`
- `Cascade_Configuration_TXBF.lua:339` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 45, 45, 51, 26, 7)`
- `Cascade_Configuration_TXBF.lua:341` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 46, 46, 4, 42, 20)`
- `Cascade_Configuration_TXBF.lua:343` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 47, 47, 22, 57, 33)`
- `Cascade_Configuration_TXBF.lua:345` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 48, 48, 40, 9, 47)`
- `Cascade_Configuration_TXBF.lua:347` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 49, 49, 58, 24, 60)`
- `Cascade_Configuration_TXBF.lua:349` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 50, 50, 11, 40, 10)`
- `Cascade_Configuration_TXBF.lua:351` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 51, 51, 29, 56, 23)`
- `Cascade_Configuration_TXBF.lua:353` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 52, 52, 48, 7, 37)`
- `Cascade_Configuration_TXBF.lua:355` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 53, 53, 1, 23, 50)`
- `Cascade_Configuration_TXBF.lua:357` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 54, 54, 19, 39, 0)`
- `Cascade_Configuration_TXBF.lua:359` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 55, 55, 38, 55, 13)`
- `Cascade_Configuration_TXBF.lua:361` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 56, 56, 56, 7, 27)`
- `Cascade_Configuration_TXBF.lua:363` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 57, 57, 10, 23, 40)`
- `Cascade_Configuration_TXBF.lua:365` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 58, 58, 28, 39, 54)`
- `Cascade_Configuration_TXBF.lua:367` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 59, 59, 47, 55, 4)`
- `Cascade_Configuration_TXBF.lua:369` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 60, 60, 0, 7, 17)`
- `Cascade_Configuration_TXBF.lua:371` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 61, 61, 19, 23, 31)`
- `Cascade_Configuration_TXBF.lua:373` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 62, 62, 37, 38, 45)`
- `Cascade_Configuration_TXBF.lua:375` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 63, 63, 55, 54, 58)`
- `Cascade_Configuration_TXBF.lua:377` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 64, 64, 9, 6, 8)`
- `Cascade_Configuration_TXBF.lua:379` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 65, 65, 28, 22, 22)`
- `Cascade_Configuration_TXBF.lua:381` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 66, 66, 46, 38, 35)`
- `Cascade_Configuration_TXBF.lua:383` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 67, 67, 0, 54, 49)`
- `Cascade_Configuration_TXBF.lua:385` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 68, 68, 18, 6, 62)`
- `Cascade_Configuration_TXBF.lua:387` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 69, 69, 36, 21, 12)`
- `Cascade_Configuration_TXBF.lua:389` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 70, 70, 54, 37, 25)`
- `Cascade_Configuration_TXBF.lua:391` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 71, 71, 7, 53, 39)`
- `Cascade_Configuration_TXBF.lua:393` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 72, 72, 25, 4, 52)`
- `Cascade_Configuration_TXBF.lua:395` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 73, 73, 43, 20, 2)`
- `Cascade_Configuration_TXBF.lua:397` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 74, 74, 61, 35, 15)`
- `Cascade_Configuration_TXBF.lua:399` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 75, 75, 15, 51, 28)`
- `Cascade_Configuration_TXBF.lua:401` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 76, 76, 32, 2, 41)`
- `Cascade_Configuration_TXBF.lua:403` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 77, 77, 50, 17, 54)`
- `Cascade_Configuration_TXBF.lua:405` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 78, 78, 3, 33, 3)`
- `Cascade_Configuration_TXBF.lua:407` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 79, 79, 20, 48, 16)`
- `Cascade_Configuration_TXBF.lua:409` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 80, 80, 37, 63, 29)`
- `Cascade_Configuration_TXBF.lua:411` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 81, 81, 54, 13, 42)`
- `Cascade_Configuration_TXBF.lua:413` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 82, 82, 7, 28, 54)`
- `Cascade_Configuration_TXBF.lua:415` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 83, 83, 24, 43, 3)`
- `Cascade_Configuration_TXBF.lua:417` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 84, 84, 41, 58, 16)`
- `Cascade_Configuration_TXBF.lua:419` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 85, 85, 57, 8, 28)`
- `Cascade_Configuration_TXBF.lua:421` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 86, 86, 9, 22, 40)`
- `Cascade_Configuration_TXBF.lua:423` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 87, 87, 26, 36, 52)`
- `Cascade_Configuration_TXBF.lua:425` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 88, 88, 42, 51, 0)`
- `Cascade_Configuration_TXBF.lua:427` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 89, 89, 58, 1, 12)`
- `Cascade_Configuration_TXBF.lua:429` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 90, 90, 9, 14, 24)`
- `Cascade_Configuration_TXBF.lua:431` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 91, 91, 25, 28, 36)`
- `Cascade_Configuration_TXBF.lua:433` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 92, 92, 40, 41, 47)`
- `Cascade_Configuration_TXBF.lua:435` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 93, 93, 56, 55, 59)`
- `Cascade_Configuration_TXBF.lua:437` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 94, 94, 6, 4, 6)`
- `Cascade_Configuration_TXBF.lua:439` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 95, 95, 22, 17, 17)`
- `Cascade_Configuration_TXBF.lua:441` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 96, 96, 36, 30, 28)`
- `Cascade_Configuration_TXBF.lua:443` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 97, 97, 51, 42, 39)`
- `Cascade_Configuration_TXBF.lua:445` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 98, 98, 1, 55, 50)`
- `Cascade_Configuration_TXBF.lua:447` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 99, 99, 15, 4, 61)`
- `Cascade_Configuration_TXBF.lua:449` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 100, 100, 29, 16, 7)`
- `Cascade_Configuration_TXBF.lua:451` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 101, 101, 43, 28, 17)`
- `Cascade_Configuration_TXBF.lua:453` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 102, 102, 56, 39, 27)`
- `Cascade_Configuration_TXBF.lua:455` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 103, 103, 5, 51, 37)`
- `Cascade_Configuration_TXBF.lua:457` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 104, 104, 19, 62, 47)`
- `Cascade_Configuration_TXBF.lua:459` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 105, 105, 32, 9, 56)`
- `Cascade_Configuration_TXBF.lua:461` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 106, 106, 44, 21, 2)`
- `Cascade_Configuration_TXBF.lua:463` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 107, 107, 56, 31, 11)`
- `Cascade_Configuration_TXBF.lua:465` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 108, 108, 4, 42, 20)`
- `Cascade_Configuration_TXBF.lua:467` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 109, 109, 16, 52, 29)`
- `Cascade_Configuration_TXBF.lua:469` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 110, 110, 28, 62, 38)`
- `Cascade_Configuration_TXBF.lua:471` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 111, 111, 39, 8, 46)`
- `Cascade_Configuration_TXBF.lua:473` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 112, 112, 50, 18, 55)`
- `Cascade_Configuration_TXBF.lua:475` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 113, 113, 61, 28, 63)`
- `Cascade_Configuration_TXBF.lua:477` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 114, 114, 7, 37, 7)`
- `Cascade_Configuration_TXBF.lua:479` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 115, 115, 18, 46, 15)`
- `Cascade_Configuration_TXBF.lua:481` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 116, 116, 28, 55, 22)`
- `Cascade_Configuration_TXBF.lua:483` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 117, 117, 38, 63, 30)`
- `Cascade_Configuration_TXBF.lua:485` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 118, 118, 48, 7, 37)`
- `Cascade_Configuration_TXBF.lua:487` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 119, 119, 57, 15, 43)`
- `Cascade_Configuration_TXBF.lua:489` : `ar1.SetPerChirpPhaseShifterConfig_mult(2, 120, 120, 1, 23, 50)`
- `Cascade_Configuration_TXBF.lua:494` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 0, 0, 35, 27, 17)`
- `Cascade_Configuration_TXBF.lua:496` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 1, 1, 40, 31, 20)`
- `Cascade_Configuration_TXBF.lua:498` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 2, 2, 46, 36, 24)`
- `Cascade_Configuration_TXBF.lua:500` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 3, 3, 52, 41, 28)`
- `Cascade_Configuration_TXBF.lua:502` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 4, 4, 58, 46, 31)`
- `Cascade_Configuration_TXBF.lua:504` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 5, 5, 1, 51, 35)`
- `Cascade_Configuration_TXBF.lua:506` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 6, 6, 7, 56, 39)`
- `Cascade_Configuration_TXBF.lua:508` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 7, 7, 14, 61, 43)`
- `Cascade_Configuration_TXBF.lua:510` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 8, 8, 20, 2, 47)`
- `Cascade_Configuration_TXBF.lua:512` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 9, 9, 27, 8, 51)`
- `Cascade_Configuration_TXBF.lua:514` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 10, 10, 34, 14, 55)`
- `Cascade_Configuration_TXBF.lua:516` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 11, 11, 41, 20, 60)`
- `Cascade_Configuration_TXBF.lua:518` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 12, 12, 49, 26, 0)`
- `Cascade_Configuration_TXBF.lua:520` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 13, 13, 56, 31, 4)`
- `Cascade_Configuration_TXBF.lua:522` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 14, 14, 1, 38, 9)`
- `Cascade_Configuration_TXBF.lua:524` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 15, 15, 8, 44, 14)`
- `Cascade_Configuration_TXBF.lua:526` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 16, 16, 16, 51, 19)`
- `Cascade_Configuration_TXBF.lua:528` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 17, 17, 24, 57, 23)`
- `Cascade_Configuration_TXBF.lua:530` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 18, 18, 33, 63, 29)`
- `Cascade_Configuration_TXBF.lua:532` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 19, 19, 41, 7, 34)`
- `Cascade_Configuration_TXBF.lua:534` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 20, 20, 50, 13, 39)`
- `Cascade_Configuration_TXBF.lua:536` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 21, 21, 58, 20, 44)`
- `Cascade_Configuration_TXBF.lua:538` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 22, 22, 3, 27, 49)`
- `Cascade_Configuration_TXBF.lua:540` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 23, 23, 12, 34, 55)`
- `Cascade_Configuration_TXBF.lua:542` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 24, 24, 21, 42, 60)`
- `Cascade_Configuration_TXBF.lua:544` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 25, 25, 30, 49, 1)`
- `Cascade_Configuration_TXBF.lua:546` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 26, 26, 39, 57, 7)`
- `Cascade_Configuration_TXBF.lua:548` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 27, 27, 49, 0, 13)`
- `Cascade_Configuration_TXBF.lua:550` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 28, 28, 58, 8, 19)`
- `Cascade_Configuration_TXBF.lua:552` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 29, 29, 4, 15, 24)`
- `Cascade_Configuration_TXBF.lua:554` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 30, 30, 14, 23, 30)`
- `Cascade_Configuration_TXBF.lua:556` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 31, 31, 24, 31, 36)`
- `Cascade_Configuration_TXBF.lua:558` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 32, 32, 34, 39, 42)`
- `Cascade_Configuration_TXBF.lua:560` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 33, 33, 44, 47, 48)`
- `Cascade_Configuration_TXBF.lua:562` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 34, 34, 54, 55, 54)`
- `Cascade_Configuration_TXBF.lua:564` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 35, 35, 1, 63, 60)`
- `Cascade_Configuration_TXBF.lua:566` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 36, 36, 11, 8, 2)`
- `Cascade_Configuration_TXBF.lua:568` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 37, 37, 21, 16, 8)`
- `Cascade_Configuration_TXBF.lua:570` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 38, 38, 31, 24, 15)`
- `Cascade_Configuration_TXBF.lua:572` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 39, 39, 42, 32, 21)`
- `Cascade_Configuration_TXBF.lua:574` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 40, 40, 53, 41, 28)`
- `Cascade_Configuration_TXBF.lua:576` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 41, 41, 0, 50, 34)`
- `Cascade_Configuration_TXBF.lua:578` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 42, 42, 10, 59, 41)`
- `Cascade_Configuration_TXBF.lua:580` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 43, 43, 21, 3, 47)`
- `Cascade_Configuration_TXBF.lua:582` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 44, 44, 32, 12, 54)`
- `Cascade_Configuration_TXBF.lua:584` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 45, 45, 43, 21, 60)`
- `Cascade_Configuration_TXBF.lua:586` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 46, 46, 54, 29, 3)`
- `Cascade_Configuration_TXBF.lua:588` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 47, 47, 1, 38, 9)`
- `Cascade_Configuration_TXBF.lua:590` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 48, 48, 12, 47, 16)`
- `Cascade_Configuration_TXBF.lua:592` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 49, 49, 23, 56, 23)`
- `Cascade_Configuration_TXBF.lua:594` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 50, 50, 34, 1, 30)`
- `Cascade_Configuration_TXBF.lua:596` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 51, 51, 45, 10, 36)`
- `Cascade_Configuration_TXBF.lua:598` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 52, 52, 56, 19, 43)`
- `Cascade_Configuration_TXBF.lua:600` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 53, 53, 4, 28, 50)`
- `Cascade_Configuration_TXBF.lua:602` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 54, 54, 16, 37, 57)`
- `Cascade_Configuration_TXBF.lua:604` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 55, 55, 26, 46, 63)`
- `Cascade_Configuration_TXBF.lua:606` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 56, 56, 38, 55, 6)`
- `Cascade_Configuration_TXBF.lua:608` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 57, 57, 49, 0, 13)`
- `Cascade_Configuration_TXBF.lua:610` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 58, 58, 61, 9, 20)`
- `Cascade_Configuration_TXBF.lua:612` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 59, 59, 8, 18, 27)`
- `Cascade_Configuration_TXBF.lua:614` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 60, 60, 20, 27, 34)`
- `Cascade_Configuration_TXBF.lua:616` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 61, 61, 31, 37, 40)`
- `Cascade_Configuration_TXBF.lua:618` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 62, 62, 42, 46, 47)`
- `Cascade_Configuration_TXBF.lua:620` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 63, 63, 53, 55, 54)`
- `Cascade_Configuration_TXBF.lua:622` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 64, 64, 1, 0, 61)`
- `Cascade_Configuration_TXBF.lua:624` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 65, 65, 13, 9, 3)`
- `Cascade_Configuration_TXBF.lua:626` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 66, 66, 23, 18, 10)`
- `Cascade_Configuration_TXBF.lua:628` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 67, 67, 35, 27, 17)`
- `Cascade_Configuration_TXBF.lua:630` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 68, 68, 46, 36, 24)`
- `Cascade_Configuration_TXBF.lua:632` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 69, 69, 57, 45, 31)`
- `Cascade_Configuration_TXBF.lua:634` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 70, 70, 5, 54, 37)`
- `Cascade_Configuration_TXBF.lua:636` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 71, 71, 16, 63, 44)`
- `Cascade_Configuration_TXBF.lua:638` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 72, 72, 27, 8, 51)`
- `Cascade_Configuration_TXBF.lua:640` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 73, 73, 38, 17, 58)`
- `Cascade_Configuration_TXBF.lua:642` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 74, 74, 49, 26, 0)`
- `Cascade_Configuration_TXBF.lua:644` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 75, 75, 60, 34, 6)`
- `Cascade_Configuration_TXBF.lua:646` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 76, 76, 7, 43, 13)`
- `Cascade_Configuration_TXBF.lua:648` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 77, 77, 18, 52, 20)`
- `Cascade_Configuration_TXBF.lua:650` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 78, 78, 29, 61, 26)`
- `Cascade_Configuration_TXBF.lua:652` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 79, 79, 39, 5, 33)`
- `Cascade_Configuration_TXBF.lua:654` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 80, 80, 50, 14, 39)`
- `Cascade_Configuration_TXBF.lua:656` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 81, 81, 61, 22, 46)`
- `Cascade_Configuration_TXBF.lua:658` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 82, 82, 8, 31, 52)`
- `Cascade_Configuration_TXBF.lua:660` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 83, 83, 18, 39, 58)`
- `Cascade_Configuration_TXBF.lua:662` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 84, 84, 28, 47, 0)`
- `Cascade_Configuration_TXBF.lua:664` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 85, 85, 39, 56, 6)`
- `Cascade_Configuration_TXBF.lua:666` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 86, 86, 49, 0, 13)`
- `Cascade_Configuration_TXBF.lua:668` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 87, 87, 59, 8, 19)`
- `Cascade_Configuration_TXBF.lua:670` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 88, 88, 5, 16, 25)`
- `Cascade_Configuration_TXBF.lua:672` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 89, 89, 15, 24, 31)`
- `Cascade_Configuration_TXBF.lua:674` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 90, 90, 25, 32, 37)`
- `Cascade_Configuration_TXBF.lua:676` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 91, 91, 35, 40, 43)`
- `Cascade_Configuration_TXBF.lua:678` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 92, 92, 44, 47, 49)`
- `Cascade_Configuration_TXBF.lua:680` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 93, 93, 54, 55, 54)`
- `Cascade_Configuration_TXBF.lua:682` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 94, 94, 0, 62, 60)`
- `Cascade_Configuration_TXBF.lua:684` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 95, 95, 9, 6, 1)`
- `Cascade_Configuration_TXBF.lua:686` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 96, 96, 18, 13, 7)`
- `Cascade_Configuration_TXBF.lua:688` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 97, 97, 27, 21, 12)`
- `Cascade_Configuration_TXBF.lua:690` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 98, 98, 36, 28, 18)`
- `Cascade_Configuration_TXBF.lua:692` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 99, 99, 45, 35, 23)`
- `Cascade_Configuration_TXBF.lua:694` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 100, 100, 53, 42, 28)`
- `Cascade_Configuration_TXBF.lua:696` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 101, 101, 62, 49, 33)`
- `Cascade_Configuration_TXBF.lua:698` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 102, 102, 6, 56, 38)`
- `Cascade_Configuration_TXBF.lua:700` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 103, 103, 15, 62, 43)`
- `Cascade_Configuration_TXBF.lua:702` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 104, 104, 22, 4, 48)`
- `Cascade_Configuration_TXBF.lua:704` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 105, 105, 31, 11, 53)`
- `Cascade_Configuration_TXBF.lua:706` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 106, 106, 38, 17, 58)`
- `Cascade_Configuration_TXBF.lua:708` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 107, 107, 46, 23, 62)`
- `Cascade_Configuration_TXBF.lua:710` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 108, 108, 54, 29, 3)`
- `Cascade_Configuration_TXBF.lua:712` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 109, 109, 61, 35, 7)`
- `Cascade_Configuration_TXBF.lua:714` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 110, 110, 5, 41, 12)`
- `Cascade_Configuration_TXBF.lua:716` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 111, 111, 12, 47, 16)`
- `Cascade_Configuration_TXBF.lua:718` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 112, 112, 19, 53, 20)`
- `Cascade_Configuration_TXBF.lua:720` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 113, 113, 25, 58, 24)`
- `Cascade_Configuration_TXBF.lua:722` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 114, 114, 32, 63, 28)`
- `Cascade_Configuration_TXBF.lua:724` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 115, 115, 38, 4, 32)`
- `Cascade_Configuration_TXBF.lua:726` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 116, 116, 45, 9, 36)`
- `Cascade_Configuration_TXBF.lua:728` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 117, 117, 51, 14, 39)`
- `Cascade_Configuration_TXBF.lua:730` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 118, 118, 56, 19, 43)`
- `Cascade_Configuration_TXBF.lua:732` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 119, 119, 63, 24, 47)`
- `Cascade_Configuration_TXBF.lua:734` : `ar1.SetPerChirpPhaseShifterConfig_mult(4, 120, 120, 4, 28, 50)`
- `Cascade_Configuration_TXBF.lua:739` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 0, 0, 3, 55, 50)`
- `Cascade_Configuration_TXBF.lua:741` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 1, 1, 6, 56, 50)`
- `Cascade_Configuration_TXBF.lua:743` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 2, 2, 8, 57, 50)`
- `Cascade_Configuration_TXBF.lua:745` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 3, 3, 10, 59, 50)`
- `Cascade_Configuration_TXBF.lua:747` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 4, 4, 13, 60, 50)`
- `Cascade_Configuration_TXBF.lua:749` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 5, 5, 15, 61, 50)`
- `Cascade_Configuration_TXBF.lua:751` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 6, 6, 18, 63, 50)`
- `Cascade_Configuration_TXBF.lua:753` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 7, 7, 20, 0, 50)`
- `Cascade_Configuration_TXBF.lua:755` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 8, 8, 23, 1, 50)`
- `Cascade_Configuration_TXBF.lua:757` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 9, 9, 26, 3, 50)`
- `Cascade_Configuration_TXBF.lua:759` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 10, 10, 29, 4, 50)`
- `Cascade_Configuration_TXBF.lua:761` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 11, 11, 32, 6, 50)`
- `Cascade_Configuration_TXBF.lua:763` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 12, 12, 35, 7, 50)`
- `Cascade_Configuration_TXBF.lua:765` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 13, 13, 37, 9, 50)`
- `Cascade_Configuration_TXBF.lua:767` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 14, 14, 41, 10, 50)`
- `Cascade_Configuration_TXBF.lua:769` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 15, 15, 44, 12, 50)`
- `Cascade_Configuration_TXBF.lua:771` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 16, 16, 47, 13, 50)`
- `Cascade_Configuration_TXBF.lua:773` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 17, 17, 50, 15, 50)`
- `Cascade_Configuration_TXBF.lua:775` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 18, 18, 53, 17, 50)`
- `Cascade_Configuration_TXBF.lua:777` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 19, 19, 57, 18, 50)`
- `Cascade_Configuration_TXBF.lua:779` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 20, 20, 60, 20, 50)`
- `Cascade_Configuration_TXBF.lua:781` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 21, 21, 0, 22, 50)`
- `Cascade_Configuration_TXBF.lua:783` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 22, 22, 3, 23, 50)`
- `Cascade_Configuration_TXBF.lua:785` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 23, 23, 7, 25, 50)`
- `Cascade_Configuration_TXBF.lua:787` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 24, 24, 11, 27, 50)`
- `Cascade_Configuration_TXBF.lua:789` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 25, 25, 15, 29, 50)`
- `Cascade_Configuration_TXBF.lua:791` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 26, 26, 18, 31, 50)`
- `Cascade_Configuration_TXBF.lua:793` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 27, 27, 22, 32, 50)`
- `Cascade_Configuration_TXBF.lua:795` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 28, 28, 25, 35, 50)`
- `Cascade_Configuration_TXBF.lua:797` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 29, 29, 29, 36, 50)`
- `Cascade_Configuration_TXBF.lua:799` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 30, 30, 33, 38, 50)`
- `Cascade_Configuration_TXBF.lua:801` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 31, 31, 37, 40, 50)`
- `Cascade_Configuration_TXBF.lua:803` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 32, 32, 41, 42, 50)`
- `Cascade_Configuration_TXBF.lua:805` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 33, 33, 45, 44, 50)`
- `Cascade_Configuration_TXBF.lua:807` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 34, 34, 49, 46, 50)`
- `Cascade_Configuration_TXBF.lua:809` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 35, 35, 53, 48, 50)`
- `Cascade_Configuration_TXBF.lua:811` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 36, 36, 57, 51, 50)`
- `Cascade_Configuration_TXBF.lua:813` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 37, 37, 62, 53, 50)`
- `Cascade_Configuration_TXBF.lua:815` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 38, 38, 2, 55, 50)`
- `Cascade_Configuration_TXBF.lua:817` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 39, 39, 6, 57, 50)`
- `Cascade_Configuration_TXBF.lua:819` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 40, 40, 10, 59, 50)`
- `Cascade_Configuration_TXBF.lua:821` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 41, 41, 15, 61, 50)`
- `Cascade_Configuration_TXBF.lua:823` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 42, 42, 19, 63, 50)`
- `Cascade_Configuration_TXBF.lua:825` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 43, 43, 23, 1, 50)`
- `Cascade_Configuration_TXBF.lua:827` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 44, 44, 28, 4, 50)`
- `Cascade_Configuration_TXBF.lua:829` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 45, 45, 32, 6, 50)`
- `Cascade_Configuration_TXBF.lua:831` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 46, 46, 36, 8, 50)`
- `Cascade_Configuration_TXBF.lua:833` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 47, 47, 41, 10, 50)`
- `Cascade_Configuration_TXBF.lua:835` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 48, 48, 45, 12, 50)`
- `Cascade_Configuration_TXBF.lua:837` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 49, 49, 50, 15, 50)`
- `Cascade_Configuration_TXBF.lua:839` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 50, 50, 54, 17, 50)`
- `Cascade_Configuration_TXBF.lua:841` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 51, 51, 59, 19, 50)`
- `Cascade_Configuration_TXBF.lua:843` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 52, 52, 63, 21, 50)`
- `Cascade_Configuration_TXBF.lua:845` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 53, 53, 4, 24, 50)`
- `Cascade_Configuration_TXBF.lua:847` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 54, 54, 8, 26, 50)`
- `Cascade_Configuration_TXBF.lua:849` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 55, 55, 13, 28, 50)`
- `Cascade_Configuration_TXBF.lua:851` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 56, 56, 18, 30, 50)`
- `Cascade_Configuration_TXBF.lua:853` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 57, 57, 22, 33, 50)`
- `Cascade_Configuration_TXBF.lua:855` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 58, 58, 26, 35, 50)`
- `Cascade_Configuration_TXBF.lua:857` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 59, 59, 31, 37, 50)`
- `Cascade_Configuration_TXBF.lua:859` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 60, 60, 35, 40, 50)`
- `Cascade_Configuration_TXBF.lua:861` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 61, 61, 40, 42, 50)`
- `Cascade_Configuration_TXBF.lua:863` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 62, 62, 45, 44, 50)`
- `Cascade_Configuration_TXBF.lua:865` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 63, 63, 49, 46, 50)`
- `Cascade_Configuration_TXBF.lua:867` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 64, 64, 54, 49, 50)`
- `Cascade_Configuration_TXBF.lua:869` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 65, 65, 58, 51, 50)`
- `Cascade_Configuration_TXBF.lua:871` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 66, 66, 63, 53, 50)`
- `Cascade_Configuration_TXBF.lua:873` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 67, 67, 3, 55, 50)`
- `Cascade_Configuration_TXBF.lua:875` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 68, 68, 8, 57, 50)`
- `Cascade_Configuration_TXBF.lua:877` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 69, 69, 13, 60, 50)`
- `Cascade_Configuration_TXBF.lua:879` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 70, 70, 17, 62, 50)`
- `Cascade_Configuration_TXBF.lua:881` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 71, 71, 21, 0, 50)`
- `Cascade_Configuration_TXBF.lua:883` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 72, 72, 26, 3, 50)`
- `Cascade_Configuration_TXBF.lua:885` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 73, 73, 30, 5, 50)`
- `Cascade_Configuration_TXBF.lua:887` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 74, 74, 35, 7, 50)`
- `Cascade_Configuration_TXBF.lua:889` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 75, 75, 39, 9, 50)`
- `Cascade_Configuration_TXBF.lua:891` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 76, 76, 43, 11, 50)`
- `Cascade_Configuration_TXBF.lua:893` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 77, 77, 48, 13, 50)`
- `Cascade_Configuration_TXBF.lua:895` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 78, 78, 52, 16, 50)`
- `Cascade_Configuration_TXBF.lua:897` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 79, 79, 56, 18, 50)`
- `Cascade_Configuration_TXBF.lua:899` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 80, 80, 61, 20, 50)`
- `Cascade_Configuration_TXBF.lua:901` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 81, 81, 1, 22, 50)`
- `Cascade_Configuration_TXBF.lua:903` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 82, 82, 5, 24, 50)`
- `Cascade_Configuration_TXBF.lua:905` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 83, 83, 9, 26, 50)`
- `Cascade_Configuration_TXBF.lua:907` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 84, 84, 14, 28, 50)`
- `Cascade_Configuration_TXBF.lua:909` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 85, 85, 18, 30, 50)`
- `Cascade_Configuration_TXBF.lua:911` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 86, 86, 22, 32, 50)`
- `Cascade_Configuration_TXBF.lua:913` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 87, 87, 26, 35, 50)`
- `Cascade_Configuration_TXBF.lua:915` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 88, 88, 30, 37, 50)`
- `Cascade_Configuration_TXBF.lua:917` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 89, 89, 34, 39, 50)`
- `Cascade_Configuration_TXBF.lua:919` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 90, 90, 38, 41, 50)`
- `Cascade_Configuration_TXBF.lua:921` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 91, 91, 41, 42, 50)`
- `Cascade_Configuration_TXBF.lua:923` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 92, 92, 46, 44, 50)`
- `Cascade_Configuration_TXBF.lua:925` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 93, 93, 49, 46, 50)`
- `Cascade_Configuration_TXBF.lua:927` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 94, 94, 53, 48, 50)`
- `Cascade_Configuration_TXBF.lua:929` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 95, 95, 57, 50, 50)`
- `Cascade_Configuration_TXBF.lua:931` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 96, 96, 60, 52, 50)`
- `Cascade_Configuration_TXBF.lua:933` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 97, 97, 0, 54, 50)`
- `Cascade_Configuration_TXBF.lua:935` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 98, 98, 4, 56, 50)`
- `Cascade_Configuration_TXBF.lua:937` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 99, 99, 7, 57, 50)`
- `Cascade_Configuration_TXBF.lua:939` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 100, 100, 11, 59, 50)`
- `Cascade_Configuration_TXBF.lua:941` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 101, 101, 14, 61, 50)`
- `Cascade_Configuration_TXBF.lua:943` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 102, 102, 18, 62, 50)`
- `Cascade_Configuration_TXBF.lua:945` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 103, 103, 21, 0, 50)`
- `Cascade_Configuration_TXBF.lua:947` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 104, 104, 24, 2, 50)`
- `Cascade_Configuration_TXBF.lua:949` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 105, 105, 27, 3, 50)`
- `Cascade_Configuration_TXBF.lua:951` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 106, 106, 30, 5, 50)`
- `Cascade_Configuration_TXBF.lua:953` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 107, 107, 34, 6, 50)`
- `Cascade_Configuration_TXBF.lua:955` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 108, 108, 36, 8, 50)`
- `Cascade_Configuration_TXBF.lua:957` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 109, 109, 39, 9, 50)`
- `Cascade_Configuration_TXBF.lua:959` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 110, 110, 42, 11, 50)`
- `Cascade_Configuration_TXBF.lua:961` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 111, 111, 45, 12, 50)`
- `Cascade_Configuration_TXBF.lua:963` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 112, 112, 48, 14, 50)`
- `Cascade_Configuration_TXBF.lua:965` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 113, 113, 51, 15, 50)`
- `Cascade_Configuration_TXBF.lua:967` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 114, 114, 53, 16, 50)`
- `Cascade_Configuration_TXBF.lua:969` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 115, 115, 56, 18, 50)`
- `Cascade_Configuration_TXBF.lua:971` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 116, 116, 58, 19, 50)`
- `Cascade_Configuration_TXBF.lua:973` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 117, 117, 61, 20, 50)`
- `Cascade_Configuration_TXBF.lua:975` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 118, 118, 63, 21, 50)`
- `Cascade_Configuration_TXBF.lua:977` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 119, 119, 2, 23, 50)`
- `Cascade_Configuration_TXBF.lua:979` : `ar1.SetPerChirpPhaseShifterConfig_mult(8, 120, 120, 4, 24, 50)`

## DisableTestSource_mult
- `Cascade_Configuration_TXBF.lua:245` : `ar1.DisableTestSource_mult(1,0)`
- `Cascade_Configuration_TXBF.lua:490` : `ar1.DisableTestSource_mult(2,0)`
- `Cascade_Configuration_TXBF.lua:735` : `ar1.DisableTestSource_mult(4,0)`
- `Cascade_Configuration_TXBF.lua:980` : `ar1.DisableTestSource_mult(8,0)`

## AdvanceFrameConfig_mult
- `Cascade_Configuration_TXBF.lua:246` : `ar1.AdvanceFrameConfig_mult(1, 1, 1536, 0, 0, 121, 16, 34848001, 1, 1, 1, 34848001, 0, 0, 121, 16, 34848001,1, 1, 1, 34848001, 0, 0, 1, 128, 8000000, 0, 1, 1, 8000000, 0, 0, 1,128, 8000000, 0, 1, 1, 8000000, 8, 1, 0, 1, 1936, 512, 1, 1936, 1, 1,128, 1, 1, 128, 1, 1)`
- `Cascade_Configuration_TXBF.lua:491` : `ar1.AdvanceFrameConfig_mult(2, 1, 1536, 0, 0, 121, 16, 34848001, 1, 1, 1, 34848001, 0, 0, 121, 16, 34848001,1, 1, 1, 34848001, 0, 0, 1, 128, 8000000, 0, 1, 1, 8000000, 0, 0, 1,128, 8000000, 0, 1, 1, 8000000, 8, 2, 0, 1, 1936, 512, 1, 1936, 1, 1,128, 1, 1, 128, 1, 1)`
- `Cascade_Configuration_TXBF.lua:736` : `ar1.AdvanceFrameConfig_mult(4, 1, 1536, 0, 0, 121, 16, 34848001, 1, 1, 1, 34848001, 0, 0, 121, 16, 34848001,1, 1, 1, 34848001, 0, 0, 1, 128, 8000000, 0, 1, 1, 8000000, 0, 0, 1,128, 8000000, 0, 1, 1, 8000000, 8, 2, 0, 1, 1936, 512, 1, 1936, 1, 1,128, 1, 1, 128, 1, 1)`
- `Cascade_Configuration_TXBF.lua:981` : `ar1.AdvanceFrameConfig_mult(8, 1, 1536, 0, 0, 121, 16, 34848001, 1, 1, 1, 34848001, 0, 0, 121, 16, 34848001,1, 1, 1, 34848001, 0, 0, 1, 128, 8000000, 0, 1, 1, 8000000, 0, 0, 1,128, 8000000, 0, 1, 1, 8000000, 8, 2, 0, 1, 1936, 512, 1, 1936, 1, 1,128, 1, 1, 128, 1, 1)`

## SetRfAnaMonConfig_mult
- `Cascade_Configuration_TXBF_AngleSweep.lua:530` : `ar1.SetRfAnaMonConfig_mult(15, 0x9, 0x0)`
- `Cascade_Monitoring_Example.lua:94` : `ar1.SetRfAnaMonConfig_mult(device_map, 0x4F07FFF, 0x0)`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:816` : `ar1.SetRfAnaMonConfig_mult(15, 0x9, 0x0)`

## SetRfTempMonConfig_mult
- `Cascade_Configuration_TXBF_AngleSweep.lua:531` : `ar1.SetRfTempMonConfig_mult(15, 2, 0, 0, 0, 0, 0)`
- `Cascade_Monitoring_Example.lua:99` : `ar1.SetRfTempMonConfig_mult(device_map, 0, -40, 135, -40, 135, 30)`
- `Cascade_Phase_Shifter_Calibration_AWRx.lua:817` : `ar1.SetRfTempMonConfig_mult(15, 2, 0, 0, 0, 0, 0)`

## FileDownloadModeFor2243
- `Cascade_Flashing_example.lua:78` : `ar1.FileDownloadModeFor2243(1,0)`
- `Cascade_Flashing_example.lua:106` : `ar1.FileDownloadModeFor2243(0,1)`
- `Cascade_Flashing_example.lua:149` : `ar1.FileDownloadModeFor2243(1,0)`
- `Cascade_Flashing_example.lua:179` : `ar1.FileDownloadModeFor2243(0,1)`
- `Cascade_Flashing_example.lua:222` : `ar1.FileDownloadModeFor2243(0,1)`

## DisableMonitoringLogging
- `Cascade_Monitoring_Example.lua:70` : `ar1.DisableMonitoringLogging(1)`

## SetCalMonTimeUnitConfig_mult
- `Cascade_Monitoring_Example.lua:74` : `The API is of the format ar1.SetCalMonTimeUnitConfig_mult(device_map, cal_mon_unit, num_devices, device_id, monitor_mode)`
- `Cascade_Monitoring_Example.lua:84` : `ar1.SetCalMonTimeUnitConfig_mult(1, cal_mon_unit, num_devices, 0, 0)`
- `Cascade_Monitoring_Example.lua:85` : `ar1.SetCalMonTimeUnitConfig_mult(2, cal_mon_unit, num_devices, 1, 0)`
- `Cascade_Monitoring_Example.lua:86` : `ar1.SetCalMonTimeUnitConfig_mult(4, cal_mon_unit, num_devices, 2, 0)`
- `Cascade_Monitoring_Example.lua:87` : `ar1.SetCalMonTimeUnitConfig_mult(8, cal_mon_unit, num_devices, 3, 0)`

## SetRfRxGainPhMonConfig_mult
- `Cascade_Monitoring_Example.lua:102` : `ar1.SetRfRxGainPhMonConfig_mult(device_map, 0, 1, 1, 1 , 0, 0, 50, 50, 50, 100, 0,`

## SetRfRxNoiseMonConfig_mult
- `Cascade_Monitoring_Example.lua:106` : `ar1.SetRfRxNoiseMonConfig_mult(device_map, 0, 1, 1, 1, 0, 30)`

## SetRfRxIfStageMonConfig_mult
- `Cascade_Monitoring_Example.lua:109` : `ar1.SetRfRxIfStageMonConfig_mult(device_map, 0, 0, 20, 2.7, 3, 3)`

## SetRfTx0PowMonConfig_mult
- `Cascade_Monitoring_Example.lua:112` : `ar1.SetRfTx0PowMonConfig_mult(device_map, 0, 1, 1, 1, 0, 3, 3)`

## SetRfTx1PowMonConfig_mult
- `Cascade_Monitoring_Example.lua:113` : `ar1.SetRfTx1PowMonConfig_mult(device_map, 0, 1, 1, 1, 0, 3, 3)`

## SetRfTx2PowMonConfig_mult
- `Cascade_Monitoring_Example.lua:114` : `ar1.SetRfTx2PowMonConfig_mult(device_map, 0, 1, 1, 1, 0, 3, 3)`

## SetRfTx0BallbreakMonConfig_mult
- `Cascade_Monitoring_Example.lua:117` : `ar1.SetRfTx0BallbreakMonConfig_mult(device_map, 0, -6)`

## SetRfTx1BallbreakMonConfig_mult
- `Cascade_Monitoring_Example.lua:118` : `ar1.SetRfTx1BallbreakMonConfig_mult(device_map, 0, -6)`

## SetRfTx2BallbreakMonConfig_mult
- `Cascade_Monitoring_Example.lua:119` : `ar1.SetRfTx2BallbreakMonConfig_mult(device_map, 0, -6)`

## SetRfTx0PhShiftMonConfig_mult
- `Cascade_Monitoring_Example.lua:122` : `ar1.SetRfTx0PhShiftMonConfig_mult(device_map, 0, 0, 7, 3, 7, 0, 5.625, 11.25, 16.875, 0, 0, 0, 0, 10, 2)`

## SetRfTx1PhShiftMonConfig_mult
- `Cascade_Monitoring_Example.lua:123` : `ar1.SetRfTx1PhShiftMonConfig_mult(device_map, 0, 0, 7, 3, 7, 0, 5.625, 11.25, 16.875, 0, 0, 0, 0, 10, 2)`

## SetRfTx2PhShiftMonConfig_mult
- `Cascade_Monitoring_Example.lua:124` : `ar1.SetRfTx2PhShiftMonConfig_mult(device_map, 0, 0, 7, 3, 7, 0, 5.625, 11.25, 16.875, 0, 0, 0, 0, 10, 2)`

## SetRfTxGainPhaseMismatchMonConfig_mult
- `Cascade_Monitoring_Example.lua:127` : `ar1.SetRfTxGainPhaseMismatchMonConfig_mult(device_map, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0,`

## SetRfSynthFreqMonConfig_mult
- `Cascade_Monitoring_Example.lua:131` : `ar1.SetRfSynthFreqMonConfig_mult(device_map, 0, 0, 4000, 25, 0, 0, 1)`

## SetRfMixerInpPowMonConfig_mult
- `Cascade_Monitoring_Example.lua:134` : `ar1.SetRfMixerInpPowMonConfig_mult(device_map, 0, 0, 1, 1, 0, 115212288)`

## SetRfPmClkLoIntAnaSignalsMonConfig_mult
- `Cascade_Monitoring_Example.lua:139` : `ar1.SetRfPmClkLoIntAnaSignalsMonConfig_mult(device_map, 0, 0)`

## SetRfGpadcIntAnaSignalsMonConfig_mult
- `Cascade_Monitoring_Example.lua:142` : `ar1.SetRfGpadcIntAnaSignalsMonConfig_mult(device_map, 0)`

## SetRfPllContrlVoltMonConfig_mult
- `Cascade_Monitoring_Example.lua:145` : `ar1.SetRfPllContrlVoltMonConfig_mult(device_map, 0, 1, 1, 1)`

## SetRfDualClkCompMonConfig_mult
- `Cascade_Monitoring_Example.lua:148` : `ar1.SetRfDualClkCompMonConfig_mult(device_map, 0, 1, 1, 1, 1, 1, 1)`
