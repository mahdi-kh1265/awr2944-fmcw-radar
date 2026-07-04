# RSTD Execution Diagnostic Report

## Environment
- RtttNetClientAPI.dll: C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\Clients\RtttNetClientController\RtttNetClientAPI.dll
- TCP 2777 open: True
- pythonnet available: True

## Known-Good API Sequence (from TI MATLAB example)

Source: `C:\ti\mmwave_studio_03_00_00_14\mmWaveStudio\MatlabExamples\
4chip_cascade_TxBF_example\RSTD\Init_RSTD_Connection.m`

```matlab
% 1. Load DLL
RSTD_Assembly = NET.addAssembly(RSTD_DLL_Path);

% 2. Init client
ErrStatus = RtttNetClientAPI.RtttNetClient.Init();

% 3. Connect to localhost:2777
ErrStatus = RtttNetClientAPI.RtttNetClient.Connect('127.0.0.1', 2777);

% 4. Send Lua command string
Lua_String = 'WriteToLog("Running script from MATLAB\n", "green")';
ErrStatus = RtttNetClientAPI.RtttNetClient.SendCommand(Lua_String);
% Returns 30000 if no error
```

## Key Notes

- `SendCommand` takes raw Lua strings, not file paths
- TI MATLAB examples send `ar1.ProfileConfig(...)` directly as strings
- For scripts, use `dofile([[C:/path/to/script.lua]])`
- Return code 30000 = command submitted, NOT proof of Lua success
- `Init()` alone is NOT enough — `Connect('127.0.0.1', 2777)` is required

## Variant Results

### raw_inline
- Submit OK: False
- Return code: -1
- File appeared: False
- Error: SENDCOMMAND_TIMEOUT: exceeded 5.0s
- Lua: `local f = io.open([[C:/Users/khams008/Documents/awr2944-fmcw-radar/ti/probe_logs/rstd_ping_raw_inline_result.json]], "w") if f then f:write('{"executed":true,"source":"inline_rstd","variant":"raw_inline"}') f:close() end`

### raw_inline_semicolons
- Submit OK: False
- Return code: -1
- File appeared: False
- Error: SENDCOMMAND_TIMEOUT: exceeded 5.0s
- Lua: `local f = io.open([[C:/Users/khams008/Documents/awr2944-fmcw-radar/ti/probe_logs/rstd_ping_raw_inline_semicolons_result.json]], "w"); if f then f:write('{"executed":true,"source":"inline_rstd","variant":"raw_inline_semicolons"}'); f:close(); end`

### write_to_log_only
- Submit OK: False
- Return code: -1
- File appeared: False
- Error: SENDCOMMAND_TIMEOUT: exceeded 5.0s
- Lua: `WriteToLog("RSTD_PING_OK\n", "green")`

## Conclusion: **All variants failed**