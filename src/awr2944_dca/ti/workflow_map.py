import json
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class WorkflowStep:
    name: str
    stage: str
    risk: str
    yaml_fields: list[str]
    allowed_yet: bool
    args: str = ""
    file: str = ""
    line: int = 0
    gui_equiv: str = ""

# Map of expected functions to their stages and yaml fields
FIRST_CAPTURE_MAP = {
    "SOPControl": ("connection-only", "state_changing", [], False, "Set SOP mode"),
    "Connect": ("connection-only", "state_changing", [], False, "Connect RS232/SPI"),
    "DownloadBSSFw": ("firmware loading", "state_changing", [], False, "Load BSS FW"),
    "DownloadMSSFw": ("firmware loading", "state_changing", [], False, "Load MSS FW"),
    "PowerOn": ("Device Boot / Power-On", "state_changing", [], False, "SPI Connect / RF Power Up"),
    "RfEnable": ("RF enable/init", "state_changing", [], False, "RF Enable"),
    "ChanNAdcConfig": ("static ADC/LVDS config", "safe_with_board_no_rf", ["rx_antennas", "adc_bits", "adc_format"], False, "StaticConfig -> ADC Config"),
    "LPModConfig": ("static ADC/LVDS config", "safe_with_board_no_rf", ["adc_format"], False, "StaticConfig -> ADC Config"),
    "RfInit": ("RF enable/init", "state_changing", [], False, "RF Init"),
    "DataPathConfig": ("static ADC/LVDS config", "safe_with_board_no_rf", ["adc_format"], False, "DataConfig -> Data Path"),
    "LvdsClkConfig": ("static ADC/LVDS config", "safe_with_board_no_rf", ["adc_format"], False, "DataConfig -> LVDS Clk"),
    "LVDSLaneConfig": ("static ADC/LVDS config", "safe_with_board_no_rf", ["lanes"], False, "DataConfig -> LVDS Lane"),
    "ProfileConfig": ("profile/chirp/frame config", "safe_with_board_no_rf", ["start_freq_ghz", "idle_time_us", "adc_start_time_us", "ramp_end_time_us", "slope_mhz_per_us", "tx_power_backoff_db", "tx_phase_shift_deg", "adc_samples", "sample_rate_ksps", "rx_gain_db"], False, "SensorConfig -> Profile"),
    "ChirpConfig": ("profile/chirp/frame config", "safe_with_board_no_rf", ["tx_antennas"], False, "SensorConfig -> Chirp"),
    "FrameConfig": ("profile/chirp/frame config", "safe_with_board_no_rf", ["frames", "chirps_per_frame", "frame_periodicity_ms"], False, "SensorConfig -> Frame"),
    "AdvanceFrameConfig": ("profile/chirp/frame config", "safe_with_board_no_rf", [], False, "SensorConfig -> Advanced Frame"),
    "SelectCaptureDevice": ("DCA1000 setup", "state_changing", ["dca_ip", "dca_mac"], False, "CaptureCard -> Select"),
    "CaptureCardConfig_EthInit": ("DCA1000 setup", "state_changing", ["dca_ip", "dca_mac"], False, "CaptureCard -> Eth Init"),
    "CaptureCardConfig_Mode": ("DCA1000 setup", "state_changing", ["adc_format"], False, "CaptureCard -> Mode"),
    "CaptureCardConfig_PacketDelay": ("DCA1000 setup", "state_changing", ["dca_delay"], False, "CaptureCard -> Packet Delay"),
    "CaptureCardConfig_StartRecord": ("capture trigger", "capture_triggering", [], False, "CaptureCard -> Start Record"),
    "StartFrame": ("capture trigger", "capture_triggering", [], False, "SensorConfig -> Start Frame"),
    "StartMatlabPostProc": ("post-processing", "safe_offline", [], False, "CaptureCard -> PostProc")
}


def extract_workflow(ti_scripts_dir: Path, source_file: str) -> list[WorkflowStep]:
    """Scan TI scripts and extract only the first-capture sequence."""
    results = []
    
    target_path = None
    for filepath in ti_scripts_dir.rglob("*.lua"):
        if filepath.name == source_file:
            target_path = filepath
            break
            
    if not target_path:
        return results

    try:
        content = target_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return results

    # We want to match `ar1.Function(args)` or just `ar1.Function`
    # More permissive regex for arguments
    pattern = re.compile(r"ar1\.([a-zA-Z0-9_]+)\s*\((.*?)\)", re.DOTALL)
    
    for i, line in enumerate(content.splitlines(), start=1):
        line_str = line.strip()
        if line_str.startswith("--"):
            continue
            
        # To handle multi-line arguments in AdvanceFrameConfig, we should probably just
        # do a basic match per line for now and join lines if needed, but the user's
        # file seems to break AdvanceFrameConfig across lines. Let's do a simple line 
        # match and clean it up.
        matches = re.finditer(r"ar1\.([a-zA-Z0-9_]+)", line_str)
        for m in matches:
            func = m.group(1)
            
            # Check if this function is in our strict allowlist
            if func in FIRST_CAPTURE_MAP:
                # Try to extract arguments if they are on the same line
                args = ""
                arg_match = re.search(rf"ar1\.{func}\s*\((.*?)\)", line_str)
                if arg_match:
                    args = arg_match.group(1)
                
                info = FIRST_CAPTURE_MAP[func]
                
                # Deduplicate sequential calls (like multiple ChirpConfigs)
                # Unless they are actually different, but for the map, we just need the first instance
                # Actually, let's keep all instances to show the real flow, but limit to 3 max per func?
                # The user asks for the sequence.
                results.append(WorkflowStep(
                    name=func,
                    stage=info[0],
                    risk=info[1],
                    yaml_fields=info[2],
                    allowed_yet=info[3],
                    args=args,
                    file=target_path.name,
                    line=i,
                    gui_equiv=info[4]
                ))

    # Deduplicate while preserving order for the workflow map
    seen = set()
    deduped = []
    for r in results:
        if r.name not in seen:
            seen.add(r.name)
            deduped.append(r)
            
    return deduped

def write_workflow_map(steps: list[WorkflowStep], out_dir: Path):
    json_path = out_dir / "first_capture_workflow_map.json"
    data = [s.__dict__ for s in steps]
    json_path.write_text(json.dumps(data, indent=2))
    
    md_path = out_dir / "first_capture_workflow_map.md"
    
    # Group by stage
    stages = [
        "offline/read-only",
        "connection-only",
        "firmware loading",
        "Device Boot / Power-On",
        "RF enable/init",
        "static ADC/LVDS config",
        "profile/chirp/frame config",
        "DCA1000 setup",
        "capture trigger",
        "post-processing"
    ]
    
    md_lines = ["# First Capture Workflow Map\n"]
    md_lines.append("This is the required API sequence for a standard first capture using mmWave Studio.\n")
    
    for stage in stages:
        stage_steps = [s for s in steps if s.stage == stage]
        if not stage_steps:
            continue
            
        md_lines.append(f"## Stage: {stage}\n")
        for step in stage_steps:
            md_lines.append(f"### `ar1.{step.name}`")
            if step.args:
                md_lines.append(f"- **Example Args:** `{step.args}`")
            md_lines.append(f"- **Source:** `{step.file}:{step.line}`")
            md_lines.append(f"- **GUI Equivalent:** {step.gui_equiv}")
            md_lines.append(f"- **Risk:** {step.risk}")
            md_lines.append(f"- **Allowed Yet:** {step.allowed_yet}")
            if step.yaml_fields:
                md_lines.append(f"- **Maps to `capture.yaml` fields:**")
                for f in step.yaml_fields:
                    md_lines.append(f"  - `{f}`")
            md_lines.append("")
            
    md_path.write_text("\n".join(md_lines))
