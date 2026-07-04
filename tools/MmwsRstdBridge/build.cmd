@echo off
REM MmwsRstdBridge build script
REM Compiles MmwsRstdBridge.cs using .NET Framework 4.x csc.exe (32-bit)
REM
REM Usage:
REM   build.cmd
REM   build.cmd "C:\custom\path\to\RtttNetClientAPI.dll"

setlocal

REM --- Locate csc.exe (32-bit .NET Framework, NOT Framework64) ---
set CSC=C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe

if not exist "%CSC%" (
    echo ERROR: csc.exe not found at %CSC%
    echo Install .NET Framework 4.x or use a machine with it pre-installed.
    exit /b 1
)

echo [build] csc.exe: %CSC%

REM --- Locate RtttNetClientAPI.dll ---
set DLL_PATH=%~1

if "%DLL_PATH%"=="" (
    REM Try known TI installation paths
    if exist "C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\Clients\RtttNetClientController\RtttNetClientAPI.dll" (
        set DLL_PATH=C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\Clients\RtttNetClientController\RtttNetClientAPI.dll
    ) else if exist "C:\ti\mmwave_studio_03_00_00_14\mmWaveStudio\Clients\RtttNetClientController\RtttNetClientAPI.dll" (
        set DLL_PATH=C:\ti\mmwave_studio_03_00_00_14\mmWaveStudio\Clients\RtttNetClientController\RtttNetClientAPI.dll
    ) else (
        echo ERROR: RtttNetClientAPI.dll not found.
        echo Pass the path as the first argument:
        echo   build.cmd "C:\path\to\RtttNetClientAPI.dll"
        exit /b 1
    )
)

if not exist "%DLL_PATH%" (
    echo ERROR: DLL not found: %DLL_PATH%
    exit /b 1
)

echo [build] RtttNetClientAPI.dll: %DLL_PATH%
echo [build] Platform: x86

REM --- Get the directory of this script ---
set SCRIPT_DIR=%~dp0
set SRC=%SCRIPT_DIR%MmwsRstdBridge.cs
set OUT=%SCRIPT_DIR%MmwsRstdBridge.exe

if not exist "%SRC%" (
    echo ERROR: Source file not found: %SRC%
    exit /b 1
)

echo [build] Source: %SRC%
echo [build] Output: %OUT%
echo.

REM --- Compile ---
"%CSC%" /target:exe /platform:x86 /optimize+ ^
    /reference:"%DLL_PATH%" ^
    /out:"%OUT%" ^
    "%SRC%"

if %ERRORLEVEL% neq 0 (
    echo.
    echo [build] FAILED with exit code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo.
echo [build] SUCCESS: %OUT%

REM --- Verify the exe exists ---
if exist "%OUT%" (
    echo [build] File size: 
    for %%A in ("%OUT%") do echo   %%~zA bytes
) else (
    echo [build] WARNING: Output file not found after compile
    exit /b 1
)

echo [build] Done.
