# Roadmap

## Milestone 1 — metadata + parser

- Pydantic schema
- expected file-size validator
- headerless `adc_data.bin` parser
- synthetic test vectors
- range profile and range-Doppler plots

## Milestone 2 — packet integrity

- parse raw DCA packet metadata
- detect missing/out-of-order packets
- reorder + zero-fill
- packet report JSON/Markdown

## Milestone 3 — config compiler

- human YAML to capture manifest
- derived radar parameters
- expected file size/duration
- TI/mmWave/DCA script skeletons
- sweep generation

## Milestone 4 — sexy DSP

- clutter/background removal
- angle FFT
- CFAR
- point cloud export
- report generator

## Milestone 5 — dashboard/replay/live

- `awr view`
- `awr replay`
- `awr live`

## Milestone 6 — calibration

- corner reflector calibration
- RX gain/phase correction
- range bias estimation

## Milestone 7 — plugins

- plugin registry
- custom detector/processor hooks
