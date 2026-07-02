# TI Bridge Roadmap

## Overview

The TI bridge allows importing/exporting configs between our `capture.yaml` format and TI mmWave Studio's Lua scripts, JSON logs, and DCA1000 configs.

Our goal is to make mmWave Studio a backend execution engine while our repo owns the reproducible config layer.

## Current Status

### Implemented

| Command | Status | Notes |
|---|---|---|
| `awr ti inspect <file>` | ✅ Working | Lua regex + JSON key extraction |
| `awr ti import <file>` | ✅ Working | Conservative — marks unknowns |
| `awr ti compare <yaml> <ti_file>` | ✅ Working | ERROR/WARNING/MATCH/SKIP levels |
| `awr ti export-lua-template <yaml>` | ⚠️ Template only | NOT hardware-validated |
| `awr ti export-dca-config <yaml>` | ✅ Working | Fails on missing fields |

### Supported TI File Formats

| Format | Inspect | Import | Notes |
|---|---|---|---|
| `.lua` (mmWave Studio scripts) | ✅ | ✅ | Regex extraction of `ar1.*()` calls |
| `.json` (mmWave Studio logs) | ✅ | ✅ | Key lookup for known field names |
| `.cfg` | ❌ | ❌ | Future — line-by-line parser |
| `.mmwave` | ❌ | ❌ | Future — binary format |

### TI Lua API Call Mapping

Parameter positions are reverse-engineered from `DataCaptureDemo_xWR.lua`:

| API Call | Parameters Extracted | Confidence |
|---|---|---|
| `ar1.ChanNAdcConfig` | txEn, rxEn, adcBits, adcFmt, iqSwap, chInterleave | Medium |
| `ar1.ProfileConfig` | startFreq, idleTime, rampEndTime, slope, samples, sampleRate | Medium |
| `ar1.FrameConfig` | chirpStart, chirpEnd, numLoops→chirps, numFrames, framePeriod | Medium |
| `ar1.DataPathConfig` | intfSel | Low |
| `ar1.LVDSLaneConfig` | laneEn | Low |

> **WARNING**: Parameter names are NOT documented in TI's Lua scripts.
> Positions are inferred from example values. Always verify against your firmware version.

## Export Limitations

### Lua Template (`export-lua-template`)
- Generated file includes a **WARNING banner** at the top
- All parameter positions are best-guess from `DataCaptureDemo_xWR.lua`
- TODO markers for firmware download, power-on sequence, and unverified parameters
- **Must be reviewed by a human before running on hardware**

### DCA1000 JSON (`export-dca-config`)
- Based on DCA1000 CLI Software Developer Guide
- Fails with clear error if `num_lvds_lanes` is not 2 or 4
- Includes firmware/schema version notes
- Default Ethernet settings (192.168.33.x) — must match your DCA1000 network config

## Planned Work

1. Support `.cfg` file parsing
2. Validate Lua exports against real hardware
3. Add `awr ti export-chirp-cfg` for mmWave Studio chirp configuration
4. Round-trip validation: export → import → compare → zero diff
5. Parameterize DCA1000 Ethernet settings from capture.yaml
