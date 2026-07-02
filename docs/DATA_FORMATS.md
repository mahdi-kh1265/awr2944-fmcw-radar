# Data formats

## Raw DCA files

Usually:

```text
adc_data_Raw_0.bin
adc_data_Raw_1.bin
...
```

These contain packet metadata plus payload. They need inspection, reorder, and zero-fill.
Files split after ~1 GB of data (per DCA1000 firmware behavior).

## Headerless ADC file

Usually:

```text
adc_data.bin
```

This is the ADC stream after packet reorder/zero-fill and metadata removal.
Produced by mmWave Studio PostProc or a custom reorder utility.

Data is stored as 16-bit two's complement (int16) values.

## Expected size

File-size validation is **layout-aware**.  The expected size depends on:
- ADC mode (real vs. complex)
- Number of LVDS lanes
- Number of enabled RX channels
- Samples per chirp
- Chirps per frame
- Number of frames

### AWR2944 real ADC (default):
```text
expected_bytes = samples_per_chirp × num_rx × chirps_per_frame × num_frames × 2
```
(2 bytes per real int16 sample per RX)

### Complex ADC (e.g., xWR14xx):
```text
expected_bytes = samples_per_chirp × num_rx × chirps_per_frame × num_frames × 4
```
(4 bytes: 2 bytes I + 2 bytes Q per RX)

## Output shape

All parsers normalize to:

```text
cube[frame, chirp, antenna_or_rx, sample]
```

For real ADC data, the cube is `float32`.
For complex ADC data, the cube is `complex64`.

Note: Real time-domain ADC samples produce complex FFT outputs.  After
range FFT, each range bin has complex amplitude and phase.  This supports
Doppler and angle processing (phase displacement Δφ = 4πΔd/λ).

## Layout status flags

Each binary layout has two status flags:

- **`swra581b_reference`**: Implementation is derived from the SWRA581B app
  note MATLAB snippets and data-format diagrams.  Does NOT mean validated.
- **`lab_validated`**: Implementation has been tested against real hardware
  captures from our exact AWR2944 + DCA1000 setup and confirmed correct.

"Unvalidated" does NOT mean we have no idea how the data is structured.
It means our Python mapping of the binary stream has not yet been **proven**
on our exact AWR2944 + DCA1000 setup.

## Validation checklist for real AWR2944 captures

Before marking a layout as `lab_validated=True`, the following must be
confirmed against real captures with known test scenarios:

- [ ] **File size**: `expected_file_size(config)` matches actual file size
- [ ] **RX order**: RX0..RX3 map to the correct physical antenna elements
- [ ] **IQ/real mode**: ADC output is correctly interpreted as real or complex
- [ ] **Chirp ordering**: Chirps within a frame are in the expected sequence
- [ ] **Frame ordering**: Frames are contiguous and correctly indexed
- [ ] **LVDS lane mapping**: Lane-to-RX mapping matches the physical wiring
- [ ] **Disabled RX behavior**: Data format when fewer than 4 RX are enabled
- [ ] **TDM-MIMO TX/chirp mapping**: Each TX fires on the correct chirp index
- [ ] **Virtual antenna ordering**: Virtual array matches expected TX×RX pattern
- [ ] **Doppler sign convention**: Approaching targets show positive/negative Doppler
- [ ] **Angle behavior**: Known target (e.g., corner reflector at 0° azimuth) produces
  correct angle output
- [ ] **Multi-file captures**: Captures spanning multiple `adc_data_Raw_*.bin` files
  are correctly handled after reorder
