# awr2944-fmcw-radar

A Python research toolkit for TI AWR2944EVM + DCA1000EVM raw ADC radar captures.

This package adds the reproducible research layer on top of TI mmWave Studio:
experiment configs, metadata, file-size validation, binary parsing, DSP
processing, plotting, and exports.

## AWR2944 layout status

The AWR2944 binary layout (`awr2944_real_interleaved_2lane_unvalidated`) is
a best-guess implementation.  It has **not been validated** against real captures.
See `docs/DATA_FORMATS.md` for the validation checklist.

## Reference documents

TI PDFs in `reference_docs/`:
- AWR2944EVM user guide (SPRUJ22C)
- DCA1000 + mmWave Studio raw capture training
- SWRA581B ADC raw data capture app report
- mmwaveSensing FMCW offline viewing deck (radar formulas)
