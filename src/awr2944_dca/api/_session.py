"""RadarSession — resolved connection settings and hardware lease.

A session holds an immutable snapshot of connection parameters and a
machine-global hardware lease.  It does NOT maintain persistent UART
or socket connections; those remain ephemeral inside the frozen
capture_session.run_capture.

States: CLOSED → OPEN → CAPTURING → OPEN → … → CLOSED
                              │
                              └──→ ERROR → CLOSED
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from awr2944_dca.api._lock import HardwareLease, LockInfo

if TYPE_CHECKING:
    from awr2944_dca.lab import RadarProject

logger = logging.getLogger(__name__)


class SessionState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    CAPTURING = "CAPTURING"
    ERROR = "ERROR"


@dataclass(frozen=True)
class ConnectionOverrides:
    """Optional one-off overrides for connection settings."""
    com_port: str | None = None
    host_ip: str | None = None
    dca_ip: str | None = None
    data_port: int | None = None
    cmd_port: int | None = None
    dca_control_exe: str | None = None
    dca_record_exe: str | None = None
    rf_api_dll: str | None = None
    cf_json_path: str | None = None


@dataclass(frozen=True)
class ResolvedConnection:
    """Immutable resolved connection settings."""
    com_port: str
    host_ip: str
    dca_ip: str
    data_port: int
    cmd_port: int
    dca_control_exe: str
    dca_record_exe: str
    rf_api_dll: str
    cf_json_path: str
    source: str  # "local.toml", "local.toml+overrides"

    def as_dict(self) -> dict:
        return {
            "com_port": self.com_port,
            "host_ip": self.host_ip,
            "dca_ip": self.dca_ip,
            "data_port": self.data_port,
            "cmd_port": self.cmd_port,
            "dca_control_exe": self.dca_control_exe,
            "dca_record_exe": self.dca_record_exe,
            "rf_api_dll": self.rf_api_dll,
            "cf_json_path": self.cf_json_path,
            "source": self.source,
        }


class ConnectionConfigError(Exception):
    """Missing or invalid connection configuration."""
    pass


def resolve_connection(
    project_root: Path,
    overrides: ConnectionOverrides | None = None,
) -> ResolvedConnection:
    """Resolve connection settings from local.toml, with optional overrides."""
    from awr2944_dca._config import ProjectConfig
    config = ProjectConfig(project_root)

    source = "local.toml"

    com_port = config.local.com_port
    host_ip = config.local.host_ip
    dca_ip = config.portable.dca_ip
    data_port = config.portable.data_port
    cmd_port = config.portable.config_port
    dca_control_exe = config.local.dca_control_exe
    dca_record_exe = config.local.dca_record_exe
    rf_api_dll = config.local.rf_api_dll
    cf_json_path = config.local.cf_json_path

    if overrides:
        source = "local.toml+overrides"
        if overrides.com_port is not None:
            com_port = overrides.com_port
        if overrides.host_ip is not None:
            host_ip = overrides.host_ip
        if overrides.dca_ip is not None:
            dca_ip = overrides.dca_ip
        if overrides.data_port is not None:
            data_port = overrides.data_port
        if overrides.cmd_port is not None:
            cmd_port = overrides.cmd_port
        if overrides.dca_control_exe is not None:
            dca_control_exe = overrides.dca_control_exe
        if overrides.dca_record_exe is not None:
            dca_record_exe = overrides.dca_record_exe
        if overrides.rf_api_dll is not None:
            rf_api_dll = overrides.rf_api_dll
        if overrides.cf_json_path is not None:
            cf_json_path = overrides.cf_json_path

    if not com_port:
        raise ConnectionConfigError(
            "COM port not configured. Set com_port in .awr2944/local.toml"
        )
    if not host_ip:
        raise ConnectionConfigError(
            "Host IP not configured. Set host_ip in .awr2944/local.toml"
        )

    return ResolvedConnection(
        com_port=com_port,
        host_ip=host_ip,
        dca_ip=dca_ip,
        data_port=data_port,
        cmd_port=cmd_port,
        dca_control_exe=dca_control_exe,
        dca_record_exe=dca_record_exe,
        rf_api_dll=rf_api_dll,
        cf_json_path=cf_json_path,
        source=source,
    )


class RadarSession:
    """Resolved connection and hardware lease.

    The session is not a persistent connection — it is a validated
    configuration snapshot with a global lock that prevents concurrent
    hardware access.
    """

    def __init__(
        self,
        project: RadarProject,
        connection: ResolvedConnection,
        lease: HardwareLease,
        lock_info: LockInfo,
    ):
        self._project = project
        self._connection = connection
        self._lease = lease
        self._lock_info = lock_info
        self._state = SessionState.OPEN

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def connection(self) -> ResolvedConnection:
        return self._connection

    @property
    def project(self) -> RadarProject:
        return self._project

    @property
    def capture(self) -> Any:
        """Access capture API through this session."""
        if not hasattr(self, '_capture_api'):
            from awr2944_dca.api._capture_run import SessionCaptureApi
            self._capture_api = SessionCaptureApi(self)
        return self._capture_api

    def _enter_capturing(self) -> None:
        """Transition to CAPTURING state. Called by capture facade."""
        if self._state == SessionState.ERROR:
            raise RuntimeError(
                "Session is in ERROR state and cannot capture. Close and reconnect."
            )
        if self._state == SessionState.CLOSED:
            raise RuntimeError("Session is closed.")
        if self._state == SessionState.CAPTURING:
            raise RuntimeError("A capture is already in progress on this session.")
        self._state = SessionState.CAPTURING

    def _exit_capturing(self, success: bool) -> None:
        """Return to OPEN or ERROR state after capture."""
        if success:
            self._state = SessionState.OPEN
        else:
            # Graceful failure from run_capture → still OPEN
            self._state = SessionState.OPEN

    def _enter_error(self) -> None:
        """Transition to ERROR due to unexpected exception."""
        self._state = SessionState.ERROR

    def close(self) -> None:
        """Release the hardware lease. Idempotent."""
        if self._state == SessionState.CLOSED:
            return
        self._lease.release()
        self._state = SessionState.CLOSED
        # Remove breadcrumb
        breadcrumb = self._project.root / ".awr2944" / "session.breadcrumb"
        try:
            breadcrumb.unlink(missing_ok=True)
        except Exception:
            pass

    def __enter__(self) -> RadarSession:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __repr__(self) -> str:
        return (
            f"RadarSession(state={self._state.value}, "
            f"com={self._connection.com_port}, "
            f"host={self._connection.host_ip})"
        )
