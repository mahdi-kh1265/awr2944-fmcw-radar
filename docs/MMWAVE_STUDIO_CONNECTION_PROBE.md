# mmWave Studio Connection Probe Workflow

This document outlines the workflow for discovering the correct COM port and generating a safe, connection-only probe script for mmWave Studio.

## 1. COM Port Discovery

COM numbers vary between PCs. The mmWave Studio RS232 connection typically uses the "Application/User UART" port.
We provide a scanner that ranks candidates based on hardware identifiers and names.

1. **Scan for ports**:
   ```bash
   awr ports scan
   ```
   This will list all Windows COM ports, classifying them (e.g., `awr-rs232`, `ti-debug-uart`, `possible_ftdi`).

2. **Resolve the RS232 port**:
   ```bash
   awr ports resolve --role awr-rs232
   ```
   This ranks candidates based on confidence. You must manually review the recommendation.

3. **Save your choice**:
   ```bash
   awr ports save --role awr-rs232 --com COM8
   ```
   This saves the setting to `local_hardware.yaml` in your experiment folder. This file is machine-local and ignored by Git.

## 2. Connection-Only Probe

Once the COM port is saved, generate the connection probe script.

1. **Generate the script**:
   ```bash
   awr ti connection-probe
   ```
   This reads `local_hardware.yaml` and creates `ti/probe_logs/connection_probe.lua`.

2. **Execute in mmWave Studio**:
   Copy the run command to your clipboard:
   ```bash
   awr ti lua-command ti/probe_logs/connection_probe.lua --copy
   ```
   Paste the output (`dofile([[...]])`) into the mmWave Studio Lua Shell.

3. **Check the Status**:
   ```bash
   awr ti connection-status
   ```
   This will report `SUCCESS` if `ar1.Connect` returns `0`, or `ERROR` if it fails. It also protects against stale results if the run IDs don't match.

## Safety Guarantees
The generated `connection_probe.lua` is strictly limited to:
- `ar1.SOPControl`
- `ar1.Connect`
- `ar1.IsConnected`

It **does not** contain commands for firmware loading, device power-on, RF initialization, static config, DCA setup, or frame triggering.
