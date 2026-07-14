"""Generates DCA1000 Lua scripts for setup and capture trigger.

Strict separation of concerns:
- Setup script contains ONLY DCA configuration (no RF transmission).
- Capture trigger script contains StartRecord and StartFrame.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from awr2944_dca.mmws.post_connect import GeneratedScript

def generate_dca_setup_script(
    run_id: str,
    out_path: Path,
    host_ip: str = "192.168.33.30",
    dca_ip: str = "192.168.33.180",
    dca_mac: str = "12:34:56:78:90:12",
    config_port: int = 4096,
    data_port: int = 4098,
    packet_delay: int = 25,
) -> GeneratedScript:
    """Generate DCA1000 setup Lua. State-changing, but no RF transmission."""
    from awr2944_dca.mmws.post_connect import (
        GeneratedScript,
        _atomic_write_manifest,
        _lua_log_progress,
        _lua_result_init_and_save,
        _lua_safe_call,
    )

    prog_path = out_path.with_name(out_path.stem + "_progress.jsonl")
    res_path = out_path.with_name(out_path.stem + "_result.json")

    _atomic_write_manifest(run_id, "dca_setup", out_path, res_path, prog_path)

    log_fn = _lua_log_progress()
    res_fn = _lua_result_init_and_save(run_id, res_path.resolve().as_posix())
    safe_fn = _lua_safe_call()

    header = [
        "-- DCA1000 Setup (Non-RF)",
        f"-- run_id: {run_id}",
        "-- stage: dca_setup",
        "-- Output paths:",
        f"--   lua: {out_path.resolve().as_posix()}",
        f"--   prog: {prog_path.resolve().as_posix()}",
        f"--   res: {res_path.resolve().as_posix()}",
        "-- Configuration parameters:",
        f"--   host_ip: {host_ip}",
        f"--   dca_ip: {dca_ip}",
        f"--   dca_mac: {dca_mac}",
        f"--   config_port: {config_port}",
        f"--   data_port: {data_port}",
        f"--   packet_delay: {packet_delay}",
        "",
        f'local run_id = "{run_id}"',
        'local run_stage = "dca_setup"',
        f'local progress_path = [[{prog_path.resolve().as_posix()}]]',
        "",
        res_fn,
        "",
        log_fn,
        "",
        safe_fn,
        "",
        'print("AWR_RUN_BEGIN run_id=" .. run_id .. " stage=" .. run_stage)',
        "",
    ]

    # Exactly 4 allowed calls
    body = [
        'if not safeCall("SelectCaptureDevice", function() return ar1.SelectCaptureDevice("DCA1000") end, true) then return end',
        "",
        f'if not safeCall("CaptureCardConfig_EthInit", function() return ar1.CaptureCardConfig_EthInit("{host_ip}", "{dca_ip}", "{dca_mac}", {config_port}, {data_port}) end, true) then return end',
        "",
        'if not safeCall("CaptureCardConfig_Mode", function() return ar1.CaptureCardConfig_Mode(1, 1, 1, 2, 3, 30) end, true) then return end',
        "",
        f'if not safeCall("CaptureCardConfig_PacketDelay", function() return ar1.CaptureCardConfig_PacketDelay({packet_delay}) end, true) then return end',
        "",
        'print("DCA1000 setup completed successfully.")',
        'result.success = true',
        'saveResult()',
        'print("AWR_RUN_END run_id=" .. run_id .. " stage=" .. run_stage .. " success=true")',
    ]

    script = "\n".join(header + body)

    metadata = {
        "run_id": run_id,
        "stage": "dca_setup",
        "host_ip": host_ip,
        "dca_ip": dca_ip,
        "dca_mac": dca_mac,
        "config_port": config_port,
        "data_port": data_port,
        "packet_delay": packet_delay,
    }

    return GeneratedScript(
        script=script,
        run_id=run_id,
        lua_path=out_path,
        result_path=res_path,
        progress_path=prog_path,
        dofile=f"dofile([[{out_path.resolve()}]])",
        metadata=metadata,
    )


def generate_capture_trigger_script(
    run_id: str,
    out_path: Path,
    output_dir: Path,
    confirm_startframe: bool = False,
) -> GeneratedScript:
    """Generate the trigger Lua script.
    
    This script is small and only executes StartRecord and StartFrame.
    Requires radar static configuration to be complete.
    """
    from awr2944_dca.mmws.post_connect import (
        GeneratedScript,
        _atomic_write_manifest,
        _lua_log_progress,
        _lua_result_init_and_save,
        _lua_safe_call,
    )

    if not confirm_startframe:
        raise ValueError(
            "ERROR: This script contains ar1.StartFrame(), which triggers RF transmission.\n"
            "Re-run with --confirm-startframe only after:\n"
            "  1. DCA setup has passed (check-run shows success)\n"
            "  2. You have visually confirmed DCA1000 STS_LED is active\n"
            "  3. The capture output directory exists"
        )
        
    if not output_dir.exists():
        raise FileNotFoundError(
            f"ERROR: Output directory does not exist: {output_dir}\n"
            f"mmWave Studio will silently fail to record. Create it or use --output-dir."
        )

    prog_path = out_path.with_name(out_path.stem + "_progress.jsonl")
    res_path = out_path.with_name(out_path.stem + "_result.json")
    _atomic_write_manifest(run_id, "capture_trigger", out_path, res_path, prog_path)

    log_fn = _lua_log_progress()
    res_fn = _lua_result_init_and_save(run_id, res_path.resolve().as_posix())
    safe_fn = _lua_safe_call()

    adc_data_path = str((output_dir / "adc_data.bin").resolve())

    header = [
        "-- ******************************************************************",
        "-- * WARNING: THIS SCRIPT CALLS ar1.StartFrame().",
        "-- * IT WILL TRIGGER RF TRANSMISSION.",
        "-- * DO NOT RUN UNLESS DCA SETUP HAS PASSED AND YOU ARE READY TO TRANSMIT.",
        "-- ******************************************************************",
        f"-- run_id: {run_id}",
        "-- stage: capture_trigger",
        "-- Output paths:",
        f"--   lua: {out_path.resolve().as_posix()}",
        f"--   prog: {prog_path.resolve().as_posix()}",
        f"--   res: {res_path.resolve().as_posix()}",
        "--",
        "-- Note: mmWave Studio StartRecord receives adc_data_path ending in .bin",
        "--       DCA raw output may appear as adc_data_Raw_0.bin",
        "--       post-processing/output target is adc_data.bin",
        f"--   adc_data_path: {adc_data_path}",
        "",
        f'local run_id = "{run_id}"',
        'local run_stage = "capture_trigger"',
        f'local progress_path = [[{prog_path.resolve().as_posix()}]]',
        "",
        res_fn,
        "",
        log_fn,
        "",
        safe_fn,
        "",
        'print("AWR_RUN_BEGIN run_id=" .. run_id .. " stage=" .. run_stage)',
        "",
    ]

    body = [
        f'local adc_data_path = [[{adc_data_path}]]',
        'if not safeCall("CaptureCardConfig_StartRecord", function() return ar1.CaptureCardConfig_StartRecord(adc_data_path, 1) end, true) then return end',
        "RSTD.Sleep(2000)",
        "",
        'if not safeCall("StartFrame", function() return ar1.StartFrame() end, true) then return end',
        "RSTD.Sleep(5000)",
        "",
        'if not safeCall("CaptureCardConfig_StopRecord", function() return ar1.CaptureCardConfig_StopRecord() end, true) then return end',
        "RSTD.Sleep(1000)",
        "",
        'print("Capture trigger completed successfully.")',
        'result.success = true',
        'saveResult()',
        'print("AWR_RUN_END run_id=" .. run_id .. " stage=" .. run_stage .. " success=true")',
    ]

    script = "\n".join(header + body)

    metadata = {
        "run_id": run_id,
        "stage": "capture_trigger",
        "output_dir": str(output_dir.resolve()),
        "adc_data_path": adc_data_path,
    }

    return GeneratedScript(
        script=script,
        run_id=run_id,
        lua_path=out_path,
        result_path=res_path,
        progress_path=prog_path,
        dofile=f"dofile([[{out_path.resolve()}]])",
        metadata=metadata,
    )


def generate_postproc_script(
    run_id: str,
    out_path: Path,
    output_dir: Path,
) -> GeneratedScript:
    """Generate Matlab post-processing Lua script."""
    prog_path = out_path.with_name(out_path.stem + "_progress.jsonl")
    res_path = out_path.with_name(out_path.stem + "_result.json")
    _atomic_write_manifest(run_id, "postproc", out_path, res_path, prog_path)

    log_fn = _lua_log_progress()
    res_fn = _lua_result_init_and_save(run_id, res_path.resolve().as_posix())
    safe_fn = _lua_safe_call()

    adc_data_path = str((output_dir / "adc_data.bin").resolve())

    header = [
        f"-- run_id: {run_id}",
        "-- stage: postproc",
        "-- Output paths:",
        f"--   lua: {out_path.resolve().as_posix()}",
        f"--   prog: {prog_path.resolve().as_posix()}",
        f"--   res: {res_path.resolve().as_posix()}",
        f"--   adc_data_path: {adc_data_path}",
        "",
        f'local run_id = "{run_id}"',
        'local run_stage = "postproc"',
        f'local progress_path = [[{prog_path.resolve().as_posix()}]]',
        "",
        res_fn,
        "",
        log_fn,
        "",
        safe_fn,
        "",
        'print("AWR_RUN_BEGIN run_id=" .. run_id .. " stage=" .. run_stage)',
        "",
    ]

    body = [
        f'local adc_data_path = [[{adc_data_path}]]',
        'if not safeCall("StartMatlabPostProc", function() return ar1.StartMatlabPostProc(adc_data_path) end, true) then return end',
        "",
        'print("Post-processing trigger completed successfully.")',
        'result.success = true',
        'saveResult()',
        'print("AWR_RUN_END run_id=" .. run_id .. " stage=" .. run_stage .. " success=true")',
    ]

    script = "\n".join(header + body)

    metadata = {
        "run_id": run_id,
        "stage": "postproc",
        "output_dir": str(output_dir.resolve()),
        "adc_data_path": adc_data_path,
    }

    return GeneratedScript(
        script=script,
        run_id=run_id,
        lua_path=out_path,
        result_path=res_path,
        progress_path=prog_path,
        dofile=f"dofile([[{out_path.resolve()}]])",
        metadata=metadata,
    )
