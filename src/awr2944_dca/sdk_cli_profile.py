"""SDK Demo CLI profile generator for AWR2944.

This module provides pure UART CLI commands for the AWR2944 mmw demo firmware.
It contains no mmWave Studio or Lua dependencies.
"""

def build_smoke_v1_cli(frames: int, chirps_per_frame: int = 128) -> list[str]:
    """Build the smoke_v1 SDK CLI configuration.
    
    Returns the exact configuration commands required between sensorStop
    and sensorStart.
    """
    commands = [
        "flushCfg",
        "dfeDataOutputMode 1",
        "channelCfg 15 7 0",
        "adcCfg 2 0",
        "adcbufCfg -1 1 1 1 1",
        "lowPower 0 0",
        "profileCfg 0 77 100 6 60 0 0 29.982 0 256 10000 0 0 30",
        "chirpCfg 0 0 0 0 0 0 0 3",
        f"frameCfg 0 0 {chirps_per_frame} {frames} 256 40 1 0",
        "lowPower 0 0",
        "guiMonitor -1 1 1 0 0 0 1",
        "cfarCfg -1 0 2 8 4 3 0 15 1",
        "cfarCfg -1 1 0 4 2 3 1 15 1",
        "multiObjBeamForming -1 1 0.5",
        "calibDcRangeSig -1 0 -5 8 256",
        "clutterRemoval -1 0",
        "antGeometryCfg 1 0 1 1 1 2 1 3 0 2 0 3 0 4 0 5 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1 11 0.5 0.8",
        "compRangeBiasAndRxChanPhase 0.0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0",
        "measureRangeBiasAndRxChanPhase 0 1.5 0.2",
        "aoaFovCfg -1 -90 90 -90 90",
        "cfarFovCfg -1 0 0 19.53",
        "cfarFovCfg -1 1 -1 1.00",
        "extendedMaxVelocity -1 0",
        "calibData 0 0 0x1f0000",
        "CQRxSatMonitor 0 3 11 121 0",
        "CQSigImgMonitor 0 127 8",
        "analogMonitor 0 0",
        "lvdsStreamCfg -1 0 1 0",
    ]
    return commands
