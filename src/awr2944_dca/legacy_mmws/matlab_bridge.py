"""MATLAB RSTD bridge for awr2944_dca."""

import os
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Optional, Any

def locate_matlab() -> dict[str, list[str]]:
    """Locate MATLAB installations and runtimes."""
    info: dict[str, list[str]] = {
        "full_matlab": [],
        "matlab_runtime": [],
        "where_matlab": [],
    }
    # First try `where matlab`
    try:
        res = subprocess.run(["where", "matlab"], capture_output=True, text=True, timeout=5)
        if res.returncode == 0:
            for line in res.stdout.strip().splitlines():
                if line:
                    info["where_matlab"].append(line)
    except Exception:
        pass

    # Try common install paths
    program_files_list = [
        os.environ.get("ProgramFiles", "C:\\Program Files"),
        os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
    ]
    for pf in program_files_list:
        pf_path = Path(pf)
        # Full MATLAB
        matlab_dir = pf_path / "MATLAB"
        if matlab_dir.exists():
            for release_dir in matlab_dir.iterdir():
                if release_dir.name == "MATLAB_Runtime":
                    for rt_release in release_dir.iterdir():
                        info["matlab_runtime"].append(str(rt_release))
                else:
                    matlab_exe = release_dir / "bin" / "matlab.exe"
                    if matlab_exe.exists():
                        info["full_matlab"].append(str(matlab_exe))

    return info

def find_matlab() -> Optional[str]:
    """Find the MATLAB executable."""
    info = locate_matlab()
    if info["where_matlab"]:
        return info["where_matlab"][0]
    if info["full_matlab"]:
        return info["full_matlab"][-1]  # Return newest
    return None

def build_matlab_script(
    dll_path: str,
    mode: str,
    script_path: Optional[str] = None,
    result_path: str = "worker_result.json",
    host: str = "127.0.0.1",
    port: int = 2777,
) -> str:
    """Build the .m script for MATLAB to execute."""
    
    # Escape paths for MATLAB
    dll_path = dll_path.replace("'", "''")
    result_path = result_path.replace("'", "''")
    
    if script_path:
        script_path = str(Path(script_path).resolve()).replace("\\", "/")

    script_content = []
    
    # Start try block
    script_content.append("try")
    # Diagnostics
    script_content.append("    disp('STEP_START: Diagnostics');")
    script_content.append("    v = ver('matlab');")
    script_content.append("    disp(['MATLAB Version: ', v.Version, ' ', v.Release]);")
    script_content.append("    disp(['Architecture: ', computer('arch')]);")
    script_content.append(f"    disp(['Loading DLL: ', '{dll_path}']);")
    script_content.append("    disp('STEP_DONE: Diagnostics');")

    script_content.append("    disp('STEP_START: Init');")
    script_content.append(f"    NET.addAssembly('{dll_path}');")
    script_content.append("    err = RtttNetClientAPI.RtttNetClient.Init();")
    script_content.append("    if err ~= 0")
    script_content.append("        error('Init failed with %d', err);")
    script_content.append("    end")
    script_content.append("    disp('STEP_DONE: Init');")
    
    script_content.append("    disp('STEP_START: Connect');")
    script_content.append(f"    err = RtttNetClientAPI.RtttNetClient.Connect('{host}', {port});")
    script_content.append("    if err ~= 0")
    script_content.append("        error('Connect failed with %d', err);")
    script_content.append("    end")
    script_content.append("    pause(1);") # official TI pattern
    script_content.append("    disp('STEP_DONE: Connect');")
    
    if mode == "ping":
        script_content.append("    res_json = '{\"mode\":\"ping\",\"success\":true}';")
    else:
        if mode == "send-inline":
            script_content.append("    lua_cmd = 'WriteToLog(\"MATLAB_INLINE_TEST\\\\n\", \"green\")';")
        elif mode in ("send-command", "dofile-test"):
            script_content.append(f"    lua_cmd = sprintf('dofile([[%s]])', '{script_path}');")
            
        script_content.append("    disp('STEP_START: SendCommand');")
        script_content.append("    try")
        script_content.append("        err = RtttNetClientAPI.RtttNetClient.SendCommand(lua_cmd);")
        script_content.append("    catch ME_send")
        script_content.append("        disp(['One-arg SendCommand failed: ', ME_send.message, '. Trying two-arg...']);")
        script_content.append("        res_arr = NET.createArray('System.Object', 1);")
        script_content.append("        try")
        script_content.append("            err = RtttNetClientAPI.RtttNetClient.SendCommand(lua_cmd, res_arr);")
        script_content.append("        catch")
        script_content.append("            [err, res_arr] = RtttNetClientAPI.RtttNetClient.SendCommand(lua_cmd, res_arr);")
        script_content.append("        end")
        script_content.append("    end")
        script_content.append("    disp('STEP_DONE: SendCommand');")
        script_content.append(f"    res_json = sprintf('{{\"mode\":\"%s\",\"success\":true,\"send_return\":%d}}', '{mode}', err);")
    
    script_content.append("    disp('STEP_START: Disconnect');")
    script_content.append("    RtttNetClientAPI.RtttNetClient.Disconnect();")
    script_content.append("    RtttNetClientAPI.RtttNetClient.Close();")
    script_content.append("    disp('STEP_DONE: Disconnect');")
    
    # Write success
    script_content.append(f"    fid = fopen('{result_path}', 'w');")
    script_content.append("    fprintf(fid, '%s', res_json);")
    script_content.append("    fclose(fid);")
    
    # Catch block
    script_content.append("catch ME")
    script_content.append("    disp('MATLAB ERROR:');")
    script_content.append("    disp(ME.message);")
    script_content.append("    if contains(ME.identifier, 'BadImageFormatException')")
    script_content.append("        disp('Bitness mismatch: Make sure you use 32-bit MATLAB for 32-bit DLL.');")
    script_content.append("    end")
    script_content.append(f"    fid = fopen('{result_path}', 'w');")
    script_content.append("    fprintf(fid, '{\"success\":false,\"exception\":\"%s\"}', strrep(ME.message, '\"', '\\\"'));")
    script_content.append("    fclose(fid);")
    script_content.append("end")
    
    script_content.append("exit;")
    return "\n".join(script_content)
