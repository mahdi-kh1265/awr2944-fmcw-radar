"""
Headless AWR2944+DCA1000 Capture — Compatibility Shim.

Re-exports from the separated implementation modules:
- headless_serial: Serial port discovery and UART communication
- mmw_demo_config: .cfg file parser/model
- dca_cli: DCA1000 CLI subprocess wrapper
- headless_workflow: Capture workflow state machine

This file is kept for backward compatibility. New code should import
from the specific modules directly.

Does NOT depend on mmWave Studio, RSTD, Lua, pywinauto, or GUI output reading.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

# Re-export from separated modules
from awr2944_dca.headless_serial import (
    AwrUartConnection,
    CommandResult,
    SerialPortInfo,
    TranscriptEntry,
    discover_serial_ports,
    identify_application_user_port,
    identify_xds110_ports,
)
from awr2944_dca.mmw_demo_config import (
    MmwDemoConfig,
    KNOWN_COMMANDS,
    ValidationIssue,
)
from awr2944_dca.dca_cli import (
    DcaCli,
    DcaCmdResult,
    DcaConfigIssue,
)
from awr2944_dca.headless_workflow import (
    HeadlessStage,
    HeadlessManifest,
    HeadlessWorkflow,
)


# ---------------------------------------------------------------------------
# Toolchain loader (kept here for compatibility)
# ---------------------------------------------------------------------------

def _find_headless_dir() -> Path:
    """Locate the headless config directory relative to the project."""
    # Walk up from this file to find exp_lau_probe/ti/headless
    src_dir = Path(__file__).resolve().parent
    project_root = src_dir.parent  # src/ -> project root
    headless_dir = project_root / "exp_lau_probe" / "ti" / "headless"
    if headless_dir.exists():
        return headless_dir
    return project_root / "headless"


_HEADLESS_DIR = _find_headless_dir()
_TOOLCHAIN_LOCAL = _HEADLESS_DIR / "toolchain.local.json"
_FLASH_PLAN_LOCAL = _HEADLESS_DIR / "flash_plan.local.json"


def load_toolchain(path: Optional[Path] = None) -> dict:
    """Load the local toolchain configuration.

    Returns a dict with all TI installation paths and port assignments.
    Raises FileNotFoundError if toolchain.local.json doesn't exist.
    """
    p = path or _TOOLCHAIN_LOCAL
    if not p.exists():
        raise FileNotFoundError(
            f"Toolchain config not found: {p}\n"
            f"Copy toolchain.example.json → toolchain.local.json and fill in paths."
        )
    with open(p) as f:
        return json.load(f)


def validate_toolchain(tc: dict) -> dict:
    """Validate that critical paths exist. Returns a status dict."""
    checks = {}
    critical = [
        "mmw_demo_appimage",
        "dca_cli_control_exe",
        "dca_cli_record_exe",
        "uart_uniflash_py",
        "sbl_uart_uniflash_tiimage",
        "sbl_qspi_tiimage",
        "sample_lvds_cfg",
    ]
    for key in critical:
        val = tc.get(key)
        if val is None:
            checks[key] = {"status": "MISSING", "detail": "null in config"}
        elif not Path(val).exists():
            checks[key] = {"status": "NOT_FOUND", "detail": str(val)}
        else:
            checks[key] = {"status": "OK", "path": str(val), "size": Path(val).stat().st_size}
    return checks


def load_flash_plan(path: Optional[Path] = None) -> dict:
    """Load the flash plan JSON."""
    p = path or _FLASH_PLAN_LOCAL
    if not p.exists():
        raise FileNotFoundError(f"Flash plan not found: {p}")
    with open(p) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Headless API facade (used by lab.headless)
# ---------------------------------------------------------------------------

class HeadlessApi:
    """Facade for headless capture operations, exposed as lab.headless.

    Provides read-only discovery, configuration inspection, and capture
    workflow management. Hardware-affecting operations require explicit
    confirmation parameters.

    Does NOT depend on mmWave Studio, RSTD, Lua, pywinauto, or GUI output reading.
    """

    def __init__(self, project_root: Path):
        self._root = Path(project_root).resolve()
        self._headless_dir = self._root / "exp_lau_probe" / "ti" / "headless"
        self._tc: dict | None = None
        self._radar: _HeadlessRadarApi | None = None
        self._dca: _HeadlessDcaApi | None = None
        self._configs: _HeadlessConfigApi | None = None

    # -- Toolchain ----------------------------------------------------------

    def toolchain(self) -> dict:
        """Validate and display toolchain paths."""
        tc = self._load_tc()
        return validate_toolchain(tc)

    def status(self) -> dict:
        """Overall headless subsystem status."""
        result: dict = {"headless_dir": str(self._headless_dir)}
        try:
            tc = self._load_tc()
            checks = validate_toolchain(tc)
            ok = sum(1 for v in checks.values() if v["status"] == "OK")
            result["toolchain_status"] = f"{ok}/{len(checks)} paths OK"
            result["toolchain_checks"] = checks
        except FileNotFoundError as e:
            result["toolchain_status"] = f"NOT_CONFIGURED: {e}"

        # Serial port discovery (read-only)
        try:
            ports = discover_serial_ports()
            xds = identify_xds110_ports()
            result["serial_ports"] = {
                "total": len(ports),
                "xds110_app_user": xds.get("application_user"),
                "xds110_auxiliary": xds.get("auxiliary_data"),
            }
        except Exception as e:
            result["serial_ports"] = {"error": str(e)}

        return result

    # -- Flash plan ---------------------------------------------------------

    def flash_plan(self) -> dict:
        """Display the flash plan. Does NOT execute flashing.

        Returns the flash plan dict for inspection. To actually flash,
        use flash() with explicit confirmation parameters — but note
        that flash() is not yet implemented until hardware validation.
        """
        try:
            return load_flash_plan(self._headless_dir / "flash_plan.local.json")
        except FileNotFoundError:
            return {"error": "flash_plan.local.json not found", "path": str(self._headless_dir)}

    def flash(self, *, confirm_device_flash: bool = False,
              confirm_sop_uart_boot: bool = False) -> dict:
        """Flash the AWR2944 with the mmw demo firmware.

        NOT YET IMPLEMENTED — requires hardware validation first.
        Both confirmation parameters must be True to proceed.
        """
        if not confirm_device_flash or not confirm_sop_uart_boot:
            raise ValueError(
                "Flashing requires explicit confirmation:\n"
                "  flash(confirm_device_flash=True, confirm_sop_uart_boot=True)\n"
                "Review the flash plan with flash_plan() first."
            )
        raise NotImplementedError(
            "Flashing is not yet implemented. "
            "Use flash_plan() to review the plan and flash manually "
            "following docs/phase5b_flash_procedure.md"
        )

    # -- Serial ports -------------------------------------------------------

    def serial_ports(self) -> dict:
        """Discover serial ports (read-only, no hardware writes)."""
        ports = discover_serial_ports()
        xds = identify_xds110_ports()
        return {
            "ports": [
                {
                    "port": p.port,
                    "name": p.name,
                    "status": p.status,
                    "vid": p.vid,
                    "pid": p.pid,
                    "is_xds110": p.is_xds110,
                    "role": p.role,
                }
                for p in ports
            ],
            "xds110": xds,
            "recommended_app_port": xds.get("application_user"),
        }

    # -- Sub-APIs -----------------------------------------------------------

    @property
    def radar(self) -> "_HeadlessRadarApi":
        if self._radar is None:
            self._radar = _HeadlessRadarApi(self)
        return self._radar

    @property
    def dca(self) -> "_HeadlessDcaApi":
        if self._dca is None:
            self._dca = _HeadlessDcaApi(self)
        return self._dca

    @property
    def configs(self) -> "_HeadlessConfigApi":
        if self._configs is None:
            self._configs = _HeadlessConfigApi(self)
        return self._configs

    # -- Capture workflow ---------------------------------------------------

    def capture(self, name: str, *, radar_config: MmwDemoConfig | None = None,
                notes: str = "", tags: list[str] | None = None) -> HeadlessWorkflow:
        """Create a new headless capture workflow.

        The workflow object tracks progress through stages and maintains
        a comprehensive manifest. Hardware actions require explicit
        confirmation at each stage.
        """
        import uuid
        wf_id = f"headless_{name}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}_{uuid.uuid4().hex[:6]}"
        capture_dir = self._root / "captures" / name
        capture_dir.mkdir(parents=True, exist_ok=True)

        wf = HeadlessWorkflow(
            workflow_id=wf_id,
            capture_dir=capture_dir,
            capture_id=name,
            notes=notes,
            tags=tags,
        )
        return wf

    # -- Internal -----------------------------------------------------------

    def _load_tc(self) -> dict:
        if self._tc is None:
            self._tc = load_toolchain(self._headless_dir / "toolchain.local.json")
        return self._tc

    def __repr__(self) -> str:
        return f"HeadlessApi(root={self._root.name!r})"


# Import datetime for HeadlessApi.capture
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Sub-APIs
# ---------------------------------------------------------------------------

class _HeadlessRadarApi:
    """Radar UART sub-API for lab.headless.radar."""

    def __init__(self, parent: HeadlessApi):
        self._parent = parent
        self._conn: AwrUartConnection | None = None

    def connect(self, port: str | None = None) -> dict:
        """Connect to the AWR2944 UART.

        If port is None, auto-discovers the XDS110 Application/User port.
        """
        if port is None:
            port = identify_application_user_port()
            if port is None:
                raise RuntimeError(
                    "Could not identify XDS110 Application/User UART port. "
                    "Specify the port manually: radar.connect('COM8')"
                )

        self._conn = AwrUartConnection(port)
        self._conn.open()
        return {"connected": True, "port": port}

    def disconnect(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def status(self) -> dict:
        return {
            "connected": self._conn is not None and self._conn.connected,
            "port": self._conn.port if self._conn else None,
        }

    def banner(self) -> str:
        """Read the boot banner from the UART."""
        self._ensure()
        return self._conn.read_boot_banner()

    def help(self) -> CommandResult:
        """Send a 'help' command to the radar CLI."""
        self._ensure()
        return self._conn.send_command("help", timeout=5.0)

    def transcript(self) -> list[TranscriptEntry]:
        """Return the UART communication transcript."""
        if self._conn is None:
            return []
        return self._conn.transcript

    def send_command(self, cmd: str, timeout: float = 5.0) -> CommandResult:
        """Send a single CLI command."""
        self._ensure()
        return self._conn.send_command(cmd, timeout=timeout)

    def send_config(self, cfg_lines: list[str], *,
                    include_sensor_start: bool = False) -> list[CommandResult]:
        """Send config lines. sensorStart is blocked unless explicitly allowed."""
        self._ensure()
        return self._conn.send_config(cfg_lines, include_sensor_start=include_sensor_start)

    def _ensure(self) -> None:
        if self._conn is None or not self._conn.connected:
            raise RuntimeError("Radar not connected. Call radar.connect() first.")


class _HeadlessDcaApi:
    """DCA1000 sub-API for lab.headless.dca."""

    def __init__(self, parent: HeadlessApi):
        self._parent = parent
        self._cli: DcaCli | None = None

    def status(self) -> dict:
        if self._cli is None:
            return {"configured": False}
        return self._cli.status()

    def configure(self, cf_json_path: str | Path | None = None,
                  dry_run: bool = True) -> dict:
        """Set up DCA CLI with paths from toolchain."""
        tc = self._parent._load_tc()
        if cf_json_path is None:
            cf_json_path = tc.get("dca_cli_cf_json", "")
        self._cli = DcaCli.from_toolchain(tc, cf_json_path)
        self._cli.dry_run = dry_run
        return self._cli.status()


class _HeadlessConfigApi:
    """Config management sub-API for lab.headless.configs."""

    def __init__(self, parent: HeadlessApi):
        self._parent = parent

    def load_ti_lvds_sample(self) -> MmwDemoConfig:
        """Load the official TI profile_LVDS.cfg."""
        tc = self._parent._load_tc()
        path = tc.get("sample_lvds_cfg")
        if not path or not Path(path).exists():
            raise FileNotFoundError(
                f"TI LVDS sample not found: {path}. "
                "Check toolchain.local.json sample_lvds_cfg path."
            )
        return MmwDemoConfig.from_cfg_file(path)

    def load_cfg(self, path: str | Path) -> MmwDemoConfig:
        """Load any .cfg file."""
        return MmwDemoConfig.from_cfg_file(path)
