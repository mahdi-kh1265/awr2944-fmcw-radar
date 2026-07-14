"""Legacy mmWave Studio backend controller package.

This subsystem is considered legacy and optional.
The primary production hardware execution path now bypasses mmWave Studio entirely,
using the AWR2944 Demo UART CLI and direct DCA1000 UDP socket capture.

This module is retained for mmWave Studio GUI validation, RSTD automation,
and specific radar features not yet supported by the SDK CLI path.
"""
