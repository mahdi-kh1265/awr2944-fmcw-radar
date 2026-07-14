"""
Headless AWR2944 serial port discovery and UART communication.

Discovers XDS110 serial ports via PnP device enumeration and provides
a timestamped UART connection for sending mmw demo CLI commands.

Does NOT depend on mmWave Studio, RSTD, Lua, pywinauto, or GUI output reading.

Serial settings from TI documentation:
    - EVM_SETUP_PAGE.html § "Setup UART Terminal": 115200 baud, 8N1
    - uart_uniflash.py line 210: baudrate=115200
"""

from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SerialPortInfo:
    """Discovered serial port metadata from PnP enumeration."""
    port: str
    name: str = ""
    description: str = ""
    status: str = ""
    instance_id: str = ""
    vid: str = ""
    pid: str = ""
    is_xds110: bool = False
    role: str = ""  # "application_user", "auxiliary_data", or ""


@dataclass
class TranscriptEntry:
    """Single entry in the UART communication transcript."""
    direction: str  # "TX" or "RX"
    text: str
    timestamp: str = ""  # ISO 8601

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class CommandResult:
    """Result of a single CLI command sent over UART."""
    command: str
    response_lines: list[str]
    success: bool
    error_msg: str = ""
    prompt_recovered: bool = False
    elapsed_s: float = 0.0
    timestamp: str = ""
    timed_out: bool = False

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_BAUDRATE = 115200
DEFAULT_BYTESIZE = 8  # 8 data bits
DEFAULT_PARITY = "N"  # No parity
DEFAULT_STOPBITS = 1  # 1 stop bit
DEFAULT_TIMEOUT_S = 5.0
XDS110_VID = "0451"
XDS110_PID_APP = "BEF3"  # XDS110 Application/User


# ---------------------------------------------------------------------------
# Discovery functions (read-only, no hardware writes)
# ---------------------------------------------------------------------------

def discover_serial_ports() -> list[SerialPortInfo]:
    """Discover all serial ports using Windows PnP device enumeration.

    Returns a list of SerialPortInfo with metadata for each COM port.
    Does not open or write to any port.
    """
    ports = []
    try:
        result = subprocess.run(
            [
                "powershell", "-NoProfile", "-Command",
                "Get-PnpDevice -Class Ports -ErrorAction SilentlyContinue | "
                "Select-Object Status, FriendlyName, InstanceId | "
                "ConvertTo-Json -Depth 2"
            ],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            return ports

        import json
        data = json.loads(result.stdout)
        if isinstance(data, dict):
            data = [data]

        for entry in data:
            friendly = entry.get("FriendlyName", "")
            instance_id = entry.get("InstanceId", "")
            status = entry.get("Status", "")

            # Extract COM port from friendly name
            com_match = re.search(r"\(COM(\d+)\)", friendly)
            if not com_match:
                continue

            port_name = f"COM{com_match.group(1)}"

            # Extract VID/PID from instance ID
            vid_match = re.search(r"VID_([0-9A-Fa-f]{4})", instance_id)
            pid_match = re.search(r"PID_([0-9A-Fa-f]{4})", instance_id)
            vid = vid_match.group(1).upper() if vid_match else ""
            pid = pid_match.group(1).upper() if pid_match else ""

            is_xds110 = vid == XDS110_VID and pid == XDS110_PID_APP

            # Determine role
            role = ""
            if is_xds110:
                if "Application" in friendly or "User" in friendly:
                    role = "application_user"
                elif "Auxiliary" in friendly:
                    role = "auxiliary_data"

            info = SerialPortInfo(
                port=port_name,
                name=friendly,
                description=friendly,
                status=status,
                instance_id=instance_id,
                vid=vid,
                pid=pid,
                is_xds110=is_xds110,
                role=role,
            )
            ports.append(info)

    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass

    return sorted(ports, key=lambda p: p.port)


def identify_xds110_ports() -> dict:
    """Identify XDS110 Application/User and Auxiliary ports.

    Returns dict with keys 'application_user' and 'auxiliary_data',
    each containing the COM port name or None.
    """
    ports = discover_serial_ports()
    result = {"application_user": None, "auxiliary_data": None}
    for p in ports:
        if p.is_xds110 and p.role == "application_user":
            result["application_user"] = p.port
        elif p.is_xds110 and p.role == "auxiliary_data":
            result["auxiliary_data"] = p.port
    return result


def identify_application_user_port() -> str | None:
    """Return the best-guess Application/User UART port name, or None."""
    xds = identify_xds110_ports()
    return xds.get("application_user")


# ---------------------------------------------------------------------------
# UART Connection
# ---------------------------------------------------------------------------

class AwrUartConnection:
    """Timestamped UART connection for mmw demo CLI communication.

    All transmitted commands and received responses are recorded in the
    transcript with timestamps.
    """

    def __init__(self, port: str, baudrate: int = DEFAULT_BAUDRATE,
                 timeout: float = DEFAULT_TIMEOUT_S):
        self._port_name = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._serial = None
        self._transcript: list[TranscriptEntry] = []
        self._connected = False

    @property
    def port(self) -> str:
        return self._port_name

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def transcript(self) -> list[TranscriptEntry]:
        return list(self._transcript)

    def open(self) -> None:
        """Open the serial port. Raises ImportError if pyserial not installed."""
        try:
            import serial
        except ImportError:
            raise ImportError(
                "pyserial is required for UART communication. "
                "Install with: pip install pyserial"
            )

        if self._connected:
            return

        self._serial = serial.Serial(
            port=self._port_name,
            baudrate=self._baudrate,
            bytesize=DEFAULT_BYTESIZE,
            parity=DEFAULT_PARITY,
            stopbits=DEFAULT_STOPBITS,
            timeout=self._timeout,
        )
        self._connected = True
        self._record("SYSTEM", f"Opened {self._port_name} at {self._baudrate} 8N1")

    def close(self) -> None:
        """Close the serial port."""
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None
        self._connected = False
        self._record("SYSTEM", f"Closed {self._port_name}")

    def read_boot_banner(self, timeout: float = 5.0) -> str:
        """Read any boot banner text available on the port.

        Reads for up to `timeout` seconds, collecting all received bytes.
        Does not send anything.
        """
        self._ensure_open()
        old_timeout = self._serial.timeout
        self._serial.timeout = timeout

        collected = b""
        deadline = time.time() + timeout
        while time.time() < deadline:
            chunk = self._serial.read(1024)
            if chunk:
                collected += chunk
            else:
                break

        self._serial.timeout = old_timeout
        text = collected.decode("utf-8", errors="replace").strip()
        if text:
            self._record("RX", text)
        return text

    def read_until_prompt(self, timeout: float = 10.0,
                          prompt_pattern: str = r"mmwDemo:/>") -> str:
        """Read until the CLI prompt appears or timeout.

        Returns all text received. The mmw demo CLI typically shows
        'mmwDemo:/>' as the prompt.
        """
        self._ensure_open()
        old_timeout = self._serial.timeout
        self._serial.timeout = 0.5  # Short polling interval

        collected = b""
        deadline = time.time() + timeout
        while time.time() < deadline:
            chunk = self._serial.read(1024)
            if chunk:
                collected += chunk
                text = collected.decode("utf-8", errors="replace")
                if re.search(prompt_pattern, text):
                    break
            if not chunk and time.time() >= deadline:
                break

        self._serial.timeout = old_timeout
        text = collected.decode("utf-8", errors="replace")
        if text.strip():
            self._record("RX", text.strip())
        return text

    def send_command(self, cmd: str, timeout: float = DEFAULT_TIMEOUT_S,
                     prompt_pattern: str = r"mmwDemo:/>") -> CommandResult:
        """Send a single CLI command and wait for response.

        Records the full command/response in the transcript.
        Detects success ("Done"), errors ("Error"), and prompt recovery.
        """
        self._ensure_open()
        cmd_clean = cmd.strip()
        t_start = time.time()

        # Flush input buffer
        self._serial.reset_input_buffer()

        # Send command with newline
        tx_bytes = (cmd_clean + "\n").encode("utf-8")
        self._serial.write(tx_bytes)
        self._record("TX", cmd_clean)

        # Read response
        old_timeout = self._serial.timeout
        self._serial.timeout = 0.5

        collected = b""
        deadline = time.time() + timeout
        timed_out = True
        while time.time() < deadline:
            chunk = self._serial.read(1024)
            if chunk:
                collected += chunk
                text = collected.decode("utf-8", errors="replace")
                if re.search(prompt_pattern, text):
                    timed_out = False
                    break
            if not chunk and len(collected) > 0:
                # Short pause then retry
                time.sleep(0.1)
                chunk = self._serial.read(1024)
                if chunk:
                    collected += chunk
                else:
                    # No more data and no prompt — might be done
                    if "Done" in collected.decode("utf-8", errors="replace"):
                        timed_out = False
                    break

        self._serial.timeout = old_timeout
        elapsed = time.time() - t_start
        response_text = collected.decode("utf-8", errors="replace")

        # Parse response lines
        lines = [l.strip() for l in response_text.splitlines() if l.strip()]
        # Remove echo of the command itself
        if lines and lines[0] == cmd_clean:
            lines = lines[1:]

        # Detect success/error
        has_error = any("Error" in l or "error" in l for l in lines)
        has_done = any("Done" in l for l in lines)
        prompt_recovered = bool(re.search(prompt_pattern, response_text))

        success = has_done and not has_error and not timed_out
        error_msg = ""
        if has_error:
            error_lines = [l for l in lines if "Error" in l or "error" in l]
            error_msg = "; ".join(error_lines)
        elif timed_out:
            error_msg = f"Timeout after {timeout}s waiting for response"

        if response_text.strip():
            self._record("RX", response_text.strip())

        return CommandResult(
            command=cmd_clean,
            response_lines=lines,
            success=success,
            error_msg=error_msg,
            prompt_recovered=prompt_recovered,
            elapsed_s=round(elapsed, 3),
            timed_out=timed_out,
        )

    def send_config(self, cfg_lines: list[str], *,
                    include_sensor_start: bool = False,
                    timeout_per_cmd: float = DEFAULT_TIMEOUT_S) -> list[CommandResult]:
        """Send multiple CLI config lines sequentially.

        If include_sensor_start is False (default), any 'sensorStart' line
        is skipped with an error result. This prevents accidental frame starts.

        Returns a list of CommandResult for each line.
        """
        results = []
        for line in cfg_lines:
            line = line.strip()
            if not line or line.startswith("%"):
                continue

            if line.startswith("sensorStart") and not include_sensor_start:
                results.append(CommandResult(
                    command=line,
                    response_lines=["BLOCKED: sensorStart requires include_sensor_start=True"],
                    success=False,
                    error_msg="sensorStart blocked by safety gate",
                ))
                continue

            result = self.send_command(line, timeout=timeout_per_cmd)
            results.append(result)

            if not result.success:
                # Stop on first error
                break

        return results

    def save_transcript(self, path: Path) -> Path:
        """Save the full transcript to a JSON file."""
        import json
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        entries = [
            {"direction": e.direction, "text": e.text, "timestamp": e.timestamp}
            for e in self._transcript
        ]
        path.write_text(json.dumps(entries, indent=2), encoding="utf-8")
        return path

    def _ensure_open(self) -> None:
        if not self._connected or self._serial is None:
            raise RuntimeError(
                f"UART port {self._port_name} is not open. Call open() first."
            )

    def _record(self, direction: str, text: str) -> None:
        self._transcript.append(TranscriptEntry(direction=direction, text=text))

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *exc):
        self.close()

    def __repr__(self) -> str:
        state = "connected" if self._connected else "disconnected"
        return f"AwrUartConnection(port={self._port_name!r}, {state})"
