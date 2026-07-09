# DCA1000 Capture Evidence Template

Create one copy of this template for each DCA1000 capture attempt. Fill it in during the run, not
from memory later.

## Attempt Summary

| Field | Value |
| --- | --- |
| Timestamp |  |
| Operator |  |
| Lab/location |  |
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

## Command Log

Paste the exact commands run and the important output lines.

```powershell
awr dca preflight
```

Result:

```text

```

```powershell
awr dca generate-setup --probe-dir ti/probe_logs
```

Generated setup Lua path:

```text

```

Setup `dofile(...)` pasted into mmWave Studio Lua shell:

```text

```

```powershell
awr mmws post check-run --run-id <dca_setup_run_id>
```

Result:

```text

```

```powershell
awr dca generate-capture --probe-dir ti/probe_logs --output-dir C:\ti\mmwave_studio\PostProc --confirm-startframe
```

Generated capture Lua path:

```text

```

Capture `dofile(...)` pasted into mmWave Studio Lua shell:

```text

```

```powershell
awr mmws post check-run --run-id <capture_run_id>
```

Result:

```text

```

```powershell
awr dca check-capture --capture-dir C:\ti\mmwave_studio\PostProc --expected-bytes 524288
```

Result:

```text

```

## File Evidence

| File | Exists | Size bytes | Modified time | Notes |
| --- | --- | ---: | --- | --- |
| `C:\ti\mmwave_studio\PostProc\adc_data_Raw_0.bin` |  |  |  | Raw file may be larger than expected post-processed size |
| `C:\ti\mmwave_studio\PostProc\adc_data.bin` |  |  |  | Expected exact size: `524288` bytes |

## Screenshot Or Photo Evidence

| Evidence item | Captured? | Path or description |
| --- | --- | --- |
| mmWave Studio connected before DCA setup |  |  |
| Setup Lua result or run result |  |  |
| Capture trigger Lua result or run result |  |  |
| PostProc directory showing capture files and timestamps |  |  |
| `check-capture` terminal output |  |  |
| DCA1000 board LEDs/cabling if failure occurred |  |  |

## Preservation Commands

Run these from the sidequest/tooling workspace after the attempt:

```powershell
python tools/collect_probe_artifacts.py --probe-dir C:\Users\khams008\Documents\awr2944-fmcw-radar\exp_lau_probe\ti\probe_logs --out artifacts\dca_attempt_bundle.zip
```

```powershell
python tools/report_probe_bundle.py --bundle artifacts\dca_attempt_bundle.zip --out artifacts\dca_attempt_report.md
```

Raw `.bin` files are not included in the probe bundle by default. Record their path, size, modified
time, and handling decision here:

```text

```