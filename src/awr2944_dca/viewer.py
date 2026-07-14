"""Python-to-MATLAB viewer launcher for AWR2944 PostProc clones."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

import numpy as np

from awr2944_dca.dsp.config import PipelineConfig, RadarProfile
from awr2944_dca.dsp.matlab_export import export_to_mat
from awr2944_dca.dsp.pipeline import load_canonical_cube, run_pipeline

def _find_matlab() -> str:
    """Find the MATLAB executable."""
    matlab_exe = shutil.which("matlab")
    if matlab_exe:
        return matlab_exe
    # Fallback to common Windows paths
    for year in range(2025, 2018, -1):
        for release in ("b", "a"):
            path = Path(rf"C:\Program Files\MATLAB\R{year}{release}\bin\matlab.exe")
            if path.exists():
                return str(path)
    raise FileNotFoundError("Could not find matlab.exe on the system PATH or standard locations.")

def export_viewer_payload(
    capture_path: str | Path,
    output_mat: str | Path,
    profile: RadarProfile,
    *,
    clim_mode: str = "fixed_global",
    display_dynamic_range_db: float = 40.0,
    mode: str = "standalone",
    mmws_fig_path: str | Path | None = None
) -> None:
    """Run production DSP and save the exhaustive viewer payload."""
    capture_path = Path(capture_path)
    output_mat_path = Path(output_mat)
    
    print(f"Loading cube from {capture_path}...")
    adc_cube, metadata = load_canonical_cube(capture_path, profile)
    
    print("Running production DSP pipeline (Raw, No Clutter Removal)...")
    from awr2944_dca.dsp.config import PipelineConfig, DopplerProcessingConfig, ClutterRemovalMode
    cfg = PipelineConfig(
        profile=profile,
        doppler_cfg=DopplerProcessingConfig(clutter_removal=ClutterRemovalMode.NONE)
    )
    result = run_pipeline(adc_cube, cfg, run_cfar=True)
    
    # Extract linear arrays
    range_complex = result.range_result.complex_cube
    # 1D Magnitude (unnormalized)
    range_mag_linear = np.abs(range_complex)
    # 1D Power in dBFS (Referenced to full scale ADC sinusoid)
    # Max possible FFT magnitude for real sinusoid = (2^15) * (N/2)
    fft_full_scale = 32768.0 * (profile.adc_samples / 2.0)
    range_power_db = 20 * np.log10(np.maximum(range_mag_linear / fft_full_scale, 1e-12))
    
    # 2D Doppler mapping (Raw)
    doppler_complex_raw = result.doppler_result.complex_cube
    doppler_power_db_raw = 10 * np.log10(np.sum(np.abs(doppler_complex_raw)**2, axis=2) + 1)

    # 2D Doppler mapping (Slow Time Mean)
    from awr2944_dca.dsp.doppler_fft import compute_doppler_fft
    d_cfg_stm = DopplerProcessingConfig(clutter_removal=ClutterRemovalMode.SLOW_TIME_MEAN)
    res_stm = compute_doppler_fft(result.range_result.complex_cube, profile, d_cfg_stm)
    doppler_power_db_slow_time_mean = 10 * np.log10(np.sum(np.abs(res_stm.complex_cube)**2, axis=2) + 1)

    # 2D Doppler mapping (Zero Notch)
    d_cfg_notch = DopplerProcessingConfig(clutter_removal=ClutterRemovalMode.ZERO_DOPPLER_NOTCH, zero_doppler_notch_bins=2)
    res_notch = compute_doppler_fft(result.range_result.complex_cube, profile, d_cfg_notch)
    doppler_power_db_zero_notch = 10 * np.log10(np.sum(np.abs(res_notch.complex_cube)**2, axis=2) + 1)
    
    # We will use raw for the default display calculation
    doppler_power_db = doppler_power_db_raw
    
    # Fixed global CLim for the 2D power map
    global_max_db = np.max(doppler_power_db)
    if clim_mode == "fixed_global":
        display_clim = [float(max(0, global_max_db - display_dynamic_range_db)), float(global_max_db)]
    else:
        # Fallback to current-frame autoscale string flag for MATLAB to handle
        display_clim = [0.0, 0.0]  # MATLAB will ignore and use auto
    
    # Detections (to struct array friendly format)
    det_v = []
    det_r = []
    det_f = []
    if result.detections:
        for d in result.detections.detections:
            det_f.append(d.frame)
            det_v.append(d.velocity_mps)
            det_r.append(d.range_m)
            
    # Sample time axis
    adc_time_axis_s = np.arange(profile.adc_samples) / profile.adc_sample_rate_hz
    
    extra_fields = {
        "payload_schema_version": "v1.0",
        "DSP_config_id": "production_default",
        
        # We must transpose linear maps for MATLAB natively [range, doppler, frame]
        "range_power_linear": np.ascontiguousarray(range_mag_linear.transpose(3, 2, 1, 0)),
        "range_power_db": range_power_db.transpose(3, 2, 1, 0),
        "doppler_power_db_raw": doppler_power_db_raw.transpose(2, 1, 0),
        "doppler_power_db_slow_time_mean": doppler_power_db_slow_time_mean.transpose(2, 1, 0),
        "doppler_power_db_zero_notch": doppler_power_db_zero_notch.transpose(2, 1, 0),
        
        # Legacy mapping for main UI component
        "doppler_power_db": doppler_power_db.transpose(2, 1, 0),
        
        # Dimensions
        "adc_time_axis_s": adc_time_axis_s,
        
        # Detections
        "det_frames": np.array(det_f, dtype=np.int32),
        "det_velocities": np.array(det_v, dtype=np.float64),
        "det_ranges": np.array(det_r, dtype=np.float64),
        
        # Normalization metadata
        "dB_definition": "20*log10(abs) for 1D, 10*log10(sum(abs^2)+1) for 2D",
        "FFT_normalization": "unnormalized",
        "window_normalization": "none",
        "display_CLim": display_clim,
        "display_normalization_mode": clim_mode,
        "display_dynamic_range_db": display_dynamic_range_db,
        "mode": mode,
        "mmws_fig_path": str(mmws_fig_path) if mmws_fig_path else "",
    }
    
    print(f"Exporting payload to {output_mat_path}...")
    export_to_mat(
        adc_cube=adc_cube,
        profile=profile,
        output_path=output_mat_path,
        canonical_raw_sha256=metadata["raw_sha256"],
        source_raw_path=metadata["source_path"],
        extra_fields=extra_fields,
    )
    return output_mat_path

def _find_native_mmws_fig() -> Path | None:
    """Find the newest compatible adc_data.fig in C:\\ti\\mmwave_studio_* installations."""
    ti_dir = Path(r"C:\ti")
    if not ti_dir.exists():
        return None
    
    candidates = list(ti_dir.glob("mmwave_studio_*/mmWaveStudio/PostProc/adc_data.fig"))
    if not candidates:
        return None
    
    candidates.sort(reverse=True)
    return candidates[0]

def export_viewer_payload_and_launch(
    capture_path: str | Path,
    profile: RadarProfile,
    *,
    clim_mode: str = "fixed_global",
    display_dynamic_range_db: float = 40.0,
    mode: str = "standalone",
    mmws_fig_path: str | Path | None = None,
    matlab_script_dir: str | Path | None = None,
) -> subprocess.Popen:
    """Run production DSP, export payload, and launch the MATLAB viewer.
    
    Parameters
    ----------
    capture_path : str | Path
        Path to the binary file to load (e.g. adc_data.bin).
    profile : RadarProfile
        Profile associated with the binary file.
    clim_mode : str, optional
        Color limit mode for 2D FFT, by default "fixed_global".
    display_dynamic_range_db : float, optional
        Dynamic range for 2D FFT mapping, by default 40.0.
    mode : str, optional
        Launch mode, by default "standalone". Other option: "native_experimental"
    mmws_fig_path : str | Path | None, optional
        Path to mmWave Studio figure (if native_experimental mode).
    matlab_script_dir : str | Path | None, optional
        Path to the dir containing dcaViewerMain.m.
    
    Returns
    -------
    subprocess.Popen
        The MATLAB process handle.
    """
    if mode not in ("auto", "native_experimental", "standalone"):
        raise ValueError("mode must be 'auto', 'native_experimental', or 'standalone'")
        
    if mode == "auto":
        mode = "standalone"
        print("Auto mode requested. Defaulting to standalone mode.")
        
    if mode == "native_experimental":
        if mmws_fig_path is None:
            fig_path = _find_native_mmws_fig()
            if fig_path is not None:
                mmws_fig_path = fig_path
                print(f"Found authentic native TI figure at: {mmws_fig_path}")
            else:
                raise RuntimeError("native_experimental mode requested, but no local mmWave Studio installation found in C:\\ti")
    
    capture_path = Path(capture_path)
    output_dir = capture_path.parent / "viewer_payload"
    output_dir.mkdir(exist_ok=True)
    payload_path = output_dir / "viewer_payload.mat"
    
    export_viewer_payload(
        capture_path, 
        payload_path, 
        profile, 
        clim_mode=clim_mode, 
        display_dynamic_range_db=display_dynamic_range_db,
        mode=mode,
        mmws_fig_path=mmws_fig_path
    )
    
    matlab_exe = _find_matlab()
    
    if matlab_script_dir is None:
        # Default to the repo structure: root/matlab/viewer
        repo_root = Path(__file__).parent.parent.parent
        matlab_script_dir = repo_root / "matlab" / "viewer"
    
    matlab_script_dir = Path(matlab_script_dir).resolve()
    payload_path_str = str(payload_path.resolve())
    
    print("Launching MATLAB viewer...")
    
    # MATLAB command: addpath, then run the UI router
    matlab_cmd = f"addpath('{matlab_script_dir}'); dcaViewerMain('{payload_path_str}');"
    
    proc = subprocess.Popen(
        [matlab_exe, "-nosplash", "-nodesktop", "-r", matlab_cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    
    print(f"MATLAB launched successfully (PID: {proc.pid}).")
    return proc
