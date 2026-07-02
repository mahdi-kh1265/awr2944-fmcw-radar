# Project spec

## Core idea

Turn AWR2944EVM + DCA1000EVM raw ADC capture from a fragile GUI-driven workflow into a reproducible research pipeline.

## What the repo should do

- Initialize standard experiment folders.
- Diagnose hardware/software setup with `awr doctor`.
- Generate and validate experiment configs.
- Save metadata next to every capture.
- Validate raw and reordered ADC file sizes.
- Inspect DCA raw packet integrity.
- Parse `adc_data.bin` into clean radar cubes.
- Run range FFT, Doppler FFT, angle FFT.
- Remove static clutter/background.
- Run CFAR and export point clouds.
- Generate high-quality figures/reports.
- Support dashboard, replay mode, and live-ish preview.
- Support sweeps over chirp/frame/capture parameters.
- Support corner-reflector calibration.
- Export to Zarr, HDF5, Parquet, CSV, PNG/SVG/HTML, and `.mat`.
- Keep MATLAB bridge optional.

## Non-goals for early versions

- Full replacement of mmWave Studio.
- Direct undocumented hardware control.
- Production real-time embedded processing.
- Hard-coded assumptions about AWR2944 data layout before validation.
