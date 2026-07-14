# Phase 5B: AWR2944 Flash Procedure

> **STOP GATE**: This document is a reference. DO NOT execute any step without
> explicit user confirmation at each gate.

## Prerequisites

| Item | Status |
|------|--------|
| MMWAVE-MCUPLUS-SDK 04.07.02.01 installed | ✅ Verified |
| `uart_uniflash.py` dependencies (`pyserial`, `tqdm`, `xmodem`) installed | ⬜ Verify before flash |
| XDS110 USB cable connected to AWR2944EVM J13 | ⬜ Verify before flash |
| COM port identified via PnP (candidate COM8, always rediscover) | ⬜ Runtime discovery |

## SOP Jumper Reference

Source: `EVM_SETUP_PAGE.html` § "BOOT MODE" (MCU+ SDK docs)

| Mode | SOP0 (J26) | SOP1 (J23) | SOP2 (J24) | Binary | Use Case |
|------|-----------|-----------|-----------|--------|----------|
| UART Boot | Short | Open | Short | 101 | Flashing via `uart_uniflash.py` |
| QSPI Boot | Short | Open | Open | 001 | Normal operation (boot from flash) |
| No-Boot/Debug | Short | Short | Open | 011 | CCS JTAG debug / mmWave Studio development |

> **mmWave Studio development mode**: Studio normally downloads firmware to RAM
> via RSTD/SPI when in no-boot (011) mode. It does NOT require QSPI restoration
> to return to Studio use — simply set SOP to 011 and restart.

## Flash Sequence

### What Gets Flashed

| Stage | What | Where | Purpose |
|-------|------|-------|---------|
| 1 | `sbl_uart_uniflash.release.tiimage` | **RAM only** (temporary) | XMODEM server to receive subsequent flash images |
| 2 | `sbl_qspi.release.tiimage` | **QSPI offset 0x0** | Secondary bootloader (ROM loads this on QSPI boot) |
| 3 | `awr2944_mmw_demoTDM.appimage` | **QSPI offset 0xA0000** | mmw demo TDM application |

> **The flash writer (stage 1) is NOT persisted to QSPI.** It is loaded
> temporarily into RAM to serve as the XMODEM receiver. After power cycle,
> it is gone. Only the SBL and appimage are permanently written to QSPI flash.

### Step-by-Step Procedure

#### Gate 1: SOP Configuration
```
⚠️  STOP — Confirm before proceeding

1. Power OFF the AWR2944EVM
2. Set SOP jumpers to UART boot mode:
   - SOP0 (J26): SHORT (jumper installed)
   - SOP1 (J23): OPEN  (jumper removed)
   - SOP2 (J24): SHORT (jumper installed)
   Binary: 101

3. Confirm: "SOP jumpers are set to 101 (UART boot)"
```

#### Gate 2: Connection
```
⚠️  STOP — Confirm before proceeding

1. Connect USB cable to J13 (XDS110 USB)
2. Power ON the AWR2944EVM
3. Run serial port discovery to identify the Application/User UART port
4. Confirm: "XDS110 Application/User UART identified as COM<N>"
```

#### Gate 3: Flash Execution
```
⚠️  STOP — Confirm before proceeding

Run the flash command:

python "C:\ti\mmwave_mcuplus_sdk_04_07_02_01\mcu_plus_sdk_awr294x_10_02_00_04\tools\boot\uart_uniflash.py" \
    -p COM<N> \
    --cfg="<path_to_flash_config>.cfg"

The flash config file should contain:
    --flash-writer=<path>/sbl_uart_uniflash.release.tiimage
    --file=<path>/sbl_qspi.release.tiimage --operation=flash --flash-offset=0x0
    --file=<path>/awr2944_mmw_demoTDM.appimage --operation=flash --flash-offset=0xA0000

Expected output: "[STATUS] SUCCESS !!!" for each file.

Confirm: "All files flashed successfully"
```

#### Gate 4: SOP Restore
```
⚠️  STOP — Confirm before proceeding

1. Power OFF the AWR2944EVM
2. Set SOP jumpers to QSPI boot mode:
   - SOP0 (J26): SHORT (jumper installed)
   - SOP1 (J23): OPEN  (jumper removed)
   - SOP2 (J24): OPEN  (jumper removed)
   Binary: 001

3. Power ON the AWR2944EVM
4. Confirm: "SOP jumpers are set to 001 (QSPI boot)"
```

#### Gate 5: Boot Verification
```
⚠️  STOP — Confirm before proceeding

1. Open a serial terminal at 115200 baud, 8N1 on the Application/User UART
2. You should see the mmw demo boot banner
3. The CLI prompt "mmwDemo:/>" should appear
4. Send "help" — the demo should list available commands
5. Confirm: "mmw demo CLI is responsive"
```

## SHA256 Hashes

| File | SHA256 | Size |
|------|--------|------|
| `uart_uniflash.py` | `F17FBADE...` | 30,387 B |
| `sbl_uart_uniflash.release.tiimage` | `67A09339...` | 58,513 B |
| `sbl_qspi.release.tiimage` | `A0013902...` | 68,321 B |
| `awr2944_mmw_demoTDM.appimage` | `5B4444B1...` | 408,528 B |

Full hashes are recorded in `flash_plan.local.json`.

## Rollback Procedures

### Return to mmWave Studio Development Mode
mmWave Studio normally downloads firmware to RAM. No QSPI restoration is needed.

1. Power OFF the EVM
2. Set SOP to no-boot/debug mode: SOP0=short, SOP1=short, SOP2=open (011)
3. Power ON the EVM
4. Launch mmWave Studio — it downloads firmware to RAM via RSTD/SPI

### Restore a Previous QSPI Application
To flash a different appimage:

1. Power OFF the EVM
2. Set SOP to UART boot: SOP0=short, SOP1=open, SOP2=short (101)
3. Power ON the EVM
4. Run `uart_uniflash.py` with a config pointing to the desired appimage
5. Set SOP back to QSPI boot (001)
6. Power cycle

### CCS/JTAG Debug Mode
No flashing needed.

1. Power OFF the EVM
2. Set SOP to no-boot/debug: SOP0=short, SOP1=short, SOP2=open (011)
3. Power ON the EVM
4. Connect CCS via XDS110 JTAG
