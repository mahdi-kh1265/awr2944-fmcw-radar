# mmWave Studio `ar1` API Map

## Overview

The `ar1` API is fully exposed and enumerable in our installed mmWave Studio instances. Using the offline inventory workflow, we found over 400 keys in the `ar1` table.

Because TI does not provide comprehensive programmatic documentation for all these APIs, we use a static, heuristic classification to map and understand them.

## Classification Limitations

> [!WARNING]
> This classification is strictly **name-based and heuristic**. It is *not* a guarantee of hardware safety. 
> A function classified as "safe" might still crash the board or alter state if called incorrectly.

We classify APIs into standard categories:
- `harmless/read-only`: Informational APIs like `Get`, `Version`, `Status`.
- `connection/setup`: RS232/SPI connections and power-up APIs.
- `firmware/loading`: BSS/MSS firmware downloads.
- `static config`: Hardware configs like `ChanNAdcConfig`.
- `profile/chirp/frame config`: Waveform configs.
- `DCA/capture`: DCA1000 routing and ARMing.
- `RF/hardware action`: Frame triggering, calibration, RF init.
- `unknown`: Everything else (defaulting to dangerous).

## Offline Generation

We generated this map strictly offline. **No hardware commands were executed.**

You can view and filter the extracted APIs yourself using:
```bash
awr ti inventory-list
awr ti inventory-list --filter Connect
```

And run the classifier via:
```bash
awr ti inventory-classify
```
This generates the classification JSON and cross-references actual API usages from local TI demo scripts (e.g., `DataCaptureDemo_xWR.lua`). Outputs are stored in `ti/probe_logs/`.
