# mmWave Studio Backend Architecture

## Design Principles

1. **Python/Jupyter is the control layer and source of truth.**
   All experiment configuration, state, and orchestration lives in Python.

2. **mmWave Studio is the execution backend.**
   mmWave Studio remains open and owns the radar RS232/SPI communication.
   The GUI may remain open for visibility/logging, but the user should not
   manually fill tabs as part of the normal workflow.

3. **Python automatically sends Lua/ar1 commands into mmWave Studio.**
   The normal workflow is:
   ```
   Python command → auto-execute Lua → result JSON → Python reads status
   ```
   Manual `dofile` paste was proof-of-concept only and is no longer the default.

4. **Python must never directly open the AWR radar RS232 port**
   while mmWave Studio owns it. All radar communication goes through
   the ar1 API inside the mmWave Studio Lua environment.

## Execution Transports

The executor sends Lua commands to mmWave Studio. It is **transport only** —
it does not bypass stage safety whitelists.

### 1. RSTD .NET Remoting (TCP:2777) — Primary

- mmWave Studio's `Startup.lua` calls `RSTD.NetStart()`, opening TCP port 2777.
- Python uses `pythonnet` to load `RtttNetClientAPI.dll` and calls
  `RtttNetClient.SendCommand(dofile(...))`.
- **SendCommand return code (30000) only means the command was submitted.**
  The result JSON is the source of truth for stage success.

### 2. pywinauto UI Lua Shell — Fallback

- Connects to the running mmWave Studio process.
- Pastes `dofile([[path]])` into the Lua Shell and presses Enter.
- **Allowed:** Focus window, reach Lua Shell, paste dofile.
- **Forbidden:** Clicking config buttons, editing RF fields, triggering capture.

### 3. Manual dofile — Debug Only

- Prints the `dofile([[...]])` command for the user to paste manually.
- **Only used when explicitly requested** (`--manual` flag).
- `--execute` will ERROR if no automatic transport is available — it will
  **never** silently fall back to manual mode.

### Installing Automation Dependencies

```bash
python -m pip install -e ".[automation]"
```

This installs `pythonnet>=3.0` and `pywinauto>=0.6` as optional dependencies.

## Stage Pipeline

Each stage has a whitelist of allowed ar1 calls and a safety flag (`allowed_yet`):

| Stage | Allowed Calls | Enabled |
|-------|--------------|---------|
| Connection-Only | SOPControl, Connect, IsConnected, Disconnect | ✓ |
| Firmware Loading | DownloadBSSFw, DownloadMSSFw | ✗ |
| Device Boot / Power-On | PowerOn | ✗ |
| RF Enable/Init | RfEnable, RfInit | ✗ |
| Static ADC/LVDS Config | ChanNAdcConfig, LPModConfig, DataPathConfig, LvdsClkConfig, LVDSLaneConfig | ✗ |
| Profile/Chirp/Frame | ProfileConfig, ChirpConfig, FrameConfig, AdvanceFrameConfig | ✗ |
| DCA1000 Setup | SelectCaptureDevice, CaptureCardConfig_* | ✗ |
| Capture Trigger | CaptureCardConfig_StartRecord, StartFrame | ✗ |
| Post-Processing | StartMatlabPostProc | ✗ |

## Manifest / Result Pattern

Every generated script uses:
- `{stage}_manifest.json` — written by Python with `run_id`
- `{stage}_result.json` — written by Lua with matching `run_id`

Status check logic:
- **NOT RUN**: result file missing
- **STALE RESULT**: `run_id` mismatch (script was regenerated since last run)
- **SUCCESS**: result present, `run_id` matches, no error
- **ERROR**: result present, `run_id` matches, error reported
- **TIMEOUT**: automatic execution submitted but no result JSON appeared

## Smoke Test

Before using hardware, verify the execution path works:

```bash
awr mmws smoke --execute
```

This generates a harmless Lua script with **no ar1 hardware calls**. It only:
- Calls `WriteToLog` via `pcall`
- Writes `smoke_result.json`

This proves: Python → mmWave Studio → Lua → JSON → Python works automatically.

## Future Bridge Design

Planned persistent bridge modes (not yet implemented):

| Mode | Description |
|------|-------------|
| `FILE_QUEUE` | Python writes commands to watched directory; Lua bridge in Studio polls |
| `MMWS_LIVE_LUA` | Persistent Lua polling loop reads inbox, executes, writes outbox |
