$dll = "C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\Clients\AR1xController\AR1xController.dll"
$out = "C:\Users\khams008\Documents\awr2944-fmcw-radar\exp_lau_probe\ti\probe_logs\ar1xcontroller_reflection_probe.txt"

$searchRoot = "C:\ti\mmwave_studio_03_01_04_04"
$depDirs = Get-ChildItem $searchRoot -Recurse -Directory -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName }
$depDirs += @(
    "C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\Clients\AR1xController",
    "C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\RunTime",
    "C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio"
)

[System.AppDomain]::CurrentDomain.add_AssemblyResolve({
    param($sender, $args)

    $asmName = New-Object System.Reflection.AssemblyName($args.Name)
    $dllName = $asmName.Name + ".dll"

    foreach ($d in $depDirs) {
        $candidate = Join-Path $d $dllName
        if (Test-Path $candidate) {
            return [System.Reflection.Assembly]::LoadFrom($candidate)
        }
    }

    return $null
})

$pattern = "Connect|SOP|Reset|Board|Gpio|Device|Variant|Chip|Radar|RS232|Port|Button|Form|Gui|Click|Set|Target|ATE|Serial|Uart|Firmware|BSS|MSS"

try {
    $asm = [System.Reflection.Assembly]::LoadFrom($dll)
    $lines = New-Object System.Collections.Generic.List[string]

    try {
        $types = $asm.GetTypes()
    } catch [System.Reflection.ReflectionTypeLoadException] {
        $types = $_.Exception.Types | Where-Object { $_ -ne $null }
        $lines.Add("PARTIAL_TYPE_LOAD: " + $_.Exception.Message)
        foreach ($loaderEx in $_.Exception.LoaderExceptions) {
            if ($loaderEx -ne $null) {
                $lines.Add("LOADER_EXCEPTION: " + $loaderEx.Message)
            }
        }
        $lines.Add("")
    }

    foreach ($t in $types) {
        $typeHit = $t.FullName -match $pattern
        $methodLines = New-Object System.Collections.Generic.List[string]

        try {
            $methods = $t.GetMethods([System.Reflection.BindingFlags]"Instance,Static,Public,NonPublic,DeclaredOnly")
            foreach ($m in $methods) {
                if ($m.Name -match $pattern) {
                    $methodLines.Add("  METHOD: " + $m.Name)
                }
            }
        } catch {
            $methodLines.Add("  METHOD_ENUM_FAILED: " + $_.Exception.Message)
        }

        if ($typeHit -or $methodLines.Count -gt 0) {
            $lines.Add("TYPE: " + $t.FullName)
            foreach ($ml in $methodLines) {
                $lines.Add($ml)
            }
            $lines.Add("")
        }
    }

    $lines | Set-Content $out
    Get-Content $out -Raw
} catch {
    "REFLECTION_FAILED: $($_.Exception.ToString())" | Set-Content $out
    Get-Content $out -Raw
}
