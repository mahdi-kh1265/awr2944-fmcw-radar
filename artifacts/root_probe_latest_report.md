# Probe Bundle Report

## Bundle Metadata
- Bundle path: `C:\Users\khams008\Documents\awr2944-codex-sidequest\artifacts\root_probe_latest_bundle.zip`
- Number of files: 10
- bundle_manifest.json exists: yes
- SHA256 hashes are present: yes
- Raw .bin files present: no

## Best Validation Found
- No post-connection validation record found.

## Guided Workflow States
### `guided_5a56e9db_state.json`
- workflow_id: 5a56e9db
- label: First guided-runner hardware validation
- current_stage: failed
- firmware_run_id: 68222a75
- config_run_id: -
- dry_run: no
- hardware_touched: no
- lua_generated: yes
- validation_recorded: no
- errors: firmware_validated failed: Firmware run failed or timed out.
#### Linked Artifacts
- linked firmware result found: yes
- linked firmware progress found: yes
- linked config result found: no
- linked config progress found: no
- unrelated artifacts ignored: 2
### `guided_a6321c61_state.json`
- workflow_id: a6321c61
- label: final dry-run before guided hardware validation
- current_stage: failed
- firmware_run_id: -
- config_run_id: -
- dry_run: yes
- hardware_touched: no
- lua_generated: no
- validation_recorded: no
- errors: session_summarized failed: [WinError 5] Access is denied: 'ti\\probe_logs\\guided_a6321c61_state.json.tmp' -> 'ti\\probe_logs\\guided_a6321c61_state.json'
#### Linked Artifacts
- linked firmware result found: no
- linked firmware progress found: no
- linked config result found: no
- linked config progress found: no
- unrelated artifacts ignored: 5

## Run Results
### `68222a75_firmware_power_result.json`
- run_id: 68222a75
- stage: firmware_power
- success: yes
- error: -
- warnings: none
### `manual_check_result.json`
- run_id: manual_check
- stage: manual_check
- success: -
- error: -
- warnings: -

## Progress Logs
### `68222a75_firmware_power_progress.jsonl`
- run_id: 68222a75
- command count: 10
- failed command count: 0
- hardware commands observed: PowerOn, RfEnable
- last command: GetBSSPatchFwVersion
### `manual_check_progress.jsonl`
- run_id: manual_check
- command count: 2
- failed command count: 0
- hardware commands observed: none
- last command: -

## Validation Records
- No validation records found.

## Suspicious Findings
- Guided state guided_5a56e9db_state.json failed but linked result 68222a75_firmware_power_result.json reports success=true
- Guided state guided_5a56e9db_state.json has hardware_touched=false but linked progress 68222a75_firmware_power_progress.jsonl contains hardware commands: PowerOn, RfEnable
