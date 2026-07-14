import argparse
import sys
import logging
import json
from pathlib import Path

from awr2944_dca.lab import RadarProject
from awr2944_dca.project import find_project_root, PROJECT_MARKER

def _resolve_project_root(provided_root: str | None) -> Path:
    if provided_root:
        p = Path(provided_root).resolve()
        if not (p / PROJECT_MARKER).is_file():
            print(f"Error: Explicit --project-root '{p}' does not contain {PROJECT_MARKER}")
            sys.exit(1)
        return p
    
    # Try CWD upward
    try:
        return find_project_root(Path.cwd())
    except FileNotFoundError:
        pass
        
    # Scan immediate subdirectories
    cwd = Path.cwd()
    sub_projects = []
    for sub in cwd.iterdir():
        if sub.is_dir() and (sub / PROJECT_MARKER).is_file():
            sub_projects.append(sub)
            
    if len(sub_projects) == 1:
        print(f"Discovered project at: {sub_projects[0]}")
        return sub_projects[0]
    elif len(sub_projects) > 1:
        print("Error: Multiple projects found in subdirectories. Please specify --project-root:")
        for sp in sub_projects:
            print(f"  {sp}")
        sys.exit(1)
        
    print("Error: Could not find project root (project.json). Run from within the radar project or specify --project-root.")
    sys.exit(1)

def run_dca_preflight(lab: RadarProject):
    print("=== DCA Preflight ===")
    
    toolchain = lab.capture._load_toolchain()
    if not toolchain:
        print("Error: Could not load toolchain.local.json")
        sys.exit(1)
        
    dca_cli = lab.capture._build_dca_cli(toolchain)
    if not dca_cli:
        print("Error: Could not construct DcaCli (missing paths?)")
        sys.exit(1)
        
    # Print resolved paths
    print("Paths:")
    print(f"  Control Exe: {dca_cli._control_exe.resolve()}")
    print(f"  Record Exe: {dca_cli._record_exe.resolve()}")
    print(f"  cf.json: {dca_cli._cf_json.resolve()}")
    print(f"  Working Dir: {dca_cli._working_dir.resolve()}")
    
    # Require existence
    if not dca_cli._control_exe.exists():
        print("Error: DCA control executable not found.")
        sys.exit(1)
    if not dca_cli._record_exe.exists():
        print("Error: DCA record executable not found.")
        sys.exit(1)
    if not dca_cli._cf_json.exists():
        print("Error: cf.json not found.")
        sys.exit(1)
    
    print("\nExecuting DCA initialization...")
    
    from awr2944_dca.capture_session import validate_dca_cmd_result, DcaInitializationError
    
    def run_op(name, func):
        print(f"\n--- {name} ---")
        res = func()
        print(f"Executable: {res.exe_path}")
        print(f"Arguments: {res.args}")
        print(f"Return Code: {res.returncode}")
        print(f"Stdout:\n{res.stdout}")
        print(f"Stderr:\n{res.stderr}")
        print(f"Elapsed Time: {res.elapsed_s:.3f}s")
        
        try:
            validate_dca_cmd_result(res, name)
            print("Validation: PASS")
        except DcaInitializationError as e:
            print(f"Validation: FAIL - {e}")
            print("\nAttempting safe cleanup...")
            dca_cli.stop_record()
            print(json.dumps({
                "hardware_touched": True,
                "dca_touched": True,
                "radar_touched": False,
                "sensor_started": False,
                "recording_started": False
            }, indent=2))
            sys.exit(1)
            
    run_op("reset_fpga", dca_cli.reset_fpga)
    import time
    time.sleep(1.0)
    run_op("configure_fpga", dca_cli.configure_fpga)
    run_op("configure_record", dca_cli.configure_record)
    
    print("\nDCA_INITIALIZATION_PASS\n")
    print(json.dumps({
        "hardware_touched": True,
        "dca_touched": True,
        "radar_touched": False,
        "sensor_started": False,
        "recording_started": False
    }, indent=2))

def main():
    parser = argparse.ArgumentParser(description="End-to-end AWR2944 Capture CLI (Direct UDP/UART)")
    parser.add_argument("profile", nargs="?", default="smoke_v1", help="Profile to run (e.g. smoke_v1)")
    parser.add_argument("--project-root", type=str, help="Path to project directory")
    parser.add_argument("--frames", type=int, default=9, help="Total frames to capture")
    parser.add_argument("--guard-frames", type=int, default=1, help="Number of guard frames to strip at the end")
    parser.add_argument("--com-port", type=str, default="COM8", help="UART COM port")
    parser.add_argument("--host-ip", type=str, default="192.168.33.30", help="Host IP for UDP receiver")
    parser.add_argument("--dca-ip", type=str, default="192.168.33.180", help="DCA EVM IP")
    parser.add_argument("--launch-viewer", action="store_true", help="Launch standalone MATLAB viewer after capture")
    parser.add_argument("--dry-run", action="store_true", help="Calculate capture parameters without touching hardware")
    parser.add_argument("--dca-preflight", action="store_true", help="Perform a hardware-touching DCA initialization preflight")
    parser.add_argument("--debug", action="store_true", help="Show full tracebacks on failure")
    
    args = parser.parse_args()
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")
    
    root_path = _resolve_project_root(args.project_root)
    lab = RadarProject(root_path)
    
    if args.dry_run:
        plan = lab.capture.dry_run(
            profile=args.profile,
            frames=args.frames,
            guard_frames=args.guard_frames,
            com_port=args.com_port,
            host_ip=args.host_ip,
            dca_ip=args.dca_ip
        )
        print(json.dumps(plan, indent=2))
        sys.exit(0)
        
    if args.dca_preflight:
        run_dca_preflight(lab)
        sys.exit(0)
    
    print(f"=== AWR2944 Production Capture ===")
    print(f"Profile: {args.profile}")
    print(f"Frames: {args.frames} ({args.frames - args.guard_frames} canonical, {args.guard_frames} guard)")
    print(f"Network: {args.host_ip} -> {args.dca_ip}")
    print(f"UART: {args.com_port}")
    
    try:
        result = lab.capture.run(
            profile=args.profile,
            frames=args.frames,
            guard_frames=args.guard_frames,
            com_port=args.com_port,
            host_ip=args.host_ip,
            dca_ip=args.dca_ip
        )
    except Exception as e:
        if args.debug:
            import traceback
            print(f"\n[DEBUG] Project root: {root_path}")
            print(f"[DEBUG] Full traceback:")
            traceback.print_exc()
        print(f"\n[FATAL] Capture failed: {e}")
        sys.exit(1)
        
    if not result.success:
        print(f"\n[FATAL] Capture failed at stage: {result.manifest.failure_stage}")
        print(f"Reason: {result.manifest.failure_reason}")
        print(f"Captured bytes: {result.manifest.captured_native_bytes} / {result.manifest.expected_native_bytes}")
        sys.exit(1)
        
    print("\n=== Capture Complete ===")
    capture_id = result.capture_dir.name
    print(f"Capture ID: {capture_id}")
    
    if args.launch_viewer:
        radar_capture = lab.get_capture(capture_id)
        radar_capture.open_viewer()
        
    print("Success.")

if __name__ == "__main__":
    main()
