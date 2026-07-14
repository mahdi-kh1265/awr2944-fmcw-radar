"""
mmw Demo CLI configuration parser and model.

Parses, validates, renders, and compares TI mmw demo .cfg files.
These are the plain-text CLI command files sent over UART to configure
the AWR2944 mmw demo firmware.

Does NOT depend on mmWave Studio, RSTD, Lua, or RadarConfig.
The from_radar_config() adapter is deferred until after hardware validation.

CLI syntax verified from mmw_cli.c (MMWAVE-MCUPLUS-SDK 04.07.02.01).
"""

from __future__ import annotations

import copy
import hashlib
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Known commands and their expected argument counts (from mmw_cli.c)
# ---------------------------------------------------------------------------

# arg_count is the number of space-separated tokens AFTER the command name.
# -1 means variable/unknown.
KNOWN_COMMANDS: dict[str, int] = {
    # CLI library built-ins
    "sensorStop": 0,
    "sensorStart": -1,  # 0 or 1 (optional reconfig flag)
    "flushCfg": 0,
    "dfeDataOutputMode": 1,
    "channelCfg": 3,
    "adcCfg": 2,
    "lowPower": 2,
    "profileCfg": 14,
    "chirpCfg": 8,
    "frameCfg": 8,
    # Demo-specific (registered in MmwDemo_CLIInit)
    "adcbufCfg": 5,
    "guiMonitor": 7,
    "lvdsStreamCfg": 4,
    "cfarCfg": 9,            # TDM
    "multiObjBeamForming": 3,  # TDM
    "calibDcRangeSig": 5,    # TDM
    "clutterRemoval": 2,     # TDM
    "antGeometryCfg": -1,    # Variable args
    "compRangeBiasAndRxChanPhase": -1,  # Variable args
    "measureRangeBiasAndRxChanPhase": 3,
    "aoaFovCfg": 5,
    "cfarFovCfg": 4,
    "extendedMaxVelocity": 2,  # TDM
    "calibData": 3,
    "CQRxSatMonitor": 5,
    "CQSigImgMonitor": 3,
    "analogMonitor": 2,
    "configDataPort": 2,
    "queryDemoStatus": 0,
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class CfgLine:
    """A single line from a .cfg file, preserving original text."""
    line_number: int
    raw_text: str
    command: str = ""       # Empty for comments/blanks
    args: list[str] = field(default_factory=list)
    is_comment: bool = False
    is_blank: bool = False
    is_sensor_start: bool = False

    @property
    def is_command(self) -> bool:
        return bool(self.command) and not self.is_comment and not self.is_blank


@dataclass
class ValidationIssue:
    """A validation warning or error for a .cfg file."""
    level: str  # "error", "warning", "info"
    line_number: int
    command: str
    message: str


# ---------------------------------------------------------------------------
# MmwDemoConfig
# ---------------------------------------------------------------------------

class MmwDemoConfig:
    """Parsed mmw demo .cfg file.

    Preserves comments, command order, unknown commands, and raw arguments.
    """

    def __init__(self):
        self.lines: list[CfgLine] = []
        self.source_path: str = ""
        self.source_sha256: str = ""

    @classmethod
    def from_cfg_file(cls, path: str | Path) -> "MmwDemoConfig":
        """Parse a .cfg file preserving all content."""
        path = Path(path)
        text = path.read_text(encoding="utf-8")
        sha = hashlib.sha256(path.read_bytes()).hexdigest().upper()

        cfg = cls()
        cfg.source_path = str(path)
        cfg.source_sha256 = sha

        for i, raw_line in enumerate(text.splitlines(), start=1):
            stripped = raw_line.strip()

            if not stripped:
                cfg.lines.append(CfgLine(
                    line_number=i, raw_text=raw_line,
                    is_blank=True,
                ))
                continue

            if stripped.startswith("%"):
                cfg.lines.append(CfgLine(
                    line_number=i, raw_text=raw_line,
                    is_comment=True,
                ))
                continue

            # Parse command and arguments
            tokens = stripped.split()
            cmd = tokens[0]
            args = tokens[1:]

            cfg.lines.append(CfgLine(
                line_number=i, raw_text=raw_line,
                command=cmd, args=args,
                is_sensor_start=cmd == "sensorStart",
            ))

        return cfg

    @classmethod
    def from_cfg_text(cls, text: str) -> "MmwDemoConfig":
        """Parse .cfg content from a string."""
        cfg = cls()
        for i, raw_line in enumerate(text.splitlines(), start=1):
            stripped = raw_line.strip()
            if not stripped:
                cfg.lines.append(CfgLine(line_number=i, raw_text=raw_line, is_blank=True))
                continue
            if stripped.startswith("%"):
                cfg.lines.append(CfgLine(line_number=i, raw_text=raw_line, is_comment=True))
                continue
            tokens = stripped.split()
            cfg.lines.append(CfgLine(
                line_number=i, raw_text=raw_line,
                command=tokens[0], args=tokens[1:],
                is_sensor_start=tokens[0] == "sensorStart",
            ))
        return cfg

    def to_cfg_text(self, *, include_sensor_start: bool = False) -> str:
        """Render back to .cfg text, preserving original formatting.

        If include_sensor_start is False, sensorStart lines are
        commented out with a safety note.
        """
        output_lines = []
        for cl in self.lines:
            if cl.is_sensor_start and not include_sensor_start:
                output_lines.append(f"% [BLOCKED] {cl.raw_text.strip()}")
            else:
                output_lines.append(cl.raw_text)
        return "\n".join(output_lines) + "\n"

    def save(self, path: str | Path, *, include_sensor_start: bool = False) -> Path:
        """Write .cfg to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        text = self.to_cfg_text(include_sensor_start=include_sensor_start)
        path.write_text(text, encoding="utf-8")
        return path

    def command_list(self, *, include_sensor_start: bool = False) -> list[str]:
        """Return list of CLI command strings (no comments/blanks)."""
        cmds = []
        for cl in self.lines:
            if not cl.is_command:
                continue
            if cl.is_sensor_start and not include_sensor_start:
                continue
            tokens = [cl.command] + cl.args
            cmds.append(" ".join(tokens))
        return cmds

    def split_start_command(self) -> tuple[list[str], str | None]:
        """Split into (config_commands, sensor_start_command).

        Returns the config commands (everything except sensorStart)
        and the sensorStart command if present, or None.
        """
        config = []
        start_cmd = None
        for cl in self.lines:
            if not cl.is_command:
                continue
            line_text = " ".join([cl.command] + cl.args)
            if cl.is_sensor_start:
                start_cmd = line_text
            else:
                config.append(line_text)
        return config, start_cmd

    def validate(self) -> list[ValidationIssue]:
        """Validate against known mmw demo CLI syntax.

        Returns a list of issues (errors, warnings, info).
        """
        issues = []
        commands_seen = {}

        for cl in self.lines:
            if not cl.is_command:
                continue

            # Track duplicates
            if cl.command in commands_seen:
                # Some commands (chirpCfg, cfarCfg, cfarFovCfg, lowPower) can appear multiple times
                repeatable = {"chirpCfg", "cfarCfg", "cfarFovCfg", "lowPower"}
                if cl.command not in repeatable:
                    issues.append(ValidationIssue(
                        level="warning", line_number=cl.line_number,
                        command=cl.command,
                        message=f"Duplicate command (first seen at line {commands_seen[cl.command]})",
                    ))
            commands_seen.setdefault(cl.command, cl.line_number)

            # Check known vs unknown
            if cl.command not in KNOWN_COMMANDS:
                issues.append(ValidationIssue(
                    level="warning", line_number=cl.line_number,
                    command=cl.command,
                    message="Unknown command — not in verified mmw demo CLI command table",
                ))
                continue

            # Check argument count
            expected = KNOWN_COMMANDS[cl.command]
            if expected >= 0 and len(cl.args) != expected:
                issues.append(ValidationIssue(
                    level="error", line_number=cl.line_number,
                    command=cl.command,
                    message=f"Expected {expected} args, got {len(cl.args)}",
                ))

        # Check required commands
        required = {"sensorStop", "flushCfg", "dfeDataOutputMode", "channelCfg",
                     "adcCfg", "profileCfg", "chirpCfg", "frameCfg"}
        for req in required:
            if req not in commands_seen:
                issues.append(ValidationIssue(
                    level="warning", line_number=0,
                    command=req,
                    message="Required command not found in configuration",
                ))

        return issues

    def get_command(self, name: str) -> CfgLine | None:
        """Return the first CfgLine for a given command name."""
        for cl in self.lines:
            if cl.command == name:
                return cl
        return None

    def get_commands(self, name: str) -> list[CfgLine]:
        """Return all CfgLines for a given command name."""
        return [cl for cl in self.lines if cl.command == name]

    def summary(self) -> dict:
        """Return a structured summary of the configuration."""
        result: dict[str, Any] = {
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "total_lines": len(self.lines),
            "command_count": sum(1 for cl in self.lines if cl.is_command),
            "comment_count": sum(1 for cl in self.lines if cl.is_comment),
            "has_sensor_start": any(cl.is_sensor_start for cl in self.lines),
        }

        # Extract key parameters
        profile = self.get_command("profileCfg")
        if profile and len(profile.args) >= 14:
            result["profile"] = {
                "profile_id": int(profile.args[0]),
                "start_freq_ghz": float(profile.args[1]),
                "idle_time_us": float(profile.args[2]),
                "adc_start_time_us": float(profile.args[3]),
                "ramp_end_time_us": float(profile.args[4]),
                "freq_slope_mhz_per_us": float(profile.args[7]),
                "num_adc_samples": int(profile.args[9]),
                "sample_rate_ksps": int(profile.args[10]),
                "rx_gain_db": int(profile.args[13]),
            }

        frame = self.get_command("frameCfg")
        if frame and len(frame.args) >= 7:
            result["frame"] = {
                "chirp_start_idx": int(frame.args[0]),
                "chirp_end_idx": int(frame.args[1]),
                "num_loops": int(frame.args[2]),
                "num_frames": int(frame.args[3]),
                "frame_periodicity_ms": float(frame.args[4]),
            }

        channel = self.get_command("channelCfg")
        if channel and len(channel.args) >= 2:
            rx_mask = int(channel.args[0])
            tx_mask = int(channel.args[1])
            result["channel"] = {
                "rx_channel_mask": rx_mask,
                "tx_channel_mask": tx_mask,
                "num_rx": bin(rx_mask).count("1"),
                "num_tx": bin(tx_mask).count("1"),
            }

        lvds = self.get_command("lvdsStreamCfg")
        if lvds and len(lvds.args) >= 4:
            result["lvds"] = {
                "sub_frame_idx": int(lvds.args[0]),
                "enable_header": int(lvds.args[1]),
                "data_fmt": int(lvds.args[2]),
                "enable_sw": int(lvds.args[3]),
            }

        chirps = self.get_commands("chirpCfg")
        if chirps:
            result["chirp_count"] = len(chirps)
            result["chirps"] = [
                {
                    "start_idx": int(c.args[0]),
                    "end_idx": int(c.args[1]),
                    "profile_id": int(c.args[2]),
                    "tx_enable": int(c.args[7]),
                }
                for c in chirps if len(c.args) >= 8
            ]

        return result

    def derived(self) -> dict:
        """Calculate derived parameters: bandwidth, timing, expected bytes.

        Returns a dict with calculated values and the assumptions used.
        """
        s = self.summary()
        result: dict[str, Any] = {"assumptions": []}
        assumptions = result["assumptions"]

        profile = s.get("profile")
        frame = s.get("frame")
        channel = s.get("channel")
        lvds = s.get("lvds")

        if not profile or not frame or not channel:
            result["error"] = "Missing profileCfg, frameCfg, or channelCfg"
            return result

        num_adc_samples = profile["num_adc_samples"]
        num_rx = channel["num_rx"]
        idle_time_us = profile["idle_time_us"]
        ramp_end_time_us = profile["ramp_end_time_us"]
        chirp_time_us = idle_time_us + ramp_end_time_us
        slope = profile["freq_slope_mhz_per_us"]
        start_freq = profile["start_freq_ghz"]
        num_loops = frame["num_loops"]
        num_frames = frame["num_frames"]
        frame_period_ms = frame["frame_periodicity_ms"]
        chirp_start = frame["chirp_start_idx"]
        chirp_end = frame["chirp_end_idx"]
        chirps_per_loop = chirp_end - chirp_start + 1

        # Bandwidth and range resolution
        bw_mhz = slope * ramp_end_time_us
        range_res_m = 3e8 / (2 * bw_mhz * 1e6) if bw_mhz > 0 else 0
        max_range_m = (num_adc_samples * 3e8) / (4 * bw_mhz * 1e6) if bw_mhz > 0 else 0

        # Velocity resolution
        lambda_m = 3e8 / (start_freq * 1e9)
        num_tx = channel["num_tx"]
        v_max = lambda_m / (4 * chirp_time_us * 1e-6 * chirps_per_loop) if chirps_per_loop > 0 else 0
        v_res = v_max * 2 / num_loops if num_loops > 0 else 0

        # LVDS bandwidth check
        n_lanes = 2
        bps_per_lane = 600e6  # 600 Mbps
        max_bytes_per_chirp = chirp_time_us * n_lanes * bps_per_lane / 8e6

        # ADC bytes per chirp — depends on format assumptions
        assumptions.append("complex int16 (4 bytes per IQ sample)")
        bytes_per_sample = 4  # complex int16 = 2 bytes I + 2 bytes Q
        adc_bytes_per_chirp = num_adc_samples * num_rx * bytes_per_sample
        assumptions.append(f"{num_rx} RX channels active")

        lvds_header_bytes = 0
        if lvds and lvds.get("enable_header"):
            lvds_header_bytes = 52  # HSI header size (approximate)
            assumptions.append("HSI header enabled: ~52 bytes per chirp")
        else:
            assumptions.append("HSI header disabled")

        sw_bytes = 0
        if lvds and lvds.get("enable_sw"):
            assumptions.append("SW payload enabled (size unknown, not included in estimate)")
        else:
            assumptions.append("SW payload disabled")

        total_per_chirp = adc_bytes_per_chirp + lvds_header_bytes + sw_bytes
        lvds_margin = max_bytes_per_chirp - total_per_chirp
        lvds_passes = lvds_margin > 0

        # Expected ADC payload bytes (without transport overhead)
        total_chirps = num_loops * chirps_per_loop * num_frames
        expected_adc_payload_bytes = total_chirps * adc_bytes_per_chirp
        assumptions.append(f"Total chirps: {num_loops} loops × {chirps_per_loop} chirps/loop × {num_frames} frames = {total_chirps}")

        # Expected capture duration
        total_duration_ms = num_frames * frame_period_ms

        result.update({
            "bandwidth_mhz": round(bw_mhz, 2),
            "range_resolution_m": round(range_res_m, 3),
            "max_range_m": round(max_range_m, 2),
            "max_velocity_m_s": round(v_max, 2),
            "velocity_resolution_m_s": round(v_res, 3),
            "chirp_time_us": chirp_time_us,
            "chirps_per_loop": chirps_per_loop,
            "total_chirps": total_chirps,
            "adc_bytes_per_chirp": adc_bytes_per_chirp,
            "lvds_max_bytes_per_chirp": round(max_bytes_per_chirp),
            "lvds_margin_bytes": round(lvds_margin),
            "lvds_bandwidth_ok": lvds_passes,
            "expected_adc_payload_bytes": expected_adc_payload_bytes,
            "expected_transport_bytes": "UNKNOWN — depends on DCA file format, LVDS headers, padding",
            "expected_duration_ms": total_duration_ms,
            "expected_duration_s": round(total_duration_ms / 1000, 2),
            "expected_adc_shape_assumption": f"[{num_frames}, {num_loops * chirps_per_loop}, {num_rx}, {num_adc_samples}]",
        })

        return result

    def compare(self, other: "MmwDemoConfig") -> list[dict]:
        """Compare two configs, returning a list of differences."""
        diffs = []
        self_cmds = {cl.command: cl for cl in self.lines if cl.is_command}
        other_cmds = {cl.command: cl for cl in other.lines if cl.is_command}

        all_cmds = set(self_cmds.keys()) | set(other_cmds.keys())
        for cmd in sorted(all_cmds):
            if cmd not in self_cmds:
                diffs.append({"command": cmd, "change": "added", "new_args": other_cmds[cmd].args})
            elif cmd not in other_cmds:
                diffs.append({"command": cmd, "change": "removed", "old_args": self_cmds[cmd].args})
            elif self_cmds[cmd].args != other_cmds[cmd].args:
                diffs.append({
                    "command": cmd, "change": "modified",
                    "old_args": self_cmds[cmd].args,
                    "new_args": other_cmds[cmd].args,
                })
        return diffs

    def __repr__(self) -> str:
        n_cmds = sum(1 for cl in self.lines if cl.is_command)
        src = Path(self.source_path).name if self.source_path else "<memory>"
        return f"MmwDemoConfig(source={src!r}, commands={n_cmds})"
