<#
.SYNOPSIS
Fixes common DCA1000EVM + mmWave Studio connection issues.
.DESCRIPTION
- Creates and validates the capture directory
- Safely terminates stale TI/mmWave processes holding UDP ports 4096/4098
- Validates/fixes the Ethernet 4 IP configuration
- Validates/adds Windows Defender Firewall rules for UDP 4096/4098
- Optionally runs a quick DCA1000 CLI FPGA query test
#>

# 1. Setup Capture Directory
$captureDir = "C:\ti\captures"
if (-not (Test-Path $captureDir)) {
    New-Item -ItemType Directory -Path $captureDir | Out-Null
    Write-Host "[OK] Created directory: $captureDir" -ForegroundColor Green
} else {
    Write-Host "[OK] Directory $captureDir already exists." -ForegroundColor Green
}

try {
    $testFile = Join-Path $captureDir "test.tmp"
    "test" | Out-File $testFile
    Remove-Item $testFile
    Write-Host "[OK] $captureDir is writable." -ForegroundColor Green
} catch {
    Write-Host "[ERROR] $captureDir is not writable. Please check permissions." -ForegroundColor Red
}

Write-Host "`n*** IMPORTANT ***" -ForegroundColor Cyan
Write-Host "In mmWave Studio, please set your Dump File path exactly to:" -ForegroundColor White
Write-Host "C:\ti\captures\adc_data.bin" -ForegroundColor Yellow
Write-Host "Do NOT point it to a .fig file or a directory that doesn't exist." -ForegroundColor Cyan
Write-Host "*****************`n"

# 2. Check UDP Ports 4096 and 4098
$targetPorts = @(4096, 4098)
$safeToKill = @("mmWaveStudio", "DCA1000EVM_CLI_Control", "MATLAB", "java") 

Write-Host "Checking for stale processes on UDP ports 4096 and 4098..." -ForegroundColor Cyan
foreach ($port in $targetPorts) {
    $endpoints = Get-NetUDPEndpoint -LocalPort $port -ErrorAction SilentlyContinue
    foreach ($ep in $endpoints) {
        $pidOwner = $ep.OwningProcess
        if ($pidOwner -eq 4 -or $pidOwner -eq 0) {
            Write-Host "[WARNING] UDP Port $port is bound by System (PID $pidOwner). Cannot kill safely." -ForegroundColor Yellow
            continue
        }
        
        $proc = Get-Process -Id $pidOwner -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "Port $port is bound by PID $($proc.Id) ($($proc.ProcessName))" -ForegroundColor Yellow
            
            $isSafe = $false
            foreach ($safeName in $safeToKill) {
                if ($proc.ProcessName -match $safeName) {
                    $isSafe = $true
                    break
                }
            }
            
            if ($isSafe) {
                Write-Host "Process $($proc.ProcessName) matches TI/mmWave tool signatures. Stopping it safely..." -ForegroundColor Cyan
                Stop-Process -Id $proc.Id -Force
                Write-Host "[OK] Stopped PID $($proc.Id)" -ForegroundColor Green
            } else {
                Write-Host "Process $($proc.ProcessName) (PID $($proc.Id)) is NOT recognized as a TI tool." -ForegroundColor Red
                $response = "y"
                if ($response -match "^[yY]") {
                    Stop-Process -Id $proc.Id -Force
                    Write-Host "[OK] Stopped PID $($proc.Id)" -ForegroundColor Green
                } else {
                    Write-Host "Skipped stopping PID $($proc.Id)." -ForegroundColor Yellow
                }
            }
        }
    }
}
Write-Host "Port check complete.`n" -ForegroundColor Green

# 3. Check Ethernet 4 Configuration
$adapterName = "Ethernet 4"
$expectedIP = "192.168.33.30"
$expectedSubnet = "255.255.255.0"

Write-Host "Checking network configuration for '$adapterName'..." -ForegroundColor Cyan
$netAdapter = Get-NetAdapter -Name $adapterName -ErrorAction SilentlyContinue
if ($netAdapter) {
    $ipConfig = Get-NetIPAddress -InterfaceAlias $adapterName -AddressFamily IPv4 -ErrorAction SilentlyContinue
    if ($ipConfig) {
        if ($ipConfig.IPAddress -eq $expectedIP -and $ipConfig.PrefixLength -eq 24) {
            Write-Host "[OK] $adapterName is configured correctly with IP $expectedIP/24." -ForegroundColor Green
        } else {
            Write-Host "[WARNING] $adapterName has IP $($ipConfig.IPAddress)/$($ipConfig.PrefixLength). Expected $expectedIP/24." -ForegroundColor Yellow
            $fixIp = "y"
            if ($fixIp -match "^[yY]") {
                Set-NetIPInterface -InterfaceAlias $adapterName -Dhcp Disabled
                Remove-NetIPAddress -InterfaceAlias $adapterName -Confirm:$false -ErrorAction SilentlyContinue
                New-NetIPAddress -InterfaceAlias $adapterName -IPAddress $expectedIP -PrefixLength 24 -Confirm:$false | Out-Null
                Write-Host "[OK] Applied static IP $expectedIP to $adapterName" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "[WARNING] $adapterName does not have an IPv4 address." -ForegroundColor Yellow
        $fixIp = "y"
        if ($fixIp -match "^[yY]") {
            Set-NetIPInterface -InterfaceAlias $adapterName -Dhcp Disabled
            New-NetIPAddress -InterfaceAlias $adapterName -IPAddress $expectedIP -PrefixLength 24 -Confirm:$false | Out-Null
            Write-Host "[OK] Applied static IP $expectedIP to $adapterName" -ForegroundColor Green
        }
    }
} else {
    Write-Host "[ERROR] Network adapter '$adapterName' not found. Please verify the name in Control Panel." -ForegroundColor Red
}

# 4. Check/Add Firewall Rules
Write-Host "`nChecking Firewall Rules..." -ForegroundColor Cyan
function Ensure-FirewallRule ($port, $direction) {
    $ruleName = "TI DCA1000 UDP $port $direction"
    $rule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    if (-not $rule) {
        Write-Host "Adding Firewall rule for UDP $port ($direction)..." -ForegroundColor Cyan
        New-NetFirewallRule -DisplayName $ruleName -Direction $direction -Protocol UDP -LocalPort $port -Action Allow -Profile Any | Out-Null
        Write-Host "[OK] Firewall rule added." -ForegroundColor Green
    } else {
        Write-Host "[OK] Firewall rule '$ruleName' already exists." -ForegroundColor Green
    }
}

Ensure-FirewallRule 4096 "Inbound"
Ensure-FirewallRule 4098 "Inbound"
Ensure-FirewallRule 4096 "Outbound"
Ensure-FirewallRule 4098 "Outbound"

# 5. Optional CLI Test
$cliPath = Get-ChildItem -Path "C:\ti\mmwave_studio_03_01_04_04" -Filter "DCA1000EVM_CLI_Control.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
if ($cliPath) {
    Write-Host "`nFound DCA1000 CLI tool at: $($cliPath.FullName)" -ForegroundColor Cyan
    $runTest = "y"
    if ($runTest -match "^[yY]") {
        $testDir = Join-Path $captureDir "cli_test"
        if (-not (Test-Path $testDir)) { New-Item -ItemType Directory -Path $testDir | Out-Null }
        
        $jsonConfig = @"
{
    "DCA1000Config": {
        "dataLoggingMode": "raw",
        "dataTransferMode": "LVDSCapture",
        "dataCaptureMode": "ethernetStream",
        "lvdsMode": 1,
        "dataFormatMode": 1,
        "packetDelay_us": 25,
        "ethernetConfig": {
            "DCA1000IPAddress": "192.168.33.180",
            "DCA1000ConfigPort": 4096,
            "DCA1000DataPort": 4098,
            "DCA1000MACAddress": "12.34.56.78.90.12",
            "systemIPAddress": "192.168.33.30",
            "systemConfigPort": 4096,
            "systemDataPort": 4098,
            "systemMACAddress": "00.00.00.00.00.00"
        }
    }
}
"@
        $jsonFile = Join-Path $testDir "sys_config.json"
        $jsonConfig | Out-File -FilePath $jsonFile -Encoding ASCII
        
        Write-Host "Running DCA1000EVM_CLI_Control.exe fpga_version..." -ForegroundColor Cyan
        # The CLI requires running from its own directory to find specific DLLs
        Push-Location $cliPath.DirectoryName
        $processArgs = "fpga_version", $jsonFile
        $proc = Start-Process -FilePath $cliPath.FullName -ArgumentList $processArgs -NoNewWindow -Wait -PassThru
        Pop-Location

        if ($proc.ExitCode -eq 0) {
            Write-Host "[OK] FPGA Version queried successfully! The DCA1000 is communicating properly over Ethernet." -ForegroundColor Green
        } else {
            Write-Host "[WARNING] CLI tool returned exit code $($proc.ExitCode). Ensure DCA is powered on and Ethernet is connected." -ForegroundColor Yellow
        }
    }
}

# 6. Manual Steps
Write-Host "`n*** NEXT STEPS ***" -ForegroundColor Cyan
Write-Host "1. Power-cycle the DCA1000 (disconnect/reconnect 5V power)."
Write-Host "2. Keep DCA J6 Ethernet connected to $adapterName."
Write-Host "3. Re-open mmWave Studio (Run as Administrator)."
Write-Host "4. Verify the Dump File path is exactly: C:\ti\captures\adc_data.bin"
Write-Host "5. Go to 'SensorConfig' tab -> 'SetUp DCA1000'."
Write-Host "6. Click 'Connect, Reset and Configure'."
Write-Host "7. Verify 'FPGA version' is read successfully in the logs."
Write-Host "8. Click 'DCA1000 ARM', wait ~2 seconds, then click 'Trigger Frame'."
Write-Host "******************`n"
