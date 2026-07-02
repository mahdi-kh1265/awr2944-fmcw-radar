# Experiment Workflow

## Overview

An experiment is a self-contained directory with everything needed to reproduce a radar capture: config, raw data, TI configs, screenshots, and notes.

## Quick Start

```bash
# 1. Initialize experiment from a preset
awr experiment init my_first_capture --preset first-capture

# 2. Review and customize the config
awr config summarize experiments/my_first_capture/capture.yaml
awr config validate experiments/my_first_capture/capture.yaml

# 3. (Optional) Export a Lua template for mmWave Studio
awr ti export-lua-template experiments/my_first_capture/capture.yaml \
    --out experiments/my_first_capture/ti_config/capture.lua

# 4. Run capture in mmWave Studio
#    - Load the Lua script or manually configure
#    - Save TI config files to ti_config/
#    - Take screenshots of mmWave Studio settings

# 5. Copy adc_data.bin to raw/
#    Place the headerless adc_data.bin (NOT adc_data_Raw_*.bin) in raw/

# 6. Validate against TI config
awr ti compare experiments/my_first_capture/capture.yaml \
    experiments/my_first_capture/ti_config/exported_config.json

# 7. Compare parser layouts
awr compare-layouts experiments/my_first_capture

# 8. Parse the data
awr parse experiments/my_first_capture/raw/adc_data.bin \
    --config experiments/my_first_capture/capture.yaml
```

## Directory Structure

```
experiments/<name>/
├── capture.yaml          # Our source of truth config
├── manifest.yaml         # Auto-generated metadata (timestamp, tool version)
├── notes.md              # Lab notes template
├── raw/                  # Raw ADC binary data
│   └── adc_data.bin      # Headerless ADC data (after PostProc)
├── ti_config/            # TI mmWave Studio configs/logs
│   ├── capture.lua       # Exported Lua template
│   └── session_log.json  # mmWave Studio session log
├── screenshots/          # mmWave Studio UI screenshots
└── compare_layouts/      # Output from awr compare-layouts
```

## File Types

| File | Source | Purpose |
|---|---|---|
| `capture.yaml` | Our tool | Canonical experiment config |
| `manifest.yaml` | Our tool (auto) | Creation metadata, tool version |
| `notes.md` | User | Free-form lab notes |
| `adc_data.bin` | mmWave Studio PostProc | Headerless ADC samples |
| `adc_data_Raw_*.bin` | DCA1000 | Raw UDP packets — needs reorder/zerofill first |
| `*.lua` | Our tool or TI | mmWave Studio Lua scripts |
| `*.json` | TI mmWave Studio | Session logs with config parameters |

## Important Notes

1. **Always use `adc_data.bin`**, not `adc_data_Raw_*.bin`. The raw files need packet reorder and zero-fill via `Packet_Reorder_Zerofill.exe` first.

2. **Always run `awr config validate`** before capturing. It catches config/layout mismatches that would produce garbled data.

3. **Always run `awr ti compare`** after capturing to verify the hardware actually used the settings you intended.

4. **Always run `awr compare-layouts`** on the first capture with new settings. Until a layout is marked `lab_validated=True`, you should check both candidates.

## Manifest Format

```yaml
experiment: my_first_capture
preset: first-capture
created: 2026-07-02T20:00:00+00:00
tool_version: 0.1.0
status: initialized
notes: ""
```

The `status` field can be updated as the experiment progresses:
- `initialized` — created but no data yet
- `captured` — raw data collected
- `validated` — parser layout confirmed
- `processed` — DSP pipeline run
