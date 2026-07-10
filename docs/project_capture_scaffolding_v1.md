# Project / Capture Scaffolding v1

Phase 0 of the AWR2944 capture management system.

## Overview

`awr project` and `awr capture` provide structured experiment-folder
management for mmWave Studio / DCA1000 captures.  This is
filesystem/data-model scaffolding only — no hardware automation, no FFT,
no Jupyter wrapper yet.

### Relationship to existing `awr experiment`

The older `awr experiment` system uses `.awr-experiment` marker files and
`manifest.yaml`.  The newer `awr project` system uses `project.json`.
Both coexist without conflict.  `awr project` is the recommended
capture-management layer going forward.

---

## project.json

The `project.json` file (schema_version=1) lives at the project root and
contains:

| Field | Description |
|-------|-------------|
| `schema_version` | Always `1` |
| `project_id` | UUID-based unique identifier |
| `name` | Human-readable project name |
| `created_at` | ISO timestamp |
| `root_path_abs` | Absolute path to project root |
| `postproc_dir_abs` | Absolute path to mmWave Studio PostProc staging |
| `probe_dir_rel` | Relative path to probe log directory |
| `expected_bytes` | Expected ADC file size (default 4,194,304) |
| `default_adc_config` | Parser configuration (frames, chirps, rx, samples, etc.) |

The `default_adc_config` includes `layout_assumption_confirmed: false` to
indicate the frame_chirp_rx_sample layout has not been verified against TI
reference scripts.

---

## Directory Layout

After `awr project init`:

```
<project_root>/
  project.json
  configs/
    mmws/
      lua/           # Frozen/generated Lua scripts
      manifests/     # Run manifests
      results/       # Run results
      snapshots/     # Config snapshots
  captures/          # One folder per capture
  logs/              # Project-level logs
  notebooks/         # Future Jupyter notebooks
  .gitignore         # Auto-managed ignore rules
```

After `awr capture new`:

```
captures/<capture_id>/
  raw/               # Binary ADC data (gitignored)
  metadata/
    mmws_logs/       # Copied mmWave Studio logs
    adc_inspect.json # ADC parser inspection output
  processed/         # Future DSP outputs (gitignored)
  notes.md           # Human notes
  capture_manifest.json  # Machine-readable manifest
```

---

## Capture ID Format

`YYYYMMDD_HHMMSS_<slug>`

The slug is derived from the capture name: lowercased, spaces/special
characters replaced with underscores, runs of underscores collapsed.

Examples:
- `20260710_143000_static_wall_test`
- `20260710_150000_toward_away_run`

---

## Import Mode vs Direct Mode

**Import mode** (default): The raw ADC file is captured via mmWave Studio's
PostProc staging area, then imported into the project structure using
`awr capture bind-mmws-output` or `awr capture import-raw`.

**Direct mode**: Reserved for future integration where capture-smoke
writes directly into the project structure.  Not implemented in Phase 0.

---

## Why PostProc is Treated as Staging

mmWave Studio writes `adc_data.bin` and logs to its PostProc directory.
This directory also contains required static files (DLLs, EXEs) that
mmWave Studio needs to function.

The project system:
- **Copies** adc_data.bin and metadata into the project structure
- **Never moves or deletes** anything from PostProc
- **Never copies** static executables/DLLs
- **Records provenance** (source path, size, SHA256) for each copied file

---

## Workflow

### 1. Create a project

```bash
cd C:\Users\khams008\Documents\awr2944-fmcw-radar\exp_lau_probe

awr project init lau_probe \
    --root . \
    --postproc-dir "C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc" \
    --probe-dir ti\probe_logs
```

### 2. Check project status

```bash
awr project status --root .
```

### 3. Create a capture slot

```bash
awr capture new static_wall_test --root . --notes "10m from wall"
```

### 4. Bind mmWave Studio output

After running a capture through mmWave Studio / capture-smoke:

```bash
awr capture bind-mmws-output 20260710_143000_static_wall_test \
    --root . \
    --postproc-dir "C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc"
```

### 5. Inspect the capture

```bash
awr capture inspect 20260710_143000_static_wall_test --root .
awr capture inspect 20260710_143000_static_wall_test --root . --format json
```

### 6. Re-run ADC inspection

```bash
awr capture inspect 20260710_143000_static_wall_test --root . --refresh-adc-inspect
```

---

## .gitignore Rules

The following are auto-added to `.gitignore`:

```
captures/**/raw/*.bin
captures/**/raw/*.dat
captures/**/processed/*.npy
captures/**/processed/*.npz
captures/**/processed/*.mat
captures/**/processed/*.fig
captures/**/processed/*.png
captures/**/metadata/mmws_logs/*.mat
captures/**/metadata/mmws_logs/*.fig
captures/**/metadata/mmws_logs/*.png
```

**Tracked** (not ignored):
- `capture_manifest.json`
- `notes.md`
- `metadata/*.json` (including `adc_inspect.json`)
- `metadata/mmws_logs/*.json` (including `cf.json`, validation JSONs)
- `metadata/mmws_logs/*.txt` (log files)

---

## Future Integration Points

### Jupyter Wrapper
The `project.py` module is fully importable.  Future Jupyter notebooks can
call `init_project()`, `new_capture()`, `import_raw()`, etc. directly
without shelling out.

### Capture-Smoke Integration
The `capture_manifest.json` schema includes fields for:
- `firmware_run_id`
- `config_run_id`
- `dca_setup_run_id`
- `capture_trigger_run_id`
- `postproc_run_id`
- `workflow_id`

These are all `null` in Phase 0 but will be populated when capture-smoke
gains the ability to write into the project structure.

### DSP Pipeline
The `processed/` directory and `.gitignore` rules for `.npy`/`.npz` are
pre-provisioned for future DSP outputs (range FFT, range-Doppler maps).
