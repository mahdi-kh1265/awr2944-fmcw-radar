"""Emergency stop facade.

Sends sensorStop and DCA stop_record using existing proven helpers.
Respects lock ownership: refuses if another live process owns the hardware
(unless force=True).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class StopOutcome:
    """Outcome of a single stop operation."""
    target: str          # "radar_uart" or "dca_udp"
    success: bool
    detail: str
    skipped: bool = False


@dataclass
class EmergencyStopReport:
    """Result of an emergency stop attempt."""
    radar_stop: StopOutcome
    dca_stop: StopOutcome
    timestamp: str
    lock_owner_info: Optional[dict] = None

    @property
    def success(self) -> bool:
        return self.radar_stop.success and self.dca_stop.success

    def summary(self) -> str:
        lines = [
            f"Emergency Stop Report ({self.timestamp})",
            f"  Radar: {'OK' if self.radar_stop.success else 'FAIL'} — {self.radar_stop.detail}",
            f"  DCA:   {'OK' if self.dca_stop.success else 'FAIL'} — {self.dca_stop.detail}",
        ]
        if self.lock_owner_info:
            lines.append(f"  Lock owner: PID {self.lock_owner_info.get('pid')}, project: {self.lock_owner_info.get('project_root')}")
        return "\n".join(lines)


def emergency_stop(
    com_port: str,
    host_ip: str,
    dca_ip: str,
    data_port: int = 4098,
    cmd_port: int = 4096,
    force: bool = False,
    project_root: str = "",
) -> EmergencyStopReport:
    """Execute emergency sensorStop + DCA stop_record.

    Uses only audited existing helpers:
    - AwrUartConnection for sensorStop (ephemeral serial, no persistent state)
    - DirectUdpCapture for stop_record (ephemeral UDP socket per call)

    Lock ownership:
    - No lock → proceed
    - Current process owns → proceed
    - Another live process owns → refuse unless force=True
    - Another live process + force → proceed but report owner
    """
    from awr2944_dca.api._lock import HardwareLease, _process_alive

    timestamp = datetime.now(timezone.utc).isoformat()
    lock_owner_info = None

    # Check lock ownership
    lease = HardwareLease(
        com_port=com_port,
        host_ip=host_ip,
        data_port=data_port,
        dca_ip=dca_ip,
        cmd_port=cmd_port,
        project_root=project_root,
    )
    is_us, lock_info = lease.check_owner()

    if lock_info is not None and not is_us:
        alive = _process_alive(lock_info.pid, lock_info.process_create_time)
        if alive and not force:
            return EmergencyStopReport(
                radar_stop=StopOutcome("radar_uart", False, "Refused: another live process owns the hardware", skipped=True),
                dca_stop=StopOutcome("dca_udp", False, "Refused: another live process owns the hardware", skipped=True),
                timestamp=timestamp,
                lock_owner_info={"pid": lock_info.pid, "project_root": lock_info.project_root},
            )
        if alive and force:
            lock_owner_info = {"pid": lock_info.pid, "project_root": lock_info.project_root}

    # --- Radar sensorStop ---
    try:
        from awr2944_dca.headless_serial import AwrUartConnection
        with AwrUartConnection(com_port, 115200) as conn:
            res = conn.send_command("sensorStop")
            radar_detail = f"sensorStop sent, response: {res.response_lines}"
            radar_outcome = StopOutcome("radar_uart", True, radar_detail)
    except Exception as e:
        radar_outcome = StopOutcome("radar_uart", False, f"sensorStop failed: {e}")

    # --- DCA stop_record ---
    try:
        from awr2944_dca.direct_udp_capture import DirectUdpCapture
        dca = DirectUdpCapture(host_ip=host_ip, dca_ip=dca_ip, cmd_port=cmd_port)
        ack = dca.stop_record()
        if ack:
            dca_outcome = StopOutcome("dca_udp", True, "stop_record acknowledged")
        else:
            dca_outcome = StopOutcome("dca_udp", False, "stop_record sent but no acknowledgement received")
    except Exception as e:
        dca_outcome = StopOutcome("dca_udp", False, f"stop_record failed: {e}")

    return EmergencyStopReport(
        radar_stop=radar_outcome,
        dca_stop=dca_outcome,
        timestamp=timestamp,
        lock_owner_info=lock_owner_info,
    )
