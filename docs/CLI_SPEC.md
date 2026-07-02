# CLI spec

Root command: `awr`

## Setup / diagnosis

```bash
awr doctor
awr doctor --deep
awr rig list
awr rig use awr2944-dca1000
awr rig show
```

## Experiment workflow

```bash
awr init experiments/walk_001
awr compile examples/configs/walking_person.yaml
awr inspect-config examples/configs/walking_person.yaml
awr capture examples/configs/walking_person.yaml --dry-run
```

## Data validation and parsing

```bash
awr inspect-raw experiments/walk_001/raw/adc_data_Raw_0.bin
awr reorder experiments/walk_001/raw/adc_data_Raw_*.bin --out experiments/walk_001/raw/adc_data.bin
awr parse experiments/walk_001
```

## Processing

```bash
awr process experiments/walk_001 --range
awr process experiments/walk_001 --doppler
awr process experiments/walk_001 --angle
awr process experiments/walk_001 --cfar
awr process experiments/walk_001 --all
```

## Calibration

```bash
awr calibrate corner experiments/corner_2m --range 2.0 --azimuth 0
awr calibrate background experiments/empty_lab
awr calibrate list
```

## Visualization

```bash
awr view experiments/walk_001
awr replay experiments/walk_001
awr live
```

- `view`: dashboard for saved experiment.
- `replay`: play saved frames like live data.
- `live`: live-ish preview from capture stream or updating files.

## Export

```bash
awr export experiments/walk_001 --mat
awr export experiments/walk_001 --zarr
awr export experiments/walk_001 --hdf5
awr export experiments/walk_001 --parquet
awr export experiments/walk_001 --all
```
