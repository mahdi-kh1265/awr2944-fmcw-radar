import pytest
from pathlib import Path
from awr2944_dca.config.specs import load_radar_spec, load_capture_card_spec

def test_load_awr2944_spec():
    spec = load_radar_spec("AWR2944EVM")
    assert spec.device_name == "AWR2944EVM"
    assert spec.hardware_limits.max_tx_channels == 4
    assert spec.hardware_limits.max_rx_channels == 4
    assert spec.hardware_limits.min_frequency_ghz == 76.0
    assert spec.hardware_limits.max_frequency_ghz == 81.0

def test_load_dca1000_spec():
    spec = load_capture_card_spec("DCA1000EVM")
    assert spec.device_name == "DCA1000EVM"
    assert spec.network.default_pc_static_ip == "192.168.33.30"
    assert "adc_data.bin" in spec.file_formats["postproc_file"].extension

def test_load_invalid_spec():
    with pytest.raises(FileNotFoundError):
        load_radar_spec("INVALID_RADAR")
