# AWR2944 Direct Capture (Phase I) - End to End Guide

This guide describes the hardened production flow for capturing raw radar data from the Texas Instruments AWR2944 and DCA1000 EVM using direct Python-based UART and UDP commands, completely bypassing mmWave Studio.

## Prerequisites

1. **Hardware Power/SOP State**: 
   - AWR2944 EVM must be powered on (5V/3A) with SOP2 jumper closed (Flashing mode) if you are flashing, or SOP jumpers open for functional mode.
   - DCA1000 EVM must be powered on (5V/3A). Switch SW2 must have position 5 in SW_CONFIG.
2. **Network Configuration**:
   - Host PC must be statically assigned to `192.168.33.30` (Subnet: `255.255.255.0`).
   - The DCA1000 EVM responds at `192.168.33.180`.
3. **UART Ports**:
   - The AWR2944 exposes two COM ports. Use the Application/User UART (often `COM8` or similar) configured to `115200` baud.

## One-Command Capture

You can use the new Command Line Interface to run an end-to-end capture easily:

```bash
python -m awr2944_dca.capture_cli smoke_v1 --frames 9 --guard-frames 1 --launch-viewer
```

Or from a Jupyter Notebook (e.g. `01_capture.ipynb`):

```python
from awr2944_dca.lab import RadarProject

lab = RadarProject.open_here()
result = lab.capture.run_smoke(frames=9, guard_frames=1)
result.summary()
result.open_viewer()
```

## Guard-Frame Extraction & DSP

The DCA1000 capture can sometimes include partial or garbage data at the very end of the transmission due to timing. To prevent analyzing corrupt data:

- **Native Capture**: The raw capture will collect 9 full frames over the physical LVDS lanes. 
  *Expected Native Bytes:* 4,718,592 bytes (includes DCA1000 2-lane to 4-slot storage expansion).
  *Logical Depadded Bytes:* 2,359,296 bytes (9 frames * 128 chirps * 4 RX * 256 samples * 2 bytes/sample for real int16).
- **Canonical Extraction**: The script automatically drops the last N guard frames (default 1) and saves `adc_data_canonical.bin` containing exactly 8 perfectly received physical frames.
  *Expected Canonical Native Bytes:* 4,194,304 bytes.
  *Canonical Logical Bytes:* 2,097,152 bytes.
  *Canonical Shape:* `[8, 128, 4, 256]` (Real int16 format)

The automated DSP pipeline exclusively parses `adc_data_canonical.bin` to ensure the final payload is completely clean.

## MATLAB Viewer Launch

Once the Python DSP completes, it saves a `viewer_payload.mat` file containing the range/doppler axes, the raw ADC cube, and necessary configuration parameters. 

You can launch the MATLAB UI simply via:
```python
result.open_viewer()
```

This will run `matlab/viewer/dcaViewerMain.m` without requiring the RSTD or mmWave Studio environments.

## Troubleshooting

1. **UDP Bind Error (Port 4098)**: Check if an old Python instance or `DCA1000EVM_CLI_Record.exe` is stuck running in the background. Use `Get-NetUDPEndpoint` to find the owning PID and kill it.
2. **Timeout Error**: Check Ethernet physical connection and ensure the host adapter is strictly `192.168.33.30`.
3. **Radar Rejected Config**: Check if you are in the correct SOP mode and if the radar is already running. Ensure a `sensorStop` is sent before configuring.
