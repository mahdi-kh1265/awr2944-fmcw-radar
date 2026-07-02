# Architecture

## Data flow

```text
TI mmWave Studio / DCA1000
    ↓
adc_data_Raw_*.bin ──→ packet inspect/reorder/zero-fill ──→ adc_data.bin
    ↓                                                       ↓
packet_report.json                                     parse_adc_data_bin()
                                                            ↓
                                         cube[frame, chirp, rx/antenna, sample]
                                                            ↓
             range FFT → clutter removal → Doppler FFT → angle FFT → CFAR
                                                            ↓
                         figures / point cloud / report / dashboard / exports
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
