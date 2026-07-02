# Parser Validation Plan

## Objective
Determine which of the two AWR2944 real ADC 2-lane layout candidates correctly maps the physical antenna and sample data. Because our mmWave Studio installation predates explicit AWR2944 parser logic, we must empirically validate the hardware's output format.

## Requirements

### 1. What Data File to Use
You **must** use the headerless `adc_data.bin` file, **not** the raw UDP capture file (`adc_data_Raw_0.bin`).

- **Raw Files (`adc_data_Raw_*.bin`)**: Contain packet sequence numbers, byte counts, and raw payload data. These are subject to network drops or out-of-order delivery.
- **Headerless Files (`adc_data.bin`)**: The cleaned, reordered, and zero-filled sequence of ADC samples.

If you capture raw data using mmWave Studio, use the **PostProc** button in the UI or run the `Packet_Reorder_Zerofill.exe` utility to produce `adc_data.bin`.

### 2. mmWave Studio Config Fields to Record
During the capture, open the mmWave Studio output window (or the saved `*.json`/`*.lua` logs) and verify the following:

- `rlDevDataFmtCfg_t.chInterleave`: This determines if the data is interleaved (`0`) or non-interleaved (`1`).
- `rlDevDataFmtCfg_t.adcFmt`: Is it real (`0`) or complex?
- `rlDevDataFmtCfg_t.iqSwapSel`: Confirm I/Q swap settings (if applicable).
- Number of active LVDS lanes (from `DataPathConfig` or `rlDevLaneEnable_t`).

Ensure your `capture.yaml` matches these hardware settings (e.g., `channel_interleave`, `num_lvds_lanes`, `is_complex`, etc.).

## How to Run `awr compare-layouts`

Once you have your `adc_data.bin` and a matching `capture.yaml`, use the built-in comparison tool.

You can run it against the experiment directory directly (if it contains `raw/adc_data.bin` and `capture.yaml`):
```bash
awr compare-layouts path/to/experiment_folder
```

Or you can run it against the specific files:
```bash
awr compare-layouts path/to/adc_data.bin --config path/to/capture.yaml
```

## How to Decide Which Layout is Correct

1. **Size Validation**: The first check is file size. If one layout passes size validation and the other fails, the passing one is strongly favored (though both candidates currently expect the same file size).
2. **Mean and Standard Deviation (Per-RX Stats)**: 
   - A correct layout will typically show similar noise floors and average power levels across all 4 RX channels.
   - If one layout shows one RX channel with zero power and another with double power, it's improperly de-interleaving the stream.
3. **Min/Max Value Bounds**: Ensure the min/max values fall within reasonable boundaries for a 16-bit signed integer (approximately -32768 to 32767). Values pinned exactly at these extremes may indicate clipping or improper layout parsing.
4. **Physical Sanity Checks**: If you put a strong corner reflector perfectly boresight (0 degrees azimuth, 0 degrees elevation) and run a single TX, all 4 RX channels should show a peak in the Range FFT at the *exact same range bin* with comparable magnitudes.

### Evidence Needed Before Marking `lab_validated=True`

Before changing `lab_validated` to `True` for a layout candidate, ensure:
- [ ] `expected_file_size()` exactly matches actual `adc_data.bin` size on disk.
- [ ] You have successfully processed a 1-TX, 4-RX capture (e.g., `first_capture.yaml`) and observed sane RX values using `compare-layouts`.
- [ ] You have successfully processed a TDM-MIMO capture (4-TX, 4-RX) and validated the correct transmission sequence mapping across chirps.
- [ ] Range FFT profiles on a known physical target (like a corner reflector at 2 meters) yield the expected range index.
- [ ] You have documented the exact mmWave Studio `rlDevDataFmtCfg_t` parameters that generated this data.

## Sample Output

```text
Comparing layouts for C:\ti\workspace\experiment_01\raw\adc_data.bin
IMPORTANT: Input file MUST be the headerless `adc_data.bin`. `adc_data_Raw_*.bin` requires packet reorder and zero-fill first.

=== awr2944_real_2lane_interleaved_candidate ===
channel_interleave: 0
Size validation: OK (Matched expected 2621440 bytes)
Cube shape: (10, 128, 4, 256)
Dtype: float32
Per-RX Stats
┏━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━┓
┃   RX ┃  Mean ┃  StdDev ┃    Min ┃   Max ┃
┡━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━┩
│    0 │ -0.00 │  412.33 │  -4021 │  4011 │
│    1 │ -0.01 │  409.81 │  -3950 │  4102 │
│    2 │  0.02 │  415.12 │  -4100 │  3989 │
│    3 │ -0.00 │  411.05 │  -4055 │  4001 │
└──────┴───────┴─────────┴────────┴───────┘
First 16 Samples (Frame 0, Chirp 0)
...

=== awr2944_real_2lane_noninterleaved_candidate ===
channel_interleave: 1
Size validation: OK (Matched expected 2621440 bytes)
...
```
