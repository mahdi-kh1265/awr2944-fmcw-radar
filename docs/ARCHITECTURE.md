# Architecture

## Data flow

```text
SDK Demo UART CLI (radar config) / DCA1000 CLI (FPGA init)
    ↓
Direct UDP Capture (streaming + metadata logging)
    ↓
adc_data.bin (native size)
    ↓
Sequence/Counter Validation & Depadding
    ↓
adc_data_canonical.bin (exact N-frame size)
    ↓
parse_adc_data_bin() → cube[frame, chirp, rx, sample]
    ↓
standalone MATLAB viewer (buildMmwsCompatibleShell.m) OR Python DSP (range/doppler FFT)
```

## Central shape

Every parser should output:

```python
cube.shape == (num_frames, chirps_per_frame, num_rx_or_virtual_antennas, samples_per_chirp)
```

Dimension order:

```text
frame, chirp, antenna/rx, sample
```

Then:

- range FFT across sample axis
- Doppler FFT across chirp axis
- angle FFT / beamforming across antenna or virtual antenna axis

## Layout abstraction

Implement binary layout classes/functions. Do not force everything into one parser.

Candidate layouts:

- `DcaXwr14xxComplex4LaneLayout`
- `DcaXwr16xxComplex2LaneLayout`
- `Awr2944DcaLvdsUnvalidatedLayout`
- `CustomLayout`

AWR2944 layout must be validated with real captures.
