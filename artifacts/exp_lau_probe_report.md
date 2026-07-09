# Probe Bundle Report

## Bundle Metadata
- Bundle path: `C:\Users\khams008\Documents\awr2944-codex-sidequest\artifacts\exp_lau_probe_bundle.zip`
- Number of files: 164
- bundle_manifest.json exists: yes
- SHA256 hashes are present: yes
- Raw .bin files present: no

## Best Validation Found
- file: `validation_20260708_154349.json`
- label: First fully completed guided-runner validation with manual connection override
- firmware_run_id: a6fc2eb6
- config_run_id: ede0c0ec
- git commit: 7968e760e6f0abe07cd0a8808434f7d4582513e6

## Guided Workflow States
### `guided_00f92e48_state.json`
- workflow_id: 00f92e48
- label: First guided-runner hardware validation
- current_stage: failed
- firmware_run_id: -
- config_run_id: -
- dry_run: -
- hardware_touched: -
- lua_generated: -
- validation_recorded: -
- errors: firmware_script_generated failed: _atomic_write_manifest() got an unexpected keyword argument 'manifest_path'
#### Linked Artifacts
- linked firmware result found: no
- linked firmware progress found: no
- linked config result found: no
- linked config progress found: no
- unrelated artifacts ignored: 111
### `guided_13870162_state.json`
- workflow_id: 13870162
- label: First fully completed guided-runner validation
- current_stage: failed
- firmware_run_id: -
- config_run_id: -
- dry_run: no
- hardware_touched: no
- lua_generated: no
- validation_recorded: no
- errors: manual_check_passed failed: Could not attach to mmWave Studio: Could not auto-resolve mmWave Studio PID: No visible candidate processes found.

Candidate processes:
  PID=19188  Name=mmWaveStudio  Handle=0  Title=''
  PID=27092  Name=MmwsRstdBridge  Handle=0  Title=''

Try running with explicit --pid <PID>.
#### Linked Artifacts
- linked firmware result found: no
- linked firmware progress found: no
- linked config result found: no
- linked config progress found: no
- unrelated artifacts ignored: 111
### `guided_3db99b0b_state.json`
- workflow_id: 3db99b0b
- label: post-fix dry-run
- current_stage: dry_run_completed
- firmware_run_id: -
- config_run_id: -
- dry_run: yes
- hardware_touched: no
- lua_generated: no
- validation_recorded: no
- errors: none
#### Linked Artifacts
- linked firmware result found: no
- linked firmware progress found: no
- linked config result found: no
- linked config progress found: no
- unrelated artifacts ignored: 111
### `guided_3e02822c_state.json`
- workflow_id: 3e02822c
- label: First fully completed guided-runner validation
- current_stage: failed
- firmware_run_id: -
- config_run_id: -
- dry_run: no
- hardware_touched: no
- lua_generated: no
- validation_recorded: no
- errors: manual_check_passed failed: Could not attach to mmWave Studio: Could not auto-resolve mmWave Studio PID: Multiple visible candidate processes found.

Candidate processes:
  PID=5716  Name=Antigravity IDE  Handle=1512770  Title='awr2944-fmcw-radar1 (Workspace) - Antigravity IDE - Walkthrough'
  PID=20084  Name=chrome  Handle=66902  Title='Summer2026-Saeed - Radar Data Capture Setup - Google Chrome'
  PID=12012  Name=mmWaveStudio  Handle=1119094  Title='mmWave Studio 3.1.4.4'

Please rerun with an explicit: --pid <PID>
#### Linked Artifacts
- linked firmware result found: no
- linked firmware progress found: no
- linked config result found: no
- linked config progress found: no
- unrelated artifacts ignored: 111
### `guided_73c13235_state.json`
- workflow_id: 73c13235
- label: First fully completed guided-runner validation with manual connection override
- current_stage: validation_recorded
- firmware_run_id: a6fc2eb6
- config_run_id: ede0c0ec
- dry_run: no
- hardware_touched: no
- lua_generated: yes
- validation_recorded: no
- errors: none
#### Linked Artifacts
- linked firmware result found: yes
- linked firmware progress found: yes
- linked config result found: yes
- linked config progress found: yes
- unrelated artifacts ignored: 105
### `guided_784a5910_state.json`
- workflow_id: 784a5910
- label: First guided-runner hardware validation after reconciliation fix
- current_stage: failed
- firmware_run_id: 645cdf51
- config_run_id: 62d8a837
- dry_run: no
- hardware_touched: no
- lua_generated: yes
- validation_recorded: no
- errors: session_summarized failed: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'OptionInfo'
#### Linked Artifacts
- linked firmware result found: yes
- linked firmware progress found: yes
- linked config result found: yes
- linked config progress found: yes
- unrelated artifacts ignored: 105
### `guided_8ab69e27_state.json`
- workflow_id: 8ab69e27
- label: First fully completed guided-runner validation
- current_stage: failed
- firmware_run_id: -
- config_run_id: -
- dry_run: no
- hardware_touched: no
- lua_generated: no
- validation_recorded: no
- errors: manual_check_passed failed: Could not attach to mmWave Studio: UIA attach failed for PID=12012: No windows for that process could be found. Verify the PID is correct and mmWave Studio is running.
If mmWave Studio was launched as Administrator, this PowerShell terminal must also be run as Administrator.
#### Linked Artifacts
- linked firmware result found: no
- linked firmware progress found: no
- linked config result found: no
- linked config progress found: no
- unrelated artifacts ignored: 111
### `guided_a3268557_state.json`
- workflow_id: a3268557
- label: First fully completed guided-runner validation
- current_stage: failed
- firmware_run_id: -
- config_run_id: -
- dry_run: no
- hardware_touched: no
- lua_generated: no
- validation_recorded: no
- errors: manual_check_passed failed: Could not attach to mmWave Studio: UIA attach failed for PID=19188: No windows for that process could be found. Verify the PID is correct and mmWave Studio is running.
#### Linked Artifacts
- linked firmware result found: no
- linked firmware progress found: no
- linked config result found: no
- linked config progress found: no
- unrelated artifacts ignored: 111
### `guided_b77939b2_state.json`
- workflow_id: b77939b2
- label: final post-fix dry-run
- current_stage: dry_run_completed
- firmware_run_id: -
- config_run_id: -
- dry_run: yes
- hardware_touched: no
- lua_generated: no
- validation_recorded: no
- errors: none
#### Linked Artifacts
- linked firmware result found: no
- linked firmware progress found: no
- linked config result found: no
- linked config progress found: no
- unrelated artifacts ignored: 111
### `guided_c1f12420_state.json`
- workflow_id: c1f12420
- label: post-fix dry-run
- current_stage: dry_run_completed
- firmware_run_id: -
- config_run_id: -
- dry_run: yes
- hardware_touched: no
- lua_generated: no
- validation_recorded: no
- errors: none
#### Linked Artifacts
- linked firmware result found: no
- linked firmware progress found: no
- linked config result found: no
- linked config progress found: no
- unrelated artifacts ignored: 111
### `guided_c83f95a5_state.json`
- workflow_id: c83f95a5
- label: First fully completed guided-runner validation with manual connection override
- current_stage: failed
- firmware_run_id: -
- config_run_id: -
- dry_run: no
- hardware_touched: no
- lua_generated: no
- validation_recorded: no
- errors: firmware_preflight_passed failed: Firmware preflight failed: ['RS232 identity gate not valid']
#### Linked Artifacts
- linked firmware result found: no
- linked firmware progress found: no
- linked config result found: no
- linked config progress found: no
- unrelated artifacts ignored: 111
### `guided_cbc23d39_state.json`
- workflow_id: cbc23d39
- label: post-fix dry-run
- current_stage: dry_run_completed
- firmware_run_id: -
- config_run_id: -
- dry_run: yes
- hardware_touched: no
- lua_generated: no
- validation_recorded: no
- errors: none
#### Linked Artifacts
- linked firmware result found: no
- linked firmware progress found: no
- linked config result found: no
- linked config progress found: no
- unrelated artifacts ignored: 111
### `guided_d4cf3fed_state.json`
- workflow_id: d4cf3fed
- label: First fully completed guided-runner validation
- current_stage: failed
- firmware_run_id: -
- config_run_id: -
- dry_run: no
- hardware_touched: no
- lua_generated: no
- validation_recorded: no
- errors: manual_check_passed failed: Could not attach to mmWave Studio: UIA attach failed for PID=19188:
No windows for that process could be found (MainWindowHandle == 0).
Verify the PID is correct and mmWave Studio is running.

Candidate processes:
  PID=19188  Name=mmWaveStudio  Handle=0  Title=''
  PID=27092  Name=MmwsRstdBridge  Handle=0  Title=''

If mmWave Studio was launched as Administrator, this PowerShell terminal must also be run as Administrator.
#### Linked Artifacts
- linked firmware result found: no
- linked firmware progress found: no
- linked config result found: no
- linked config progress found: no
- unrelated artifacts ignored: 111
### `guided_d6e10ccf_state.json`
- workflow_id: d6e10ccf
- label: dry-run guided validation test
- current_stage: validation_recorded
- firmware_run_id: dryrunfw
- config_run_id: dryruncfg
- dry_run: -
- hardware_touched: -
- lua_generated: -
- validation_recorded: -
- errors: none
#### Linked Artifacts
- linked firmware result found: no
- linked firmware progress found: no
- linked config result found: no
- linked config progress found: no
- unrelated artifacts ignored: 111
### `guided_d8bb7e61_state.json`
- workflow_id: d8bb7e61
- label: First fully completed guided-runner validation
- current_stage: failed
- firmware_run_id: -
- config_run_id: -
- dry_run: no
- hardware_touched: no
- lua_generated: no
- validation_recorded: no
- errors: manual_check_passed failed: Manual check failed: Expected Device Status containing AWR2944, GP, and SOP:2. Found: ''
#### Linked Artifacts
- linked firmware result found: no
- linked firmware progress found: no
- linked config result found: no
- linked config progress found: no
- unrelated artifacts ignored: 111
### `guided_da68e343_state.json`
- workflow_id: da68e343
- label: First fully completed guided-runner validation
- current_stage: failed
- firmware_run_id: -
- config_run_id: -
- dry_run: no
- hardware_touched: no
- lua_generated: no
- validation_recorded: no
- errors: manual_check_passed failed: Could not attach to mmWave Studio: UIA attach failed for PID=19188: No windows for that process could be found. Verify the PID is correct and mmWave Studio is running.
#### Linked Artifacts
- linked firmware result found: no
- linked firmware progress found: no
- linked config result found: no
- linked config progress found: no
- unrelated artifacts ignored: 111
### `guided_fed46ce3_state.json`
- workflow_id: fed46ce3
- label: First fully completed guided-runner validation
- current_stage: failed
- firmware_run_id: -
- config_run_id: -
- dry_run: no
- hardware_touched: no
- lua_generated: no
- validation_recorded: no
- errors: manual_check_passed failed: Manual check failed: Expected Device Status containing AWR2944, GP, and SOP:2. Found: ''
#### Linked Artifacts
- linked firmware result found: no
- linked firmware progress found: no
- linked config result found: no
- linked config progress found: no
- unrelated artifacts ignored: 111

## Run Results
### `028c4e5d_smoke_known_awr2944_result.json`
- run_id: 028c4e5d
- stage: smoke_known_awr2944
- success: no
- error: DisableTestSource failed: -1
- warnings: -
### `1f1d3208_smoke_known_awr2944_result.json`
- run_id: 1f1d3208
- stage: smoke_known_awr2944
- success: -
- error: -
- warnings: ChanNAdcConfig: GUI-emitted; captured during dirty session; replay validation required
### `3ecac52f_smoke_known_awr2944_result.json`
- run_id: 3ecac52f
- stage: smoke_known_awr2944
- success: yes
- error: -
- warnings: none
### `40cf1af4_post_status_result.json`
- run_id: 40cf1af4
- stage: post_status
- success: -
- error: OUTPUT_TEXT_EMPTY_OR_UNREADABLE
- warnings: -
### `50167110_smoke_known_awr2944_result.json`
- run_id: 50167110
- stage: smoke_known_awr2944
- success: yes
- error: -
- warnings: none
### `6018a96c_smoke_known_awr2944_result.json`
- run_id: 6018a96c
- stage: smoke_known_awr2944
- success: no
- error: ChanNAdcConfig failed: -2
- warnings: none
### `62d8a837_smoke_config_result.json`
- run_id: 62d8a837
- stage: smoke_config
- success: yes
- error: -
- warnings: none
### `645cdf51_firmware_power_result.json`
- run_id: 645cdf51
- stage: firmware_power
- success: yes
- error: -
- warnings: none
### `6c184749_smoke_known_awr2944_result.json`
- run_id: 6c184749
- stage: smoke_known_awr2944
- success: yes
- error: -
- warnings: none
### `6dc4e842_smoke_known_awr2944_result.json`
- run_id: 6dc4e842
- stage: smoke_known_awr2944
- success: no
- error: ChanNAdcConfig failed: -2
- warnings: none
### `701a5f04_firmware_power_result.json`
- run_id: 701a5f04
- stage: firmware_power
- success: yes
- error: -
- warnings: -
### `7db407f0_smoke_known_awr2944_result.json`
- run_id: 7db407f0
- stage: smoke_known_awr2944
- success: no
- error: ProfileConfig failed: 46
- warnings: none
### `82c660e2_firmware_power_result.json`
- run_id: 82c660e2
- stage: firmware_power
- success: yes
- error: -
- warnings: none
### `a6fc2eb6_firmware_power_result.json`
- run_id: a6fc2eb6
- stage: firmware_power
- success: yes
- error: -
- warnings: none
### `b475130e_firmware_power_result.json`
- run_id: b475130e
- stage: firmware_power
- success: yes
- error: -
- warnings: none
### `cc0f8b8c_firmware_power_result.json`
- run_id: cc0f8b8c
- stage: firmware_power
- success: yes
- error: -
- warnings: -
### `connection_connect_gui_result.json`
- run_id: ecc03ca3
- stage: connection_connect_gui
- success: -
- error: -
- warnings: -
### `connection_return3_diag_result.json`
- run_id: d4ca630a
- stage: connection_return3_diag
- success: -
- error: -
- warnings: -
### `connection_set1_discovery_result.json`
- run_id: ca154c9d
- stage: connection_set1_discovery
- success: -
- error: -
- warnings: -
### `d19fa41a_firmware_power_result.json`
- run_id: d19fa41a
- stage: firmware_power
- success: yes
- error: -
- warnings: none
### `da0ce6de_firmware_power_result.json`
- run_id: da0ce6de
- stage: firmware_power
- success: yes
- error: -
- warnings: none
### `da446bf8_parser_test_result.json`
- run_id: da446bf8
- stage: parser_test
- success: -
- error: -
- warnings: -
### `dc6f0cd0_parser_test_result.json`
- run_id: dc6f0cd0
- stage: parser_test
- success: -
- error: -
- warnings: -
### `ede0c0ec_smoke_config_result.json`
- run_id: ede0c0ec
- stage: smoke_config
- success: yes
- error: -
- warnings: none
### `f76a2c57_firmware_power_result.json`
- run_id: f76a2c57
- stage: firmware_power
- success: no
- error: RfEnable failed: -1
- warnings: none
### `fresh_gui_human_set_lua_connect_result.json`
- run_id: fresh_gui_human_set_lua_connect
- stage: fresh_gui_human_set_lua_connect
- success: -
- error: -
- warnings: -
### `fresh_gui_lua_connect_no_fullreset_result.json`
- run_id: fresh_gui_lua_connect_no_fullreset
- stage: fresh_gui_lua_connect_no_fullreset
- success: -
- error: -
- warnings: -
### `fresh_gui_lua_set_only_result.json`
- run_id: fresh_gui_lua_set_only
- stage: fresh_gui_lua_set_only
- success: -
- error: -
- warnings: -
### `gui_connect_click_flow_result.json`
- run_id: gui_connect_click_flow
- stage: gui_connect_click_flow
- success: -
- error: -
- warnings: -
### `gui_connect_status_result.json`
- run_id: gui_connect_status
- stage: gui_connect_status
- success: -
- error: -
- warnings: -
### `inventory_result.json`
- run_id: inventory
- stage: inventory
- success: -
- error: -
- warnings: -
### `lua_exposed_gui_method_probe_result.json`
- run_id: lua_exposed_gui_method_probe
- stage: lua_exposed_gui_method_probe
- success: -
- error: -
- warnings: -
### `lua_launch_ar1_methods_result.json`
- run_id: 851fc238
- stage: lua_launch_ar1_methods
- success: -
- error: -
- warnings: -
### `lua_launch_ar1_readonly_probe_result.json`
- run_id: dde88be4
- stage: lua_launch_ar1_readonly_probe
- success: -
- error: -
- warnings: -
### `lua_launch_connect_only_result.json`
- run_id: f3405fef
- stage: lua_launch_connect_only
- success: -
- error: ..._lau_probe\ti\probe_logs\lua_launch_connect_only.lua:95: HUNG_AT_CONNECT: System.NullReferenceException: Object reference not set to an instance of an object.
   at AR1xController.DllOps.Connect_Ext(UInt32 RadarDeviceId, UInt32 con_type, UInt32 com_port, UInt32 baud_rate, UInt32 timeout, UInt32 board_type, UInt32 dest)
   at AR1xController.AR1xxxWrapper.Connect(UInt32 com_port, UInt32 baud_rate, UInt32 timeout): 35320229
- warnings: -
### `lua_launch_env_probe_result.json`
- run_id: 2ee8c951
- stage: lua_launch_env_probe
- success: -
- error: -
- warnings: -
### `lua_launch_path_env_probe_result.json`
- run_id: 18dfa6b0
- stage: lua_launch_path_env_probe
- success: -
- error: -
- warnings: -
### `lua_launch_radarapi_connect_probe_result.json`
- run_id: 3b277b79
- stage: lua_launch_radarapi_connect_probe
- success: -
- error: ...\ti\probe_logs\lua_launch_radarapi_connect_probe.lua:123: CONNECT_EXCEPTION: System.NullReferenceException: Object reference not set to an instance of an object.
   at AR1xController.DllOps.Connect_Ext(UInt32 RadarDeviceId, UInt32 con_type, UInt32 com_port, UInt32 baud_rate, UInt32 timeout, UInt32 board_type, UInt32 dest)
   at AR1xController.AR1xxxWrapper.Connect(UInt32 com_port, UInt32 baud_rate, UInt32 timeout): 35320229
- warnings: -
### `lua_launch_radarapi_init_probe_result.json`
- run_id: 1cd68112
- stage: lua_launch_radarapi_init_probe
- success: -
- error: ...obe\ti\probe_logs\lua_launch_radarapi_init_probe.lua:87: SHOWGUI_FAILED
- warnings: -
### `lua_launch_radarapi_v3_connect_probe_result.json`
- run_id: 2a8c65ab
- stage: lua_launch_radarapi_v3_connect_probe
- success: -
- error: -
- warnings: -
### `lua_launch_registerdll_probe_result.json`
- run_id: ee34430b
- stage: lua_launch_registerdll_probe
- success: -
- error: -
- warnings: -
### `lua_launch_rstd_env_probe_result.json`
- run_id: 3b4aa646
- stage: lua_launch_rstd_env_probe
- success: -
- error: -
- warnings: -
### `lua_launch_smoke_result.json`
- run_id: 1ea860ca
- stage: lua_launch_smoke
- success: -
- error: -
- warnings: -
### `lua_launch_startup_lite_probe_result.json`
- run_id: cf7b6c2a
- stage: lua_launch_startup_lite_probe
- success: -
- error: -
- warnings: -
### `lua_launch_startup_lite_v3_probe_result.json`
- run_id: a55ccf71
- stage: lua_launch_startup_lite_v3_probe
- success: -
- error: -
- warnings: -
### `manual_check_result.json`
- run_id: manual_check
- stage: manual_check
- success: -
- error: Expected Device Status containing AWR2944, GP, and SOP:2. Found: ''
- warnings: -
### `manual_com_sweep_after_set_result.json`
- run_id: manual_com_sweep_after_set
- stage: manual_com_sweep_after_set
- success: -
- error: -
- warnings: -
### `manual_connected_state_snapshot_result.json`
- run_id: manual_connected_state_snapshot
- stage: manual_connected_state_snapshot
- success: -
- error: -
- warnings: -
### `manual_gui_no_direct_fullreset_connect_result.json`
- run_id: manual_gui_no_direct_fullreset_connect
- stage: manual_gui_no_direct_fullreset_connect
- success: -
- error: -
- warnings: -
### `manual_normal_gui_connect_result.json`
- run_id: manual_gui_connect
- stage: manual_normal_gui_connect
- success: -
- error: -
- warnings: -
### `manual_normal_gui_env_snapshot_result.json`
- run_id: manual_normal_gui_env_snapshot
- stage: manual_normal_gui_env_snapshot
- success: -
- error: -
- warnings: -
### `manual_normal_gui_paths_result.json`
- run_id: manual_normal_gui_paths
- stage: manual_normal_gui_paths
- success: -
- error: -
- warnings: -
### `manual_select_set_connect_result.json`
- run_id: manual_select_set_connect
- stage: manual_select_set_connect
- success: -
- error: -
- warnings: -
### `manual_sop_then_connect_result.json`
- run_id: manual_sop_then_connect
- stage: manual_sop_then_connect
- success: -
- error: -
- warnings: -
### `manual_sopcontrol2_result.json`
- run_id: manual_sopcontrol2
- stage: manual_sopcontrol2
- success: -
- error: -
- warnings: -
### `post_status_result.json`
- run_id: post_status
- stage: post_status
- success: -
- error: -
- warnings: -
### `probe_result.json`
- run_id: probe
- stage: probe
- success: -
- error: -
- warnings: -

## Progress Logs
### `028c4e5d_smoke_known_awr2944_progress.jsonl`
- run_id: 028c4e5d
- command count: 13
- failed command count: 0
- hardware commands observed: RfInit, ProfileConfig, ChirpConfig
- last command: DisableTestSource
### `3ecac52f_smoke_known_awr2944_progress.jsonl`
- run_id: 3ecac52f
- command count: 13
- failed command count: 0
- hardware commands observed: RfInit, ProfileConfig, ChirpConfig, FrameConfig
- last command: FrameConfig
### `4890c210_extracted_replay_progress.jsonl`
- run_id: 4890c210
- command count: 4
- failed command count: 0
- hardware commands observed: PowerOn, RfEnable
- last command: RfEnable
### `50167110_smoke_known_awr2944_progress.jsonl`
- run_id: 50167110
- command count: 13
- failed command count: 0
- hardware commands observed: RfInit, ProfileConfig, ChirpConfig, FrameConfig
- last command: FrameConfig
### `6018a96c_smoke_known_awr2944_progress.jsonl`
- run_id: 6018a96c
- command count: 1
- failed command count: 0
- hardware commands observed: none
- last command: ChanNAdcConfig
### `62d8a837_smoke_config_progress.jsonl`
- run_id: 62d8a837
- command count: 13
- failed command count: 0
- hardware commands observed: RfInit, ProfileConfig, ChirpConfig, FrameConfig
- last command: FrameConfig
### `645cdf51_firmware_power_progress.jsonl`
- run_id: 645cdf51
- command count: 10
- failed command count: 0
- hardware commands observed: PowerOn, RfEnable
- last command: GetBSSPatchFwVersion
### `6c184749_smoke_known_awr2944_progress.jsonl`
- run_id: 6c184749
- command count: 13
- failed command count: 0
- hardware commands observed: RfInit, ProfileConfig, ChirpConfig, FrameConfig
- last command: FrameConfig
### `6dc4e842_smoke_known_awr2944_progress.jsonl`
- run_id: 6dc4e842
- command count: 1
- failed command count: 0
- hardware commands observed: none
- last command: ChanNAdcConfig
### `701a5f04_firmware_power_result_progress.jsonl`
- run_id: 701a5f04
- command count: 4
- failed command count: 0
- hardware commands observed: PowerOn, RfEnable
- last command: RfEnable
### `7db407f0_smoke_known_awr2944_progress.jsonl`
- run_id: 7db407f0
- command count: 11
- failed command count: 0
- hardware commands observed: RfInit, ProfileConfig
- last command: ProfileConfig
### `82c660e2_firmware_power_result_progress.jsonl`
- run_id: 82c660e2
- command count: 10
- failed command count: 0
- hardware commands observed: PowerOn, RfEnable
- last command: GetBSSPatchFwVersion
### `a2a7272c_smoke_config_progress.jsonl`
- run_id: a2a7272c
- command count: 0
- failed command count: 0
- hardware commands observed: none
- last command: -
### `a6fc2eb6_firmware_power_progress.jsonl`
- run_id: a6fc2eb6
- command count: 10
- failed command count: 0
- hardware commands observed: PowerOn, RfEnable
- last command: GetBSSPatchFwVersion
### `b475130e_firmware_power_result_progress.jsonl`
- run_id: b475130e
- command count: 10
- failed command count: 0
- hardware commands observed: PowerOn, RfEnable
- last command: GetBSSPatchFwVersion
### `cc0f8b8c_firmware_power_result_progress.jsonl`
- run_id: cc0f8b8c
- command count: 10
- failed command count: 0
- hardware commands observed: PowerOn, RfEnable
- last command: GetBSSPatchFwVersion
### `connection_connect_gui_progress.jsonl`
- run_id: connection_connect_gui
- command count: 32
- failed command count: 0
- hardware commands observed: none
- last command: -
### `connection_return3_diag_progress.jsonl`
- run_id: connection_return3_diag
- command count: 13
- failed command count: 0
- hardware commands observed: none
- last command: -
### `connection_set1_discovery_progress.jsonl`
- run_id: connection_set1_discovery
- command count: 7
- failed command count: 0
- hardware commands observed: none
- last command: -
### `d19fa41a_firmware_power_result_progress.jsonl`
- run_id: d19fa41a
- command count: 10
- failed command count: 0
- hardware commands observed: PowerOn, RfEnable
- last command: GetBSSPatchFwVersion
### `da0ce6de_firmware_power_result_progress.jsonl`
- run_id: da0ce6de
- command count: 10
- failed command count: 0
- hardware commands observed: PowerOn, RfEnable
- last command: GetBSSPatchFwVersion
### `ede0c0ec_smoke_config_progress.jsonl`
- run_id: ede0c0ec
- command count: 13
- failed command count: 0
- hardware commands observed: RfInit, ProfileConfig, ChirpConfig, FrameConfig
- last command: FrameConfig
### `f76a2c57_firmware_power_result_progress.jsonl`
- run_id: f76a2c57
- command count: 7
- failed command count: 0
- hardware commands observed: PowerOn, RfEnable
- last command: RfEnable
### `fresh_gui_human_set_lua_connect_progress.jsonl`
- run_id: fresh_gui_human_set_lua_connect
- command count: 4
- failed command count: 0
- hardware commands observed: none
- last command: -
### `fresh_gui_lua_connect_no_fullreset_progress.jsonl`
- run_id: fresh_gui_lua_connect_no_fullreset
- command count: 14
- failed command count: 0
- hardware commands observed: none
- last command: -
### `fresh_gui_lua_set_only_progress.jsonl`
- run_id: fresh_gui_lua_set_only
- command count: 10
- failed command count: 0
- hardware commands observed: none
- last command: -
### `gui_connect_click_flow_progress.jsonl`
- run_id: gui_connect_click_flow
- command count: 22
- failed command count: 0
- hardware commands observed: none
- last command: -
### `lua_launch_ar1_readonly_probe_progress.jsonl`
- run_id: lua_launch_ar1_readonly_probe
- command count: 5
- failed command count: 0
- hardware commands observed: none
- last command: -
### `lua_launch_connect_only_progress.jsonl`
- run_id: lua_launch_connect_only
- command count: 6
- failed command count: 0
- hardware commands observed: none
- last command: -
### `lua_launch_path_env_probe_progress.jsonl`
- run_id: lua_launch_path_env_probe
- command count: 17
- failed command count: 0
- hardware commands observed: none
- last command: -
### `lua_launch_radarapi_connect_probe_progress.jsonl`
- run_id: lua_launch_radarapi_connect_probe
- command count: 5
- failed command count: 0
- hardware commands observed: none
- last command: -
### `lua_launch_radarapi_connect_probe_result_progress.jsonl`
- run_id: lua_launch_radarapi_connect_probe
- command count: 5
- failed command count: 0
- hardware commands observed: none
- last command: -
### `lua_launch_radarapi_init_probe_progress.jsonl`
- run_id: lua_launch_radarapi_init_probe
- command count: 5
- failed command count: 0
- hardware commands observed: none
- last command: -
### `lua_launch_radarapi_init_probe_result_progress.jsonl`
- run_id: lua_launch_radarapi_init_probe
- command count: 5
- failed command count: 0
- hardware commands observed: none
- last command: -
### `lua_launch_radarapi_v3_connect_probe_progress.jsonl`
- run_id: lua_launch_radarapi_v3_connect_probe
- command count: 8
- failed command count: 0
- hardware commands observed: none
- last command: -
### `lua_launch_startup_lite_v3_probe_progress.jsonl`
- run_id: lua_launch_startup_lite_v3_probe
- command count: 15
- failed command count: 0
- hardware commands observed: none
- last command: -
### `manual_check_progress.jsonl`
- run_id: manual_check
- command count: 2
- failed command count: 0
- hardware commands observed: none
- last command: -
### `manual_com_sweep_after_set_progress.jsonl`
- run_id: manual_com_sweep_after_set
- command count: 8
- failed command count: 0
- hardware commands observed: none
- last command: -
### `manual_gui_no_direct_fullreset_connect_progress.jsonl`
- run_id: manual_gui_no_direct_fullreset_connect
- command count: 14
- failed command count: 0
- hardware commands observed: none
- last command: -
### `manual_normal_gui_connect_progress.jsonl`
- run_id: manual_normal_gui_connect
- command count: 5
- failed command count: 0
- hardware commands observed: none
- last command: -
### `manual_select_set_connect_progress.jsonl`
- run_id: manual_select_set_connect
- command count: 14
- failed command count: 0
- hardware commands observed: none
- last command: -
### `manual_sop_then_connect_progress.jsonl`
- run_id: manual_sop_then_connect
- command count: 8
- failed command count: 0
- hardware commands observed: none
- last command: -
### `manual_sopcontrol2_progress.jsonl`
- run_id: manual_sopcontrol2
- command count: 4
- failed command count: 0
- hardware commands observed: none
- last command: -

## Validation Records
### `validation_20260707_131318.json`
- label: First clean positive post-connection validation
- firmware_run_id: da0ce6de
- config_run_id: 3ecac52f
- post_connection_config_validated: yes
- git commit: 5786958c04ade2c8e43b26364d8ce5d8643819dc
### `validation_20260707_175408.json`
- label: First guided-runner hardware validation after reconciliation fix
- firmware_run_id: 645cdf51
- config_run_id: 62d8a837
- post_connection_config_validated: yes
- git commit: 7968e760e6f0abe07cd0a8808434f7d4582513e6
### `validation_20260707_182123.json`
- label: Guided-runner hardware validation manually finalized after summary bug
- firmware_run_id: 645cdf51
- config_run_id: 62d8a837
- post_connection_config_validated: yes
- git commit: 7968e760e6f0abe07cd0a8808434f7d4582513e6
### `validation_20260708_154349.json`
- label: First fully completed guided-runner validation with manual connection override
- firmware_run_id: a6fc2eb6
- config_run_id: ede0c0ec
- post_connection_config_validated: yes
- git commit: 7968e760e6f0abe07cd0a8808434f7d4582513e6

## Suspicious Findings
- Malformed JSONL in 4890c210_extracted_replay_progress.jsonl: line 2 column 48
- Malformed JSONL in 4890c210_extracted_replay_progress.jsonl: line 3 column 53
- Malformed JSONL in 4890c210_extracted_replay_progress.jsonl: line 5 column 48
- Malformed JSONL in 701a5f04_firmware_power_result_progress.jsonl: line 2 column 54
- Malformed JSONL in 701a5f04_firmware_power_result_progress.jsonl: line 3 column 59
- Malformed JSONL in 701a5f04_firmware_power_result_progress.jsonl: line 5 column 54
- Malformed JSONL in 701a5f04_firmware_power_result_progress.jsonl: line 8 column 54
- Malformed JSONL in 701a5f04_firmware_power_result_progress.jsonl: line 9 column 54
- Malformed JSONL in 701a5f04_firmware_power_result_progress.jsonl: line 10 column 59
- Malformed JSONL in a2a7272c_smoke_config_progress.jsonl: line 1 column 92
- Result 028c4e5d_smoke_known_awr2944_result.json reports success=false
- Result 6018a96c_smoke_known_awr2944_result.json reports success=false
- Result 6dc4e842_smoke_known_awr2944_result.json reports success=false
- Result 7db407f0_smoke_known_awr2944_result.json reports success=false
- Result f76a2c57_firmware_power_result.json reports success=false
- Guided state guided_73c13235_state.json has hardware_touched=false but linked progress a6fc2eb6_firmware_power_progress.jsonl contains hardware commands: PowerOn, RfEnable
- Guided state guided_73c13235_state.json has hardware_touched=false but linked progress ede0c0ec_smoke_config_progress.jsonl contains hardware commands: RfInit, ProfileConfig, ChirpConfig, FrameConfig
- Guided state guided_784a5910_state.json failed but linked result 62d8a837_smoke_config_result.json reports success=true
- Guided state guided_784a5910_state.json failed but linked result 645cdf51_firmware_power_result.json reports success=true
- Guided state guided_784a5910_state.json has hardware_touched=false but linked progress 645cdf51_firmware_power_progress.jsonl contains hardware commands: PowerOn, RfEnable
- Guided state guided_784a5910_state.json has hardware_touched=false but linked progress 62d8a837_smoke_config_progress.jsonl contains hardware commands: RfInit, ProfileConfig, ChirpConfig, FrameConfig
