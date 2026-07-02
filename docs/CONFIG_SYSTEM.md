# Config System

## Philosophy

`capture.yaml` is our **canonical source of truth** for every experiment.

- It defines exactly what the radar should do: ADC mode, RX/TX channels, chirp profile, frame timing.
- It is version-controlled alongside the experiment data.
- TI mmWave Studio configs (Lua, JSON, logs) are **compatibility artifacts** — we can import from and export to them, but they are not our primary format.

## Presets

Presets are conservative starting points. Use `awr config new --preset <name>` to generate a `capture.yaml`.

| Preset | TX | RX | Mode | Chirps | Frames | Notes |
|---|---|---|---|---|---|---|
| `first-capture` | 1 | 4 | single_tx | 128 | 10 | Conservative first lab test |
| `parser-validation` | 1 | 4 | single_tx | 32 | 4 | Small file for parser testing |
| `corner-reflector` | 4 | 4 | tdm_mimo | 128 | 50 | **EXPERIMENTAL** — TDM-MIMO unvalidated |
| `walking-person` | 4 | 4 | tdm_mimo | 128 | 200 | **EXPERIMENTAL** — TDM-MIMO unvalidated |

All presets default to:
- Real ADC (not complex)
- 16-bit
- `channel_interleave = 1` (non-interleaved)
- `layout = awr2944_real_2lane_noninterleaved_candidate`
- DCA1000 Ethernet capture

## Validation Rules

`awr config validate` runs deep checks beyond Pydantic schema:

| Check | Severity | Rule |
|---|---|---|
| ADC mode vs layout name | **ERROR** | real config must use "real" layout, complex must use "complex" |
| channel_interleave vs layout name | **ERROR** | interleave=0 must use "interleaved" layout, interleave=1 must use "noninterleaved" |
| LVDS lanes vs layout name | **ERROR** | 2-lane config must use "2lane" layout |
| ADC bits | **ERROR** | Must be 12, 14, or 16 |
| RX count | **ERROR** | Must be 1–4 |
| samples_per_chirp power of 2 | **WARNING** | FFT performance may be suboptimal |
| Layout candidate/unvalidated | **WARNING** | Must confirm with real capture |
| TDM-MIMO mode | **WARNING** | Virtual antenna ordering unvalidated |
| Expected file size | **INFO** | Always displayed |

## Config Lifecycle

```
awr config new --preset first-capture --out capture.yaml
    ↓
awr config validate capture.yaml
    ↓
awr config summarize capture.yaml
    ↓
[Capture with mmWave Studio]
    ↓
awr ti inspect ti_config/captured_config.json
    ↓
awr ti compare capture.yaml ti_config/captured_config.json
    ↓
awr compare-layouts raw/adc_data.bin --config capture.yaml
```
