import json
import os
import sys
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

from rich.console import Console

from ..cli import _lua_launch_probe_dir
from .post_connect import (
    connection_gate,
    dump_output_snapshot,
    audit_session,
    preflight_firmware,
    preflight_config,
    generate_firmware_power_script,
    generate_smoke_known_awr2944,
)
from .gui_connect import attach_mmwave_studio, manual_check

console = Console()

@dataclass
class GuidedWorkflowState:
    workflow_id: str
    label: str
    pid: Optional[int]
    state_path: str
    current_stage: str
    firmware_run_id: str = ""
    config_run_id: str = ""
    firmware_dofile: str = ""
    config_dofile: str = ""
    firmware_result_path: str = ""
    config_result_path: str = ""
    firmware_progress_path: str = ""
    config_progress_path: Optional[str] = None

    # Dry-run tracking
    dry_run: bool = False
    hardware_touched: bool = False
    lua_generated: bool = False
    validation_recorded: bool = False
    dry_run_preview: dict[str, str] = field(default_factory=dict)
    manual_connection_override: bool = False
    manual_connection_source: str = ""
    rs232_identity_gate_override: bool = False
    
    validation_file: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def save(self):
        self.updated_at = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = self.updated_at
            
        sp = Path(self.state_path)
        sp.parent.mkdir(parents=True, exist_ok=True)
        import uuid
        import time
        tmp_path = sp.with_suffix(f'.{uuid.uuid4().hex[:8]}.tmp')
        
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)
            
        for _ in range(5):
            try:
                os.replace(tmp_path, sp)
                break
            except PermissionError:
                time.sleep(0.1)
        else:
            os.replace(tmp_path, sp) # Let it crash if still failing
        
    @classmethod
    def load(cls, path: str) -> "GuidedWorkflowState":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)


def run_stage(state: GuidedWorkflowState, stage_name: str, fn, *args, **kwargs):
    """Run a stage, and if it fails, mark state as failed and exit."""
    try:
        res = fn(*args, **kwargs)
        state.current_stage = stage_name
        state.save()
        return res
    except Exception as e:
        state.current_stage = "failed"
        state.errors.append(f"{stage_name} failed: {e}")
        state.save()
        console.print(f"[red]Workflow failed at {stage_name}: {e}[/red]")
        sys.exit(1)


def watch_run_sync(run_id: str, timeout: int, probe_dir: Optional[Path] = None):
    """Wrapper around mmws_post_watch_run that catches SystemExit/typer.Exit."""
    from ..cli import mmws_post_watch_run
    import typer
    
    try:
        mmws_post_watch_run(run_id=run_id, timeout=timeout, probe_dir=probe_dir)
        return True
    except (SystemExit, typer.Exit) as e:
        code = getattr(e, 'code', getattr(e, 'exit_code', 1))
        if code == 0:
            return True
        return False


def summarize_session_sync(firmware_run_id: str, config_run_id: str, probe_dir: str) -> bool:
    """Wrapper around summarize_session logic."""
    from ..cli import summarize_session_impl
    import typer
    try:
        summarize_session_impl(firmware_run_id=firmware_run_id, config_run_id=config_run_id, probe_dir=probe_dir)
        return True
    except (SystemExit, typer.Exit) as e:
        code = getattr(e, 'code', getattr(e, 'exit_code', 1))
        return code == 0


def record_validation_sync(firmware_run_id: str, config_run_id: str, label: str, probe_dir: str):
    from ..cli import record_validation_impl
    import typer
    try:
        record_validation_impl(firmware_run_id=firmware_run_id, config_run_id=config_run_id, label=label, probe_dir=probe_dir)
        return True
    except (SystemExit, typer.Exit) as e:
        code = getattr(e, 'code', getattr(e, 'exit_code', 1))
        return code == 0


def step_manual_check(state: GuidedWorkflowState, pid: Optional[int], dry_run: bool,
                      assume_manual_connected: bool = False):
    if dry_run:
        console.print("[yellow]DRY-RUN: Skipping manual-check...[/yellow]")
        return

    if assume_manual_connected:
        console.print("[bold yellow]MANUAL OVERRIDE: assuming mmWave Studio is connected "
                      "to AWR2944/GP/SOP:2 based on user confirmation.[/bold yellow]")
        state.manual_connection_override = True
        state.manual_connection_source = "user_confirmed"
        return

    console.print("[cyan]Running manual-check...[/cyan]")
    probe_dir = _lua_launch_probe_dir()
    vlog = lambda m: None
    try:
        app, window = attach_mmwave_studio(pid=pid, probe_dir=probe_dir, verbose_log=vlog)
    except RuntimeError as e:
        raise RuntimeError(f"Could not attach to mmWave Studio: {e}")

    res = manual_check(window, probe_dir=probe_dir, verbose_log=vlog)
    if res.status != "MANUAL_CONNECTION_VALID":
        raise RuntimeError(f"Manual check failed:\n{res.error}")

def step_session_audit(state: GuidedWorkflowState, pid: Optional[int], dry_run: bool,
                       assume_manual_connected: bool = False):
    if dry_run:
        console.print("[yellow]DRY-RUN: Skipping session-audit...[/yellow]")
        return

    console.print("[cyan]Running session-audit...[/cyan]")
    probe_dir = _lua_launch_probe_dir()
    vlog = lambda m: None
    app, window = attach_mmwave_studio(pid=pid, probe_dir=probe_dir, verbose_log=vlog)

    if assume_manual_connected:
        # Skip connection_gate GUI scrape — user confirmed connection
        console.print("[yellow]MANUAL OVERRIDE: bypassing RS232 identity gate "
                      "(user confirmed Device Status).[/yellow]")
        rs232_valid = True
        state.rs232_identity_gate_override = True
    else:
        device_status = connection_gate(window, vlog)
        rs232_valid = device_status.get("gate_passed", False)

    snap_path = probe_dir / f"{state.workflow_id}_session_audit_snapshot.txt"
    dump_output_snapshot(window, vlog, snap_path)

    doc_text = snap_path.read_text(encoding="utf-8") if snap_path.exists() else ""
    audit = audit_session(doc_text, rs232_valid=rs232_valid)
    if audit.requires_power_cycle:
        raise RuntimeError("Session audit: requires_power_cycle is true. Session dirty.")
    return audit

def step_preflight_firmware(state: GuidedWorkflowState, audit, dry_run: bool,
                            assume_manual_connected: bool = False):
    if dry_run:
        console.print("[yellow]DRY-RUN: Skipping preflight-firmware...[/yellow]")
        return

    console.print("[cyan]Running preflight-firmware...[/cyan]")
    passed, reasons = preflight_firmware(audit)
    if not passed:
        if assume_manual_connected:
            # Filter out only the RS232 identity gate reason
            remaining = [r for r in reasons if not r.startswith("RS232 identity gate not valid")]
            if not remaining:
                console.print("[yellow]MANUAL OVERRIDE: RS232 identity gate overridden "
                              "(user confirmed Device Status).[/yellow]")
                state.rs232_identity_gate_override = True
                return
            else:
                raise RuntimeError(f"Firmware preflight failed (even with override): {remaining}")
        raise RuntimeError(f"Firmware preflight failed: {reasons}")

def step_generate_firmware(state: GuidedWorkflowState, dry_run: bool):
    if dry_run:
        console.print("[yellow]DRY-RUN: Would generate firmware script[/yellow]")
        state.dry_run_preview["firmware_run_id"] = "dryrunfw"
        return
        
    console.print("[cyan]Generating firmware-power-script...[/cyan]")
    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    lua_path = probe_dir / f"{run_id}_firmware_power.lua"
    
    generated = generate_firmware_power_script(run_id, lua_path)
    lua_path.write_text(generated.script, encoding="utf-8")
    state.lua_generated = True
    
    state.firmware_run_id = generated.run_id
    state.firmware_result_path = str(generated.result_path)
    state.firmware_progress_path = str(generated.progress_path)
    state.firmware_dofile = generated.dofile

def step_watch_firmware(state: GuidedWorkflowState, dry_run: bool, timeout: int, probe_dir: Path):
    if dry_run:
        console.print("[yellow]DRY-RUN: Would wait for firmware script to finish[/yellow]")
        return
        
    console.print(f"\n[bold]Paste this into mmWave Studio Lua Shell:[/bold]")
    console.print(f"[green]{state.firmware_dofile}[/green]\n")
    
    ok = watch_run_sync(state.firmware_run_id, timeout, probe_dir=probe_dir)
    if not ok:
        from .post_connect import load_run_result
        res = load_run_result(state.firmware_run_id, probe_dir=probe_dir)
        if res.exists and res.success:
            console.print("[green]Reconciled missed update: Firmware run completed successfully.[/green]")
        else:
            raise RuntimeError("Firmware run failed or timed out.")

def step_preflight_config(state: GuidedWorkflowState, pid: Optional[int], dry_run: bool):
    if dry_run:
        console.print("[yellow]DRY-RUN: Skipping preflight-config...[/yellow]")
        return
        
    console.print("[cyan]Running preflight-config...[/cyan]")
    probe_dir = _lua_launch_probe_dir()
    vlog = lambda m: None
    app, window = attach_mmwave_studio(pid=pid, probe_dir=probe_dir, verbose_log=vlog)
    device_status = connection_gate(window, vlog)
    rs232_valid = device_status.get("gate_passed", False)
    
    snap_path = probe_dir / f"{state.workflow_id}_preflight_cfg_snapshot.txt"
    dump_output_snapshot(window, vlog, snap_path)
    
    doc_text = snap_path.read_text(encoding="utf-8") if snap_path.exists() else ""
    audit = audit_session(doc_text, rs232_valid=rs232_valid)
    
    passed, reasons = preflight_config(audit)
    if not passed:
        raise RuntimeError(f"Config preflight failed: {reasons}")

def step_generate_config(state: GuidedWorkflowState, dry_run: bool):
    if dry_run:
        console.print("[yellow]DRY-RUN: Would generate config script[/yellow]")
        state.dry_run_preview["config_run_id"] = "dryruncfg"
        return
        
    console.print("[cyan]Generating smoke-from-known-awr2944...[/cyan]")
    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    lua_path = probe_dir / f"{run_id}_smoke_config.lua"
    
    generated = generate_smoke_known_awr2944(run_id, lua_path)
    lua_path.write_text(generated.script, encoding="utf-8")
    state.lua_generated = True
    
    state.config_run_id = generated.run_id
    state.config_result_path = str(generated.result_path)
    state.config_progress_path = str(generated.progress_path)
    state.config_dofile = generated.dofile

def step_watch_config(state: GuidedWorkflowState, dry_run: bool, timeout: int, probe_dir: Path):
    if dry_run:
        console.print("[yellow]DRY-RUN: Would wait for config script to finish[/yellow]")
        return
        
    console.print(f"\n[bold]Paste this into mmWave Studio Lua Shell:[/bold]")
    console.print(f"[green]{state.config_dofile}[/green]\n")
    
    ok = watch_run_sync(state.config_run_id, timeout, probe_dir=probe_dir)
    if not ok:
        from .post_connect import load_run_result
        res = load_run_result(state.config_run_id, probe_dir=probe_dir)
        if res.exists and res.success:
            console.print("[green]Reconciled missed update: Config run completed successfully.[/green]")
        else:
            raise RuntimeError("Config run failed or timed out.")

def step_summarize(state: GuidedWorkflowState, dry_run: bool):
    if dry_run:
        console.print("[yellow]DRY-RUN: Would summarize session[/yellow]")
        return
        
    console.print("[cyan]Running summarize-session...[/cyan]")
    probe_dir = str(Path(state.state_path).parent) if state.state_path else None
    ok = summarize_session_sync(state.firmware_run_id, state.config_run_id, probe_dir)
    if not ok:
        raise RuntimeError("summarize-session returned post_connection_config_validated=False")

def step_record(state: GuidedWorkflowState, dry_run: bool):
    if dry_run:
        console.print("[yellow]DRY-RUN: Would record validation[/yellow]")
        return
        
    console.print("[cyan]Running record-validation...[/cyan]")
    probe_dir = str(Path(state.state_path).parent) if state.state_path else None
    ok = record_validation_sync(state.firmware_run_id, state.config_run_id, state.label, probe_dir)
    if not ok:
        raise RuntimeError("record-validation failed.")
    
    state.validation_file = "recorded"


def run_guided_workflow(
    label: str,
    pid: Optional[int],
    dry_run: bool,
    timeout_firmware: int,
    timeout_config: int,
    probe_dir: Optional[str] = None,
    assume_manual_connected: bool = False,
):
    """Main conductor logic for guided-validate."""
    workflow_id = str(uuid.uuid4())[:8]
    probe_dir_path = _lua_launch_probe_dir(probe_dir)
    state_path = str(probe_dir_path / f"guided_{workflow_id}_state.json")
    
    state = GuidedWorkflowState(
        workflow_id=workflow_id,
        label=label,
        pid=pid,
        state_path=state_path,
        current_stage="created",
        dry_run=dry_run,
        manual_connection_override=assume_manual_connected,
    )
    state.save()
    
    if dry_run:
        console.print("[yellow]Starting Guided Validation in DRY-RUN mode[/yellow]")
    else:
        console.print("[green]Starting Guided Validation workflow[/green]")
    
    # 1. manual-check
    run_stage(state, "manual_check_passed", step_manual_check, state, pid, dry_run, assume_manual_connected)
    
    # 2. session-audit
    audit = run_stage(state, "session_audit_passed", step_session_audit, state, pid, dry_run, assume_manual_connected)
    
    # 3. preflight-firmware
    run_stage(state, "firmware_preflight_passed", step_preflight_firmware, state, audit, dry_run, assume_manual_connected)
    
    # 4. generate firmware
    run_stage(state, "firmware_script_generated", step_generate_firmware, state, dry_run)
    
    # 5/6/7. wait/watch firmware
    run_stage(state, "firmware_validated", step_watch_firmware, state, dry_run, timeout_firmware, probe_dir_path)
    
    # 9. preflight config
    run_stage(state, "config_preflight_passed", step_preflight_config, state, pid, dry_run)
    
    # 10. generate config
    run_stage(state, "config_script_generated", step_generate_config, state, dry_run)
    
    # 11/12/13. wait/watch config
    run_stage(state, "config_validated", step_watch_config, state, dry_run, timeout_config, probe_dir_path)
    
    # 14. summarize session
    run_stage(state, "session_summarized", step_summarize, state, dry_run)
    
    if dry_run:
        def step_dry_run_finish(state: GuidedWorkflowState):
            pass
        run_stage(state, "dry_run_completed", step_dry_run_finish, state)
        console.print("[yellow]DRY-RUN completed. No hardware was touched. No validation was recorded.[/yellow]")
    else:
        # 15. record validation
        run_stage(state, "validation_recorded", step_record, state, dry_run)
        console.print(f"\n[bold green]Workflow {workflow_id} fully validated and recorded![/bold green]")


def resume_guided_workflow(
    state_path: str,
    timeout_firmware: int = 180,
    timeout_config: int = 120,
):
    state = GuidedWorkflowState.load(state_path)
    
    if state.current_stage == "failed":
        console.print("[red]Cannot resume a failed workflow automatically.[/red]")
        console.print(f"Errors: {state.errors}")
        sys.exit(1)
        
    console.print(f"[cyan]Resuming workflow from stage: {state.current_stage}[/cyan]")
    
    stage = state.current_stage
    
    if stage in ["created", "manual_check_passed", "session_audit_passed", "firmware_preflight_passed"]:
        # Safety constraint: resuming early stages implies needing live connection
        console.print("[red]Cannot reliably resume early stages without running preflight again.[/red]")
        sys.exit(1)
        
    probe_dir_path = Path(state_path).parent
    
    if stage in ["firmware_script_generated", "firmware_waiting"]:
        run_stage(state, "firmware_validated", step_watch_firmware, state, False, timeout_firmware, probe_dir_path)
        stage = "firmware_validated"
        
    if stage == "firmware_validated":
        run_stage(state, "config_preflight_passed", step_preflight_config, state, state.pid, False)
        stage = "config_preflight_passed"
        
    if stage == "config_preflight_passed":
        run_stage(state, "config_script_generated", step_generate_config, state, False)
        stage = "config_script_generated"
        
    if stage in ["config_script_generated", "config_waiting"]:
        run_stage(state, "config_validated", step_watch_config, state, state.dry_run, timeout_config, probe_dir_path)
        stage = "config_validated"
        
    if stage == "config_validated":
        run_stage(state, "session_summarized", step_summarize, state, state.dry_run)
        stage = "session_summarized"
        
    if stage == "session_summarized":
        if state.dry_run:
            def step_dry_run_finish(s: GuidedWorkflowState):
                pass
            run_stage(state, "dry_run_completed", step_dry_run_finish, state)
            stage = "dry_run_completed"
        else:
            run_stage(state, "validation_recorded", step_record, state, False)
            stage = "validation_recorded"
        
    if stage == "validation_recorded":
        console.print(f"\n[bold green]Workflow {state.workflow_id} is already complete![/bold green]")
        
    if stage == "dry_run_completed":
        console.print("[yellow]DRY-RUN completed. No hardware was touched. No validation was recorded.[/yellow]")
