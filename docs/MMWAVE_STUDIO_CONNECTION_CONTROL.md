# mmWave Studio Connection Control

## Overview

This document describes the full workflow for establishing an RS232 connection
to the AWR2944EVM through mmWave Studio's Lua Shell.

## Workflow

### 1. Discover COM Ports

```bash
awr ports scan
```

COM numbers vary between PCs. The scanner classifies ports by role:
- `awr-rs232`: The Application/User UART port (high confidence)
- `ti-debug-uart`: XDS110 debug ports
- `possible_ftdi`: FTDI-based ports (could be DCA1000 or DevPack)
- `capture_control`: DCA1000 or DevPack control ports

### 2. Resolve the RS232 Port

```bash
awr ports resolve --role awr-rs232
```

This ranks candidates by confidence. It does not silently save — you must
explicitly confirm your choice.

### 3. Save Your Choice

```bash
awr ports save --role awr-rs232 --com COM6
```

This writes `local_hardware.yaml` in your experiment root. The file is
machine-specific and gitignored.

### 4. Review the Connection Plan

```bash
awr mmws connection plan
```

Shows the ar1 calls that will be generated (SOPControl, Connect, IsConnected).

### 5. Generate the Connection Script

```bash
awr mmws connection script
```

Or with explicit COM:
```bash
awr mmws connection script --com COM6 --baud 921600
```

This generates `ti/probe_logs/connection_only.lua` and a manifest JSON.

### 6. Execute in mmWave Studio

```bash
awr ti lua-command ti/probe_logs/connection_only.lua --copy
```

Paste the `dofile([[...]])` command into the mmWave Studio Lua Shell.

### 7. Check Status

```bash
awr mmws connection status
```

Reports: `NOT RUN`, `STALE RESULT`, `SUCCESS`, or `ERROR`.

## COM Port Normalization

- Stored/displayed as `COM6`
- Passed to `ar1.Connect` as numeric `6`: `ar1.Connect(6, 921600, 1000)`

## Safety Guarantees

The generated script contains **only**:
- `ar1.SOPControl(2)`
- `ar1.Connect(com_num, baud, timeout_ms)`
- `ar1.IsConnected()` (optional)
- `WriteToLog` via `pcall`
- `io.open` for JSON output

It does **not** contain firmware loading, PowerOn, RF init, static config,
DCA setup, capture trigger, or post-processing calls.
