# External mmWave Studio Automation Patterns

This document tracks known working automation patterns for TI's mmWave Studio and the DCA1000EVM capture card, mined from open-source repositories and official TI examples. The goal is to adopt robust communication logic without blindly copying scripts meant for different firmware/hardware.

---

## 1. TI E2E / MATLAB Examples (Local Installation)

**Source:** `C:\ti\mmwave_studio_*\mmWaveStudio\MatlabExamples\Init_RSTD_Connection.m`
**Mechanism:** RSTD .NET Remoting API (`RtttNetClientAPI.dll`)

**Patterns Found:**
- Requires mmWave Studio to run with `RSTD.NetStart()`, opening TCP port `2777`.
- The mandated `.NET` connection sequence is:
  1. `RtttNetClient.Init()`
  2. `RtttNetClient.Connect('127.0.0.1', 2777)`
  3. `RtttNetClient.SendCommand(lua_command_string)`
- `SendCommand` returns `30000` on successful **submission** only. It does not indicate that the Lua script succeeded, only that RSTD accepted the command over TCP.

**What we should adopt now:**
- Adopt the strict `Init()` -> `Connect()` -> `SendCommand()` flow.
- Acknowledge that `30000` is submission only, and rely on `.json` files written by the Lua script to verify actual success.

---

## 2. DingdongD/RadarConfigure

**Source:** [DingdongD/RadarConfigure](https://github.com/DingdongD/RadarConfigure)
**Mechanism:** Automation wrappers over PyAutoGUI and RSTD.

**Patterns Found:**
- Explicit COM port identification heuristic: "XDS110 Class Application/User UART" maps to RS232 (Application port) while "Data" maps to the Auxiliary port.
- Emphasizes SOP Mode 4 (functional) vs SOP Mode 2 (development/flashing).
- Device configurations differ across radar variants (e.g., IWR1443 vs IWR1642 vs IWR6843).

**What we should adopt now:**
- The logic for aggressively identifying the exact COM port using OS-level names like "XDS110 Class Application/User UART" (this validates our `ports.py` heuristic).

**What to save for later:**
- Firmware path distinctions based on exact board type. Do not hardcode firmware names, leave them to `capture.yaml`.

---

## 3. DingdongD/SIMFNet

**Source:** [DingdongD/SIMFNet](https://github.com/DingdongD/SIMFNet)
**Mechanism:** Python-to-mmWave-Studio via `RtttNetClient.SendCommand("dofile(...)")`.

**Patterns Found:**
- Heavy reliance on `dofile("C:\\path\\DataCaptureDemo.lua")`.
- Structured sequence for initiating captures: `CaptureCardConfig_StartRecord` must precede `StartFrame`.

**What we should adopt now:**
- Using `dofile()` inside `SendCommand` is the industry-standard way to execute large blocks of Lua without escaping issues.

**What to save for later:**
- The staging flow for `StartRecord` vs `StartFrame` is critical, but we should map it systematically using our `workflow-map` rather than hardcoding this specific repository's exact delay timings.

---

## 4. EsonJohn/mmWave_script

**Source:** [EsonJohn/mmWave_script](https://github.com/EsonJohn/mmWave_script)
**Mechanism:** Headless DCA1000 configuration (Bypassing mmWave Studio).

**Patterns Found:**
- mmWave Studio is completely bypassed.
- Uses a compiled `DCA1000EVM_CLI_Control.exe` and `DCA1000EVM_CLI_Record.exe` built via MinGW to control the DCA1000 directly.
- The radar board (IWR1642BOOST) is triggered by a separate Python script after flashing the `mmWave_Demo` firmware and booting into SOP 4.

**What to save for later:**
- If we ever drop mmWave Studio entirely, we will need to adopt this headless C++/CLI architecture for the DCA1000. For this milestone, we are explicitly keeping mmWave Studio as the execution backend.

---

## 5. mmwave-capture-std

**Source:** [mmwave-capture-std](https://github.com/mmwave-capture-std)
**Mechanism:** Python-centric architecture with separated hardware interfaces.

**Patterns Found:**
- Decouples the radar interface from the DCA1000 interface.
- Employs a `CaptureManager` to synchronize the two.
- Optimized raw data parsing directly to `np.ndarray[np.complex64]`.

**What to save for later:**
- Our long-term architecture aligns closely with this: a Python/Jupyter control layer (our `.venv` and `capture.yaml`), with a decoupled radar backend (currently mmWave Studio, maybe direct later) and a decoupled DCA interface. We will adopt their separation of concerns for the eventual data parsing layer.
