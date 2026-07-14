import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Union

from ..cli import _lua_launch_probe_dir
from .guided_runner import GuidedWorkflowState

@dataclass
class FailureReport:
    detected_failure_type: str = "unknown"
    primary_artifact: str = ""
    workflow_id: str = ""
    run_id: str = ""
    label: str = ""
    current_stage: str = ""
    errors: List[str] = field(default_factory=list)
    related_artifacts: List[str] = field(default_factory=list)
    orphan_artifacts: List[str] = field(default_factory=list)
    resume_safe: str = "maybe"  # true, false, maybe, not_needed
    hardware_likely_touched: Union[bool, str] = "unknown"  # True, False, "unknown"
    likely_root_cause: str = ""
    recommended_next_action: str = ""
    power_cycle_required: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "detected_failure_type": self.detected_failure_type,
            "primary_artifact": self.primary_artifact,
            "workflow_id": self.workflow_id,
            "run_id": self.run_id,
            "label": self.label,
            "current_stage": self.current_stage,
            "errors": self.errors,
            "related_artifacts": self.related_artifacts,
            "orphan_artifacts": self.orphan_artifacts,
            "resume_safe": self.resume_safe,
            "hardware_likely_touched": self.hardware_likely_touched,
            "likely_root_cause": self.likely_root_cause,
            "recommended_next_action": self.recommended_next_action,
            "power_cycle_required": self.power_cycle_required
        }

def _get_time_threshold(since_minutes: int) -> float:
    return (datetime.now(timezone.utc) - timedelta(minutes=since_minutes)).timestamp()

from typing import Union

def _check_hardware_touched(probe_dir: Path, run_id: str) -> Union[bool, str]:
    """Checks if progress.jsonl for the run_id has executed hardware commands."""
    if not run_id:
        return False
        
    hardware_commands = {"PowerOn", "RfEnable", "RfInit", "ProfileConfig", "ChirpConfig", "FrameConfig", "StartFrame"}
    touched = False
    found_progress = False
    for progress_file in probe_dir.glob(f"{run_id}_*_progress.jsonl"):
        found_progress = True
        try:
            lines = progress_file.read_text(encoding="utf-8").strip().split("\n")
            for line in lines:
                if not line:
                    continue
                entry = json.loads(line)
                cmd = entry.get("cmd", "")
                if cmd in hardware_commands:
                    touched = True
                    break
        except Exception:
            pass
            
    if touched:
        return True
    elif found_progress:
        return False
    else:
        return "unknown"

def _evaluate_resume_safety(stage: str, result_success: bool, power_cycle_required: bool, is_dry_run: bool) -> str:
    if is_dry_run and stage == "dry_run_completed":
        return "false"
    if stage == "failed" or not result_success or power_cycle_required:
        return "false"
    if stage == "validation_recorded":
        return "not_needed"
    if stage in ["firmware_script_generated", "firmware_waiting", "config_script_generated", "config_waiting"]:
        return "maybe"
    return "unknown"

def _analyze_errors_for_root_cause(errors: List[str]) -> tuple[str, str]:
    cause = ""
    action = ""
    for err in errors:
        if "_atomic_write_manifest() got an unexpected keyword argument 'manifest_path'" in err:
            cause = "guided_runner called a private manifest helper with an incompatible signature."
            action = "Do not resume this workflow. Fix guided_runner to call the public firmware/config script generator and consume returned metadata instead of calling private helper internals. Then start a new guided workflow."
            break
            
    return cause, action

def _find_orphans(probe_dir: Path, since_ts: float) -> List[str]:
    orphans = []
    # Collect all run_ids referenced by any state file
    referenced_run_ids = set()
    for sf in probe_dir.glob("guided_*_state.json"):
        try:
            st = json.loads(sf.read_text(encoding="utf-8"))
            referenced_run_ids.add(st.get("firmware_run_id", ""))
            referenced_run_ids.add(st.get("config_run_id", ""))
            if "dry_run_preview" in st:
                referenced_run_ids.add(st["dry_run_preview"].get("firmware_run_id", ""))
                referenced_run_ids.add(st["dry_run_preview"].get("config_run_id", ""))
        except Exception:
            pass
            
    for mf in probe_dir.glob("*_manifest.json"):
        if mf.stat().st_mtime < since_ts:
            continue
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
            m_run_id = data.get("run_id", "")
            has_result = False
            has_prog = False
            for f in probe_dir.glob(f"{m_run_id}_*_result.json"):
                has_result = True
            for f in probe_dir.glob(f"{m_run_id}_*_progress.jsonl"):
                has_prog = True
                
            if not has_result and not has_prog and m_run_id not in referenced_run_ids:
                orphans.append(mf.name)
        except Exception:
            pass
    return orphans

def generate_failure_report(
    latest: bool = False,
    state_path: Optional[str] = None,
    run_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    probe_dir_override: Optional[str] = None,
    since_minutes: int = 30,
    probe_dir_str: Optional[str] = None
) -> FailureReport:
    """Analyze the probe dir and produce a FailureReport based on requested arguments."""
    override_dir = probe_dir_override or probe_dir_str
    if override_dir:
        probe_dir = Path(override_dir)
    else:
        probe_dir = _lua_launch_probe_dir()
        
    if not probe_dir.exists():
        return FailureReport(detected_failure_type="unknown", errors=["Probe directory not found."])
        
    since_ts = _get_time_threshold(since_minutes)
    
    orphans = _find_orphans(probe_dir, since_ts)
    
    # Target discovery
    target_state_file = None
    target_result_file = None
    target_audit_file = None
    
    if state_path:
        target_state_file = Path(state_path)
    elif workflow_id:
        target_state_file = probe_dir / f"guided_{workflow_id}_state.json"
    elif run_id:
        # Search for state file containing this run_id
        for sf in probe_dir.glob("guided_*_state.json"):
            try:
                st = json.loads(sf.read_text(encoding="utf-8"))
                if st.get("firmware_run_id") == run_id or st.get("config_run_id") == run_id:
                    target_state_file = sf
                    break
            except Exception:
                pass
        
        # Also look for a matching result file
        candidates = list(probe_dir.glob(f"{run_id}_*_result.json"))
        if candidates:
            target_result_file = max(candidates, key=lambda x: x.stat().st_mtime)
            
    elif latest:
        # Priority finding
        # 1. guided_*_state.json with current_stage == "failed"
        failed_states = []
        for sf in probe_dir.glob("guided_*_state.json"):
            if sf.stat().st_mtime >= since_ts:
                try:
                    st = json.loads(sf.read_text(encoding="utf-8"))
                    if st.get("current_stage") == "failed":
                        failed_states.append(sf)
                except Exception:
                    pass
        if failed_states:
            target_state_file = max(failed_states, key=lambda x: x.stat().st_mtime)
        else:
            # 2. *_result.json with success == false
            failed_results = []
            for rf in probe_dir.glob("*_result.json"):
                if rf.stat().st_mtime >= since_ts:
                    try:
                        res = json.loads(rf.read_text(encoding="utf-8"))
                        if res.get("success") is False:
                            failed_results.append(rf)
                    except Exception:
                        pass
            if failed_results:
                target_result_file = max(failed_results, key=lambda x: x.stat().st_mtime)
            else:
                # 3. session_audit.json with requires_power_cycle == true
                bad_audits = []
                for af in probe_dir.glob("*_session_audit.json"):
                    if af.stat().st_mtime >= since_ts:
                        try:
                            aud = json.loads(af.read_text(encoding="utf-8"))
                            if aud.get("requires_power_cycle") is True:
                                bad_audits.append(af)
                        except Exception:
                            pass
                if bad_audits:
                    target_audit_file = max(bad_audits, key=lambda x: x.stat().st_mtime)
    
    report = FailureReport()
    report.orphan_artifacts = orphans
    
    # Process target
    if target_state_file and target_state_file.exists():
        report.primary_artifact = str(target_state_file)
        try:
            state = GuidedWorkflowState.load(str(target_state_file))
            report.workflow_id = state.workflow_id
            report.label = state.label
            report.current_stage = state.current_stage
            report.run_id = state.config_run_id if state.config_run_id else state.firmware_run_id
            report.errors = state.errors
            
            # Semantic check for dry-run bugs
            has_fake_id = (state.firmware_run_id == "dryrunfw" or state.config_run_id == "dryruncfg")
            if state.current_stage == "validation_recorded" and (state.dry_run or has_fake_id):
                report.errors.append("Semantic BUG: validation_recorded reached during dry_run or fake run IDs present")
                report.detected_failure_type = "semantic_dry_run_bug"
            elif state.current_stage == "failed":
                report.detected_failure_type = "guided_workflow_failed"
                # Check for OptionInfo summary bug
                if any("OptionInfo" in err for err in state.errors):
                    report.detected_failure_type = "guided_summary_failed"
                    report.likely_root_cause = "CLI OptionInfo leak into internal implementation."
                    report.recommended_next_action = "run summarize-session/record-validation after fixing CLI OptionInfo leak; do not rerun firmware/config blindly."
                # Check for watch_run mismatch
                elif any("timed out" in err for err in state.errors):
                    # Check if actual result json says success
                    from .post_connect import load_run_result
                    if report.run_id:
                        res = load_run_result(report.run_id, probe_dir=probe_dir)
                        if res.exists and res.success:
                            report.detected_failure_type = "guided_watch_result_mismatch"
            else:
                report.detected_failure_type = "unknown"
                
            report.hardware_likely_touched = _check_hardware_touched(probe_dir, report.run_id)
            report.resume_safe = _evaluate_resume_safety(state.current_stage, True, False, state.dry_run)
            
            cause, action = _analyze_errors_for_root_cause(report.errors)
            if cause:
                report.likely_root_cause = cause
                report.recommended_next_action = action
                
            # Grab related artifacts
            if state.firmware_run_id:
                for f in probe_dir.glob(f"{state.firmware_run_id}*"):
                    report.related_artifacts.append(f.name)
            if state.config_run_id:
                for f in probe_dir.glob(f"{state.config_run_id}*"):
                    report.related_artifacts.append(f.name)
                    
        except Exception as e:
            report.errors.append(f"Could not load state file: {e}")
            
    elif target_result_file and target_result_file.exists():
        report.detected_failure_type = "run_failed"
        report.primary_artifact = str(target_result_file)
        try:
            res = json.loads(target_result_file.read_text(encoding="utf-8"))
            report.run_id = res.get("run_id", "")
            report.resume_safe = "false"
            report.hardware_likely_touched = _check_hardware_touched(probe_dir, report.run_id)
            if "errors" in res:
                report.errors = res["errors"]
        except Exception:
            pass
            
    elif target_audit_file and target_audit_file.exists():
        report.detected_failure_type = "dirty_session"
        report.primary_artifact = str(target_audit_file)
        report.power_cycle_required = True
        report.resume_safe = "false"
        
    elif orphans:
        report.detected_failure_type = "orphan_manifest"
        report.primary_artifact = orphans[0]
        report.hardware_likely_touched = "unknown"
        report.resume_safe = "unknown"
        
    else:
        # We found nothing specific
        if orphans:
            report.detected_failure_type = "orphan_manifest"
        else:
            report.detected_failure_type = "unknown"
    
    return report
