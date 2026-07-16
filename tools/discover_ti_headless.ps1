# Phase 5: TI Headless Capture Discovery Script (Read-Only)
# Repeatable PowerShell script to inventory TI installations.
# SAFE: Does not modify any hardware, firmware, or network settings.

param(
    [string]$TiRoot = "C:\ti",
    [string]$OutputFile = ""
)

$ErrorActionPreference = "SilentlyContinue"

function Write-Section($title) {
    Write-Host "`n$('=' * 70)" -ForegroundColor Cyan
    Write-Host "  $title" -ForegroundColor Cyan
    Write-Host "$('=' * 70)" -ForegroundColor Cyan
}

# --------------------------------------------------------------------------
Write-Section "1. SDK Installations under $TiRoot"
# --------------------------------------------------------------------------
Get-ChildItem -Path $TiRoot -Directory | ForEach-Object {
    Write-Host "  $($_.Name)" -ForegroundColor Green
}

# --------------------------------------------------------------------------
Write-Section "2. Pre-built AWR2944 AppImages"
# --------------------------------------------------------------------------
Get-ChildItem -Path $TiRoot -Recurse -Include "*.appimage","*.appimage.hs" -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like "*awr2944*" -or $_.Name -like "*studio*cli*" } |
    Select-Object @{N='File';E={$_.Name}}, @{N='Size';E={$_.Length}}, @{N='Path';E={$_.DirectoryName}} |
    Format-Table -AutoSize -Wrap

# --------------------------------------------------------------------------
Write-Section "3. DCA1000 CLI Tools"
# --------------------------------------------------------------------------
Get-ChildItem -Path $TiRoot -Recurse -Include "DCA1000EVM_CLI_Control.exe","DCA1000EVM_CLI_Record.exe","RF_API.dll","cf.json" -ErrorAction SilentlyContinue |
    Select-Object FullName, Length |
    Format-Table -AutoSize -Wrap

# --------------------------------------------------------------------------
Write-Section "4. Studio CLI / Radar Toolbox Search"
# --------------------------------------------------------------------------
$studioCli = Get-ChildItem -Path $TiRoot -Recurse -Include "mmwave_studio_cli*","*studio*cli*.exe","*studio*cli*.appimage" -ErrorAction SilentlyContinue
if ($studioCli) {
    $studioCli | Select-Object FullName, Length | Format-Table -AutoSize -Wrap
} else {
    Write-Host "  NOT FOUND - mmWave Studio CLI / Radar Toolbox not installed" -ForegroundColor Yellow
}

# --------------------------------------------------------------------------
Write-Section "5. Flash Tools"
# --------------------------------------------------------------------------
Get-ChildItem -Path $TiRoot -Recurse -Include "uart_uniflash.py","sbl_uart_uniflash*","default_sbl_qspi*" -ErrorAction SilentlyContinue |
    Select-Object FullName, Length |
    Format-Table -AutoSize -Wrap

# --------------------------------------------------------------------------
Write-Section "6. AWR294x Profile Configs (.cfg)"
# --------------------------------------------------------------------------
Get-ChildItem -Path $TiRoot -Recurse -Include "*.cfg" -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -like "*awr294*" -or $_.FullName -like "*LVDS*" -or $_.Name -like "*profile*" } |
    Select-Object @{N='File';E={$_.Name}}, @{N='Size';E={$_.Length}}, @{N='Dir';E={$_.DirectoryName}} |
    Format-Table -AutoSize -Wrap

# --------------------------------------------------------------------------
Write-Section "7. Documentation Files"
# --------------------------------------------------------------------------
Get-ChildItem -Path $TiRoot -Recurse -Include "*.pdf","*.chm" -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "(user|guide|DCA|studio|release|mmwave)" } |
    Select-Object @{N='File';E={$_.Name}}, @{N='Size';E={'{0:N0} KB' -f ($_.Length/1024)}}, @{N='Path';E={$_.DirectoryName}} |
    Format-Table -AutoSize -Wrap

# --------------------------------------------------------------------------
Write-Section "8. COM Ports (Read-Only)"
# --------------------------------------------------------------------------
Get-PnpDevice -Class Ports -ErrorAction SilentlyContinue |
    Select-Object Status, FriendlyName, InstanceId |
    Format-Table -AutoSize -Wrap

# --------------------------------------------------------------------------
Write-Section "9. Network Adapters (Read-Only)"
# --------------------------------------------------------------------------
Get-NetAdapter | Select-Object Name, InterfaceDescription, Status, MacAddress, LinkSpeed | Format-Table -AutoSize

# --------------------------------------------------------------------------
Write-Section "10. DCA Ethernet IP Config"
# --------------------------------------------------------------------------
Get-NetIPAddress -InterfaceAlias "Ethernet 5" -ErrorAction SilentlyContinue |
    Select-Object IPAddress, PrefixLength, AddressFamily |
    Format-Table -AutoSize

# --------------------------------------------------------------------------
Write-Section "11. Python Parser Scripts"
# --------------------------------------------------------------------------
Get-ChildItem -Path $TiRoot -Recurse -Include "parser_mmw_demo.py","mmw_demo_example_script.py","data_parser*" -ErrorAction SilentlyContinue |
    Select-Object FullName, Length |
    Format-Table -AutoSize -Wrap

Write-Host "`nDiscovery complete. No hardware was modified." -ForegroundColor Green
