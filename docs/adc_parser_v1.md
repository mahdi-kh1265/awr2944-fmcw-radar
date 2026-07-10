# ADC Parser v1

## Overview

Parser v1 reads **`adc_data.bin`** (post-processed output from `StartMatlabPostProc`), NOT `adc_data_Raw_0.bin` (raw UDP dump from DCA1000).

## Size Model

```
samples_per_chirp   = 256
bytes_per_sample    = 4          (complex int16: I int16 + Q int16)
rx_channels         = 4
chirps_per_frame    = 128
frames              = 8

expected_bytes = 256 × 4 × 4 × 128 × 8 = 4,194,304 bytes
```

## Default Output Shape

```python
cube.shape = (8, 128, 4, 256)  # (frames, chirps, rx, samples)
cube.dtype = complex64
```

## Layout Assumption

The default layout `frame_chirp_rx_sample` is a **hypothesis** based on the validated capture. It has NOT been confirmed against:

- TI MATLAB reference post-processing scripts
- Controlled synthetic captures with known patterns per-channel

Until confirmed, the parser labels this explicitly:
- `layout_assumption: "frame_chirp_rx_sample"`
- `layout_assumption_confirmed: false`

## IQ Order

Default: `iq` (I first, Q second in the interleaved int16 stream).

`complex_sample = I + j*Q` for `iq_order="iq"`
`complex_sample = Q + j*I` for `iq_order="qi"`

## CLI Usage

```bash
# Text inspection
awr adc inspect --bin path/to/adc_data.bin

# JSON inspection
awr adc inspect --bin path/to/adc_data.bin --format json

# Custom dimensions
awr adc inspect --bin path/to/adc_data.bin --frames 1 --chirps 64 --rx 2 --samples 128
```

## What Is NOT Implemented

- FFT (range, Doppler, angle)
- CFAR detection
- Point cloud export
- Beamforming
- Layout confirmation against TI MATLAB

These belong in the DSP pipeline (`src/awr2944_dca/dsp/`), not the parser.
