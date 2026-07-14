# awr2944-fmcw-radar

A Python research toolkit for TI AWR2944EVM + DCA1000EVM raw ADC radar captures.

This package provides a robust, native direct-capture pipeline that is free from mmWave Studio GUI automation and Lua scripts.

## Architecture

The production capture chain uses:
1. SDK Demo UART CLI for radar configuration
2. TI DCA1000 CLI utilities (external dependency) for FPGA initialization
3. Native direct UDP capture with zero-copy stream processing and metadata logging
4. Sequence/counter validation and DCA depadding
5. Canonical ADC cube extraction
6. Python DSP and standalone MATLAB viewer `buildMmwsCompatibleShell.m`

Historical mmWave Studio GUI automation is available as an optional `legacy-mmws` dependency extra for compatibility and debugging.

## Reference documents

TI PDFs in `reference_docs/`:
- AWR2944EVM user guide (SPRUJ22C)
- DCA1000 + mmWave Studio raw capture training
- SWRA581B ADC raw data capture app report
- mmwaveSensing FMCW offline viewing deck (radar formulas)
