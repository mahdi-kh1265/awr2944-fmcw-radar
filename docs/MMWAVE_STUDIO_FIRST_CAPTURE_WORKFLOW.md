# mmWave Studio First Capture Workflow

## Overview
While the `ar1` API contains hundreds of functions, a standard offline data capture requires only a small, specific sequence of them. 
This document maps out that exact sequence, extracting it statically from `DataCaptureDemo_xWR.lua`.

**No hardware commands are executed to generate this map.**

## The Pipeline

The workflow must proceed in these stages:

1. **Connection-Only**: `SOPControl`, `Connect`. This establishes RS232/SPI.
2. **Firmware Loading**: `DownloadBSSFw` and `DownloadMSSFw`.
3. **Device Boot / Power-On**: `PowerOn`. This powers the RF subsystem.
4. **RF Enable/Init**: `RfEnable` and `RfInit`.
5. **Static ADC/LVDS Config**: `ChanNAdcConfig`, `LPModConfig`, `DataPathConfig`, `LvdsClkConfig`, `LVDSLaneConfig`.
6. **Profile/Chirp/Frame Config**: `ProfileConfig`, `ChirpConfig`, `FrameConfig` (or `AdvanceFrameConfig`).
7. **DCA1000 Setup**: `SelectCaptureDevice`, `CaptureCardConfig_EthInit`, `CaptureCardConfig_Mode`, `CaptureCardConfig_PacketDelay`.
8. **Capture Trigger**: `CaptureCardConfig_StartRecord`, `StartFrame`.
9. **Post-Processing**: `StartMatlabPostProc`.

## Backend Mapping

Our `capture.yaml` files drive these APIs. 
For example, `adc_format`, `adc_bits`, and `rx_antennas` from the YAML strictly control the arguments for `ChanNAdcConfig` and `DataPathConfig`.

To view the current static map:
```bash
awr ti workflow-map
```
This generates:
- `ti/probe_logs/first_capture_workflow_map.md`
- `ti/probe_logs/first_capture_workflow_map.json`

## Next Steps
The next runnable milestone for the backend will be implementing the **Connection-Only** stage locally (without RF or capture trigger).
