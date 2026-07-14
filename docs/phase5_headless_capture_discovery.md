# Phase 5: Headless AWR2944+DCA1000 Capture — Discovery Report

**Generated**: 2026-07-10  
**SDK**: MMWAVE-MCUPLUS-SDK 04.07.02.01 (MCU+ SDK AWR294x 10.02.00)  
**Safety**: No hardware was flashed, reset, or modified during this discovery.

---

## Executive Summary

**Recommended Path: Option B — SDK mmw Demo (TDM) + DCA1000 CLI**

Option A (mmWave Studio CLI host tool) is **NOT FEASIBLE** with the current installation.
The TI mmWave Studio CLI host executable (`mmwave_studio_cli.exe`) and the AWR29xx
Studio CLI device appimage are **not present** anywhere in the installed SDK, mmWave Studio,
or CCS. These are part of TI **Radar Toolbox**, which is not installed.

Option B is **fully feasible** without any recompilation. The installed SDK contains:
- Pre-built `awr2944_mmw_demoTDM.appimage` (408,528 bytes)
- Official LVDS streaming profile: `profile_LVDS.cfg`
- `DCA1000EVM_CLI_Control.exe` and `DCA1000EVM_CLI_Record.exe`
- Python UART flash script (`uart_uniflash.py`)
- Python UART parser scripts
- Complete documentation for flashing, booting, and CLI commands

The mmw demo accepts radar configuration over UART as text CLI commands (the same
`.cfg` file format used by mmWave Demo Visualizer), supports LVDS raw ADC streaming
via `lvdsStreamCfg` command, and can be controlled with `sensorStart`/`sensorStop`.

**One physical action is required**: Flash the mmw demo appimage to the AWR2944 using
`uart_uniflash.py`. This replaces whatever application is currently on the board.
The original state can be restored by re-flashing the CCS debug appimage or the
mmWave Studio firmware.

---

## 1. Installed Package Inventory

### SDK Installation
| Item | Value |
|------|-------|
| SDK Root | `C:\ti\mmwave_mcuplus_sdk_04_07_02_01` |
| MCU+ SDK AWR294x | `C:\ti\mmwave_mcuplus_sdk_04_07_02_01\mcu_plus_sdk_awr294x_10_02_00_04` |
| mmWave MCU+ SDK | `C:\ti\mmwave_mcuplus_sdk_04_07_02_01\mmwave_mcuplus_sdk_04_07_02_01` |
| mmWave DFP | `C:\ti\mmwave_mcuplus_sdk_04_07_02_01\mmwave_dfp_02_04_18_01` |
| SDK Version | 10.02.00 |
| mmWave Studio (working) | `C:\ti\mmwave_studio_03_01_04_04` |
| mmWave Studio (older) | `C:\ti\mmwave_studio_03_00_00_14` |
| CCS | `C:\ti\ccs2100` |

### Key Files Found

#### Pre-built AWR2944 Application Images
| File | Path | Size |
|------|------|------|
| `awr2944_mmw_demoTDM.appimage` | `.../ti/demo/awr294x/mmw/` | 408,528 |
| `awr2944_mmw_demoTDM.appimage.hs` | `.../ti/demo/awr294x/mmw/` | 410,224 |
| `awr2944_mmw_demoDDM.appimage` | `.../ti/demo/awr294x/mmw/` | 404,864 |
| `awr2944_mmw_demoDDM.appimage.hs` | `.../ti/demo/awr294x/mmw/` | 406,560 |
| `awr2944_mmw_demoTDMEnet.appimage` | `.../ti/demo/awr294x/mmw/` | 568,976 |
| `awr2944_ccsdebug.appimage` | `.../ti/utils/ccsdebug/` | (restore image) |

#### AWR2944 TDM Profiles (LVDS capable)
| File | Path | Size |
|------|------|------|
| **`profile_LVDS.cfg`** | `.../profiles/tdm_awr2944/` | 1,159 |
| `profile_2d_2AzimTx.cfg` | `.../profiles/tdm_awr2944/` | 1,076 |
| `profile_2d_3AzimTx.cfg` | `.../profiles/tdm_awr2944/` | 1,054 |
| `profile_3d_2Azim_1ElevTx.cfg` | `.../profiles/tdm_awr2944/` | 1,092 |
| `profile_3d_3Azim_1ElevTx.cfg` | `.../profiles/tdm_awr2944/` | 1,087 |
| `profile_Enet.cfg` | `.../profiles/tdm_awr2944/` | 1,058 |
| `profile_advanced_chirp.cfg` | `.../profiles/tdm_awr2944/` | 2,037 |
| `profile_calibration.cfg` | `.../profiles/tdm_awr2944/` | 836 |

#### DCA1000 CLI Tools (from mmWave Studio)
| File | Path | Size |
|------|------|------|
| `DCA1000EVM_CLI_Control.exe` | `C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc\` | 2,858,838 |
| `DCA1000EVM_CLI_Record.exe` | `C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc\` | 2,871,793 |
| `RF_API.dll` | `C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc\` | 244,106 |
| `cf.json` | `C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc\` | 1,492 |

#### Flash Tools
| File | Path | Size |
|------|------|------|
| `uart_uniflash.py` | `.../mcu_plus_sdk_awr294x_.../tools/boot/` | 30,387 |
| `sbl_uart_uniflash.release.tiimage` | `.../tools/boot/sbl_prebuilt/awr294x-evm/` | 58,513 |
| `sbl_qspi.release.tiimage` | `.../tools/boot/sbl_prebuilt/awr294x-evm/` | 68,321 |
| `default_sbl_qspi.cfg` | `.../tools/boot/sbl_prebuilt/awr294x-evm/` | 1,590 |

#### Python Parser Scripts
| File | Path | Size |
|------|------|------|
| `parser_mmw_demo.py` | `.../ti/demo/parser_scripts/` | 15,325 |
| `mmw_demo_example_script.py` | `.../ti/demo/parser_scripts/` | 6,282 |
| `data_parser_awr2x44x.py` | `.../ti/demo/parser_scripts/` | 8,447 |

#### Documentation
| File | Path | Size |
|------|------|------|
| `mmwave_mcuplus_sdk_user_guide.pdf` | `.../docs/` | 25,354,478 |
| `mmwave_mcuplus_sdk_release_notes.pdf` | `.../docs/` | 169,990 |
| `mmWave_Demo_Visualizer_UserGuide.pdf` | `.../docs/` | 1,158,386 |
| `TI_DCA1000EVM_CLI_Software_UserGuide.pdf` | `.../ReferenceCode/DCA1000/Docs/` | 1,588,627 |
| `TI_DCA1000EVM_CLI_Software_DeveloperGuide.pdf` | `.../ReferenceCode/DCA1000/Docs/` | 351,479 |
| `DCA1000_Quick_Start_Guide.pdf` | `.../docs/` | 175,668 |
| `DCA1000_Debugging_Handbook.pdf` | `.../docs/` | 83,191 |
| mmw Demo Doxygen HTML | `.../demo/awr294x/mmw/docs/doxygen/html/index.html` | 51,105 |

### NOT Found (Option A components)
| Item | Status |
|------|--------|
| `mmwave_studio_cli.exe` | **MISSING** — Not in SDK, mmWave Studio, or CCS |
| `mmwave_studio_cli_awr29xx.appimage` | **MISSING** — Not in SDK |
| Any `*studio*cli*.appimage` | **MISSING** |
| TI Radar Toolbox installation | **MISSING** |
| UniFlash standalone installer | **MISSING** (SDK provides `uart_uniflash.py` instead) |

---

## 2. Documentation Findings

### Q1: Does this SDK officially support AWR2944?
**YES**. The SDK contains pre-built AWR2944 appimages, AWR2944-specific profiles,
and AWR2944-specific documentation. See `ti/demo/awr294x/mmw/`.

### Q2: Does it contain the Studio CLI host executable?
**NO**. The Studio CLI host tool is part of TI **Radar Toolbox**, which is a
separate download/installation. It is not included in the MMWAVE-MCUPLUS-SDK.

### Q3: Does it contain the AWR29xx Studio CLI device appimage?
**NO**. Same as above — Radar Toolbox component.

### Q4: Is the host executable supplied by Radar Toolbox?
**YES**. The mmWave Studio CLI is distributed as part of TI Radar Toolbox.
See: https://www.ti.com/tool/MMWAVE-RADAR-TOOLBOX

### Q5: What exact firmware image is prescribed for AWR2944?
For headless LVDS capture: **`awr2944_mmw_demoTDM.appimage`**
- Full path: `C:\ti\mmwave_mcuplus_sdk_04_07_02_01\mmwave_mcuplus_sdk_04_07_02_01\ti\demo\awr294x\mmw\awr2944_mmw_demoTDM.appimage`
- Size: 408,528 bytes

### Q6: COM port identification
From Windows PnP device enumeration:

| Port | Device | VID:PID | Role |
|------|--------|---------|------|
| COM8 | XDS110 Class Application/User UART | 0451:BEF3 | **Primary CLI/flash port** |
| COM7 | XDS110 Class Auxiliary Data Port | 0451:BEF3 | Data/debug port |
| COM3 | AR-DevPack-EVM-012 | 0451:FD03 | FTDI port A |
| COM4 | AR-DevPack-EVM-012 | 0451:FD03 | FTDI port B |
| COM5 | AR-DevPack-EVM-012 | 0451:FD03 | FTDI port C |
| COM6 | AR-DevPack-EVM-012 | 0451:FD03 | FTDI port D |

> **Note**: COM7 and COM8 show "Unknown" status — they may need a power cycle
> or driver reconnect. COM3-6 (FTDI AR-DevPack) are OK.

The SDK docs say: "We use the 'Application/User' USB serial port" for flashing
and CLI — that is **COM8** (XDS110 Application/User UART).

### Q7: Baud rate and serial framing
**115200 baud, 8N1** (8 data bits, no parity, 1 stop bit)
- Source: EVM_SETUP_PAGE.html § "Setup UART Terminal"

### Q8: Configuration file format
Plain text `.cfg` file with one CLI command per line. Comments use `%`.
Commands include `sensorStop`, `flushCfg`, `profileCfg`, `chirpCfg`,
`frameCfg`, `lvdsStreamCfg`, `sensorStart`, etc.
- Source: `profile_LVDS.cfg` and mmw demo doxygen

### Q9: DCA1000 configuration file
JSON format, named `cf.json`. Current working config at:
`C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc\cf.json`

Key fields: `dataLoggingMode`, `dataTransferMode`, `lvdsMode`,
`ethernetConfig` (DCA IP, config port, data port),
`captureConfig` (file path, prefix, max size, stop mode).

### Q10: Host tool capabilities
The **mmw demo** (Option B) supports via UART CLI:
- ✅ Radar configuration (profileCfg, chirpCfg, frameCfg, etc.)
- ✅ LVDS streaming enable (lvdsStreamCfg)
- ✅ Start/stop sensor (sensorStart/sensorStop)
- ❌ DCA configuration — managed separately by DCA CLI tools
- ❌ Raw ADC output path — managed by DCA CLI `cf.json`
- ❌ Post-processing — done offline with parser scripts

### Q11: LVDS lane count/mode for AWR2944
From `profile_LVDS.cfg` line 38: `lvdsStreamCfg -1 0 1 0`
- `-1` = applies to all subframes
- `0` = HSI header disabled
- `1` = HW data format: ADC data (raw ADC samples)
- `0` = SW data disabled

From the documentation (§ "Streaming data over LVDS"):
AWR294x supports 2-lane LVDS at up to 600 Mbps per lane.
The inter-chirp time must be sufficient: `Tc * n * B / 8 >= numAdcSamples * numRxChannels * 4`

### Q12: SOP states
From EVM_SETUP_PAGE.html:

| Mode | SOP0 | SOP1 | SOP2 | Purpose |
|------|------|------|------|---------|
| **UART Boot** | Short | Open | Short | Flash firmware via `uart_uniflash.py` |
| **QSPI Boot** | Short | Open | Open | Normal boot from flash |
| **No Boot** | Short | Short | Open | CCS/JTAG debug (GEL files) |

### Q13: UniFlash procedure
The SDK uses a **Python-based** UART flash script, NOT TI UniFlash GUI:
```
cd <SDK_INSTALL_PATH>/tools/boot
python uart_uniflash.py -p COM8 --cfg=<flash_config>.cfg
```
The flash config `.cfg` file specifies:
1. Flash writer: `sbl_uart_uniflash.release.tiimage`
2. Bootloader: `sbl_qspi.release.tiimage` at offset 0x0
3. Application: `<appimage>` at offset 0xA0000

### Q14: Does flashing replace the current board application?
**YES**. Flashing overwrites QSPI flash. The docs explicitly warn:
> "Flashing an application will overwrite the SOC init application that was
> flashed earlier."

**Restore procedure**: Re-flash the original image. For CCS debug, flash
`awr2944_ccsdebug.appimage`. For mmWave Studio, the Studio has its own
firmware loading procedure via RSTD/SPI.

### Q15: Official sample AWR2944+DCA1000 config?
**YES**: `profile_LVDS.cfg` in `profiles/tdm_awr2944/` is the official sample
for LVDS streaming. However, it uses different chirp parameters than our
validated smoke_v1 config. We can create a custom `.cfg` with our parameters
plus `lvdsStreamCfg`.

---

## 3. Hardware/Port Inventory (Read-Only)

### COM Ports
| Port | Status | Name | VID:PID |
|------|--------|------|---------|
| COM1 | Unknown | Communications Port | ACPI PNP0501 |
| COM3 | OK | AR-DevPack-EVM-012 | 0451:FD03 (FTDI) |
| COM4 | OK | AR-DevPack-EVM-012 | 0451:FD03 (FTDI) |
| COM5 | OK | AR-DevPack-EVM-012 | 0451:FD03 (FTDI) |
| COM6 | OK | AR-DevPack-EVM-012 | 0451:FD03 (FTDI) |
| COM7 | Unknown | XDS110 Auxiliary Data Port | 0451:BEF3 |
| COM8 | Unknown | XDS110 Application/User UART | 0451:BEF3 |

**Likely CLI port**: COM8 (XDS110 Application/User UART)

### Network Adapters
| Name | Description | Status | MAC | Link |
|------|-------------|--------|-----|------|
| Ethernet | Intel I219-LM | Up | 00:BE:43:93:FC:49 | 1 Gbps |
| **Ethernet 5** | ASIX AX88179 USB 3.0 | Up | 9C:69:D3:99:F4:3F | 1 Gbps |

### DCA1000 Network Configuration
| Parameter | Current Value | Expected |
|-----------|---------------|----------|
| Host adapter | Ethernet 5 | ✅ Match |
| Host IP | 192.168.33.30/24 | ✅ Match |
| DCA IP (from cf.json) | 192.168.33.180 | ✅ Match |
| Config port | 4096 | ✅ Match |
| Data port | 4098 | ✅ Match |

---

## 4. Option A Feasibility Matrix

| Requirement | Status | Notes |
|-------------|--------|-------|
| Studio CLI Windows host executable | ❌ **MISSING** | Not in SDK; part of Radar Toolbox |
| AWR2944/AWR29xx CLI appimage | ❌ **MISSING** | Not in SDK; part of Radar Toolbox |
| Official AWR2944 sample radar config | ❌ **MISSING** | Studio CLI uses different format |
| DCA1000 host components | ✅ PASS | DCA CLI tools present in mmWave Studio |
| Documented AWR2944 flash procedure | ✅ PASS | uart_uniflash.py |
| Documented functional boot procedure | ✅ PASS | SOP states documented |
| Required COM port identifiable | ✅ PASS | COM8 (XDS110 App/User) |
| Raw ADC output format documented | ✅ PASS | Via DCA CLI user guide |
| First capture without compiling firmware | ❌ **BLOCKED** | Need Radar Toolbox CLI appimage |
| Post-processing available | ✅ PASS | Parser scripts included |

### Missing Package for Option A
| Item | Value |
|------|-------|
| Package name | **TI MMWAVE-RADAR-TOOLBOX** |
| Expected version | Latest compatible with AWR2944 |
| Download | https://www.ti.com/tool/MMWAVE-RADAR-TOOLBOX |
| Installation | Side-by-side with existing SDK — no conflicts expected |
| Contains | `mmwave_studio_cli.exe`, `mmwave_studio_cli_awr29xx.appimage` |

**Option A verdict: NOT READY. Requires installing Radar Toolbox first.**

---

## 5. Option B Feasibility Matrix

| Requirement | Status | Notes |
|-------------|--------|-------|
| Pre-built AWR2944 appimage with LVDS | ✅ PASS | `awr2944_mmw_demoTDM.appimage` |
| UART CLI for radar config | ✅ PASS | profileCfg, chirpCfg, frameCfg, lvdsStreamCfg |
| ADCBUF support | ✅ PASS | ADC buffer configured via adcbufCfg command |
| CBUFF/LVDS raw streaming | ✅ PASS | lvdsStreamCfg enables raw ADC over LVDS |
| DCA1000 capture | ✅ PASS | DCA CLI tools + cf.json present |
| sensorStart/sensorStop CLI | ✅ PASS | Standard demo commands |
| Sample LVDS .cfg | ✅ PASS | `profile_LVDS.cfg` in tdm_awr2944/ |
| Flash procedure documented | ✅ PASS | uart_uniflash.py + documented SOP states |
| COM port identifiable | ✅ PASS | COM8 |
| No recompilation needed | ✅ PASS | Pre-built appimage included |
| Parser scripts | ✅ PASS | `parser_mmw_demo.py`, `data_parser_awr2x44x.py` |

### Execution Sequence (Option B)
1. **Flash** (one-time, requires UART boot mode SOP):
   ```
   cd C:\ti\mmwave_mcuplus_sdk_04_07_02_01\mcu_plus_sdk_awr294x_10_02_00_04\tools\boot
   python uart_uniflash.py -p COM8 --cfg=<custom_flash.cfg>
   ```
   Where `<custom_flash.cfg>` points to `awr2944_mmw_demoTDM.appimage`.

2. **Boot** (switch SOP to QSPI boot, power cycle).

3. **Configure radar** (send .cfg commands over COM8 at 115200):
   ```
   sensorStop
   flushCfg
   dfeDataOutputMode 1
   channelCfg 15 7 0
   adcCfg 2 0
   adcbufCfg -1 1 1 1 1
   profileCfg ...
   chirpCfg ...
   frameCfg ...
   lvdsStreamCfg -1 0 1 0
   ```

4. **Arm DCA1000** (separate process):
   ```
   DCA1000EVM_CLI_Control.exe fpga_config cf.json
   DCA1000EVM_CLI_Record.exe start cf.json
   ```

5. **Start sensor** (over UART):
   ```
   sensorStart
   ```

6. **Stop** (after capture):
   ```
   sensorStop
   DCA1000EVM_CLI_Record.exe stop cf.json
   ```

**Option B verdict: READY. All components present. Only needs flashing.**

---

## 6. Config Mapping: smoke_v1 → SDK CLI Format

### Our Validated Parameters
| Parameter | Value |
|-----------|-------|
| Start frequency | 77 GHz |
| Idle time | 100 µs |
| ADC start time | 6 µs |
| Ramp end time | 60 µs |
| Frequency slope | 29.982 MHz/µs |
| ADC samples | 256 |
| Sample rate | 10000 ksps |
| RX gain | 30 dB |
| Chirp start/end index | 0 to 0 |
| TX selection | per smoke_v1 |
| Frames | 8 |
| Loops per frame | 128 |
| Frame period | 40 ms |
| Expected raw bytes | 4,194,304 |
| ADC shape | [8, 128, 4, 256] |

### SDK CLI Command Mapping

**`profileCfg` syntax** (from mmw_cli.c registration):
```
profileCfg <profileId> <startFreq_GHz> <idleTime_us> <adcStartTime_us> <rampEndTime_us>
           <txOutPower> <txPhaseShifter> <freqSlopeConst_MHz/us> <txStartTime_us>
           <numAdcSamples> <digOutSampleRate_ksps> <hpfCornerFreq1> <hpfCornerFreq2>
           <rxGain_dB>
```

Our mapping:
```
profileCfg 0 77 100 6 60 0 0 29.982 0 256 10000 0 0 30
```
> **CONFIDENCE: HIGH** — syntax matches `profile_LVDS.cfg` structure.

**`chirpCfg` syntax**:
```
chirpCfg <startIdx> <endIdx> <profileId> <startFreqVar> <freqSlopeVar>
         <idleTimeVar> <adcStartTimeVar> <txEnable>
```

For single chirp (index 0), TX0 enabled:
```
chirpCfg 0 0 0 0 0 0 0 1
```
> **CONFIDENCE: HIGH** — matches sample profiles.

**`frameCfg` syntax**:
```
frameCfg <chirpStartIdx> <chirpEndIdx> <numLoops> <numFrames>
         <framePeriodicity_ms> <triggerSelect> <frameTriggerDelay_ms> <padding>
```

Our mapping:
```
frameCfg 0 0 128 8 40 0 0 0
```
> **CONFIDENCE: MEDIUM** — frame count=8 is finite. The `framePeriodicity_ms` of
> 40ms with 128 loops needs verification against the chirp timing budget.

**`lvdsStreamCfg` for raw ADC**:
```
lvdsStreamCfg -1 0 1 0
```
> **CONFIDENCE: HIGH** — matches official `profile_LVDS.cfg`.

**LVDS bandwidth check** (from docs):
- Chirp time Tc = idle + ramp = 100 + 60 = 160 µs
- 2 lanes × 600 Mbps = 1200 Mbps = 150 MB/s
- Per-chirp data: 256 samples × 4 RX × 4 bytes = 4096 bytes
- Max bytes in Tc: 160 × 2 × 600 / 8 = 24,000 bytes
- 24,000 >> 4,096 → ✅ **PASSES bandwidth check**

### Items Marked UNKNOWN
| Item | Reason |
|------|--------|
| `channelCfg` RX/TX mask | Depends on which TX antennas smoke_v1 uses. Our mmWave Studio config used `ar1.ChannelConfig` with specific masks. Need to verify the exact TX enable bits. |
| `adcCfg` format | Value `2` = complex 2x (I/Q interleaved). Matches our mmWave Studio config but should be verified. |
| `dfeDataOutputMode` | Value `1` = frame-based chirps (legacy frame). Should be correct for our use case. |
| Frame periodicity budget | 40ms for 128 chirps × 160µs each = 20.48ms active. 40ms total allows ~19.5ms inter-frame. Should work. |

---

## 7. Unresolved Risks

1. **COM8 shows "Unknown" status** — May need EVM power cycle before first use.
2. **Flashing is destructive** — Replaces whatever is currently on the AWR2944.
   Restore by re-flashing the ccsdebug appimage or mmWave Studio firmware.
3. **DCA1000 MAC address mismatch** — `cf.json` has `12.34.56.78.90.12` but
   the known DCA MAC is `0C:22:38:4E:5A:0C`. The `cf.json` needs to be updated
   before use. (The `ethernetConfigUpdate` section may need to match actual DCA MAC.)
4. **channelCfg TX mask** — Must match our smoke_v1 TX configuration exactly.
   Wrong TX mask will produce incorrect ADC data shape.
5. **First-time LVDS streaming** — The demo has been tested with Visualizer but
   not yet with our raw capture pipeline. The ADC data format from LVDS may differ
   slightly from what mmWave Studio produces.

---

## 8. Physical Steps (When User Returns)

### Immediate Next 5 Steps
1. **Verify COM8 works**: Open a terminal (PuTTY/Tera Term) to COM8 at 115200 8N1.
   Power cycle the AWR2944 EVM. You should see boot messages or nothing (if in
   mmWave Studio mode). Close the terminal afterward.

2. **Create flash config**: Copy `default_sbl_qspi.cfg` and modify to point
   `--file=` at `awr2944_mmw_demoTDM.appimage` at offset 0xA0000.

3. **Set UART boot SOP**: Power OFF. Set SOP0=Short, SOP1=Open, SOP2=Short.
   Power ON. Verify "C" characters appear on COM8.

4. **Flash the demo**: Run:
   ```
   cd C:\ti\mmwave_mcuplus_sdk_04_07_02_01\mcu_plus_sdk_awr294x_10_02_00_04\tools\boot
   python uart_uniflash.py -p COM8 --cfg=<our_flash.cfg>
   ```

5. **Switch to QSPI boot**: Power OFF. Set SOP0=Short, SOP1=Open, SOP2=Open.
   Power ON. Connect terminal to COM8. Send the LVDS .cfg commands.
   Verify "sensorStart" succeeds.

### Rollback Procedure
To restore mmWave Studio operation:
1. Set UART boot SOP
2. Flash `awr2944_ccsdebug.appimage` (or appropriate mmWave Studio firmware)
3. Switch back to QSPI boot SOP
4. Re-launch mmWave Studio as before

---

## 9. Citations

All paths relative to `C:\ti\mmwave_mcuplus_sdk_04_07_02_01`:

| Topic | Source |
|-------|--------|
| mmw Demo overview | `mmwave_mcuplus_sdk_04_07_02_01/ti/demo/awr294x/mmw/docs/doxygen/html/index.html` § "Introduction" |
| LVDS streaming | Same file § "Streaming data over LVDS" |
| lvdsStreamCfg syntax | Same file § "Streaming data over LVDS" + `mss/mmw_cli.c` line 2227 |
| CLI command table | `mss/mmw_cli.c` lines 2100-2270 |
| Boot modes/SOP | `mcu_plus_sdk_awr294x_10_02_00_04/docs/api_guide_awr294x/EVM_SETUP_PAGE.html` § "BOOT MODE" |
| Flash procedure | `mcu_plus_sdk_awr294x_10_02_00_04/docs/api_guide_awr294x/GETTING_STARTED_FLASH.html` |
| UART terminal setup | `EVM_SETUP_PAGE.html` § "Setup UART Terminal" |
| DCA CLI config format | `C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\PostProc\cf.json` |
| DCA CLI user guide | `C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\ReferenceCode\DCA1000\Docs\TI_DCA1000EVM_CLI_Software_UserGuide.pdf` |
