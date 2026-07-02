# DSP pipeline

Core chain:

```text
ADC cube
→ ADC sanity checks
→ DC offset removal
→ range window
→ range FFT
→ static clutter/background removal
→ Doppler window
→ Doppler FFT
→ antenna calibration
→ angle FFT / beamforming
→ CFAR
→ point cloud
→ plotting/export/report
```

Required early processing:

- range FFT
- Doppler FFT
- static clutter removal
- range profile plot
- range-Doppler plot

Required later processing:

- angle FFT / beamforming
- CFAR
- point cloud export
- background library
- corner reflector calibration
- replay dashboard
- live-ish preview
- capture health score
- packet-loss heatmap
