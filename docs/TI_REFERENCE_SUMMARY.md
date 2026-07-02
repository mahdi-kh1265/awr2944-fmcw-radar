# TI reference summary

This summarizes the included TI references. Use the PDFs in `reference_docs/` as source material.

## AWR2944EVM guide (`spruj22c.pdf`)

Key facts:

- AWR2944/AWR2944P EVM supports 76-81 GHz mmWave sensing.
- Onboard antenna is 4TX/4RX.
- EVM has C66x DSP, ARM Cortex-R5F controller, and hardware accelerator.
- EVM has direct DCA1000EVM connectivity.
- Power is 12 V with >2.5 A current capability.
- After applying 12 V, TI recommends pressing NRST/SW1 once for reliable boot.
- J10 FTDI USB provides UART/SPI/I2C/RS232/SOP through FT4232H.
- J8 XDS USB provides JTAG and MSS UART interfaces and is used for OOB/flash.
- Debug 60-pin connector carries LVDS signals to the DCA1000 plus SPI/I2C/JTAG/control lines.

## DCA1000 + mmWave Studio training deck/transcript

Key facts:

- DCA1000 sends ADC capture data over Ethernet/UDP.
- Target PC static IPv4 should be `192.168.33.30` with subnet `255.255.255.0`.
- UDP ports 4096 and 4098 must not be blocked.
- Typical mmWave Studio flow: RS232 connect → load BSS → load MSS → SPI connect → RF power up → StaticConfig → DataConfig → SensorConfig profile/chirp/frame → SetUp DCA1000 → Connect/Reset/Configure → DCA1000 ARM → Trigger Frame → PostProc.
- Raw captures are first stored as `adc_data_Raw_0.bin` etc.
- Files may split around ~1 GB.
- Because Ethernet/UDP packets can be out of order or missing, packet reorder + zero-fill is required.
- mmWave Studio PostProc removes packet metadata and writes `adc_data.bin`.
- Normal TI PostProc may only automatically process the first raw file set, so multi-file raw support is a major opportunity for this repo.
- **LVDS lane configuration**: DCA1000 captures over 4 lanes for xWR12xx/xWR14xx and 2 lanes for xWR16xx.  AWR2944 lane count must be verified from mmWave Studio DataConfig.

## SWRA581B ADC raw data app report

Key facts:

- Explains how to interpret raw ADC data from Capture Demo or mmWave Studio.
- Gives DCA1000 and TSW1400 data layouts for older devices.
- Gives MATLAB snippets for custom post-processing.
- `adc_data.bin` is the headerless ADC sample file after DCA packet reorder/zero-fill.
- DCA1000 samples are 2-byte two's-complement values.
- Complex data uses real and imaginary parts.
- Older xWR12xx/xWR14xx DCA examples use four LVDS lanes.
- Older xWR16xx/IWR6843 DCA examples use two LVDS lanes.
- MATLAB examples return receiver data in rows, with chirps sequential in columns.

## mmwaveSensing FMCW offline viewing deck

**Source of truth for radar formulas used in M1.**

### Range formulas
- IF frequency: `f_IF = S × 2d / c`
  *(chirp slope S in Hz/s, distance d in meters)*
- Range resolution: `d_res = c / (2B)`
  *(B = chirp bandwidth in Hz)*
- Max range: `d_max = Fs × c / (2S)`
  *(Fs = ADC sample rate in Hz, S = slope in Hz/s)*

### Velocity formulas
- Phase displacement from movement: `Δφ = 4π Δd / λ`
- Velocity from Doppler phase: `v = λω / (4π Tc)`
  *(Tc = chirp period, ω = phase change rate)*
- Max unambiguous velocity: `v_max = λ / (4 Tc)`
- Velocity resolution: `v_res = λ / (2 Tf)`
  *(Tf = frame active time = N_chirps × Tc)*

### Angle formulas (TODO — requires validated array geometry)
- Angle relation: `θ = asin(λ Δφ / (2π d))`
  *(d = antenna spacing)*
- Angular resolution: `θ_res = λ / (N d cos θ)`
  *(N = number of virtual antennas)*

### Notes
- Velocity and angle formulas are labeled as **estimates** in the code until
  chirp timing (especially TDM-MIMO sequencing) and antenna array geometry
  are fully characterized for our specific AWR2944 setup.
- For TDM-MIMO, effective Tc = num_tx × single_chirp_period.

## Important warning

Do not assume AWR2944 is exactly identical to the old xWR14xx/xWR16xx layouts.
Implement layout abstraction and validate empirically.

AWR2944 default capture mode appears to be **real ADC** (not complex) based on
the ADC configuration in mmWave Studio.  Treat the default as real ADC unless
the provided TI docs prove otherwise for our exact capture path.

## TI Install Audit Findings (July 2026)

An audit of the local mmWave Studio 3.0.0.14 install revealed:
- **No AWR2944-specific parsing logic exists locally** (our install predates it).
- `rawDataReader.m` only supports complex data, not real data.
- The compiled `Packet_Reorder_Zerofill.exe` handles packet reassembly, but its source is not readable.
- **LVDS lane count** determines the physical transport formatting (AWR2944 uses 2 lanes).
- **`chInterleave`** (`channelInterleave` in `rlDevDataFmtCfg_t`) determines the logical RX ordering in the reassembled `adc_data.bin` stream.
  - `chInterleave=0` (interleaved): RX channels cycle per sample clock.
  - `chInterleave=1` (non-interleaved): All samples for RX0, then all for RX1, etc.
- TI's `rawDataReader.m` enforces `chInterleave=1` for known 2-lane devices.
- Final validation requires checking the actual mmWave Studio DataConfig generated during the first capture, especially `rlDevDataFmtCfg_t.chInterleave` and `adcFmt`.
