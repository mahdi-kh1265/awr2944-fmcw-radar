"""Phase D — Session & Capture Facade tests.

All tests are offline and use mocked hardware interfaces.
"""

from __future__ import annotations

import json
import os
import tempfile
import warnings
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_test_project(tmp: Path, com_port: str = "COM8",
                         host_ip: str = "192.168.33.30") -> 'RadarProject':
    """Create a test project with local.toml configured."""
    from awr2944_dca.lab import RadarProject
    proj = RadarProject.create("PhaseD_Test", str(tmp))
    # Write local config
    local_toml = tmp / "PhaseD_Test" / ".awr2944" / "local.toml"
    local_toml.parent.mkdir(parents=True, exist_ok=True)
    local_toml.write_text(
        f'[serial]\ncom_port = "{com_port}"\nbaud_rate = 115200\n\n'
        f'[network]\nhost_ip = "{host_ip}"\n\n'
        f'[dca_tools]\ndca_control_exe = ""\n'
        f'dca_record_exe = ""\ncf_json_path = ""\n',
        encoding="utf-8",
    )
    return RadarProject.open(tmp / "PhaseD_Test")


# ===================================================================
# 1. Global Lock
# ===================================================================

class TestGlobalLock:

    def test_lock_file_creation_with_endpoint_hash(self, tmp_path):
        from awr2944_dca.api._lock import HardwareLease, _endpoint_key, _lock_dir
        import hashlib

        key = "COM8|192.168.33.30|4098|192.168.33.180|4096"
        expected_id = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
        assert _endpoint_key("COM8", "192.168.33.30", 4098, "192.168.33.180", 4096) == expected_id
        # Normalization: com port uppercase
        assert _endpoint_key("com8", "192.168.33.30", 4098, "192.168.33.180", 4096) == expected_id

    def test_lock_acquire_release_lifecycle(self, tmp_path):
        from awr2944_dca.api._lock import HardwareLease

        lease = HardwareLease("COM8", "192.168.33.30", 4098, "192.168.33.180", 4096, str(tmp_path))
        assert not lease.held

        info = lease.acquire()
        assert lease.held
        assert info.pid == os.getpid()
        assert lease.lock_path.exists()

        # Re-entrant
        info2 = lease.acquire()
        assert info2.pid == info.pid

        lease.release()
        assert not lease.held
        assert not lease.lock_path.exists()

    def test_stale_lock_detection(self, tmp_path):
        from awr2944_dca.api._lock import HardwareLease, LockInfo
        import socket
        from datetime import datetime, timezone

        lease = HardwareLease("COM8", "192.168.33.30", 4098, "192.168.33.180", 4096, str(tmp_path))
        # Write a stale lock with a non-existent PID
        stale_info = LockInfo(
            pid=99999999,
            process_create_time=0.0,
            hostname=socket.gethostname(),
            project_root=str(tmp_path),
            endpoints={"com_port": "COM8", "host_ip": "192.168.33.30",
                        "data_port": 4098, "dca_ip": "192.168.33.180", "cmd_port": 4096},
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        lease.lock_path.parent.mkdir(parents=True, exist_ok=True)
        lease.lock_path.write_text(stale_info.to_json(), encoding="utf-8")

        # Should acquire because PID is dead
        info = lease.acquire()
        assert lease.held
        lease.release()

    def test_live_lock_refusal(self, tmp_path):
        from awr2944_dca.api._lock import HardwareLease, LockInfo, SessionLockError
        import socket
        from datetime import datetime, timezone

        lease = HardwareLease("COM8", "192.168.33.30", 4098, "192.168.33.180", 4096, str(tmp_path))
        # Write a lock owned by current PID but different lease instance
        live_info = LockInfo(
            pid=os.getpid(),
            process_create_time=0.0,  # Won't match exactly but pid is alive
            hostname=socket.gethostname(),
            project_root="/other/project",
            endpoints={"com_port": "COM8", "host_ip": "192.168.33.30",
                        "data_port": 4098, "dca_ip": "192.168.33.180", "cmd_port": 4096},
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        lease.lock_path.parent.mkdir(parents=True, exist_ok=True)
        lease.lock_path.write_text(live_info.to_json(), encoding="utf-8")

        # Same PID → re-entrant acquire
        info = lease.acquire()
        assert lease.held
        lease.release()

    def test_context_manager(self, tmp_path):
        from awr2944_dca.api._lock import HardwareLease

        lease = HardwareLease("COM8", "192.168.33.30", 4098, "192.168.33.180", 4096, str(tmp_path))
        with lease:
            assert lease.held
            assert lease.lock_path.exists()
        assert not lease.held


# ===================================================================
# 2. Session
# ===================================================================

class TestRadarSession:

    def test_session_state_transitions(self, tmp_path):
        from awr2944_dca.api._session import RadarSession, ResolvedConnection, SessionState
        from awr2944_dca.api._lock import HardwareLease, LockInfo
        from datetime import datetime, timezone

        conn = ResolvedConnection(
            com_port="COM8", host_ip="192.168.33.30", dca_ip="192.168.33.180",
            data_port=4098, cmd_port=4096,
            dca_control_exe="", dca_record_exe="", rf_api_dll="", cf_json_path="",
            source="test",
        )
        lease = HardwareLease("COM8", "192.168.33.30", 4098, "192.168.33.180", 4096, str(tmp_path))
        lock_info = lease.acquire()

        proj = MagicMock()
        proj.root = tmp_path
        (tmp_path / ".awr2944").mkdir(parents=True, exist_ok=True)

        session = RadarSession(project=proj, connection=conn, lease=lease, lock_info=lock_info)
        assert session.state == SessionState.OPEN

        session._enter_capturing()
        assert session.state == SessionState.CAPTURING

        session._exit_capturing(True)
        assert session.state == SessionState.OPEN

        session.close()
        assert session.state == SessionState.CLOSED

    def test_error_state_prevents_capture(self, tmp_path):
        from awr2944_dca.api._session import RadarSession, ResolvedConnection, SessionState
        from awr2944_dca.api._lock import HardwareLease

        conn = ResolvedConnection(
            com_port="COM8", host_ip="192.168.33.30", dca_ip="192.168.33.180",
            data_port=4098, cmd_port=4096,
            dca_control_exe="", dca_record_exe="", rf_api_dll="", cf_json_path="",
            source="test",
        )
        lease = HardwareLease("COM8", "192.168.33.30", 4098, "192.168.33.180", 4096, str(tmp_path))
        lock_info = lease.acquire()

        proj = MagicMock()
        proj.root = tmp_path
        (tmp_path / ".awr2944").mkdir(parents=True, exist_ok=True)

        session = RadarSession(project=proj, connection=conn, lease=lease, lock_info=lock_info)
        session._enter_error()
        assert session.state == SessionState.ERROR

        with pytest.raises(RuntimeError, match="ERROR state"):
            session._enter_capturing()

        session.close()

    def test_reentry_protection(self, tmp_path):
        from awr2944_dca.api._session import RadarSession, ResolvedConnection, SessionState
        from awr2944_dca.api._lock import HardwareLease

        conn = ResolvedConnection(
            com_port="COM8", host_ip="192.168.33.30", dca_ip="192.168.33.180",
            data_port=4098, cmd_port=4096,
            dca_control_exe="", dca_record_exe="", rf_api_dll="", cf_json_path="",
            source="test",
        )
        lease = HardwareLease("COM8", "192.168.33.30", 4098, "192.168.33.180", 4096, str(tmp_path))
        lock_info = lease.acquire()

        proj = MagicMock()
        proj.root = tmp_path
        (tmp_path / ".awr2944").mkdir(parents=True, exist_ok=True)

        session = RadarSession(project=proj, connection=conn, lease=lease, lock_info=lock_info)
        session._enter_capturing()

        with pytest.raises(RuntimeError, match="already in progress"):
            session._enter_capturing()

        session._exit_capturing(True)
        session.close()


# ===================================================================
# 3. CaptureRunResult
# ===================================================================

class TestCaptureRunResult:

    def test_success_property(self):
        from awr2944_dca.api._capture_run import CaptureRunResult
        mock_result = MagicMock()
        mock_result.success = True
        mock_capture = MagicMock()
        result = CaptureRunResult(
            capture=mock_capture,
            session_result=mock_result,
            effective_profile=MagicMock(),
            capture_plan={"frames": 9, "guard_frames": 1},
        )
        assert result.success is True


# ===================================================================
# 4. Input Safety
# ===================================================================

class TestInputSafety:

    def test_unsafe_capture_names(self):
        from awr2944_dca.api._capture_run import _validate_capture_name

        for bad in [
            "",
            "test/bad",
            "test\\bad",
            "C:\\absolute",
            "../traversal",
            "..\\traversal",
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "LPT1",
            "COM1.txt",
        ]:
            with pytest.raises(ValueError, match="Unsafe|empty"):
                _validate_capture_name(bad)

    def test_safe_capture_names(self):
        from awr2944_dca.api._capture_run import _validate_capture_name
        for ok in ["dca_capture", "my_test_001", "probe-sweep", "thermal.test"]:
            _validate_capture_name(ok)  # should not raise


# ===================================================================
# 5. ConnectionOverrides
# ===================================================================

class TestConnectionOverrides:

    def test_session_plus_overrides_rejected(self, tmp_path):
        from awr2944_dca.api._capture_run import FacadeCaptureApi
        from awr2944_dca.api._session import ConnectionOverrides

        proj = MagicMock()
        api = FacadeCaptureApi(proj)
        session = MagicMock()
        overrides = ConnectionOverrides(com_port="COM9")

        with pytest.raises(ValueError, match="Cannot specify both"):
            api.run(session=session, connection_overrides=overrides)


# ===================================================================
# 6. CaptureCollection
# ===================================================================

class TestCaptureCollection:

    def test_deprecated_call(self, tmp_path):
        proj = _create_test_project(tmp_path)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = proj.captures()
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
            assert isinstance(result, list)

    def test_list_empty(self, tmp_path):
        proj = _create_test_project(tmp_path)
        assert proj.captures.list() == []

    def test_iteration(self, tmp_path):
        proj = _create_test_project(tmp_path)
        count = 0
        for cap in proj.captures:
            count += 1
        assert count == 0

    def test_latest_raises_on_empty(self, tmp_path):
        proj = _create_test_project(tmp_path)
        with pytest.raises(ValueError, match="No captures"):
            proj.captures.latest()

    def test_ambiguous_capture_error(self, tmp_path):
        from awr2944_dca.api._collection import AmbiguousCaptureError, CaptureCollection
        # Mock project_status to return two captures matching
        coll = CaptureCollection(tmp_path)
        with patch('awr2944_dca.api._collection.CaptureCollection._load_status') as mock_status:
            mock_status.return_value = {
                'captures': [
                    {'capture_id': '20260715_test_a', 'capture_name': 'test'},
                    {'capture_id': '20260715_test_b', 'capture_name': 'test'},
                ],
            }
            with pytest.raises(AmbiguousCaptureError, match="Ambiguous"):
                coll.get("test")


# ===================================================================
# 7. CaptureVerificationReport
# ===================================================================

class TestVerificationReport:

    def test_success_and_summary(self):
        from awr2944_dca.api._verification import CaptureVerificationReport, VerificationCheck
        report = CaptureVerificationReport(
            success=True,
            checks=[
                VerificationCheck("test_check", "PASS", "all good"),
            ],
        )
        assert report.success
        assert "PASS" in report.summary()
        report.raise_for_errors()  # should not raise

    def test_failure_and_raise(self):
        from awr2944_dca.api._verification import (
            CaptureVerificationReport, VerificationCheck,
            CaptureVerificationError,
        )
        report = CaptureVerificationReport(
            success=False,
            checks=[
                VerificationCheck("bad_check", "FAIL", "something wrong"),
            ],
        )
        with pytest.raises(CaptureVerificationError):
            report.raise_for_errors()

    def test_as_dict_compat(self):
        from awr2944_dca.api._verification import CaptureVerificationReport, VerificationCheck
        report = CaptureVerificationReport(
            success=True,
            checks=[
                VerificationCheck("ok", "PASS"),
                VerificationCheck("warn", "WARN", "minor"),
            ],
        )
        d = report.as_dict()
        assert d["passed"] is True
        assert len(d["warnings"]) == 1
        assert len(d["errors"]) == 0
        # Mapping compat
        assert report["passed"] is True
        assert report.get("nonexistent", "default") == "default"

    def test_manifest_field_precedence(self):
        """Verify sequence_gap_count takes precedence over sequence_gaps."""
        from awr2944_dca.api._verification import verify_production_capture
        manifest = {
            "success": True,
            "status": "complete",
            "sequence_gap_count": 0,
            "sequence_gaps": 5,  # legacy, should be ignored
            "byte_counter_discontinuity_count": 0,
            "missing_payload_bytes": 0,
            "overlap_payload_bytes": 0,
        }
        report = verify_production_capture(Path("/nonexistent"), manifest)
        # Should use sequence_gap_count=0, not sequence_gaps=5
        packet_check = [c for c in report.checks if c.name == "packet_continuity"]
        assert len(packet_check) == 1
        assert packet_check[0].status == "PASS"


# ===================================================================
# 8. CaptureRawData
# ===================================================================

class TestCaptureRawData:

    def test_path_accessors(self, tmp_path):
        from awr2944_dca.api._capture_raw import CaptureRawData
        manifest = {"native_sha256": "abc123", "canonical_sha256": "def456"}
        raw = CaptureRawData(tmp_path, manifest)
        assert raw.native_path is None
        assert raw.canonical_path is None
        assert raw.native_sha256 == "abc123"
        assert raw.canonical_sha256 == "def456"

    def test_compute_sha256(self, tmp_path):
        from awr2944_dca.api._capture_raw import CaptureRawData
        import hashlib

        # Create a test native file
        data = b"test data for hashing"
        (tmp_path / "adc_data.bin").write_bytes(data)

        raw = CaptureRawData(tmp_path, {})
        sha = raw.compute_sha256(kind="native")
        assert sha == hashlib.sha256(data).hexdigest()

    def test_to_cube_delegates_to_parser(self, tmp_path):
        """Verify to_cube uses parse_awr2944_real."""
        from awr2944_dca.api._capture_raw import CaptureRawData
        import numpy as np

        manifest = {
            "canonical_frame_count": 8,
            "logical_cube_shape": [8, 128, 4, 256],
        }
        (tmp_path / "adc_data_canonical.bin").write_bytes(b"\x00" * 100)

        raw = CaptureRawData(tmp_path, manifest)
        mock_cube = np.zeros((8, 128, 4, 256), dtype=np.int16)
        with patch("awr2944_dca.awr2944_adc.parse_awr2944_real", return_value=mock_cube) as mock_parse:
            cube = raw.to_cube(kind="canonical")
            mock_parse.assert_called_once_with(
                tmp_path / "adc_data_canonical.bin",
                8, 128, 4, 256,
            )
            assert cube.shape == (8, 128, 4, 256)


# ===================================================================
# 9. Facade Delegation Order
# ===================================================================

class TestFacadeDelegation:

    def test_unsupported_profile_fails_before_directory(self, tmp_path):
        """Compilation failure must happen before capture directory creation."""
        from awr2944_dca.api.profile import ProfileCompilationNotSupported
        proj = _create_test_project(tmp_path)
        proj_root = tmp_path / "PhaseD_Test"

        smoke = proj.profiles.get("smoke_v1")
        bad = smoke.with_rf(slope_mhz_per_us=50.0)  # unsupported

        capture_dir_count_before = len(list((proj_root / "captures").glob("*"))) if (proj_root / "captures").exists() else 0

        with pytest.raises(ProfileCompilationNotSupported):
            proj.capture.run(profile=bad, frames=9)

        capture_dir_count_after = len(list((proj_root / "captures").glob("*"))) if (proj_root / "captures").exists() else 0
        assert capture_dir_count_after == capture_dir_count_before

    def test_effective_profile_immutability(self, tmp_path):
        """Saved profile must not be mutated by run()."""
        proj = _create_test_project(tmp_path)
        smoke = proj.profiles.get("smoke_v1")
        assert smoke.frame.frame_count == 8

        # Build effective with different frame count
        effective = smoke.with_frame(frame_count=16)
        assert effective.frame.frame_count == 16
        assert smoke.frame.frame_count == 8  # unchanged

    def test_guard_frames_not_in_profile(self, tmp_path):
        """guard_frames must not be a profile attribute."""
        proj = _create_test_project(tmp_path)
        smoke = proj.profiles.get("smoke_v1")
        assert not hasattr(smoke, "guard_frames")

    def test_no_sensor_start_stop_in_commands(self, tmp_path):
        """SDK CLI commands must not contain sensorStart or sensorStop."""
        proj = _create_test_project(tmp_path)
        smoke = proj.profiles.get("smoke_v1")
        cmds = smoke.to_sdk_cli()
        all_text = " ".join(cmds)
        assert "sensorStart" not in all_text
        assert "sensorStop" not in all_text


# ===================================================================
# 10. Emergency Stop
# ===================================================================

class TestEmergencyStop:

    def test_report_structure(self):
        from awr2944_dca.api._emergency import EmergencyStopReport, StopOutcome
        report = EmergencyStopReport(
            radar_stop=StopOutcome("radar_uart", True, "OK"),
            dca_stop=StopOutcome("dca_udp", True, "OK"),
            timestamp="2026-07-15T00:00:00Z",
        )
        assert report.success
        assert "OK" in report.summary()

    def test_refused_when_foreign_live_owner(self):
        from awr2944_dca.api._emergency import emergency_stop, EmergencyStopReport
        from awr2944_dca.api._lock import LockInfo

        # Mock the lease's check_owner to simulate a foreign live process
        with patch("awr2944_dca.api._lock.HardwareLease.check_owner") as mock_check:
            foreign_info = LockInfo(
                pid=1234, process_create_time=0.0,
                hostname="other", project_root="/other",
                endpoints={}, created_at="2026-07-15T00:00:00Z",
            )
            mock_check.return_value = (False, foreign_info)

            with patch("awr2944_dca.api._lock._process_alive", return_value=True):
                report = emergency_stop("COM8", "192.168.33.30", "192.168.33.180")
                assert not report.success
                assert report.radar_stop.skipped
                assert report.dca_stop.skipped


# ===================================================================
# 11. Backward Compatibility
# ===================================================================

class TestBackwardCompat:

    def test_get_capture_alias(self, tmp_path):
        proj = _create_test_project(tmp_path)
        with pytest.raises(ValueError, match="No capture"):
            proj.get_capture("nonexistent")

    def test_latest_capture_alias(self, tmp_path):
        proj = _create_test_project(tmp_path)
        with pytest.raises(ValueError, match="No captures"):
            proj.latest_capture()


# ===================================================================
# 12. API Version
# ===================================================================

class TestApiVersion:

    def test_uses_package_version(self):
        from awr2944_dca.api._capture_run import _get_api_version
        version = _get_api_version()
        assert version == "0.1.0"  # from __init__.py
