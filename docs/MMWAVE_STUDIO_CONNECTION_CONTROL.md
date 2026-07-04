# mmWave Studio Connection Control

## Overview

This document describes the workflow for establishing an RS232 connection
to the AWR2944EVM through mmWave Studio.

**Normal workflow:** Python generates and automatically executes Lua scripts
in mmWave Studio. Manual dofile paste is debug-only.

## Quick Start

### 1. Install automation dependencies

```bash
python -m pip install -e ".[automation]"
```

### 2. Verify mmWave Studio is reachable

```bash
awr mmws studio status
awr mmws inspect-execution
```

These commands do NOT require an experiment context.

### 3. Run smoke test

```bash
awr mmws smoke --execute
```

Proves Python → mmWave Studio → Lua → JSON → Python works. No hardware calls.

### 4. Discover and save COM port

```bash
awr ports scan
awr ports resolve --role awr-rs232
awr ports save --role awr-rs232 --com COM6
```

### 5. Connect

```bash
awr mmws connection script --com COM6 --execute
```

With `--execute`:
1. Generates connection Lua script
2. Auto-executes in mmWave Studio via RSTD .NET Remoting
3. Waits for `connection_result.json`
4. Prints connection status

### 6. Check status (if needed)

```bash
awr mmws connection status
```

## Execution Modes

| Flag | Behavior |
|------|----------|
| `--execute` | Auto-run via RSTD or pywinauto. **ERRORS** if no transport available. |
| `--manual` | Print dofile command only (debug fallback). |
| (neither) | Generate script, print instructions. |

**`--execute` never silently falls back to manual.** If no automatic transport
works, it returns ERROR with install/help instructions.

## Studio Management (no experiment needed)

```bash
awr mmws studio launch     # Start mmWave Studio
awr mmws studio attach     # Check if Python can reach Studio
awr mmws studio status     # Process + RSTD port status table
awr mmws inspect-execution # Discover available transports
```

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

The executor is **transport only** — it does not bypass stage whitelists.
RSTD `SendCommand` return code only means the command was submitted.
The result JSON is the source of truth for stage success.
