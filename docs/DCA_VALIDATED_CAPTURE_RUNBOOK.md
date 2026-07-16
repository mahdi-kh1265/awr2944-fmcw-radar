# DCA1000 Validated Capture Runbook

**Status: HARDWARE VALIDATED** on 2026-07-09

## Validated Capture Configuration

| Field | Value |
|-------|-------|
| Device | AWR2944/GP/ASIL-B/SOP:2/ES:2.0 |
| DCA IP | 192.168.33.180 |
| Host IP | 192.168.33.30 |
| adc_data.bin size | 4,194,304 bytes |
| firmware run_id | df1f275c |
| config run_id | 4b87faae |
| dca_setup run_id | bb965a49 (or equivalent) |
| capture_trigger run_id | 7bbbee5c |
| postproc run_id | 00339bb1 |

## Validated Capture Sequence

> **IMPORTANT: Do not change this sequence.** It has been hardware-validated end-to-end.

### Step 1 — DCA Preflight (read-only)
```
awr dca preflight
```
Expected: `READY_WITH_WARNINGS` or `READY` with ARP resolved to `0C:22:38:4E:5A:0C`.

### Step 2 — Guided AWR Run (Firmware + Config)
```
awr guided validate --assume-manual-connected --probe-dir ti\probe_logs
```
Confirms: firmware-power, smoke-config, and summarize-session.

### Step 3 — DCA Setup (Non-RF)
```
awr dca generate-setup --probe-dir ti\probe_logs
```
Run the generated `dofile(...)` in mmWave Studio Lua Shell.

Verify with:
```
awr dca check-run <dca_setup_run_id> --probe-dir ti\probe_logs
```

### Step 4 — Capture Trigger (RF Transmission)
```
awr dca generate-capture --probe-dir ti\probe_logs \
    --output-dir "C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc" \
    --confirm-startframe
```
Run the generated `dofile(...)` in mmWave Studio Lua Shell.

**The validated Lua sequence is:**
```lua
local adc_data_path = [[C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc\adc_data.bin]]
ar1.CaptureCardConfig_StartRecord(adc_data_path, 1)  -- .bin extension required
RSTD.Sleep(2000)
ar1.StartFrame()
RSTD.Sleep(5000)
ar1.CaptureCardConfig_StopRecord()  -- required to finalize file
RSTD.Sleep(1000)
```

> **Path rule**: `StartRecord` **requires** the `.bin` suffix in the path (unlike some older
> documentation). Passing a bare base path (without `.bin`) causes
> `System.ArgumentOutOfRangeException` in `CopyMatlabLogFileForDCA1000ForAnalysis`.

### Step 5 — Post-Processing (separate stage)
```
awr dca generate-postproc --probe-dir ti\probe_logs \
    --output-dir "C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc"
```
Run the generated `dofile(...)` in mmWave Studio Lua Shell.

**The validated Lua sequence is:**
```lua
local adc_data_path = [[C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc\adc_data.bin]]
ar1.StartMatlabPostProc(adc_data_path)
```

### Step 6 — Validate Capture
```
awr dca check-capture \
    --capture-dir "C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc" \
    --expected-bytes 4194304
```
Expected: `adc_data.bin FOUND size=4194304 PASS exact match`

### Step 7 — Record & Summarize
```
awr dca record-validation \
    --capture-dir "C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc" \
    --expected-bytes 4194304 \
    --capture-run-id 7bbbee5c \
    --postproc-run-id 00339bb1 \
    --probe-dir ti\probe_logs

awr dca summarize-capture \
    --capture-dir "C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc"
```

---

## Expected Capture Size Model

The validated post-processed output size is **4,194,304 bytes**.

The earlier provisional smoke-test estimate was 524,288 bytes (based on a smaller window).
Observed ratio = 8.0x (4194304 / 524288 = 8.0).

**Size derivation formula:**

```
samples_per_chirp   = numAdcSamples        (e.g., 256)
bytes_per_sample    = (adc_bits / 8) * 2   (complex I/Q, 2 bytes each for 16-bit)
rx_channels         = active_rx_antennas   (e.g., 4)
chirps_per_frame    = numLoops * numChirps (e.g., 128 * 1 = 128)
frames              = numFrames            (e.g., 1)

expected_bytes = samples_per_chirp * bytes_per_sample * rx_channels
                 * chirps_per_frame * frames
               = 256 * 4 * 4 * 128 * 1 = 524,288  (smoke config, 1 frame)
```

The validated capture used **16 frames** (or equivalent config):
```
256 * 4 * 4 * 128 * frames = 4,194,304
=> frames = 4,194,304 / 524,288 = 8
```

Use `awr dca check-capture --expected-bytes 4194304` for the validated hardware config.

---

## Artifact Layout

After a successful capture, artifacts should be saved with:
```
my_radar_project\captures\first_real_dca_capture_<timestamp>\
  adc_data.bin                          (4,194,304 bytes validated)
  cf.json                               (DCA configuration)
  LogFile.txt
  CLI_LogFile.txt
  adc_data_LogFile.txt
  <capture_trigger_run_id>_capture_trigger_result.json
  <capture_trigger_run_id>_capture_trigger_progress.jsonl
  <postproc_run_id>_postproc_result.json
  <postproc_run_id>_postproc_progress.jsonl
  dca_validation_<timestamp>.json       (from record-validation)
```
