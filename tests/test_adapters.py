import pytest
from unittest.mock import patch
from awr2944_dca.dca.adapters import NetworkAdapter, score_adapter, suggest_dca_adapter
from awr2944_dca.cli import app
from typer.testing import CliRunner

runner = CliRunner()

def test_score_campus_ethernet_rejected():
    """Ethernet with campus IP/default gateway is rejected as DCA candidate."""
    a = NetworkAdapter(
        interface_alias="Ethernet",
        interface_index=15,
        status="Up",
        link_speed="1 Gbps",
        mac_address="00-11-22-33-44-55",
        ipv4_addresses=["128.101.169.148"],
        has_default_gateway=True,
        has_dns=True
    )
    score, reason, is_safe = score_adapter(a)
    assert not is_safe
    assert score < 0
    assert "default gateway" in reason.lower()

def test_score_ethernet_5_suggested():
    """Ethernet 5 with APIPA/no gateway is suggested."""
    a = NetworkAdapter(
        interface_alias="Ethernet 5",
        interface_index=27,
        status="Disconnected",
        link_speed="1 Gbps",
        mac_address="9C-69-D3-99-F4-3F",
        ipv4_addresses=["169.254.4.237"],
        has_default_gateway=False,
        has_dns=False
    )
    score, reason, is_safe = score_adapter(a)
    assert is_safe
    assert score > 0
    assert "apipa" in reason.lower()
    assert "ethernet" in reason.lower()
    assert "no default gateway" in reason.lower()

def test_score_already_configured():
    """Adapter already set to 192.168.33.30/24 is strong PASS."""
    a = NetworkAdapter(
        interface_alias="Ethernet 5",
        interface_index=27,
        status="Up",
        link_speed="1 Gbps",
        mac_address="9C-69-D3-99-F4-3F",
        ipv4_addresses=["192.168.33.30"],
        has_default_gateway=False,
        has_dns=False
    )
    score, reason, is_safe = score_adapter(a)
    assert is_safe
    assert score >= 100
    assert "strong pass" in reason.lower()

def test_configure_adapter_dry_run_makes_no_changes(monkeypatch):
    """configure-adapter --dry-run makes no changes and prints commands."""
    a = NetworkAdapter(
        interface_alias="Ethernet 5",
        interface_index=27,
        status="Disconnected",
        link_speed="1 Gbps",
        mac_address="9C-69-D3-99-F4-3F",
        ipv4_addresses=["169.254.4.237"],
        has_default_gateway=False,
        has_dns=False
    )
    monkeypatch.setattr("awr2944_dca.dca.adapters.get_adapters", lambda: [a])
    
    # We mock check_call to raise an exception if it's called, proving it wasn't
    def fail_if_called(*args, **kwargs):
        pytest.fail("check_call should not be invoked on dry-run")
        
    monkeypatch.setattr("subprocess.check_call", fail_if_called)
    
    res = runner.invoke(app, ["dca", "configure-adapter", "--interface", "Ethernet 5", "--dry-run"])
    assert res.exit_code == 0
    assert "Dry-run for adapter 'Ethernet 5'" in res.stdout
    assert "New-NetIPAddress" in res.stdout
    assert "192.168.33.30" in res.stdout

def test_configure_adapter_without_yes_or_dry_run_refuses():
    """configure-adapter without --yes refuses."""
    res = runner.invoke(app, ["dca", "configure-adapter", "--interface", "Ethernet 5"])
    assert res.exit_code == 1
    assert "must specify either --yes or --dry-run" in res.stdout

def test_configure_adapter_refuses_gateway_adapter(monkeypatch):
    """configure-adapter refuses gateway adapter unless --allow-gateway-adapter."""
    a = NetworkAdapter(
        interface_alias="Ethernet",
        interface_index=15,
        status="Up",
        link_speed="1 Gbps",
        mac_address="00-11-22-33-44-55",
        ipv4_addresses=["128.101.169.148"],
        has_default_gateway=True,
        has_dns=True
    )
    monkeypatch.setattr("awr2944_dca.dca.adapters.get_adapters", lambda: [a])
    
    # without allow flag
    res1 = runner.invoke(app, ["dca", "configure-adapter", "--interface", "Ethernet", "--dry-run"])
    assert res1.exit_code == 1
    assert "Safety Error: Refusing to modify adapter with a default gateway" in res1.stdout
    
    # with allow flag
    res2 = runner.invoke(app, ["dca", "configure-adapter", "--interface", "Ethernet", "--dry-run", "--allow-gateway-adapter"])
    assert res2.exit_code == 0
    assert "Dry-run for adapter 'Ethernet'" in res2.stdout

def test_preflight_prints_suggested_adapter(monkeypatch):
    """preflight prints suggested adapter when host IP missing but APIPA candidate exists."""
    # mock preflight to return FAIL for the adapter IP
    from awr2944_dca.dca.preflight import PreflightReport, PreflightCheck
    
    mock_report = PreflightReport(
        checks=[
            PreflightCheck("Adapter IP 192.168.33.30", "FAIL", "Not found on any local adapter")
        ],
        overall="NOT_READY"
    )
    
    monkeypatch.setattr("awr2944_dca.dca.preflight.run_dca_preflight", lambda **k: mock_report)
    
    # mock adapter list
    a = NetworkAdapter(
        interface_alias="Ethernet 5",
        interface_index=27,
        status="Disconnected",
        link_speed="1 Gbps",
        mac_address="9C-69-D3-99-F4-3F",
        ipv4_addresses=["169.254.4.237"],
        has_default_gateway=False,
        has_dns=False
    )
    monkeypatch.setattr("awr2944_dca.dca.adapters.get_adapters", lambda: [a])
    
    res = runner.invoke(app, ["dca", "preflight"])
    
    # Should exit 1 because NOT_READY, but we should see the suggestion in stdout
    assert res.exit_code == 1
    assert "Suggested DCA adapter: Ethernet 5" in res.stdout
    assert "awr dca configure-adapter --interface \"Ethernet 5\"" in res.stdout
