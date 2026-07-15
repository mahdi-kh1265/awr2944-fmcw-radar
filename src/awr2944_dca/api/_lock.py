"""Machine-global hardware lease for AWR2944/DCA1000.

Prevents two processes from targeting the same physical hardware
simultaneously, even across different projects.

Lock files are stored under the OS-appropriate user-state directory
(via platformdirs) and keyed by a hash of the hardware endpoint tuple.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _lock_dir() -> Path:
    """Return the OS-appropriate lock directory, creating it if needed."""
    import platformdirs
    d = Path(platformdirs.user_state_dir("awr2944-dca")) / "locks"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _endpoint_key(
    com_port: str,
    host_ip: str,
    data_port: int,
    dca_ip: str,
    cmd_port: int,
) -> str:
    """Deterministic key for a hardware endpoint tuple."""
    key = f"{com_port.upper()}|{host_ip}|{data_port}|{dca_ip}|{cmd_port}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def _process_alive(pid: int, create_time: float | None) -> bool:
    """Check if a process with the given PID is alive, with PID-recycle guard."""
    try:
        import psutil
        proc = psutil.Process(pid)
        if create_time is not None:
            # Allow 2-second tolerance for clock skew
            if abs(proc.create_time() - create_time) > 2.0:
                return False
        return proc.is_running()
    except Exception:
        # psutil not available or PID not found
        try:
            os.kill(pid, 0)
            # Without psutil, we can't check create_time reliably
            if create_time is not None:
                return True  # conservative: assume alive
            return True
        except (OSError, ProcessLookupError):
            return False


def _current_process_create_time() -> float:
    """Get the creation time of the current process."""
    try:
        import psutil
        return psutil.Process(os.getpid()).create_time()
    except Exception:
        return time.time()


class HardwareLockError(Exception):
    """Raised when a hardware lock cannot be acquired."""
    pass


class SessionLockError(HardwareLockError):
    """Raised when a live process owns the hardware."""
    pass


@dataclass
class LockInfo:
    """Contents of a hardware lock file."""
    pid: int
    process_create_time: float
    hostname: str
    project_root: str
    endpoints: dict
    created_at: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, text: str) -> LockInfo:
        data = json.loads(text)
        return cls(**data)


class HardwareLease:
    """Machine-global hardware lease.

    Uses atomic exclusive file creation to prevent TOCTOU races.
    """

    def __init__(
        self,
        com_port: str,
        host_ip: str,
        data_port: int,
        dca_ip: str,
        cmd_port: int,
        project_root: str,
    ):
        self._com_port = com_port
        self._host_ip = host_ip
        self._data_port = data_port
        self._dca_ip = dca_ip
        self._cmd_port = cmd_port
        self._project_root = project_root

        self._lock_id = _endpoint_key(com_port, host_ip, data_port, dca_ip, cmd_port)
        self._lock_path = _lock_dir() / f"{self._lock_id}.lock"
        self._held = False

    @property
    def lock_path(self) -> Path:
        return self._lock_path

    @property
    def held(self) -> bool:
        return self._held

    @property
    def lock_id(self) -> str:
        return self._lock_id

    def acquire(self, force: bool = False) -> LockInfo:
        """Attempt to acquire the hardware lock.

        Uses os.open with O_CREAT | O_EXCL for atomic creation.

        Raises SessionLockError if another live process owns the lock.
        """
        if self._held:
            return self._read_lock()

        # Check for existing lock
        if self._lock_path.exists():
            existing = self._read_lock()
            if existing is not None:
                alive = _process_alive(existing.pid, existing.process_create_time)
                if alive:
                    if existing.pid == os.getpid():
                        # We already own it (re-entrant)
                        self._held = True
                        return existing
                    raise SessionLockError(
                        f"Hardware is locked by PID {existing.pid} "
                        f"(project: {existing.project_root}, "
                        f"since: {existing.created_at}). "
                        f"Cannot acquire lock."
                    )
                else:
                    # Stale lock — remove it
                    if force or True:  # stale locks are always removable
                        logger.info(
                            f"Removing stale lock (PID {existing.pid} no longer alive): "
                            f"{self._lock_path}"
                        )
                        try:
                            self._lock_path.unlink()
                        except FileNotFoundError:
                            pass
            else:
                # Corrupt lock file, remove
                try:
                    self._lock_path.unlink()
                except FileNotFoundError:
                    pass

        # Atomic creation
        import socket
        info = LockInfo(
            pid=os.getpid(),
            process_create_time=_current_process_create_time(),
            hostname=socket.gethostname(),
            project_root=self._project_root,
            endpoints={
                "com_port": self._com_port,
                "host_ip": self._host_ip,
                "data_port": self._data_port,
                "dca_ip": self._dca_ip,
                "cmd_port": self._cmd_port,
            },
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        try:
            fd = os.open(
                str(self._lock_path),
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            )
            try:
                os.write(fd, info.to_json().encode("utf-8"))
            finally:
                os.close(fd)
            self._held = True
            return info
        except FileExistsError:
            # Race condition: another process created the lock between our
            # check and our create. Re-read and report.
            existing = self._read_lock()
            if existing is not None:
                raise SessionLockError(
                    f"Hardware lock acquired by another process (PID {existing.pid}) "
                    f"during race. Project: {existing.project_root}"
                )
            raise HardwareLockError("Failed to acquire lock (race condition).")

    def release(self) -> None:
        """Release the hardware lock."""
        if not self._held:
            return
        try:
            # Only delete if we still own it
            existing = self._read_lock()
            if existing is not None and existing.pid == os.getpid():
                self._lock_path.unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"Failed to release lock: {e}")
        finally:
            self._held = False

    def _read_lock(self) -> LockInfo | None:
        """Read and parse the lock file. Returns None if unreadable."""
        try:
            text = self._lock_path.read_text(encoding="utf-8")
            return LockInfo.from_json(text)
        except (FileNotFoundError, json.JSONDecodeError, TypeError, KeyError):
            return None

    @classmethod
    def inspect_owner(
        cls,
        com_port: str,
        host_ip: str,
        data_port: int,
        dca_ip: str,
        cmd_port: int,
    ) -> tuple[str, LockInfo | None]:
        """Read-only check for the current lock owner without side effects.
        
        Returns:
            (state, lock_info)
            where state is one of:
            "unlocked", "owned_by_us", "owned_by_other_live", "stale", "malformed"
        """
        lock_id = _endpoint_key(com_port, host_ip, data_port, dca_ip, cmd_port)
        import platformdirs
        d = Path(platformdirs.user_state_dir("awr2944-dca")) / "locks"
        lock_path = d / f"{lock_id}.lock"
        
        if not lock_path.exists():
            return "unlocked", None
            
        try:
            text = lock_path.read_text(encoding="utf-8")
            info = LockInfo.from_json(text)
        except Exception:
            return "malformed", None
            
        if info.pid == os.getpid():
            return "owned_by_us", info
        alive = _process_alive(info.pid, info.process_create_time)
        if alive:
            return "owned_by_other_live", info
        return "stale", info

    def check_owner(self) -> tuple[bool, LockInfo | None]:
        """Check who currently owns the lock.

        Returns (is_us, lock_info).
        """
        state, info = self.inspect_owner(
            self._com_port, self._host_ip, self._data_port, self._dca_ip, self._cmd_port
        )
        return (state == "owned_by_us", info)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *exc):
        self.release()
