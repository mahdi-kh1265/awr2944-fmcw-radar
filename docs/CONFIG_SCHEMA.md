# Config schema

Human-facing experiment configs should be YAML.

Core sections:

- `experiment`: name, operator, description, notes.
- `rig`: rig profile such as `awr2944-dca1000`.
- `hardware`: TX/RX channels, antenna mode.
- `adc`: samples per chirp, bits, complex/real, IQ order, binary layout.
- `profile`: start frequency, slope, sample rate, idle time, ramp time.
- `frame`: chirps per frame, frames, frame period.
- `capture`: output path, raw files, packet delay, DCA settings.
- `calibration_target`: optional known target info.

The compiler should derive:

- expected file size
- capture duration
- bandwidth
- range resolution
- max range estimate
- velocity resolution
- max unambiguous velocity estimate
- number of virtual antennas
- expected disk usage
