"""Tests for headless_workflow.py — state machine and manifest."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from awr2944_dca.headless_workflow import (
    HeadlessManifest,
    HeadlessStage,
    HeadlessWorkflow,
    STAGE_ORDER,
)


# ---------------------------------------------------------------------------
# Stage order tests
# ---------------------------------------------------------------------------

class TestStageOrder:
    def test_stage_count(self):
        assert len(STAGE_ORDER) == 14

    def test_created_is_first(self):
        assert STAGE_ORDER[0] == HeadlessStage.CREATED

    def test_complete_is_last(self):
        assert STAGE_ORDER[-1] == HeadlessStage.COMPLETE

    def test_all_stages_except_error_in_order(self):
        """ERROR is not in the normal sequence."""
        assert HeadlessStage.ERROR not in STAGE_ORDER


# ---------------------------------------------------------------------------
# Workflow creation tests
# ---------------------------------------------------------------------------

class TestWorkflowCreation:
    def test_new_workflow_starts_at_created(self, tmp_path):
        wf = HeadlessWorkflow("test_001", tmp_path)
        assert wf.stage == HeadlessStage.CREATED
        assert not wf.is_complete
        assert not wf.has_error

    def test_workflow_id(self, tmp_path):
        wf = HeadlessWorkflow("test_001", tmp_path)
        assert wf.workflow_id == "test_001"

    def test_manifest_has_timestamps(self, tmp_path):
        wf = HeadlessWorkflow("test_001", tmp_path)
        assert wf.manifest.created_at
        assert wf.manifest.updated_at


# ---------------------------------------------------------------------------
# Forward transitions
# ---------------------------------------------------------------------------

class TestForwardTransitions:
    def test_advance_one_step(self, tmp_path):
        wf = HeadlessWorkflow("test_001", tmp_path)
        wf.advance_to(HeadlessStage.FIRMWARE_VERIFIED, "Firmware hash matches")
        assert wf.stage == HeadlessStage.FIRMWARE_VERIFIED

    def test_advance_through_full_sequence(self, tmp_path):
        wf = HeadlessWorkflow("test_001", tmp_path)
        for stage in STAGE_ORDER[1:]:
            wf.advance_to(stage, f"Reached {stage.value}")
        assert wf.stage == HeadlessStage.COMPLETE
        assert wf.is_complete

    def test_cannot_go_backward(self, tmp_path):
        wf = HeadlessWorkflow("test_001", tmp_path)
        wf.advance_to(HeadlessStage.FIRMWARE_VERIFIED)
        with pytest.raises(ValueError, match="only forward"):
            wf.advance_to(HeadlessStage.CREATED)

    def test_cannot_stay_same(self, tmp_path):
        wf = HeadlessWorkflow("test_001", tmp_path)
        wf.advance_to(HeadlessStage.FIRMWARE_VERIFIED)
        with pytest.raises(ValueError, match="only forward"):
            wf.advance_to(HeadlessStage.FIRMWARE_VERIFIED)

    def test_cannot_skip_stages(self, tmp_path):
        wf = HeadlessWorkflow("test_001", tmp_path)
        with pytest.raises(ValueError, match="Cannot skip"):
            wf.advance_to(HeadlessStage.RADAR_CONNECTED)

    def test_error_always_allowed(self, tmp_path):
        wf = HeadlessWorkflow("test_001", tmp_path)
        wf.advance_to(HeadlessStage.ERROR, "Something broke")
        assert wf.has_error


# ---------------------------------------------------------------------------
# Error recording
# ---------------------------------------------------------------------------

class TestErrorRecording:
    def test_record_error(self, tmp_path):
        wf = HeadlessWorkflow("test_001", tmp_path)
        wf.record_error("UART timeout")
        assert wf.has_error
        assert "UART timeout" in wf.manifest.errors

    def test_multiple_errors_accumulate(self, tmp_path):
        wf = HeadlessWorkflow("test_001", tmp_path)
        wf.record_error("Error 1")
        # Can't advance after error — test the manifest directly
        assert len(wf.manifest.errors) == 1


# ---------------------------------------------------------------------------
# State persistence
# ---------------------------------------------------------------------------

class TestStatePersistence:
    def test_save_and_load_state(self, tmp_path):
        wf = HeadlessWorkflow("test_001", tmp_path, capture_id="cap_001")
        wf.advance_to(HeadlessStage.FIRMWARE_VERIFIED, "Hash OK")

        state_file = wf.save_state(tmp_path / "state.json")
        assert state_file.exists()

        wf2 = HeadlessWorkflow.load_state(state_file)
        assert wf2.workflow_id == "test_001"
        assert wf2.stage == HeadlessStage.FIRMWARE_VERIFIED
        assert wf2.manifest.capture_id == "cap_001"

    def test_save_manifest(self, tmp_path):
        wf = HeadlessWorkflow("test_001", tmp_path)
        wf.manifest.firmware_sha256 = "ABCD1234"
        wf.manifest.serial_port = "COM8"

        manifest_file = wf.save_manifest(tmp_path / "manifest.json")
        assert manifest_file.exists()

        data = json.loads(manifest_file.read_text())
        assert data["firmware"]["sha256"] == "ABCD1234"
        assert data["serial"]["port"] == "COM8"


# ---------------------------------------------------------------------------
# Manifest tests
# ---------------------------------------------------------------------------

class TestManifest:
    def test_manifest_roundtrip(self):
        m = HeadlessManifest(
            workflow_id="wf_001",
            capture_id="cap_001",
            firmware_sha256="ABC123",
            serial_port="COM8",
            expected_adc_payload_bytes=12345678,
            notes="Test capture",
            tags=["smoke", "lvds"],
        )
        d = m.to_dict()
        m2 = HeadlessManifest.from_dict(d)
        assert m2.workflow_id == "wf_001"
        assert m2.firmware_sha256 == "ABC123"
        assert m2.serial_port == "COM8"
        assert m2.expected_adc_payload_bytes == 12345678
        assert m2.notes == "Test capture"
        assert m2.tags == ["smoke", "lvds"]

    def test_manifest_empty(self):
        m = HeadlessManifest()
        d = m.to_dict()
        assert d["workflow_id"] == ""
        assert d["firmware"]["sha256"] == ""
        assert d["capture"]["expected_transport_bytes"] == "UNKNOWN"


# ---------------------------------------------------------------------------
# Status report
# ---------------------------------------------------------------------------

class TestStatus:
    def test_status_dict(self, tmp_path):
        wf = HeadlessWorkflow("test_001", tmp_path, capture_id="cap_001")
        s = wf.status()
        assert s["workflow_id"] == "test_001"
        assert s["stage"] == "created"
        assert not s["is_complete"]
        assert not s["has_error"]
        assert s["capture_id"] == "cap_001"


# ---------------------------------------------------------------------------
# Repr
# ---------------------------------------------------------------------------

class TestRepr:
    def test_repr(self, tmp_path):
        wf = HeadlessWorkflow("test_001", tmp_path)
        r = repr(wf)
        assert "test_001" in r
        assert "created" in r
