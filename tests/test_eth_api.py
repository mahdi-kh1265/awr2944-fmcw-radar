"""Tests for Ethernet pairing/configuration (eth.py).

All tests are pure-logic — no PowerShell, no hardware.
Uses synthetic adapter dicts to exercise snapshot diffing,
candidate selection, and configure commands.
"""

import json
from pathlib import Path

import pytest

from awr2944_dca.eth import (
    AdapterInfo,
    EthernetPairing,
    EthernetSnapshot,
    PairingSession,
    begin_pairing,
    build_configure_commands,
    diff_snapshots,
    finish_pairing,
    load_pairing,
    remove_pairing,
    save_pairing,
    select_candidate,
    snapshot_from_dicts,
)
from awr2944_dca.project import init_project


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_adapter(
    alias="Ethernet 5",
    index=27,
    status="Up",
    mac="AA:BB:CC:DD:EE:01",
    ips=None,
    gateway=False,
    dns=False,
    media_type="802.3",
) -> dict:
    """Build a raw PowerShell adapter dict."""
    return {
        "InterfaceAlias": alias,
        "InterfaceIndex": index,
        "Status": status,
        "LinkSpeed": "1 Gbps",
        "MacAddress": mac,
        "IPv4Addresses": ips or [],
        "HasDefaultGateway": gateway,
        "HasDns": dns,
        "MediaType": media_type,
    }


def _make_project(tmp_path):
    """Init a project for testing."""
    return init_project(name="eth_test", root=tmp_path)


# ---------------------------------------------------------------------------
# snapshot_from_dicts
# ---------------------------------------------------------------------------

def test_snapshot_from_dicts():
    raw = [
        _make_adapter(alias="Ethernet 1", index=5, mac="AA:01"),
        _make_adapter(alias="Ethernet 2", index=6, mac="AA:02"),
    ]
    snap = snapshot_from_dicts(raw)
    assert len(snap.adapters) == 2
    assert snap.adapters[0].interface_alias == "Ethernet 1"
    assert snap.adapters[1].mac_address == "AA:02"
    assert snap.timestamp  # non-empty


# ---------------------------------------------------------------------------
# diff_snapshots
# ---------------------------------------------------------------------------

def test_diff_snapshots_detects_new_adapter():
    before = snapshot_from_dicts([
        _make_adapter(alias="Eth1", index=1, mac="AA:01"),
    ])
    after = snapshot_from_dicts([
        _make_adapter(alias="Eth1", index=1, mac="AA:01"),
        _make_adapter(alias="Eth2", index=2, mac="AA:02", status="Up"),
    ])
    candidates = diff_snapshots(before, after)
    assert len(candidates) == 1
    assert candidates[0].interface_alias == "Eth2"


def test_diff_snapshots_detects_status_change():
    before = snapshot_from_dicts([
        _make_adapter(alias="Eth1", index=1, mac="AA:01", status="Disconnected"),
    ])
    after = snapshot_from_dicts([
        _make_adapter(alias="Eth1", index=1, mac="AA:01", status="Up"),
    ])
    candidates = diff_snapshots(before, after)
    assert len(candidates) == 1
    assert candidates[0].interface_alias == "Eth1"


def test_diff_snapshots_no_change():
    before = snapshot_from_dicts([
        _make_adapter(alias="Eth1", index=1, mac="AA:01", status="Up"),
    ])
    after = snapshot_from_dicts([
        _make_adapter(alias="Eth1", index=1, mac="AA:01", status="Up"),
    ])
    candidates = diff_snapshots(before, after)
    assert candidates == []


# ---------------------------------------------------------------------------
# select_candidate
# ---------------------------------------------------------------------------

def test_select_candidate_single():
    adapter = AdapterInfo(
        interface_alias="Ethernet 5", interface_index=27, status="Up",
        link_speed="1 Gbps", mac_address="AA:BB",
    )
    result = select_candidate([adapter])
    assert result.interface_alias == "Ethernet 5"


def test_select_candidate_refuses_wifi():
    wifi = AdapterInfo(
        interface_alias="Wi-Fi", interface_index=3, status="Up",
        link_speed="300 Mbps", mac_address="CC:DD",
        media_type="Native 802.11",
    )
    with pytest.raises(ValueError, match="Wi-Fi"):
        select_candidate([wifi])


def test_select_candidate_refuses_gateway():
    adapter = AdapterInfo(
        interface_alias="Ethernet 1", interface_index=5, status="Up",
        link_speed="1 Gbps", mac_address="AA:BB",
        has_default_gateway=True,
    )
    with pytest.raises(ValueError, match="default gateway"):
        select_candidate([adapter])


def test_select_candidate_ambiguous_error():
    a1 = AdapterInfo(
        interface_alias="Eth1", interface_index=1, status="Up",
        link_speed="1 Gbps", mac_address="AA:01",
    )
    a2 = AdapterInfo(
        interface_alias="Eth2", interface_index=2, status="Up",
        link_speed="1 Gbps", mac_address="AA:02",
    )
    with pytest.raises(ValueError, match="Ambiguous"):
        select_candidate([a1, a2])


def test_select_candidate_none_error():
    with pytest.raises(ValueError, match="No new or changed"):
        select_candidate([])


def test_select_candidate_force_allows_gateway():
    adapter = AdapterInfo(
        interface_alias="Ethernet 1", interface_index=5, status="Up",
        link_speed="1 Gbps", mac_address="AA:BB",
        has_default_gateway=True,
    )
    result = select_candidate([adapter], force=True)
    assert result.interface_alias == "Ethernet 1"


# ---------------------------------------------------------------------------
# build_configure_commands
# ---------------------------------------------------------------------------

def test_build_configure_commands():
    adapter = AdapterInfo(
        interface_alias="Ethernet 5", interface_index=27, status="Up",
        link_speed="1 Gbps", mac_address="AA:BB",
    )
    cmds = build_configure_commands(adapter, host_ip="192.168.33.30", prefix_length=24)
    assert len(cmds) == 4
    assert any("New-NetIPAddress" in c for c in cmds)
    assert any("192.168.33.30" in c for c in cmds)
    assert any("27" in c for c in cmds)


# ---------------------------------------------------------------------------
# begin/finish pairing
# ---------------------------------------------------------------------------

def test_begin_finish_pairing_detects_new_adapter(tmp_path):
    _make_project(tmp_path)

    before_data = [_make_adapter(alias="Eth1", index=1, mac="AA:01")]
    after_data = [
        _make_adapter(alias="Eth1", index=1, mac="AA:01"),
        _make_adapter(alias="DCA Eth", index=5, mac="AA:05", status="Up"),
    ]

    session = begin_pairing(snapshot_fn=lambda: snapshot_from_dicts(before_data))
    assert session.before is not None
    assert session.after is None

    result = finish_pairing(
        session,
        project_root=tmp_path,
        apply=False,
        snapshot_fn=lambda: snapshot_from_dicts(after_data),
    )

    assert result["paired"] is True
    assert result["adapter"]["interface_alias"] == "DCA Eth"
    assert result["applied"] is False
    assert len(result["commands"]) == 4


def test_begin_finish_pairing_detects_down_to_up(tmp_path):
    _make_project(tmp_path)

    before_data = [_make_adapter(alias="Eth5", index=5, mac="AA:05", status="Disconnected")]
    after_data = [_make_adapter(alias="Eth5", index=5, mac="AA:05", status="Up")]

    session = begin_pairing(snapshot_fn=lambda: snapshot_from_dicts(before_data))
    result = finish_pairing(
        session,
        project_root=tmp_path,
        apply=False,
        snapshot_fn=lambda: snapshot_from_dicts(after_data),
    )

    assert result["paired"] is True
    assert result["adapter"]["interface_alias"] == "Eth5"


def test_finish_pairing_refuses_ambiguous(tmp_path):
    _make_project(tmp_path)

    before_data = [_make_adapter(alias="Eth1", index=1, mac="AA:01")]
    after_data = [
        _make_adapter(alias="Eth1", index=1, mac="AA:01"),
        _make_adapter(alias="Eth2", index=2, mac="AA:02"),
        _make_adapter(alias="Eth3", index=3, mac="AA:03"),
    ]

    session = begin_pairing(snapshot_fn=lambda: snapshot_from_dicts(before_data))
    with pytest.raises(ValueError, match="Ambiguous"):
        finish_pairing(
            session,
            project_root=tmp_path,
            apply=False,
            snapshot_fn=lambda: snapshot_from_dicts(after_data),
        )


def test_finish_pairing_refuses_wifi(tmp_path):
    _make_project(tmp_path)

    before_data = []
    after_data = [
        _make_adapter(alias="Wi-Fi", index=3, mac="CC:01", media_type="Native 802.11"),
    ]

    session = begin_pairing(snapshot_fn=lambda: snapshot_from_dicts(before_data))
    with pytest.raises(ValueError, match="Wi-Fi"):
        finish_pairing(
            session,
            project_root=tmp_path,
            apply=False,
            snapshot_fn=lambda: snapshot_from_dicts(after_data),
        )


def test_finish_pairing_refuses_gateway(tmp_path):
    _make_project(tmp_path)

    before_data = []
    after_data = [
        _make_adapter(alias="Ethernet 1", index=5, mac="AA:05", gateway=True),
    ]

    session = begin_pairing(snapshot_fn=lambda: snapshot_from_dicts(before_data))
    with pytest.raises(ValueError, match="default gateway"):
        finish_pairing(
            session,
            project_root=tmp_path,
            apply=False,
            snapshot_fn=lambda: snapshot_from_dicts(after_data),
        )


def test_configure_dry_run_does_not_apply(tmp_path):
    _make_project(tmp_path)

    before_data = []
    after_data = [
        _make_adapter(alias="Eth5", index=5, mac="AA:05", status="Up"),
    ]

    session = begin_pairing(snapshot_fn=lambda: snapshot_from_dicts(before_data))
    result = finish_pairing(
        session,
        project_root=tmp_path,
        apply=False,
        snapshot_fn=lambda: snapshot_from_dicts(after_data),
    )

    assert result["applied"] is False
    assert len(result["commands"]) == 4
    assert result["apply_results"] == []


# ---------------------------------------------------------------------------
# Pairing persistence
# ---------------------------------------------------------------------------

def test_pairing_stored_in_local_not_project_json(tmp_path):
    _make_project(tmp_path)

    pairing = EthernetPairing(
        interface_alias="Eth5",
        interface_index=5,
        host_adapter_mac="AA:05",
        paired_at="2026-07-10T12:00:00",
    )
    save_pairing(tmp_path, pairing)

    # Machine-local file exists
    assert (tmp_path / ".local" / "eth_pairing.json").exists()

    # project.json does NOT contain adapter pairing
    proj = json.loads((tmp_path / "project.json").read_text(encoding="utf-8"))
    assert "eth" not in proj
    assert "interface_alias" not in json.dumps(proj)

    # .gitignore contains .local/
    gi = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert ".local/" in gi


def test_project_json_stores_shared_dca_profile_only(tmp_path):
    from awr2944_dca.project import set_dca_profile
    _make_project(tmp_path)
    set_dca_profile(tmp_path, dca_mac="0C:22:38:4E:5A:0C")

    proj = json.loads((tmp_path / "project.json").read_text(encoding="utf-8"))
    assert "dca_profile" in proj
    assert proj["dca_profile"]["dca_mac"] == "0C:22:38:4E:5A:0C"
    # No machine-local adapter info in project.json
    assert "interface_alias" not in json.dumps(proj)
    assert "interface_index" not in json.dumps(proj)


def test_load_and_remove_pairing(tmp_path):
    _make_project(tmp_path)

    assert load_pairing(tmp_path) is None

    pairing = EthernetPairing(
        interface_alias="Eth5",
        interface_index=5,
        host_adapter_mac="AA:05",
        paired_at="2026-07-10T12:00:00",
    )
    save_pairing(tmp_path, pairing)
    loaded = load_pairing(tmp_path)
    assert loaded is not None
    assert loaded.interface_alias == "Eth5"

    remove_pairing(tmp_path)
    assert load_pairing(tmp_path) is None
