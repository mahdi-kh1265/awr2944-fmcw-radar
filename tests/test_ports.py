import pytest
from awr2944_dca.hardware.ports import scan_ports, resolve_port, save_local_hardware

class MockPort:
    def __init__(self, device, description, manufacturer, hwid):
        self.device = device
        self.description = description
        self.manufacturer = manufacturer
        self.hwid = hwid

def test_ports_heuristics(monkeypatch):
    import awr2944_dca.hardware.ports
    monkeypatch.setattr(awr2944_dca.hardware.ports, "HAVE_PYSERIAL", True)
    
    import sys
    from unittest.mock import MagicMock
    mock_serial = MagicMock()
    mock_serial.tools.list_ports.comports.return_value = [
        MockPort("COM3", "XDS110 Class Application/User UART", "Texas Instruments", "USB\\VID_0451&PID_BEF3"),
        MockPort("COM4", "XDS110 Class Auxiliary Data Port", "Texas Instruments", "USB\\VID_0451&PID_BEF3"),
        MockPort("COM5", "USB Serial Port", "FTDI", "USB\\VID_0403&PID_6015"),
        MockPort("COM6", "Standard Serial over Bluetooth link", "Microsoft", "BTHENUM"),
        MockPort("COM7", "AR-DevPack", "TI", "USB\\VID"),
    ]
    monkeypatch.setattr(awr2944_dca.hardware.ports, "serial", mock_serial, raising=False)
    
    ports = scan_ports()
    assert len(ports) == 5
    
    assert ports[0].com == "COM3"
    assert ports[0].likely_role == "awr_rs232_candidate"
    assert ports[0].confidence == "high"
    
    assert ports[1].com == "COM4"
    assert ports[1].likely_role == "awr_xds_uart_candidate"
    assert ports[1].confidence == "high"
    
    assert ports[2].com == "COM5"
    assert ports[2].likely_role == "awr_ftdi_control_candidate"
    
    assert ports[3].com == "COM6"
    assert ports[3].likely_role == "unknown"
    
    assert ports[4].com == "COM7"
    assert ports[4].likely_role == "awr_ftdi_control_candidate"

def test_ports_resolve(monkeypatch):
    import awr2944_dca.hardware.ports
    monkeypatch.setattr(awr2944_dca.hardware.ports, "HAVE_PYSERIAL", True)
    
    import sys
    from unittest.mock import MagicMock
    mock_serial = MagicMock()
    mock_serial.tools.list_ports.comports.return_value = [
        MockPort("COM4", "XDS110 Class Auxiliary Data Port", "TI", ""),
        MockPort("COM3", "XDS110 Class Application/User UART", "TI", ""),
    ]
    monkeypatch.setattr(awr2944_dca.hardware.ports, "serial", mock_serial, raising=False)
    
    candidates = resolve_port("awr_rs232_candidate")
    assert candidates[0].com == "COM3"  # Ranks higher because confidence is high

def test_save_local_hardware(tmp_path):
    cfg = save_local_hardware(tmp_path, "awr-rs232", "COM8")
    assert cfg.exists()
    assert "COM8" in cfg.read_text()
