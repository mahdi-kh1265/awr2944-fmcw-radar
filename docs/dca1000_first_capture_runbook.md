# DCA1000 First Capture Runbook

Use this runbook for the first DCA1000 capture attempt after Guided Runner v1 validation has
completed successfully. This is an operator procedure, not an implementation note.

Do not start this procedure while another tool is changing mmWave Studio connection state,
AWR firmware/config state, or DCA1000 network setup.

## Prerequisites

Confirm every item before starting.

| Item | Expected state | Checked |
| --- | --- | --- |
| Guided Runner v1 validation | Completed successfully | [ ] |
| AWR firmware/config | Validated by the guided run | [ ] |
| DCA1000 | Powered | [ ] |
| Ethernet | PC connected to DCA1000 capture Ethernet | [ ] |
| PC static IP | `192.168.33.30/24` on the DCA1000 network adapter | [ ] |
| DCA1000 IP | Expected at `192.168.33.180` | [ ] |
| mmWave Studio | Open and connected to AWR | [ ] |
| PostProc directory | `C:\ti\mmwave_studio\PostProc` exists | [ ] |
| Old capture files | Old `adc_data*.bin` files manually moved or deleted before capture | [ ] |

If any prerequisite is not true, stop and fix that item before generating setup or capture Lua.

## Safety Split

The first capture path is split into three phases. Treat each phase differently.

### A. `awr dca preflight`

Read-only. This checks local assumptions and expected paths/network settings. It should not change
AWR RF state, DCA1000 state, or mmWave Studio state.

### B. `awr dca generate-setup`

DCA setup, no RF. This generates Lua for DCA1000 setup such as Ethernet/recording preparation. It
should not transmit RF and should not call `StartFrame`.

### C. `awr dca generate-capture --confirm-startframe`

RF-transmitting capture trigger. This phase intentionally generates the capture trigger path.

**STARTFRAME WARNING**

**Do not run generated capture Lua unless the lab area is ready for RF transmission, the operator
has confirmed the intended target scene, and old capture files have already been moved or deleted.**

**`StartFrame` is the point where the sensor capture is triggered. Review the generated Lua before
pasting the `dofile(...)` command into the mmWave Studio Lua shell.**

## Command Sequence

Run these commands from the repository root that contains the new DCA CLI.

### 1. Preflight

```powershell
awr dca preflight
```

Expected result:

- PC/DCA network assumptions are reported.
- `C:\ti\mmwave_studio\PostProc` is present.
- No RF or DCA setup action is performed.

Stop if preflight reports a missing static IP, missing PostProc path, or unreachable DCA1000.

### 2. Generate and run DCA setup Lua

```powershell
awr dca generate-setup --probe-dir ti/probe_logs
```

Then:

1. Read the generated Lua path and run ID from command output.
2. Inspect the generated Lua. Confirm it is setup-only and does not call `StartFrame`.
3. Paste the printed `dofile(...)` command into the mmWave Studio Lua shell.
4. Check the run result:

```powershell
awr mmws post check-run --run-id <dca_setup_run_id>
```

Expected result:

- DCA setup run result reports success.
- No `adc_data*.bin` file is expected yet.

### 3. Generate and run capture trigger Lua

```powershell
awr dca generate-capture --probe-dir ti/probe_logs --output-dir C:\ti\mmwave_studio\PostProc --confirm-startframe
```

Then:

1. Inspect the generated Lua before running it.
2. Confirm old `adc_data*.bin` files are not present in `C:\ti\mmwave_studio\PostProc`.
3. Confirm the lab is ready for RF transmission.
4. Paste the printed `dofile(...)` command into the mmWave Studio Lua shell.
5. Check the run result:

```powershell
awr mmws post check-run --run-id <capture_run_id>
```

Expected result:

- Capture trigger run result reports success.
- `adc_data_Raw_0.bin` appears in `C:\ti\mmwave_studio\PostProc`.
- `adc_data.bin` appears after post-processing.

### 4. Check capture size

```powershell
awr dca check-capture --capture-dir C:\ti\mmwave_studio\PostProc --expected-bytes 524288
```

Expected result:

- `adc_data.bin` exists.
- `adc_data.bin` size is exactly `524288` bytes.
- The check result is recorded in the evidence checklist.

## Expected File Sizes

The expected post-processed file is:

```text
adc_data.bin = 524,288 bytes
```

This is based on:

```text
256 samples x 1 RX x 8 chirps/frame x 128 frames x 2 bytes/sample = 524,288 bytes
```

`adc_data_Raw_0.bin` may be larger than `adc_data.bin`. Do not exact-size check the raw file. For
first capture evidence, record whether `adc_data_Raw_0.bin` exists and record its observed size.

## Evidence Checklist

Use `docs/dca1000_capture_evidence_template.md` during the attempt. Keep one filled copy per
capture attempt.

| Field | Value |
| --- | --- |
| Timestamp |  |
| Operator |  |
| AWR validation run ID |  |
| DCA setup run ID |  |
| Capture trigger run ID |  |
| Preflight result |  |
| Setup result |  |
| Capture result |  |
| `adc_data_Raw_0.bin` exists/size |  |
| `adc_data.bin` exists/size |  |
| `check-capture` result |  |
| Screenshot/photo evidence needed |  |
| Notes |  |

Recommended screenshots/photos:

- mmWave Studio connection state before DCA setup.
- DCA setup Lua result in the Lua shell or run result file.
- Capture trigger Lua result in the Lua shell or run result file.
- `C:\ti\mmwave_studio\PostProc` showing `adc_data_Raw_0.bin` and `adc_data.bin` with timestamps.
- `check-capture` terminal output.

## Failure Matrix

Use the detailed matrix in `docs/dca1000_troubleshooting_matrix.md`. The short operator view is:

| Symptom | Likely cause | What to check | Safe next action | Power-cycle? |
| --- | --- | --- | --- | --- |
| DCA ping fails | DCA unpowered, wrong adapter, wrong subnet, cable issue | DCA power LEDs, Ethernet link, PC IP `192.168.33.30/24`, ping `192.168.33.180` | Fix network/power, rerun preflight only | DCA: maybe. AWR/mmWave Studio: no |
| PC missing `192.168.33.30` | Static IP not configured on DCA adapter | Windows adapter IPv4 settings and route table | Set static IP, rerun preflight | No |
| Setup `EthInit` fails | DCA network path or stale DCA state | DCA IP, firewall, one active DCA adapter, previous record state | Stop, fix network, rerun setup | DCA: maybe. AWR: no |
| `StartRecord` fails | DCA not initialized or output path problem | Setup success, PostProc exists, old files removed | Rerun setup after cleanup | DCA: maybe. AWR: no |
| `StartFrame` fails | AWR not armed/configured or mmWave Studio state changed | Guided validation, Studio connection, generated Lua run ID | Do not retry blindly. Revalidate AWR state | AWR/Studio: maybe |
| No `adc_data_Raw_0.bin` | Recording never started or trigger never reached DCA | Setup/capture result, DCA LEDs, PostProc timestamps | Preserve logs, rerun setup before capture | DCA: maybe |
| Raw exists but `adc_data.bin` missing | PostProc did not run or failed | PostProc logs, MATLAB/post process output, raw file timestamp | Preserve raw, rerun post-processing if safe | No |
| `adc_data.bin` wrong size | Wrong capture config, stale file, partial capture | File timestamp, expected bytes, generated config run ID | Move files aside, rerun from preflight | Maybe after repeated failure |
| File all zeros | No useful ADC data, RF/config/trigger issue | File contents, target scene, AWR config, trigger timing | Preserve file, rerun guided validation before another capture | AWR/Studio: maybe |
| Stale old capture suspected | Old `adc_data*.bin` was not removed | File timestamps before/after capture | Move/delete old files, rerun capture sequence | No |

## Evidence Preservation

After any failure or validation attempt, preserve probe logs before rerunning workflows that may
overwrite evidence. From the sidequest/tooling workspace, collect and report the main repo logs:

```powershell
python tools/collect_probe_artifacts.py --probe-dir C:\Users\khams008\Documents\awr2944-fmcw-radar\exp_lau_probe\ti\probe_logs --out artifacts\dca_attempt_bundle.zip
```

```powershell
python tools/report_probe_bundle.py --bundle artifacts\dca_attempt_bundle.zip --out artifacts\dca_attempt_report.md
```

Raw ADC `.bin` files are not included by default. Handle `adc_data_Raw_0.bin` and `adc_data.bin`
separately according to lab data handling rules. At minimum, record their full paths, sizes,
timestamps, and hashes if they need to be shared.

## Stop Conditions

Stop the attempt and preserve evidence if:

- The generated capture Lua contains unexpected commands.
- `StartFrame` fails.
- DCA setup succeeds but no raw file appears after capture.
- `adc_data.bin` exists but the size is not `524288` bytes.
- Any operator is unsure whether the current files are stale or newly captured.