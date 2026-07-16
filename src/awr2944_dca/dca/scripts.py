"""Generates DCA1000 Lua scripts for setup and capture trigger.

Strict separation of concerns:
- Setup script contains ONLY DCA configuration (no RF transmission).
- Capture trigger script contains StartRecord and StartFrame.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional



def generate_dca_setup_script(
    run_id: str,
    out_path: Path,
    host_ip: str = "192.168.33.30",
    dca_ip: str = "192.168.33.180",
    dca_mac: str = "12:34:56:78:90:12",
    config_port: int = 4096,
    data_port: int = 4098,
    packet_delay: int = 25,
) -> GeneratedScript:
    """Generate DCA1000 setup Lua. State-changing, but no RF transmission."""
    raise NotImplementedError("Legacy mmWave Studio automation has been removed.")


def generate_capture_trigger_script(
    run_id: str,
    out_path: Path,
    output_dir: Path,
    confirm_startframe: bool = False,
) -> GeneratedScript:
    """Generate the trigger Lua script.
    
    This script is small and only executes StartRecord and StartFrame.
    Requires radar static configuration to be complete.
    """
    raise NotImplementedError("Legacy mmWave Studio automation has been removed.")


def generate_postproc_script(
    run_id: str,
    out_path: Path,
    output_dir: Path,
) -> GeneratedScript:
    """Generate Matlab post-processing Lua script."""
    raise NotImplementedError("Legacy mmWave Studio automation has been removed.")
