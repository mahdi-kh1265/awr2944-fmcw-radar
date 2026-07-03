# mmWave Studio Backend Architecture

## Design Principles

1. **Python/Jupyter is the control layer and source of truth.**
   All experiment configuration, state, and orchestration lives in Python.

2. **mmWave Studio is the execution backend.**
   mmWave Studio remains open and owns the radar RS232/SPI communication.
   The GUI may remain open for visibility/logging, but the user should not
   manually fill tabs as part of the normal workflow.

3. **Python controls mmWave Studio through Lua/ar1 scripts.**
   Python generates Lua scripts → user (or future bridge) runs them in
   mmWave Studio → Lua writes result JSON → Python reads status.

4. **Python must never directly open the AWR radar RS232 port**
   while mmWave Studio owns it. All radar communication goes through
   the ar1 API inside the mmWave Studio Lua Shell.

## Bridge Modes

The bridge connects Python commands to mmWave Studio execution.

### `manual_one_shot` (current)

1. Python generates a stage-specific Lua script
2. Python writes a manifest JSON with a `run_id` (UUID)
3. User copies `dofile([[path]])` into mmWave Studio Lua Shell
4. Lua executes the ar1 calls and writes a result JSON with the matching `run_id`
5. Python reads the result and reports status

### Future modes (not yet implemented)

| Mode | Description |
|------|-------------|
| `FILE_QUEUE` | Python writes Lua scripts to a watched directory; mmWave Studio polls and executes |
| `NAMED_PIPE` | IPC pipe between Python and a mmWave Studio Lua polling loop |
| `MMWS_LIVE_LUA` | Direct Lua injection via mmWave Studio's automation interface |

**Note:** None of these modes involve Python directly opening the AWR radar COM port.

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

## Safety Model

Generated Lua scripts are statically validated before being written to disk.
Every script is scanned against the stage's forbidden-call list. If any
forbidden ar1 call is found, the script is rejected with a `RuntimeError`.
