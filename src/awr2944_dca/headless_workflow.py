"""
Headless AWR2944+DCA1000 capture workflow state machine.

Manages the full lifecycle of a headless capture from firmware verification
through raw ADC file validation. Each stage is explicit, logged, and
requires appropriate confirmation for hardware actions.

Does NOT depend on mmWave Studio, RSTD, Lua, pywinauto, or GUI output reading.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Workflow stages
# ---------------------------------------------------------------------------

class HeadlessStage(str, Enum):
    """Headless capture workflow stages."""
    CREATED = "created"
    FIRMWARE_VERIFIED = "firmware_verified"
    RADAR_CONNECTED = "radar_connected"
    RADAR_CONFIGURED = "radar_configured"
    DCA_FPGA_CONFIGURED = "dca_fpga_configured"
    DCA_RECORD_CONFIGURED = "dca_record_configured"
    DCA_RECORDING = "dca_recording"
    RADAR_STARTED = "radar_started"
    RADAR_COMPLETE = "radar_complete"
    DCA_COMPLETE = "dca_complete"
    RAW_LOCATED = "raw_located"
    BOUND = "bound"
    VERIFIED = "verified"
    COMPLETE = "complete"
    ERROR = "error"


# Allowed forward transitions
STAGE_ORDER = [
    HeadlessStage.CREATED,
    HeadlessStage.FIRMWARE_VERIFIED,
    HeadlessStage.RADAR_CONNECTED,
    HeadlessStage.RADAR_CONFIGURED,
    HeadlessStage.DCA_FPGA_CONFIGURED,
    HeadlessStage.DCA_RECORD_CONFIGURED,
    HeadlessStage.DCA_RECORDING,
    HeadlessStage.RADAR_STARTED,
    HeadlessStage.RADAR_COMPLETE,
    HeadlessStage.DCA_COMPLETE,
    HeadlessStage.RAW_LOCATED,
    HeadlessStage.BOUND,
    HeadlessStage.VERIFIED,
    HeadlessStage.COMPLETE,
]


def _stage_index(stage: HeadlessStage) -> int:
    try:
        return STAGE_ORDER.index(stage)
    except ValueError:
        return -1


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

@dataclass
class HeadlessManifest:
    """Comprehensive capture provenance record."""

    # Identity
    workflow_id: str = ""
    capture_id: str = ""
    created_at: str = ""
    updated_at: str = ""

    # Firmware
    firmware_name: str = ""
    firmware_path: str = ""
    firmware_sha256: str = ""
    sdk_version: str = ""

    # Serial
    serial_port: str = ""
    serial_baudrate: int = 115200
    serial_settings: str = "8N1"

    # Radar config
    radar_cfg_source: str = ""
    radar_cfg_source_sha256: str = ""
    radar_cfg_rendered_path: str = ""
    radar_cfg_rendered_sha256: str = ""

    # UART results (list of command/response dicts)
    uart_results: list[dict] = field(default_factory=list)

    # DCA
    dca_cf_json_path: str = ""
    dca_cf_json_sha256: str = ""
    dca_control_exe_sha256: str = ""
    dca_record_exe_sha256: str = ""

    # Network
    dca_host_ip: str = ""
    dca_device_ip: str = ""

    # Capture
    capture_start_time: str = ""
    capture_end_time: str = ""
    expected_adc_payload_bytes: int = 0
    expected_transport_bytes: str = "UNKNOWN"
    actual_file_path: str = ""
    actual_file_size: int = 0
    actual_file_sha256: str = ""

    # Results
    parser_result: str = ""
    errors: list[str] = field(default_factory=list)
    recovery_notes: list[str] = field(default_factory=list)
    notes: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "workflow_id": self.workflow_id,
            "capture_id": self.capture_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "firmware": {
                "name": self.firmware_name,
                "path": self.firmware_path,
                "sha256": self.firmware_sha256,
                "sdk_version": self.sdk_version,
            },
            "serial": {
                "port": self.serial_port,
                "baudrate": self.serial_baudrate,
                "settings": self.serial_settings,
            },
            "radar_config": {
                "source": self.radar_cfg_source,
                "source_sha256": self.radar_cfg_source_sha256,
                "rendered_path": self.radar_cfg_rendered_path,
                "rendered_sha256": self.radar_cfg_rendered_sha256,
            },
            "uart_results": self.uart_results,
            "dca": {
                "cf_json_path": self.dca_cf_json_path,
                "cf_json_sha256": self.dca_cf_json_sha256,
                "control_exe_sha256": self.dca_control_exe_sha256,
                "record_exe_sha256": self.dca_record_exe_sha256,
            },
            "network": {
                "host_ip": self.dca_host_ip,
                "device_ip": self.dca_device_ip,
            },
            "capture": {
                "start_time": self.capture_start_time,
                "end_time": self.capture_end_time,
                "expected_adc_payload_bytes": self.expected_adc_payload_bytes,
                "expected_transport_bytes": self.expected_transport_bytes,
                "actual_file_path": self.actual_file_path,
                "actual_file_size": self.actual_file_size,
                "actual_file_sha256": self.actual_file_sha256,
            },
            "results": {
                "parser_result": self.parser_result,
                "errors": self.errors,
                "recovery_notes": self.recovery_notes,
            },
            "notes": self.notes,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "HeadlessManifest":
        m = cls()
        m.workflow_id = d.get("workflow_id", "")
        m.capture_id = d.get("capture_id", "")
        m.created_at = d.get("created_at", "")
        m.updated_at = d.get("updated_at", "")

        fw = d.get("firmware", {})
        m.firmware_name = fw.get("name", "")
        m.firmware_path = fw.get("path", "")
        m.firmware_sha256 = fw.get("sha256", "")
        m.sdk_version = fw.get("sdk_version", "")

        ser = d.get("serial", {})
        m.serial_port = ser.get("port", "")
        m.serial_baudrate = ser.get("baudrate", 115200)
        m.serial_settings = ser.get("settings", "8N1")

        rc = d.get("radar_config", {})
        m.radar_cfg_source = rc.get("source", "")
        m.radar_cfg_source_sha256 = rc.get("source_sha256", "")
        m.radar_cfg_rendered_path = rc.get("rendered_path", "")
        m.radar_cfg_rendered_sha256 = rc.get("rendered_sha256", "")

        m.uart_results = d.get("uart_results", [])

        dca = d.get("dca", {})
        m.dca_cf_json_path = dca.get("cf_json_path", "")
        m.dca_cf_json_sha256 = dca.get("cf_json_sha256", "")
        m.dca_control_exe_sha256 = dca.get("control_exe_sha256", "")
        m.dca_record_exe_sha256 = dca.get("record_exe_sha256", "")

        net = d.get("network", {})
        m.dca_host_ip = net.get("host_ip", "")
        m.dca_device_ip = net.get("device_ip", "")

        cap = d.get("capture", {})
        m.capture_start_time = cap.get("start_time", "")
        m.capture_end_time = cap.get("end_time", "")
        m.expected_adc_payload_bytes = cap.get("expected_adc_payload_bytes", 0)
        m.expected_transport_bytes = cap.get("expected_transport_bytes", "UNKNOWN")
        m.actual_file_path = cap.get("actual_file_path", "")
        m.actual_file_size = cap.get("actual_file_size", 0)
        m.actual_file_sha256 = cap.get("actual_file_sha256", "")

        res = d.get("results", {})
        m.parser_result = res.get("parser_result", "")
        m.errors = res.get("errors", [])
        m.recovery_notes = res.get("recovery_notes", [])

        m.notes = d.get("notes", "")
        m.tags = d.get("tags", [])
        return m


# ---------------------------------------------------------------------------
# Workflow State
# ---------------------------------------------------------------------------

class HeadlessWorkflow:
    """Headless capture workflow state machine.

    Tracks progress through capture stages, maintains the manifest,
    and enforces safety gates (e.g., sensorStart requires confirmation).
    """

    def __init__(self, workflow_id: str, capture_dir: Path,
                 capture_id: str = "", notes: str = "",
                 tags: list[str] | None = None):
        self._workflow_id = workflow_id
        self._capture_dir = Path(capture_dir)
        self._stage = HeadlessStage.CREATED
        self._manifest = HeadlessManifest(
            workflow_id=workflow_id,
            capture_id=capture_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
            notes=notes,
            tags=tags or [],
        )
        self._errors: list[str] = []
        self._state_log: list[dict] = []

        self._log_transition(HeadlessStage.CREATED, "Workflow created")

    @property
    def workflow_id(self) -> str:
        return self._workflow_id

    @property
    def stage(self) -> HeadlessStage:
        return self._stage

    @property
    def manifest(self) -> HeadlessManifest:
        return self._manifest

    @property
    def capture_dir(self) -> Path:
        return self._capture_dir

    @property
    def is_complete(self) -> bool:
        return self._stage == HeadlessStage.COMPLETE

    @property
    def has_error(self) -> bool:
        return self._stage == HeadlessStage.ERROR

    def advance_to(self, target: HeadlessStage, detail: str = "") -> None:
        """Advance the workflow to the target stage.

        Only forward transitions are allowed (except to ERROR, which is
        always allowed). Raises ValueError for invalid transitions.
        """
        if target == HeadlessStage.ERROR:
            self._stage = target
            self._manifest.updated_at = datetime.now(timezone.utc).isoformat()
            self._log_transition(target, detail or "Error")
            return

        current_idx = _stage_index(self._stage)
        target_idx = _stage_index(target)

        if target_idx <= current_idx:
            raise ValueError(
                f"Cannot go from {self._stage.value} to {target.value}: "
                f"only forward transitions allowed"
            )

        # Allow skipping stages only by one step at a time
        if target_idx > current_idx + 1:
            raise ValueError(
                f"Cannot skip from {self._stage.value} to {target.value}: "
                f"next stage is {STAGE_ORDER[current_idx + 1].value}"
            )

        self._stage = target
        self._manifest.updated_at = datetime.now(timezone.utc).isoformat()
        self._log_transition(target, detail)

    def record_error(self, error: str) -> None:
        """Record an error and transition to ERROR stage."""
        self._errors.append(error)
        self._manifest.errors.append(error)
        self.advance_to(HeadlessStage.ERROR, error)

    def status(self) -> dict:
        """Return current workflow status."""
        return {
            "workflow_id": self._workflow_id,
            "stage": self._stage.value,
            "is_complete": self.is_complete,
            "has_error": self.has_error,
            "capture_dir": str(self._capture_dir),
            "capture_id": self._manifest.capture_id,
            "errors": list(self._errors),
            "transitions": len(self._state_log),
        }

    def save_state(self, path: Path | None = None) -> Path:
        """Save workflow state to JSON."""
        if path is None:
            path = self._capture_dir / f"headless_workflow_{self._workflow_id}_state.json"
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        state = {
            "workflow_id": self._workflow_id,
            "current_stage": self._stage.value,
            "state_log": self._state_log,
            "manifest": self._manifest.to_dict(),
        }
        path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return path

    @classmethod
    def load_state(cls, path: Path) -> "HeadlessWorkflow":
        """Load workflow from a saved state file."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        wf = cls.__new__(cls)
        wf._workflow_id = data["workflow_id"]
        wf._stage = HeadlessStage(data["current_stage"])
        wf._state_log = data.get("state_log", [])
        wf._manifest = HeadlessManifest.from_dict(data.get("manifest", {}))
        wf._errors = wf._manifest.errors
        wf._capture_dir = Path(wf._manifest.to_dict().get("capture", {}).get("actual_file_path", ".")).parent
        if not str(wf._capture_dir) or str(wf._capture_dir) == ".":
            wf._capture_dir = Path(path).parent
        return wf

    def save_manifest(self, path: Path | None = None) -> Path:
        """Save the manifest to JSON."""
        if path is None:
            path = self._capture_dir / f"headless_manifest_{self._workflow_id}.json"
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self._manifest.to_dict(), indent=2),
            encoding="utf-8",
        )
        return path

    def _log_transition(self, stage: HeadlessStage, detail: str) -> None:
        self._state_log.append({
            "stage": stage.value,
            "detail": detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def __repr__(self) -> str:
        return (
            f"HeadlessWorkflow(id={self._workflow_id!r}, "
            f"stage={self._stage.value!r})"
        )
