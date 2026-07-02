# awr2944-fmcw-radar

A Python research toolkit for TI AWR2944EVM + DCA1000EVM raw ADC radar captures.

This package adds the reproducible research layer on top of TI mmWave Studio:
experiment configs, metadata, file-size validation, binary parsing, DSP
processing, plotting, and exports.

## AWR2944 layout status

The AWR2944 binary layout (`awr2944_real_interleaved_2lane_unvalidated`) is
a best-guess implementation.  It has **not been validated** against real captures.
See `docs/DATA_FORMATS.md` for the validation checklist.

**Do not assume results are correct until the layout is validated.**

## Dependencies

Core (M1): numpy, scipy, pydantic, typer, rich, pyyaml, matplotlib.

Optional groups: `storage` (xarray/zarr/h5py), `dashboard` (plotly/streamlit/dash),
`tables` (polars), `hardware` (pyserial/psutil), `speed` (numba), `dev` (pytest/ruff/mypy).

## Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Config schema](docs/CONFIG_SCHEMA.md)
- [Data formats & validation checklist](docs/DATA_FORMATS.md)
- [DSP pipeline](docs/DSP_PIPELINE.md)
- [TI reference summary & formulas](docs/TI_REFERENCE_SUMMARY.md)
- [CLI spec](docs/CLI_SPEC.md)
- [Roadmap](docs/ROADMAP.md)

## Reference documents

TI PDFs in `reference_docs/`:
- AWR2944EVM user guide (SPRUJ22C)
- DCA1000 + mmWave Studio raw capture training
- SWRA581B ADC raw data capture app report
- mmwaveSensing FMCW offline viewing deck (radar formulas)
