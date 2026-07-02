# mmWave Studio API Probe

## Overview

The `awr ti probe --offline` command tests whether we can automate mmWave Studio locally via Lua without connecting to hardware. Due to limitations in the TI mmWave Studio CLI headless mode, automation may fail or hang.

If `awr ti probe` reports `PARTIAL` or `FAIL`, you must execute the generated Lua scripts manually.

## Manual Fallback Execution

If automated headless execution hangs, you can manually run the generated scripts in the mmWave Studio Lua Shell.

1. Generate the probe and get the copy command:
   ```bash
   awr ti probe --offline
   awr ti lua-command ti/probe_logs/probe.lua --copy
   ```
2. Open **mmWave Studio** and paste the command into the **Lua Shell** tab.
3. Check the results in the CLI:
   ```bash
   awr ti probe-status
   ```
4. If successful, extract the API inventory:
   ```bash
   awr ti inventory --offline
   awr ti lua-command ti/probe_logs/inventory.lua --copy
   ```
5. Paste into the mmWave Studio **Lua Shell**.
6. Check the extracted inventory:
   ```bash
   awr ti inventory-status
   ```

## Warning: Hardware Actions

Do not run Lua scripts containing hardware actions (`ar1.Connect`, `ar1.PowerOn`, etc.) unless you are actively performing a capture and have reviewed the parameters. Use `awr ti run-lua <script> --offline` to statically scan a script for dangerous actions before attempting to run it.
