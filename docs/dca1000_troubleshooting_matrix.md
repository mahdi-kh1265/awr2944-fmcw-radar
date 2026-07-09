# DCA1000 Troubleshooting Matrix

Use this matrix during the first DCA1000 capture attempt. Prefer the safest next action that
preserves evidence and avoids changing AWR RF state unless the step explicitly requires it.

| Symptom | Likely cause | What to check | Safe next action | Power-cycle guidance |
| --- | --- | --- | --- | --- |
| DCA ping fails | DCA1000 is unpowered, Ethernet is disconnected, the wrong PC adapter is active, or the PC is not on the `192.168.33.0/24` subnet | DCA1000 power LEDs, Ethernet link LEDs, cable seating, Windows adapter list, PC static IP `192.168.33.30/24`, ping to `192.168.33.180` | Fix power/cabling/IP and rerun `awr dca preflight` only | Power-cycle DCA1000 if link/IP looks correct but ping still fails. Do not power-cycle AWR or mmWave Studio for this symptom alone |
| PC missing `192.168.33.30` | Static IPv4 address is missing or assigned to the wrong adapter | Windows adapter IPv4 settings, route table, disabled/enabled network interfaces | Assign `192.168.33.30/24` to the DCA1000 adapter, keep only the intended DCA path active if possible, rerun preflight | No power-cycle needed |
| Setup `EthInit` fails | DCA network path is not ready, firewall blocks UDP, DCA1000 is in stale state, or wrong adapter is selected | DCA ping, Windows firewall/profile, adapter metrics, DCA LEDs, previous setup/capture state | Preserve logs, fix network/firewall, rerun setup Lua after preflight passes | Power-cycle DCA1000 if repeated after network checks. AWR power-cycle is not the first action |
| `StartRecord` fails | DCA setup did not complete, recording path is invalid, stale recording state remains, or old files/path permissions interfere | `generate-setup` run result, `C:\ti\mmwave_studio\PostProc` existence, old `adc_data*.bin`, DCA state in mmWave Studio output | Move/delete old capture files, rerun setup, then rerun capture only after setup passes | Power-cycle DCA1000 if stale recording state persists. Avoid AWR power-cycle unless capture trigger also fails |
| `StartFrame` fails | AWR is not connected, firmware/config state changed, RF state is not armed, or generated capture Lua does not match the validated configuration | mmWave Studio connection, latest guided validation run IDs, capture Lua contents, run result error text | Stop. Preserve logs. Re-run guided validation or reconnect mmWave Studio before another capture attempt | Power-cycle AWR/mmWave Studio only if reconnect/revalidation requires it. DCA power-cycle only if DCA state is also suspect |
| No `adc_data_Raw_0.bin` | DCA did not record, capture trigger did not reach DCA, output path was wrong, or files were written elsewhere | Setup result, capture result, DCA LEDs, PostProc path, file timestamps, mmWave Studio output | Preserve probe logs, confirm output path, rerun setup before any new capture | Power-cycle DCA1000 if setup/capture claim success but no raw file appears twice. AWR power-cycle only after preserving evidence |
| Raw exists but `adc_data.bin` missing | Post-processing did not run, post-processing failed, MATLAB/postproc dependency issue, or raw file is incomplete | Raw file timestamp/size, post-processing console/log output, `C:\ti\mmwave_studio\PostProc`, generated Lua postproc commands | Preserve raw file. Rerun post-processing only if it will not overwrite evidence, otherwise move raw aside first | No board power-cycle needed for post-processing-only failures |
| `adc_data.bin` wrong size | Wrong capture parameters, partial capture, stale file, post-processing used old raw data, or check used wrong expected bytes | `adc_data.bin` timestamp, `adc_data_Raw_0.bin` timestamp, expected `524288` bytes, validation/config run IDs, old files in PostProc | Move current files aside, preserve logs, rerun from preflight and setup | Power-cycle only after repeated wrong-size captures with clean file handling |
| File all zeros | RF scene/config produced no useful samples, capture triggered before useful data, AWR/RF config issue, or post-processing misread raw data | Quick binary inspection, target scene, AWR config validation, capture timing, whether raw file also appears zero-like | Preserve files. Do not overwrite. Re-run guided validation before another capture | AWR/mmWave Studio power-cycle may be appropriate after preserving evidence. DCA power-cycle is secondary unless recording state is suspect |
| Stale old capture file suspected | Old `adc_data*.bin` files were not moved/deleted before capture or timestamps are ambiguous | File modified times, file sizes before/after capture, operator notes, PostProc directory screenshot | Stop and preserve current files separately. Clean PostProc, rerun capture sequence from preflight | No power-cycle needed unless other failures are present |

## Evidence Before Retry

Before any retry after a failure, preserve the probe logs:

```powershell
python tools/collect_probe_artifacts.py --probe-dir C:\Users\khams008\Documents\awr2944-fmcw-radar\exp_lau_probe\ti\probe_logs --out artifacts\dca_attempt_bundle.zip
```

```powershell
python tools/report_probe_bundle.py --bundle artifacts\dca_attempt_bundle.zip --out artifacts\dca_attempt_report.md
```

Move raw capture files to a separate evidence folder before deleting or rerunning. Raw `.bin` files
are not included in the probe bundle by default.