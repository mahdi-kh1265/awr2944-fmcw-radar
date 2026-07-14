"""Jupyter-friendly lab API for AWR2944 + DCA1000 radar experiments.

Provides human-friendly wrappers around the validated backend modules:
``project.py``, ``dca/workflow.py``, ``eth.py``, ``mmws_auto.py``.

Supports both manual dofile paste and automated execution via
the mmWave Studio RSTD bridge. StartFrame requires explicit confirmation.

Usage::

    from awr2944_dca.lab import RadarProject

    lab = RadarProject.open("exp_lau_probe")
    lab.set_defaults(firmware_run_id="df1f275c", config_run_id="4b87faae")

    run = lab.capture_smoke("my_capture")
    print(run.dofile())       # paste into mmWave Studio
    run = run.resume()        # check result, advance
    cap = run.capture()       # get the bound RadarCapture
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any

from awr2944_dca.project import (
    PROJECT_DEFAULTS,
    add_capture_note,
    add_capture_tags,
    find_project_root,
    get_defaults,
    inspect_capture,
    load_project,
    new_capture,
    project_status,
    set_defaults as _set_defaults,
    verify_capture,
)
from awr2944_dca.dca.workflow import (
    CaptureWorkflowState,
    find_latest_state,
    load_state,
    resume_workflow,
    save_state,
    start_workflow,
)



# ---------------------------------------------------------------------------
# Radar Config
# ---------------------------------------------------------------------------

class ConfigStep:
    """Dofile step for radar configuration.

    Supports both manual paste (``dofile()``) and automated execution
    (``run()``). When created via ``RadarManager.apply_config()``, has
    a back-reference to the project for automation access.
    """

    def __init__(
        self,
        dofile_cmd: str,
        dofile_path: str,
        *,
        project: "RadarProject | None" = None,
        result_path: str | None = None,
        progress_path: str | None = None,
        run_id: str | None = None,
    ):
        self._dofile_cmd = dofile_cmd
        self._dofile_path = dofile_path
        self._project = project
        self._result_path = result_path
        self._progress_path = progress_path
        self._run_id = run_id
        self._last_result: dict | None = None

    def dofile(self) -> str:
        """Return the dofile command string for manual pasting."""
        return self._dofile_cmd

    def dofile_path(self) -> str:
        """Return the absolute path to the Lua script."""
        return self._dofile_path

    def next_action(self) -> str:
        """Return guidance on what to do next."""
        return "Paste the dofile into mmWave Studio Lua Shell."

    def next(self) -> str:
        """Alias for next_action()."""
        return self.next_action()

    def run(self, *, timeout_s: float = 60, verbose: bool = False) -> dict:
        """Execute the config dofile automatically via mmWave Studio.

        1. Executes the dofile through lab.mmws (RSTD bridge / pywinauto)
        2. Waits for the radar config result JSON
        3. Validates that every ar1 command succeeded
        4. On failure, attempts to save an output snapshot for debugging

        Returns:
            Dict with execution and validation results.

        Raises:
            RuntimeError: If no project reference or automation unavailable.
        """
        if self._project is None:
            raise RuntimeError(
                "ConfigStep has no project reference. "
                "Use lab.radar.apply_config(cfg) to get an automated ConfigStep."
            )

        from awr2944_dca.mmws_auto import safe_execute_dofile

        # Execute the dofile (radar config is always safe — no StartFrame)
        exec_result = safe_execute_dofile(
            Path(self._dofile_path),
            allow_startframe=False,
            timeout_s=timeout_s,
            verbose=verbose,
        )
        self._last_result = exec_result

        if not exec_result.get("executed") or exec_result.get("error"):
            return exec_result

        # Wait for result JSON if we have a result path
        if self._result_path:
            result_data = self.check(timeout_s=timeout_s)
            exec_result["config_result"] = result_data
            if result_data and not result_data.get("success"):
                exec_result["error"] = (
                    f"Radar config failed: {result_data.get('error', 'unknown')}"
                )
                # Try to save output snapshot for debugging
                try:
                    from awr2944_dca.mmws_auto import save_output_snapshot
                    probe = self._project._probe_dir()
                    save_output_snapshot(probe, label=f"config_fail_{self._run_id}")
                except Exception:
                    pass
            elif result_data is None:
                exec_result["error"] = (
                    "Radar config dofile submitted but result JSON not found. "
                    "RSTD return code alone is not proof of success."
                )

        return exec_result

    def check(self, timeout_s: float = 30) -> dict | None:
        """Read and return the radar config result JSON.

        Returns None if result not yet available.
        """
        if not self._result_path:
            return None
        from awr2944_dca.mmws.executor import wait_for_result_json
        return wait_for_result_json(Path(self._result_path), timeout=timeout_s)

    def status(self) -> str:
        """Return step status: 'pending', 'success', or 'error'."""
        if self._last_result is None:
            return "pending"
        if self._last_result.get("error"):
            return "error"
        config_result = self._last_result.get("config_result")
        if config_result and config_result.get("success"):
            return "success"
        if config_result and not config_result.get("success"):
            return "error"
        return "pending"

    def __repr__(self) -> str:
        return f"<ConfigStep {self._dofile_path} status={self.status()}>"


class RadarManager:
    """Radar configuration manager for a project."""
    def __init__(self, project: "RadarProject"):
        self.project = project

    def presets(self) -> list[str]:
        return ["smoke_v1"]

    def smoke_config(self) -> "RadarConfig":
        from awr2944_dca.radar_config import smoke_config_preset
        return smoke_config_preset()

    def new_config(self, name: str = "") -> "RadarConfig":
        from awr2944_dca.radar_config import RadarConfig
        return RadarConfig(name)

    def load_config(self, name_or_path: str) -> "RadarConfig":
        import json
        from pathlib import Path
        from awr2944_dca.radar_config import RadarConfig
        
        p = Path(name_or_path)
        if not p.is_absolute():
            p = self.project.root / "configs" / "radar" / p
            if not p.suffix:
                p = p.with_suffix(".json")
                
        if not p.exists():
            raise FileNotFoundError(f"Config not found: {p}")
            
        data = json.loads(p.read_text(encoding="utf-8"))
        return RadarConfig.from_dict(data)

    def save_config(self, cfg: "RadarConfig", name: str = "") -> Path:
        return cfg.save(name or cfg.name, project_root=self.project.root)

    def export_lua(self, cfg: "RadarConfig", name: str = "") -> Path:
        return cfg.export_lua(name or cfg.name, project_root=self.project.root)

    def apply_config(self, cfg: "RadarConfig") -> ConfigStep:
        """Export Lua with result tracking and return a ConfigStep.

        The exported Lua writes a result JSON capturing every ar1 command
        return value, so ConfigStep.run() can verify success beyond just
        the RSTD 30000 return code.
        """
        import uuid
        run_id = str(uuid.uuid4())[:8]
        name = cfg.name or "custom_config"

        out_dir = self.project.root / "configs" / "mmws" / "lua"
        out_dir.mkdir(parents=True, exist_ok=True)
        lua_path = out_dir / f"{name}.lua"
        result_path = out_dir / f"{name}_{run_id}_result.json"
        progress_path = out_dir / f"{name}_{run_id}_progress.jsonl"

        lua_content = cfg.to_lua_with_result(
            run_id=run_id,
            result_path=result_path.resolve().as_posix(),
            progress_path=progress_path.resolve().as_posix(),
        )
        lua_path.write_text(lua_content, encoding="utf-8")

        dofile = f'dofile([[{lua_path.resolve()}]])'
        return ConfigStep(
            dofile,
            str(lua_path.resolve()),
            project=self.project,
            result_path=str(result_path.resolve()),
            progress_path=str(progress_path.resolve()),
            run_id=run_id,
        )

    def configs(self) -> list[str]:
        out = self.project.root / "configs" / "radar"
        if not out.exists():
            return []
        return [f.stem for f in out.glob("*.json")]

    def compare(self, cfg_a: "RadarConfig", cfg_b: "RadarConfig") -> dict:
        """Compare two configs."""
        import copy
        da = cfg_a.to_dict()
        db = cfg_b.to_dict()
        return {"a": da, "b": db, "match": da == db}


# ---------------------------------------------------------------------------
# RadarProject
# ---------------------------------------------------------------------------

class RadarProject:
    """Jupyter-friendly wrapper for an AWR2944 radar project.

    Open a project with :meth:`open` or :meth:`open_here`, then use
    :meth:`capture_smoke` to start a manual-paste capture workflow.
    """

    def __init__(self, root: Path):
        self._root = Path(root).resolve()
        self._proj = load_project(self._root)
        self._mmws_manager: "MmWaveStudioManager | None" = None
        self._headless_api: "HeadlessApi | None" = None


    @classmethod
    def open(cls, root: str | Path) -> "RadarProject":
        """Open a project by path."""
        return cls(Path(root))

    @classmethod
    def open_here(cls) -> "RadarProject":
        """Find project.json by walking up from cwd."""
        root = find_project_root(Path.cwd())
        return cls(root)

    @property
    def root(self) -> Path:
        return self._root

    @property
    def name(self) -> str:
        return self._proj.get("name", "")

    @property
    def project_id(self) -> str:
        return self._proj.get("project_id", "")


    # -- Headless API -------------------------------------------------------

    @property
    def headless(self) -> "HeadlessApi":
        """Access the headless capture API (AWR2944 mmw demo + DCA CLI).

        Lazy-loaded to avoid import overhead when not needed.
        Independent of mmWave Studio, RSTD, Lua, pywinauto.
        """
        if self._headless_api is None:
            from awr2944_dca.headless import HeadlessApi
            self._headless_api = HeadlessApi(self._root)
        return self._headless_api

    @property
    def capture(self) -> "CaptureApi":
        """Production capture API (direct UDP + UART)."""
        if not hasattr(self, "_capture_api"):
            self._capture_api = CaptureApi(self)
        return self._capture_api


    # -- Status -------------------------------------------------------------

    def status(self) -> dict:
        """Return project status summary dict."""
        return project_status(self._root)


    # -- Defaults -----------------------------------------------------------

    def show_defaults(self) -> dict:
        """Return current project defaults, merged with fallbacks."""
        return get_defaults(self._root)

    def set_defaults(self, **kwargs: Any) -> dict:
        """Update project defaults. Returns updated defaults dict.

        Valid keys: firmware_run_id, config_run_id, expected_bytes,
        archive_existing, confirm_startframe, bind_force, ensure_eth.
        """
        return _set_defaults(self._root, **kwargs)

    # -- Captures -----------------------------------------------------------

    def captures(self) -> list["RadarCapture"]:
        """Return list of RadarCapture objects for all managed captures."""
        st = project_status(self._root)
        return [
            RadarCapture(self._root, c["capture_id"])
            for c in st.get("captures", [])
        ]

    def get_capture(self, query: str) -> "RadarCapture":
        """Fuzzy lookup: match by capture_id prefix, name substring, or date.

        - 0 matches → ValueError with helpful message
        - 1 match   → return RadarCapture
        - >1 matches → ValueError listing all matches
        """
        st = project_status(self._root)
        all_captures = st.get("captures", [])

        matches = []
        for c in all_captures:
            cid = c.get("capture_id", "")
            cname = c.get("capture_name", "")
            if (
                cid == query
                or cid.startswith(query)
                or query.lower() in cname.lower()
            ):
                matches.append(c)

        if len(matches) == 0:
            available = [c.get("capture_id", "") for c in all_captures]
            raise ValueError(
                f"No capture matching '{query}'. "
                f"Available: {available}"
            )
        if len(matches) > 1:
            listing = [
                f"  {c['capture_id']}  ({c.get('capture_name', '')})"
                for c in matches
            ]
            raise ValueError(
                f"Ambiguous: '{query}' matches {len(matches)} captures. "
                f"Use the full capture_id:\n" + "\n".join(listing)
            )

        return RadarCapture(self._root, matches[0]["capture_id"])

    def latest_capture(self) -> "RadarCapture":
        """Return the newest managed capture."""
        st = project_status(self._root)
        newest = st.get("newest_capture")
        if newest is None:
            raise ValueError("No captures in this project.")
        return RadarCapture(self._root, newest["capture_id"])

    # -- Workflows ----------------------------------------------------------

    def _probe_dir(self) -> Path:
        """Return the probe directory for this project."""
        rel = self._proj.get("probe_dir_rel", "ti/probe_logs")
        return self._root / rel

    def workflows(self) -> list[dict]:
        """List capture-smoke workflow state files."""
        probe = self._probe_dir()
        if not probe.exists():
            return []

        results = []
        for f in sorted(probe.glob("dca_capture_smoke_*_state.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                results.append({
                    "workflow_id": data.get("workflow_id", ""),
                    "current_stage": data.get("current_stage", ""),
                    "completed": data.get("completed", False),
                    "created_at": data.get("created_at", ""),
                    "updated_at": data.get("updated_at", ""),
                    "capture_id": data.get("capture_id", ""),
                    "state_file": str(f),
                })
            except (json.JSONDecodeError, IOError):
                pass
        return results

    def latest_workflow(self) -> "CaptureSmokeRun":
        """Reconnect to the latest capture-smoke workflow."""
        probe = self._probe_dir()
        state = find_latest_state(probe)
        if state is None:
            raise ValueError(
                f"No capture-smoke workflow state files in {probe}"
            )
        return CaptureSmokeRun(state, self)

    def get_workflow(self, workflow_id: str) -> "CaptureSmokeRun":
        """Reconnect to a specific workflow by ID."""
        probe = self._probe_dir()
        state = load_state(workflow_id, probe)
        return CaptureSmokeRun(state, self)

    # -- Capture smoke ------------------------------------------------------

    def capture_smoke(
        self,
        name: str,
        *,
        notes: str = "",
        tags: list[str] | None = None,
        radar_config=None,
        **overrides: Any,
    ) -> "CaptureSmokeRun":
        """Start a new capture-smoke workflow using project defaults.

        Args:
            name: Capture name (used for auto-created capture folder).
            notes: Optional notes to attach to the capture.
            tags: Optional tags to attach to the capture.
            **overrides: Override any project default (e.g. firmware_run_id).

        Returns:
            CaptureSmokeRun wrapping the new workflow.
        """
        defaults = get_defaults(self._root)
        merged = {**defaults, **overrides}

        # Ethernet check
        if merged.get("ensure_eth", True):
            from awr2944_dca import eth as eth_mod
            pairing = eth_mod.load_pairing(self._root)
            if pairing is None:
                raise ValueError(
                    "No Ethernet pairing configured. Run lab.eth.pair() first, "
                    "or pass ensure_eth=False to skip."
                )
            from awr2944_dca.project import get_dca_profile
            profile = get_dca_profile(self._root)
            status = eth_mod.check_adapter_status(pairing, host_ip=profile["host_ip"])
            if not status.get("ready"):
                raise ValueError(
                    f"DCA Ethernet not ready: {status}. "
                    "Run lab.eth.repair() or lab.eth.configure(dry_run=False)."
                )

        probe = self._probe_dir()
        proj = load_project(self._root)
        postproc = proj.get("postproc_dir_abs", "")

        state = start_workflow(
            probe_dir=probe,
            capture_dir=Path(postproc),
            firmware_run_id=merged.get("firmware_run_id", ""),
            config_run_id=merged.get("config_run_id", ""),
            confirm_startframe=merged.get("confirm_startframe", True),
            expected_bytes=merged.get("expected_bytes", 4_194_304),
            archive_existing=merged.get("archive_existing", True),
            project_root=self._root,
            capture_name=name,
            auto_create_capture=True,
            bind_force=merged.get("bind_force", False),
            radar_config=radar_config,
        )

        # Attach notes and tags to the capture if created
        if state.capture_id:
            if notes:
                try:
                    add_capture_note(self._root, state.capture_id, notes)
                except Exception:
                    pass
            if tags:
                try:
                    add_capture_tags(self._root, state.capture_id, *tags)
                except Exception:
                    pass

        return CaptureSmokeRun(state, self)


    # -- Radar Config -------------------------------------------------------

    @property
    def radar(self) -> "RadarManager":
        """Access the Radar Configuration manager."""
        return RadarManager(self)

    # -- mmWave Studio Automation -------------------------------------------

    @property
    def mmws(self) -> "MmWaveStudioManager":
        """Access the mmWave Studio automation manager.

        The instance is cached so attach() state persists across calls.
        """
        if self._mmws_manager is None:
            self._mmws_manager = MmWaveStudioManager(self)
        return self._mmws_manager

    # -- Ethernet -----------------------------------------------------------

    @property
    def eth(self) -> "EthernetManager":
        """Access the Ethernet pairing manager."""
        return EthernetManager(self)

    # -- Display ------------------------------------------------------------

    def __repr__(self) -> str:
        st = project_status(self._root)
        return (
            f"RadarProject('{self.name}', "
            f"id={self.project_id}, "
            f"captures={st['capture_count']}, "
            f"root={self._root})"
        )

    def _repr_html_(self) -> str:
        st = project_status(self._root)
        caps = st.get("captures", [])
        rows = ""
        for c in caps[-10:]:  # show last 10
            rows += (
                f"<tr><td><code>{c['capture_id']}</code></td>"
                f"<td>{c.get('capture_name', '')}</td>"
                f"<td>{c.get('status', '')}</td>"
                f"<td>{c.get('created_at', '')}</td></tr>\n"
            )

        cap_table = ""
        if rows:
            cap_table = (
                "<table><thead><tr>"
                "<th>Capture ID</th><th>Name</th><th>Status</th><th>Created</th>"
                "</tr></thead><tbody>\n" + rows + "</tbody></table>"
            )
        else:
            cap_table = "<p><em>No captures yet.</em></p>"

        return (
            f"<div style='font-family: monospace; padding: 8px; "
            f"border: 1px solid #444; border-radius: 4px; "
            f"background: #1a1a2e; color: #e0e0e0;'>"
            f"<h3 style='margin: 0 0 8px;'>🛰️ {self.name}</h3>"
            f"<p>Project ID: <code>{self.project_id}</code> · "
            f"Captures: {st['capture_count']} · "
            f"Root: <code>{self._root}</code></p>"
            f"{cap_table}"
            f"</div>"
        )


# ---------------------------------------------------------------------------
# CaptureSmokeRun
# ---------------------------------------------------------------------------

class CaptureSmokeRun:
    """Wraps CaptureWorkflowState for notebook use.

    Use :meth:`next` to see what to do, :meth:`dofile` to get the command
    to paste, and :meth:`resume` to advance after pasting.
    """

    def __init__(self, state: CaptureWorkflowState, project: RadarProject):
        self._state = state
        self._project = project

    @property
    def workflow_id(self) -> str:
        return self._state.workflow_id

    def refresh(self) -> "CaptureSmokeRun":
        """Reload state from disk."""
        probe = Path(self._state.probe_dir)
        self._state = load_state(self._state.workflow_id, probe)
        return self

    def status(self) -> dict:
        """Return workflow status as a dict."""
        return {
            "workflow_id": self._state.workflow_id,
            "current_stage": self._state.current_stage,
            "completed": self._state.completed,
            "capture_id": self._state.capture_id,
            "pending_operator_action": self._state.pending_operator_action,
            "pending_dofile": bool(self._state.pending_dofile),
            "errors": self._state.errors,
            "warnings": self._state.warnings,
        }

    def next_action(self) -> str:
        """Return the pending operator action string.

        Rewrites CLI-style guidance to notebook-native instructions.
        When automation is available, suggests run_next_step().
        """
        msg = self._state.pending_operator_action
        if msg:
            import re
            msg = re.sub(
                r"(?i)then run: awr dca capture-smoke resume --workflow-id [\w-]+",
                "After mmWave Studio finishes, run: run.run_next_step() (or run.resume() for manual)",
                msg
            )
        return msg

    def next(self) -> str:
        """Alias for next_action(). Returns what to do next."""
        return self.next_action()

    def dofile(self) -> str:
        """Return the dofile command string to paste into mmWave Studio."""
        return self._state.pending_dofile

    def dofile_path(self) -> Path | None:
        """Return path to the current .lua script file, or None."""
        stage = self._state.current_stage
        if "setup" in stage and self._state.dca_setup.script_path:
            return Path(self._state.dca_setup.script_path)
        if "capture" in stage and self._state.capture_trigger.script_path:
            return Path(self._state.capture_trigger.script_path)
        if "postproc" in stage and self._state.postproc.script_path:
            return Path(self._state.postproc.script_path)
        return None

    def copy_dofile(self) -> bool:
        """Copy dofile command to clipboard. Returns True on success."""
        cmd = self._state.pending_dofile
        if not cmd:
            return False
        try:
            import pyperclip
            pyperclip.copy(cmd)
            return True
        except (ImportError, Exception):
            return False

    def resume(self) -> "CaptureSmokeRun":
        """Check result files and advance the workflow. Returns self."""
        probe = Path(self._state.probe_dir)
        self._state = resume_workflow(self._state.workflow_id, probe)
        return self

    # -- Automated execution ------------------------------------------------

    def run_next_step(
        self,
        *,
        confirm_startframe: bool = False,
        timeout_s: float = 60,
        verbose: bool = False,
        mode: str | None = None,
    ) -> "CaptureSmokeRun":
        """Execute the pending dofile and advance the workflow.

        1. Gets the pending dofile path
        2. Classifies it for safety
        3. Refuses capture trigger unless confirm_startframe=True
        4. Executes via mmws_auto.safe_execute_dofile
        5. Calls resume() to advance the workflow state

        Args:
            confirm_startframe: Must be True to execute capture trigger
            timeout_s: Execution timeout
            verbose: Enable verbose executor logging

        Returns:
            self (for chaining)

        Raises:
            ValueError: If capture trigger and confirm_startframe=False
            RuntimeError: If no pending dofile or automation unavailable
        """
        dofile_path = self.dofile_path()
        if dofile_path is None:
            raise RuntimeError(
                f"No pending dofile for stage '{self._state.current_stage}'. "
                "The workflow may already be complete or in an error state."
            )

        from awr2944_dca.mmws_auto import safe_execute_dofile
        from awr2944_dca.mmws.executor import wait_for_result_json

        # Figure out which result file to wait for
        result_path = None
        stage = self._state.current_stage
        if stage == "dca_setup_script_generated":
            result_path = self._state.dca_setup.result_path
        elif stage == "capture_script_generated":
            result_path = self._state.capture_trigger.result_path
        elif stage == "postproc_script_generated":
            result_path = self._state.postproc.result_path

        # Execute/submit the script
        result = safe_execute_dofile(
            dofile_path,
            allow_startframe=confirm_startframe,
            timeout_s=timeout_s,
            verbose=verbose,
            mode=mode or "auto",
        )

        if not result.get("executed") or result.get("error"):
            raise RuntimeError(
                f"Dofile execution failed: {result.get('error', 'unknown')}"
            )

        # Wait for result if applicable (e.g. ui_lua_shell submits async)
        if result_path:
            wait_result = wait_for_result_json(Path(result_path), timeout=timeout_s)
            if not wait_result:
                # We do not raise here, because resume() will handle missing files
                # and put the workflow into an expected manual-intervention state
                pass

        # Advance the workflow
        return self.resume()

    def run_until_blocked(self) -> "CaptureSmokeRun":
        """Execute safe steps until a dangerous step (capture trigger) is reached.

        Stops before any step requiring confirm_startframe.
        """
        while not self._state.completed and not self._state.errors:
            dofile_path = self.dofile_path()
            if dofile_path is None:
                break

            from awr2944_dca.mmws_auto import classify_dofile, DofileSafety
            classification = classify_dofile(dofile_path)
            if classification.safety == DofileSafety.DANGEROUS:
                break  # Stop before dangerous step

            self.run_next_step()
        return self

    def run_all_manual_safe_steps(self) -> "CaptureSmokeRun":
        """Alias for run_until_blocked()."""
        return self.run_until_blocked()

    def run_capture_trigger(self, *, confirm_startframe: bool = True) -> "CaptureSmokeRun":
        """Execute the capture trigger step (StartFrame + StartRecord).

        This is the dangerous step that starts RF transmission.
        Requires confirm_startframe=True by default.
        """
        return self.run_next_step(confirm_startframe=confirm_startframe)

    def finish_postproc(self) -> "CaptureSmokeRun":
        """Execute the postproc step."""
        return self.run_next_step()

    def capture(self) -> "RadarCapture | None":
        """Return the bound RadarCapture if workflow completed with binding."""
        if not self._state.capture_id:
            return None
        if not self._state.bind_completed:
            return None
        return RadarCapture(self._project._root, self._state.capture_id)

    # -- Display ------------------------------------------------------------

    def __repr__(self) -> str:
        stage = self._state.current_stage
        wid = self._state.workflow_id
        completed = self._state.completed
        return (
            f"CaptureSmokeRun(workflow_id='{wid}', "
            f"stage='{stage}', completed={completed})"
        )

    def _repr_html_(self) -> str:
        s = self._state
        dofile_html = ""
        if s.pending_dofile:
            dofile_html = (
                f"<div style='background: #2d2d44; padding: 8px; "
                f"border-radius: 4px; margin: 4px 0;'>"
                f"<strong>Dofile:</strong><br>"
                f"<code style='color: #7fdbca;'>{s.pending_dofile}</code>"
                f"</div>"
            )

        action_html = ""
        if s.pending_operator_action:
            action_html = (
                f"<p style='color: #ffd700;'>⚡ {s.pending_operator_action}</p>"
            )

        status_color = "#7fdbca" if s.completed else "#ffa07a"

        return (
            f"<div style='font-family: monospace; padding: 8px; "
            f"border: 1px solid #444; border-radius: 4px; "
            f"background: #1a1a2e; color: #e0e0e0;'>"
            f"<h3 style='margin: 0 0 8px;'>🔬 Capture Smoke Run</h3>"
            f"<p>Workflow: <code>{s.workflow_id}</code> · "
            f"Stage: <span style='color: {status_color};'>{s.current_stage}</span></p>"
            f"{action_html}"
            f"{dofile_html}"
            f"</div>"
        )


# ---------------------------------------------------------------------------
# RadarCapture
# ---------------------------------------------------------------------------

class RadarCapture:
    """Wraps a single capture folder for notebook use.

    Provides verification, inspection, notes, and tag management.
    """

    def __init__(self, root: Path, capture_id: str):
        self._root = Path(root).resolve()
        self._capture_id = capture_id
        self._manifest: dict | None = None
        self._load_manifest()

    def _load_manifest(self) -> None:
        """Load manifest from disk."""
        path = self._root / "captures" / self._capture_id / "capture_manifest.json"
        if path.exists():
            self._manifest = json.loads(path.read_text(encoding="utf-8"))
        else:
            self._manifest = None

    @property
    def capture_id(self) -> str:
        return self._capture_id

    def refresh(self) -> "RadarCapture":
        """Reload manifest from disk."""
        self._load_manifest()
        return self

    def status(self) -> dict:
        """Return capture status as a dict."""
        if self._manifest is None:
            return {"capture_id": self._capture_id, "status": "not_found"}
        return {
            "capture_id": self._capture_id,
            "capture_name": self._manifest.get("capture_name", ""),
            "status": self._manifest.get("status", ""),
            "created_at": self._manifest.get("created_at", ""),
            "workflow_id": self._manifest.get("workflow_id"),
            "raw_file_rel": self._manifest.get("raw_file_rel"),
            "tags": self._manifest.get("tags", []),
        }

    def verify(self) -> dict:
        """Run capture verification. Returns result dict."""
        return verify_capture(self._root, self._capture_id)

    def open_viewer(self):
        """Open the standalone MATLAB viewer for this capture."""
        canonical_path = self._root / "captures" / self._capture_id / "adc_data_canonical.bin"
        if not canonical_path.exists():
            print(f"Canonical raw data missing: {canonical_path}")
            return
            
        from awr2944_dca.dsp.config import RadarProfile
        from awr2944_dca.viewer import export_viewer_payload_and_launch
        import awr2944_dca
        from pathlib import Path
        import dataclasses
        
        prof = None
        
        # Check for v2 profile serialization
        if self._manifest and self._manifest.get("profile"):
            from awr2944_dca.capture_manifest import profile_from_manifest_dict
            prof = profile_from_manifest_dict(self._manifest["profile"])
        # Fall back to parsing SDK CLI or legacy lua config
        elif self._manifest and self._manifest.get("sdk_cli_commands"):
            prof = self._reconstruct_profile_from_config_lines(self._manifest["sdk_cli_commands"])
        elif self._manifest and self._manifest.get("radar_config"):
            prof = self._reconstruct_profile_from_config_lines(self._manifest["radar_config"])
            
        if prof is None:
            print("Could not find or reconstruct radar profile from manifest.")
            return

        matlab_dir = Path(awr2944_dca.__file__).parent.parent.parent / "matlab"
        
        export_viewer_payload_and_launch(
            capture_path=canonical_path,
            profile=prof,
            mode="standalone",
            matlab_script_dir=matlab_dir / "viewer"
        )
        
    def _reconstruct_profile_from_config_lines(self, config_lines: list[str]):
        """Legacy helper to reconstruct RadarProfile from UART command lines."""
        from awr2944_dca.dsp.config import RadarProfile
        import dataclasses
        
        frame_count = None
        for line in config_lines:
            line = line.strip()
            if line.startswith("frameCfg"):
                parts = line.split()
                if len(parts) >= 5:
                    frame_count = int(parts[4])
            elif line.startswith("ar1.FrameConfig"):
                line = line.replace("(", " ").replace(")", " ").replace(",", " ")
                parts = line.split()
                if len(parts) >= 4:
                    frame_count = int(parts[3])

        if frame_count is None:
            return None
            
        prof = RadarProfile.from_smoke_v1()
        return dataclasses.replace(prof, frame_count=frame_count)


    def inspect_adc(self, refresh: bool = False) -> dict:
        """Run or reload ADC inspection. Returns inspection dict."""
        return inspect_capture(
            self._root, self._capture_id,
            refresh_adc_inspect=refresh,
        )

    def add_note(self, text: str) -> None:
        """Append a timestamped note to notes.md."""
        add_capture_note(self._root, self._capture_id, text)

    def notes(self) -> str:
        """Read notes.md content."""
        path = self._root / "captures" / self._capture_id / "notes.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def add_tags(self, *tags: str) -> list[str]:
        """Add tags to the capture manifest. Returns updated tag list."""
        result = add_capture_tags(self._root, self._capture_id, *tags)
        self._load_manifest()
        return result

    @property
    def raw_path(self) -> Path | None:
        """Path to raw/adc_data.bin, or None if not present."""
        p = self._root / "captures" / self._capture_id / "raw" / "adc_data.bin"
        return p if p.exists() else None

    @property
    def manifest(self) -> dict | None:
        """Return the capture manifest dict."""
        return self._manifest

    @property
    def adc_inspect(self) -> dict | None:
        """Return adc_inspect.json content, or None."""
        path = (
            self._root / "captures" / self._capture_id
            / "metadata" / "adc_inspect.json"
        )
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                return None
        return None

    # -- Display ------------------------------------------------------------

    def __repr__(self) -> str:
        status = self._manifest.get("status", "?") if self._manifest else "not_found"
        name = self._manifest.get("capture_name", "") if self._manifest else ""
        return (
            f"RadarCapture('{self._capture_id}', "
            f"name='{name}', status='{status}')"
        )

    def _repr_html_(self) -> str:
        if self._manifest is None:
            return f"<p>Capture <code>{self._capture_id}</code> not found.</p>"

        m = self._manifest
        status = m.get("status", "unknown")
        status_color = {
            "complete": "#7fdbca",
            "created": "#888",
            "imported": "#ffa07a",
            "inspected": "#ffd700",
            "bound": "#87ceeb",
            "error": "#ff6b6b",
            "verify_failed": "#ff6b6b",
            "bind_failed": "#ff6b6b",
        }.get(status, "#ccc")

        tags_html = ""
        tags = m.get("tags", [])
        if tags:
            tags_html = " · ".join(
                f"<span style='background: #2d2d44; padding: 2px 6px; "
                f"border-radius: 3px; font-size: 0.85em;'>{t}</span>"
                for t in tags
            )

        return (
            f"<div style='font-family: monospace; padding: 8px; "
            f"border: 1px solid #444; border-radius: 4px; "
            f"background: #1a1a2e; color: #e0e0e0;'>"
            f"<h3 style='margin: 0 0 8px;'>📡 {m.get('capture_name', self._capture_id)}</h3>"
            f"<p>ID: <code>{self._capture_id}</code> · "
            f"Status: <span style='color: {status_color};'>{status}</span> · "
            f"Created: {m.get('created_at', '')}</p>"
            f"{f'<p>Tags: {tags_html}</p>' if tags_html else ''}"
            f"</div>"
        )


# ---------------------------------------------------------------------------
# MmWaveStudioManager
# ---------------------------------------------------------------------------

class MmWaveStudioManager:
    """Notebook-facing mmWave Studio automation manager.

    Access via ``lab.mmws``.

    Wraps the executor transport backends with a safety layer and
    provides mmWave Studio Output panel reading for diagnostics.

    After ``attach()``, the selected mode is persisted and used for
    all subsequent ``smoke_test()``, ``execute_dofile()``, and
    ``execute_step()`` calls unless explicitly overridden.
    """

    def __init__(self, project: RadarProject):
        self._project = project
        self._last_result: dict | None = None
        self._selected_mode: str | None = None
        self._attached_mode: str | None = None
        self._last_execution_mode: str | None = None

    def status(self) -> dict:
        """Detect available automation transports and mmWave Studio state.

        Returns a dict with available modes, best mode, selected mode, and process info.
        """
        from awr2944_dca.mmws.executor import detect_available_modes, _is_mmws_running

        modes = detect_available_modes()
        best = None
        for m in modes:
            if m.available:
                best = m.mode.value
                break

        return {
            "mmws_running": _is_mmws_running(),
            "best_mode": best,
            "selected_mode": self._selected_mode,
            "attached_mode": self._attached_mode,
            "last_execution_mode": self._last_execution_mode,
            "modes": [
                {
                    "mode": m.mode.value,
                    "available": m.available,
                    "confidence": m.confidence,
                    "detail": m.detail,
                }
                for m in modes
            ],
        }

    def detect(self) -> list[dict]:
        """Return raw transport info list."""
        from awr2944_dca.mmws.executor import detect_available_modes

        return [
            {
                "mode": m.mode.value,
                "available": m.available,
                "confidence": m.confidence,
                "detail": m.detail,
            }
            for m in detect_available_modes()
        ]

    def attach(self) -> dict:
        """Verify connection to mmWave Studio and build bridge if needed.

        Persists the selected mode so all subsequent calls use it.
        Returns a dict with connection status and any build output.
        """
        from awr2944_dca.mmws.executor import (
            _find_csharp_bridge,
            _is_rstd_port_open,
            _is_mmws_running,
            build_csharp_bridge,
        )

        result: dict = {"attached": False, "mode": None, "detail": ""}

        if not _is_mmws_running():
            result["detail"] = "mmWave Studio not running. Start it first."
            return result

        # Try C# bridge first
        bridge = _find_csharp_bridge()
        if bridge is None:
            # Try to build it
            ok, msg = build_csharp_bridge()
            result["bridge_build"] = msg
            if not ok:
                result["detail"] = f"C# bridge build failed: {msg}"
            else:
                bridge = _find_csharp_bridge()

        if bridge and _is_rstd_port_open():
            result["attached"] = True
            result["mode"] = "csharp_rstd"
            result["detail"] = "Connected via C# RSTD bridge"
            self._attached_mode = "csharp_rstd"
            self._selected_mode = "csharp-rstd"  # executor uses hyphenated form
            return result

        if _is_rstd_port_open():
            result["attached"] = True
            result["mode"] = "rstd_net_remoting"
            result["detail"] = "RSTD port open (legacy pythonnet)"
            self._attached_mode = "rstd_net_remoting"
            self._selected_mode = "rstd"
            return result

        # Check pywinauto
        try:
            import pywinauto  # type: ignore[import-untyped]
            result["attached"] = True
            result["mode"] = "ui_lua_shell"
            result["detail"] = "Connected via pywinauto UI automation"
            self._attached_mode = "ui_lua_shell"
            self._selected_mode = "pywinauto"
            return result
        except ImportError:
            pass

        result["detail"] = "No automation transport available"
        return result

    def smoke_test(self, *, mode: str | None = None, timeout_s: float = 15.0) -> dict:
        """Run a connectivity smoke test against mmWave Studio.

        Uses a result-file-only Lua script — no WriteToLog required.
        WriteToLog is nil in many execution contexts and must not be depended on.
        Success is determined by the result file appearing, not by WriteToLog.

        Uses the attached/selected mode by default. Pass mode= to override.

        Args:
            mode: Override executor mode (e.g. "csharp-rstd", "lua-launch", "pywinauto")
            timeout_s: Timeout in seconds (default 15s)

        Returns:
            Dict with success, mode, return_code, error, elapsed_seconds, result_file_found
        """
        effective_mode = mode or self._selected_mode or "auto"

        import tempfile
        from awr2944_dca.mmws_auto import make_smoke_lua
        from awr2944_dca.mmws.executor import execute_script

        with tempfile.TemporaryDirectory() as tmpdir:
            result_path = Path(tmpdir) / "smoke_result.json"
            lua_src = make_smoke_lua(result_path)
            lua_path = Path(tmpdir) / "mmws_smoke_test.lua"
            lua_path.write_text(lua_src, encoding="utf-8")

            exec_result = execute_script(
                lua_path,
                mode=effective_mode,
                timeout=timeout_s,
                verbose=False,
            )

            from awr2944_dca.mmws.executor import wait_for_result_json
            result_data = wait_for_result_json(result_path, timeout=timeout_s)
            result_file_found = bool(result_data)

        self._last_execution_mode = exec_result.mode.value
        # Success requires: transport submitted AND result file was written
        success = exec_result.success and result_file_found
        return {
            "success": success,
            "mode": exec_result.mode.value,
            "selected_mode": effective_mode,
            "return_code": exec_result.return_code,
            "error": exec_result.error,
            "elapsed_seconds": exec_result.elapsed_seconds,
            "result_file_found": result_file_found,
        }

    def execute_dofile(
        self,
        path: str | Path,
        *,
        timeout_s: float = 60,
        allow_startframe: bool = False,
        verbose: bool = False,
        mode: str | None = None,
    ) -> dict:
        """Execute a Lua dofile with safety checks.

        Uses the attached/selected mode by default. Pass mode= to override.

        Args:
            path: Path to the .lua file
            timeout_s: Execution timeout
            allow_startframe: Must be True for dangerous scripts
            verbose: Enable verbose logging
            mode: Override executor mode

        Returns:
            Dict with classification, execution result, and status
        """
        effective_mode = mode or self._selected_mode or "auto"

        from awr2944_dca.mmws_auto import safe_execute_dofile

        result = safe_execute_dofile(
            Path(path),
            allow_startframe=allow_startframe,
            timeout_s=timeout_s,
            verbose=verbose,
            mode=effective_mode,
        )
        self._last_result = result

        # Track the mode that was actually used
        exec_result = result.get("exec_result")
        if exec_result:
            self._last_execution_mode = exec_result.get("mode")

        return result

    def execute_step(
        self,
        step: ConfigStep,
        *,
        timeout_s: float = 60,
        allow_startframe: bool = False,
        verbose: bool = False,
        mode: str | None = None,
    ) -> dict:
        """Execute a ConfigStep's dofile.

        Uses the attached/selected mode by default. Pass mode= to override.

        Args:
            step: The ConfigStep to execute
            timeout_s: Execution timeout
            allow_startframe: Must be True for dangerous scripts
            verbose: Enable verbose logging
            mode: Override executor mode
        """
        return self.execute_dofile(
            step.dofile_path(),
            timeout_s=timeout_s,
            allow_startframe=allow_startframe,
            verbose=verbose,
            mode=mode,
        )

    def last_result(self) -> dict | None:
        """Return the cached result from the last execution."""
        return self._last_result

    # -- Output reading -----------------------------------------------------

    def read_output(self, max_chars: int = 20000) -> dict:
        """Read the mmWave Studio Output/Console panel text.

        Returns a dict with 'text' (str or None), 'available' (bool),
        and diagnostic fields. Never silently returns None.
        """
        from awr2944_dca.mmws_auto import find_mmws_output
        result = find_mmws_output()
        text = result.text
        if text is not None and len(text) > max_chars:
            text = text[-max_chars:]
        return {
            "text": text,
            "available": result.available,
            "backend": result.backend,
            "strategy": result.strategy,
            "error": result.error,
            "control_info": result.control_info,
        }

    def tail_output(self, lines: int = 100) -> dict:
        """Return the last N lines of mmWave Studio output.

        Returns a dict with 'text' (str, possibly empty) and diagnostic fields.
        Never silently returns None.
        """
        output = self.read_output()
        raw_text = output.get("text")
        if raw_text is not None:
            all_lines = raw_text.splitlines()
            output["text"] = "\n".join(all_lines[-lines:])
        else:
            output["text"] = None
        return output

    def save_output_snapshot(self, label: str | None = None) -> dict:
        """Save current mmWave Studio output to probe_logs.

        Returns a dict with 'path' (str or None) and diagnostic info.
        """
        from awr2944_dca.mmws_auto import save_output_snapshot
        output_dir = self._project._probe_dir()
        path = save_output_snapshot(output_dir, label=label)
        return {
            "saved": path is not None,
            "path": str(path) if path else None,
        }

    def wait_for_output(self, pattern: str, timeout_s: float = 60) -> bool:
        """Wait for a regex pattern to appear in mmWave Studio output.

        Returns True if found within timeout.
        """
        from awr2944_dca.mmws_auto import wait_for_output
        return wait_for_output(pattern, timeout_s=timeout_s)

    def bridge_health_check(self, *, timeout_s: float = 15.0, verbose: bool = False) -> dict:
        """Run a real health check for the C# RSTD bridge.

        Sends a smoke Lua via csharp-rstd and verifies the result file appears.
        TCP:2777 open is not sufficient alone — this confirms end-to-end delivery.

        Returns:
            Dict with: healthy, mode, elapsed_seconds, error, result_file_found
        """
        from awr2944_dca.mmws_auto import bridge_health_check
        return bridge_health_check(timeout_s=timeout_s, verbose=verbose)

    def restart_bridge(self, *, verbose: bool = False) -> dict:
        """Kill stale MmwsRstdBridge.exe processes and check bridge readiness.

        Use when csharp_rstd hangs BEFORE_SENDCOMMAND.

        Returns:
            Dict with: killed_count, bridge_found, port_open, ready
        """
        from awr2944_dca.mmws_auto import restart_bridge
        result = restart_bridge(verbose=verbose)
        # Clear cached mode so next attach() re-selects
        if not result.get("ready"):
            self._selected_mode = None
            self._attached_mode = None
        return result

    def smoke_matrix(
        self,
        *,
        timeout_csharp: float = 15.0,
        timeout_cli: float = 25.0,
        verbose: bool = False,
    ) -> dict:
        """Test all available execution backends and report results.

        Tests: csharp_rstd, cli_lua_launch, ui_lua_shell, manual.

        cli_lua_launch is proven to work (writes result files via mmWaveStudio.exe /lua)
        but does not guarantee current GUI session state — safe for smoke only.

        Returns:
            Dict keyed by backend, each with health info.
            Includes 'recommended' key with the best working backend.
        """
        from awr2944_dca.mmws_auto import smoke_matrix
        return smoke_matrix(
            timeout_csharp=timeout_csharp,
            timeout_cli=timeout_cli,
            verbose=verbose,
        )

    def list_output_controls(self) -> list[dict]:
        """List all candidate output controls in mmWave Studio window.

        Returns a list of dicts with control info for debugging
        when read_output() cannot find the output panel.
        """
        from awr2944_dca.mmws_auto import list_output_controls
        return list_output_controls()

    def diagnostics(self) -> dict:
        """Return comprehensive diagnostic information.

        Includes transport status, mode tracking, last result,
        output reader status, and output tail.
        """
        diag: dict = {
            "status": self.status(),
            "selected_mode": self._selected_mode,
            "attached_mode": self._attached_mode,
            "last_execution_mode": self._last_execution_mode,
            "last_result": self._last_result,
        }

        # Check if selected differs from best
        st = diag["status"]
        best = st.get("best_mode")
        if self._selected_mode and best:
            # Normalize for comparison (csharp-rstd vs csharp_rstd)
            norm_sel = self._selected_mode.replace("-", "_")
            norm_best = best.replace("-", "_")
            diag["mode_mismatch"] = norm_sel != norm_best
        else:
            diag["mode_mismatch"] = False

        # Output reader diagnostics (diagnostic-only, not source of truth)
        from awr2944_dca.mmws_auto import find_mmws_output
        output_result = find_mmws_output()
        diag["output_reader"] = {
            "available": output_result.available,
            "backend": output_result.backend,
            "strategy": output_result.strategy,
            "error": output_result.error,
            "control_info": output_result.control_info,
            "advisory": (
                "Output panel reading is diagnostic-only. If unavailable, check: "
                "(1) match admin/non-admin privilege between mmWave Studio and Python; "
                "(2) 32-bit mmWaveStudio.exe may be inaccessible from 64-bit Python. "
                "Automation success depends on result JSON files, not output scraping."
            ),
        }

        # Output tail
        if output_result.text is not None:
            all_lines = output_result.text.splitlines()
            diag["output_tail"] = "\n".join(all_lines[-50:])
        else:
            diag["output_tail"] = f"(unavailable: {output_result.error})"

        return diag

    def __repr__(self) -> str:
        mode = self._selected_mode or "none"
        attached = self._attached_mode or "none"
        return f"<MmWaveStudioManager selected={mode} attached={attached}>"


# ---------------------------------------------------------------------------
# EthernetManager
# ---------------------------------------------------------------------------

class EthernetManager:
    """Notebook-facing Ethernet pairing manager.

    Access via ``lab.eth``.
    """

    def __init__(self, project: RadarProject):
        self._project = project
        self._root = project._root

    def snapshot(self) -> "Any":
        """Take a network adapter snapshot."""
        from awr2944_dca import eth as eth_mod
        return eth_mod.take_snapshot()

    def begin_pairing(self, snapshot_fn=None) -> "Any":
        """Step 1: Take a 'before' snapshot (before plugging in DCA).

        Returns a PairingSession to pass to finish_pairing().
        """
        from awr2944_dca import eth as eth_mod
        return eth_mod.begin_pairing(snapshot_fn=snapshot_fn)

    def finish_pairing(
        self,
        session,
        *,
        force: bool = False,
        apply: bool = False,
        snapshot_fn=None,
        apply_fn=None,
    ) -> dict:
        """Step 2: Take 'after' snapshot and detect DCA adapter.

        Args:
            session: PairingSession from begin_pairing().
            force: Allow gateway adapters.
            apply: If True, configure the adapter now (default: dry-run).
        """
        from awr2944_dca import eth as eth_mod
        from awr2944_dca.project import get_dca_profile
        profile = get_dca_profile(self._root)
        return eth_mod.finish_pairing(
            session,
            self._root,
            host_ip=profile["host_ip"],
            prefix_length=profile["prefix_length"],
            force=force,
            apply=apply,
            snapshot_fn=snapshot_fn,
            apply_fn=apply_fn,
        )

    def pair(self, *, force: bool = False, apply: bool = False) -> dict:
        """Convenience: interactive pairing (begin + prompt + finish)."""
        from awr2944_dca import eth as eth_mod
        session = self.begin_pairing()
        input(
            "🔌 Unplug all non-essential Ethernet cables, then plug in "
            "the DCA1000 Ethernet cable.\nPress Enter when ready..."
        )
        return self.finish_pairing(session, force=force, apply=apply)

    def status(self) -> dict:
        """Check current Ethernet pairing status."""
        from awr2944_dca import eth as eth_mod
        pairing = eth_mod.load_pairing(self._root)
        if pairing is None:
            return {"paired": False, "message": "No Ethernet pairing configured."}

        from awr2944_dca.project import get_dca_profile
        profile = get_dca_profile(self._root)
        adapter_status = eth_mod.check_adapter_status(
            pairing, host_ip=profile["host_ip"]
        )
        return {
            "paired": True,
            "interface_alias": pairing.interface_alias,
            "interface_index": pairing.interface_index,
            "host_adapter_mac": pairing.host_adapter_mac,
            "paired_at": pairing.paired_at,
            **adapter_status,
        }

    def ensure_ready(self) -> dict:
        """Validate saved pairing. Raises if not ready."""
        st = self.status()
        if not st.get("paired"):
            raise ValueError(
                "No Ethernet pairing configured. Run lab.eth.pair() first."
            )
        if not st.get("ready"):
            raise ValueError(
                f"DCA Ethernet not ready: adapter '{st.get('interface_alias')}' "
                f"status={st.get('status')}, has_correct_ip={st.get('has_correct_ip')}. "
                f"Run lab.eth.repair() to fix."
            )
        return st

    def configure(self, dry_run: bool = True) -> dict:
        """Apply saved pairing configuration.

        Args:
            dry_run: If True (default), return commands without executing.
        """
        from awr2944_dca import eth as eth_mod
        pairing = eth_mod.load_pairing(self._root)
        if pairing is None:
            raise ValueError("No Ethernet pairing configured.")

        adapter = eth_mod.AdapterInfo(
            interface_alias=pairing.interface_alias,
            interface_index=pairing.interface_index,
            status="Up",
            link_speed="",
            mac_address=pairing.host_adapter_mac,
        )

        from awr2944_dca.project import get_dca_profile
        profile = get_dca_profile(self._root)
        commands = eth_mod.build_configure_commands(
            adapter,
            host_ip=profile["host_ip"],
            prefix_length=profile["prefix_length"],
        )

        result = {"commands": commands, "applied": False}
        if not dry_run:
            apply_results = eth_mod.apply_configuration(commands)
            result["applied"] = True
            result["apply_results"] = apply_results

        return result

    def repair(self) -> dict:
        """Re-apply saved pairing config (dry_run=False)."""
        return self.configure(dry_run=False)

    def unpair(self) -> None:
        """Remove Ethernet pairing from this project."""
        from awr2944_dca import eth as eth_mod
        eth_mod.remove_pairing(self._root)

    def restore_last_snapshot(self) -> dict:
        """Restore pre-pairing IP config (not yet implemented)."""
        raise NotImplementedError(
            "restore_last_snapshot requires the pre-pairing snapshot "
            "to be replayed. This feature will be added in a future phase."
        )


# ---------------------------------------------------------------------------
# Capture API
# ---------------------------------------------------------------------------

class CaptureApi:
    """Production capture API delegating to capture_session."""

    def __init__(self, project: "RadarProject"):
        self._project = project
        self._root = project.root

    def _resolve_profile(self, profile: str):
        if profile != "smoke_v1":
            raise ValueError(f"Profile '{profile}' not found or unsupported.")
            
        from awr2944_dca.dsp.config import RadarProfile
        prof = RadarProfile.from_smoke_v1()
        return prof

    def _load_toolchain(self) -> "dict | None":
        """Load toolchain.local.json from the project's headless directory.
        
        This is a neutral JSON loader from headless.py — it does NOT import
        mmws, Lua, RSTD, or any GUI automation code.
        Returns None if toolchain.local.json does not exist.
        """
        from awr2944_dca.headless import load_toolchain
        # Try project-root-relative path first (root = exp_lau_probe/)
        # then fall back to repo-root-relative path (root = repo/)
        candidates = [
            self._root / "ti" / "headless" / "toolchain.local.json",
            self._root / "exp_lau_probe" / "ti" / "headless" / "toolchain.local.json",
        ]
        for tc_path in candidates:
            if tc_path.exists():
                try:
                    return load_toolchain(tc_path)
                except FileNotFoundError:
                    continue
        return None

    def _build_dca_cli(self, toolchain: dict):
        """Construct a DcaCli from the toolchain dict, resolving cf.json path."""
        from awr2944_dca.dca_cli import DcaCli
        from pathlib import Path
        # Resolve cf.json: prefer toolchain field, then project-relative, then system
        cf_json_path = Path(toolchain.get("dca_cli_cf_json", ""))
        if not cf_json_path.exists():
            cf_json_path = self._root / "tools" / "dca1000" / "cf.json"
        if not cf_json_path.exists():
            cf_json_path = Path(r"C:\ti\cf.json")
        return DcaCli.from_toolchain(toolchain, cf_json_path)

    def run(
        self,
        profile: str,
        frames: int,
        guard_frames: int = 1,
        com_port: str = "COM8",
        host_ip: str = "192.168.33.30",
        dca_ip: str = "192.168.33.180",
    ):
        """Execute a full production capture."""
        from awr2944_dca.capture_session import run_capture
        from awr2944_dca.project import new_capture
        from awr2944_dca.sdk_cli_profile import build_smoke_v1_cli
        import dataclasses
        
        prof = self._resolve_profile(profile)
        prof = dataclasses.replace(prof, frame_count=frames)
        
        sdk_cli_commands = build_smoke_v1_cli(frames, prof.chirps_per_frame)
        
        # Load DcaCli from toolchain.local.json
        toolchain = self._load_toolchain()
        dca_cli = None
        dca_configuration = {}
        if toolchain and toolchain.get("dca_cli_control_exe"):
            dca_cli = self._build_dca_cli(toolchain)
            dca_cli.dry_run = False
            
            try:
                dca_configuration = dca_cli.render_config()
            except Exception:
                pass
        
        # Generate capture directory
        manifest = new_capture(self._root, "dca_capture")
        output_dir = self._root / "captures" / manifest["capture_id"]
        
        return run_capture(
            output_dir=output_dir,
            sdk_cli_commands=sdk_cli_commands,
            profile=prof,
            guard_frames=guard_frames,
            com_port=com_port,
            host_ip=host_ip,
            dca_ip=dca_ip,
            dca_cli=dca_cli,
            dca_configuration=dca_configuration
        )

    def run_smoke(self, **kwargs):
        """Convenience wrapper for the smoke_v1 profile."""
        return self.run(profile="smoke_v1", **kwargs)

    def dry_run(
        self,
        profile: str,
        frames: int,
        guard_frames: int = 1,
        com_port: str = "COM8",
        host_ip: str = "192.168.33.30",
        dca_ip: str = "192.168.33.180",
    ) -> dict:
        """Calculate and report capture plan without touching hardware."""
        import dataclasses
        from pathlib import Path
        from awr2944_dca.sdk_cli_profile import build_smoke_v1_cli
        prof = self._resolve_profile(profile)
        prof = dataclasses.replace(prof, frame_count=frames)
        
        sdk_cli_commands = build_smoke_v1_cli(frames, prof.chirps_per_frame)
        
        total_frames = prof.frame_count
        canonical_frames = total_frames - guard_frames
        
        from awr2944_dca.awr2944_adc import expected_raw_dca_bytes, active_payload_bytes, AWR2944AdcLayout
        
        native_bytes_per_frame = expected_raw_dca_bytes(1, prof.chirps_per_frame, prof.rx_count, prof.adc_samples, AWR2944AdcLayout())
        logical_bytes_per_frame = active_payload_bytes(1, prof.chirps_per_frame, prof.rx_count, prof.adc_samples)
        
        native_bytes = native_bytes_per_frame * total_frames
        canonical_bytes = native_bytes_per_frame * canonical_frames
        
        cube_shape = [
            canonical_frames,
            prof.chirps_per_frame,
            prof.rx_count,
            prof.adc_samples
        ]
        
        # Resolve DCA tooling paths for validation
        toolchain = self._load_toolchain()
        dca_control_exe = "NOT_CONFIGURED"
        dca_config_source = "NOT_CONFIGURED"
        dca_config_runtime_path = "NOT_CONFIGURED"
        if toolchain:
            dca_control_exe = toolchain.get("dca_cli_control_exe", "NOT_CONFIGURED")
            dca_config_source = toolchain.get("dca_cli_cf_json", "NOT_CONFIGURED")
            # Resolve the actual cf.json that would be used at runtime
            cf_json_path = Path(toolchain.get("dca_cli_cf_json", ""))
            if not cf_json_path.exists():
                cf_json_path = self._root / "tools" / "dca1000" / "cf.json"
            if not cf_json_path.exists():
                cf_json_path = Path(r"C:\ti\cf.json")
            dca_config_runtime_path = str(cf_json_path)
        
        return {
            "project_root": str(self._root),
            "profile": profile,
            "total_frames": total_frames,
            "guard_frames": guard_frames,
            "canonical_frames": canonical_frames,
            "expected_native_dca_bytes": native_bytes,
            "expected_canonical_dca_bytes": canonical_bytes,
            "logical_depacked_bytes": logical_bytes_per_frame * total_frames,
            "canonical_logical_bytes": logical_bytes_per_frame * canonical_frames,
            "canonical_cube": cube_shape,
            "physical_lvds_lanes": AWR2944AdcLayout().physical_lvds_lanes,
            "dca_word_slots": AWR2944AdcLayout().dca_word_slots,
            "dca_storage_expansion_factor": AWR2944AdcLayout().dca_word_slots // AWR2944AdcLayout().physical_lvds_lanes,
            "uart_settings": {"com_port": com_port, "baud": 115200},
            "network_settings": {"host_ip": host_ip, "dca_ip": dca_ip},
            "dca_control_executable": dca_control_exe,
            "dca_config_source": dca_config_source,
            "dca_config_runtime_path": dca_config_runtime_path,
            "prospective_output_paths": {
                "native": "adc_data.bin",
                "canonical": "adc_data_canonical.bin",
                "manifest": "manifest.json"
            },
            "configuration_transport": "sdk_demo_uart_cli",
            "legacy_mmws_used": False,
            "dca_full_initialization": True,
            "sdk_cli_commands": sdk_cli_commands,
            "hardware_touched": False
        }
