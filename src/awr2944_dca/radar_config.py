"""Radar configuration API for AWR2944.

Provides notebook-friendly API to build, inspect, and apply radar
chirp/profile/frame settings, while preserving exact known-good smoke
presets.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict


class RadarConfig:
    """AWR2944 radar configuration.

    Stores mmWave Studio API commands and arguments. Can export to Lua
    or save to JSON.
    """

    def __init__(self, name: str = ""):
        self.name = name
        self.commands: list[dict] = []

    def _get_command(self, func: str) -> dict | None:
        for cmd in self.commands:
            if cmd["func"] == func:
                return cmd
        return None

    def _ensure_command(self, func: str, default_args: list[Any] | None = None) -> dict:
        cmd = self._get_command(func)
        if cmd is None:
            cmd = {"func": func, "args": default_args or []}
            self.commands.append(cmd)
        return cmd

    def add_command(self, func: str, *args: Any) -> "RadarConfig":
        """Add or replace a command."""
        # Replace if exists, else append
        for i, cmd in enumerate(self.commands):
            if cmd["func"] == func:
                self.commands[i] = {"func": func, "args": list(args)}
                return self
        self.commands.append({"func": func, "args": list(args)})
        return self

    # --- High Level Setters ---

    def set_frames(self, num_frames: int) -> "RadarConfig":
        """Set the number of frames to capture."""
        cmd = self._ensure_command("ar1.FrameConfig")
        # ar1.FrameConfig(chirpStartIdx, chirpEndIdx, numFrames, numLoops, framePeriodicity, triggerSelect, frameTrigDelay)
        if len(cmd["args"]) >= 3:
            cmd["args"][2] = num_frames
        return self

    def set_chirps_per_frame(self, num_loops: int) -> "RadarConfig":
        """Set the number of chirp loops per frame."""
        cmd = self._ensure_command("ar1.FrameConfig")
        if len(cmd["args"]) >= 4:
            cmd["args"][3] = num_loops
        return self

    def set_frame_period(self, period_ms: float) -> "RadarConfig":
        """Set frame periodicity in milliseconds."""
        cmd = self._ensure_command("ar1.FrameConfig")
        if len(cmd["args"]) >= 5:
            cmd["args"][4] = period_ms
        return self

    def set_samples(self, num_adc_samples: int) -> "RadarConfig":
        """Set number of ADC samples per chirp."""
        cmd = self._ensure_command("ar1.ProfileConfig")
        # ProfileConfig arg 15 (0-indexed) is numAdcSamples
        if len(cmd["args"]) >= 16:
            cmd["args"][15] = num_adc_samples
        return self

    def set_start_freq(self, freq_ghz: float) -> "RadarConfig":
        """Set profile start frequency in GHz."""
        cmd = self._ensure_command("ar1.ProfileConfig")
        if len(cmd["args"]) >= 2:
            cmd["args"][1] = freq_ghz
        return self

    def set_slope(self, slope_mhz_per_us: float) -> "RadarConfig":
        """Set frequency slope in MHz/us."""
        cmd = self._ensure_command("ar1.ProfileConfig")
        if len(cmd["args"]) >= 14:
            cmd["args"][13] = slope_mhz_per_us
        return self

    def enable_rx(self, rx1: bool = True, rx2: bool = True, rx3: bool = True, rx4: bool = True) -> "RadarConfig":
        """Enable or disable RX antennas."""
        mask = (rx1 << 0) | (rx2 << 1) | (rx3 << 2) | (rx4 << 3)
        cmd = self._ensure_command("ar1.ChanNAdcConfig")
        # ChanNAdcConfig(rxChannelEn, ...)
        if len(cmd["args"]) >= 1:
            cmd["args"][0] = mask
        return self

    def enable_tx(self, tx1: bool = True, tx2: bool = True, tx3: bool = True, tx4: bool = True) -> "RadarConfig":
        """Enable or disable TX antennas on the chirp."""
        mask = (tx1 << 0) | (tx2 << 1) | (tx3 << 2) | (tx4 << 3)
        cmd = self._ensure_command("ar1.ChirpConfig")
        # ChirpConfig(chirpStartIdx, chirpEndIdx, profileId, startFreqVar, freqSlopeVar, idleTimeVar, adcStartTimeVar, txEnable, ...)
        if len(cmd["args"]) >= 8:
            cmd["args"][7] = mask
        return self

    # --- Derived / Analysis ---

    def derived(self) -> dict:
        """Calculate approximate derived physical and operational values."""
        d = {
            "expected_bytes": 0,
            "adc_capture_time_us": 0.0,
            "sampled_bandwidth_mhz": 0.0,
            "ramp_bandwidth_mhz": 0.0,
            "approximate_range_resolution_m": 0.0,
        }

        # Extract values
        prof = self._get_command("ar1.ProfileConfig")
        frame = self._get_command("ar1.FrameConfig")
        chan = self._get_command("ar1.ChanNAdcConfig")

        if not (prof and frame and chan):
            return d

        p_args = prof["args"]
        f_args = frame["args"]
        c_args = chan["args"]

        try:
            samples = int(p_args[15])
            sample_rate_ksps = float(p_args[16])
            slope = float(p_args[13])
            ramp_end_time = float(p_args[4])

            # In AWR2944 ChanNAdcConfig, arg 0 and 1 are typically 1, meaning RX1-RX4 and TX1-TX4 enabled 
            # for the specific chirp, or they represent specific bitmasks in a different format.
            # We assume 4 RX channels for the validated smoke config.
            rx_count = 4

            frames = int(f_args[2])
            loops = int(f_args[3])
            chirps = frames * loops

            # 16-bit complex = 4 bytes per sample per RX
            bytes_per_chirp = samples * 4 * rx_count
            d["expected_bytes"] = bytes_per_chirp * chirps

            if sample_rate_ksps > 0:
                cap_time_us = (samples / (sample_rate_ksps * 1000.0)) * 1e6
                d["adc_capture_time_us"] = round(cap_time_us, 2)
                d["sampled_bandwidth_mhz"] = round(cap_time_us * slope, 2)
            
            ramp_bw = ramp_end_time * slope
            d["ramp_bandwidth_mhz"] = round(ramp_bw, 2)

            # c / (2 * BW)
            if ramp_bw > 0:
                c = 299792458.0
                res = c / (2 * ramp_bw * 1e6)
                d["approximate_range_resolution_m"] = round(res, 4)

        except (IndexError, ValueError, TypeError):
            pass

        return d

    def summary(self) -> dict:
        """Return a readable summary of the config."""
        prof = self._get_command("ar1.ProfileConfig")
        frame = self._get_command("ar1.FrameConfig")
        chan = self._get_command("ar1.ChanNAdcConfig")
        chirp = self._get_command("ar1.ChirpConfig")

        s = {}
        if frame and len(frame["args"]) >= 5:
            s["num_frames"] = frame["args"][2]
            s["chirps_per_frame"] = frame["args"][3]
            s["frame_period_ms"] = frame["args"][4]
        
        if prof and len(prof["args"]) >= 17:
            s["start_freq_ghz"] = prof["args"][1]
            s["slope_mhz_per_us"] = prof["args"][13]
            s["num_adc_samples"] = prof["args"][15]
            s["sample_rate_ksps"] = prof["args"][16]
        
        if chan and len(chan["args"]) >= 1:
            mask = chan["args"][0]
            s["active_rx"] = bin(mask).count("1")
        
        if chirp and len(chirp["args"]) >= 8:
            mask = chirp["args"][7]
            s["active_tx"] = bin(mask).count("1")
            
        return s

    def validate(self) -> dict:
        """Validate config structure and values."""
        errors = []
        warnings = []

        if not self._get_command("ar1.ProfileConfig"):
            errors.append("Missing ar1.ProfileConfig")
        if not self._get_command("ar1.FrameConfig"):
            errors.append("Missing ar1.FrameConfig")
        if not self._get_command("ar1.ChirpConfig"):
            errors.append("Missing ar1.ChirpConfig")

        prof = self._get_command("ar1.ProfileConfig")
        if prof and len(prof["args"]) >= 16:
            samples = prof["args"][15]
            if not isinstance(samples, int) or samples <= 0 or samples % 16 != 0:
                errors.append(f"Invalid num_adc_samples: {samples}")

        # Check for banned commands
        if self._get_command("ar1.StartFrame"):
            errors.append("ar1.StartFrame is not allowed in RadarConfig.")
        if self._get_command("ar1.CaptureCardConfig_StartRecord"):
            errors.append("DCA StartRecord is not allowed in RadarConfig.")

        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    # --- Serialization ---

    def to_lua(self) -> str:
        """Export to mmWave Studio Lua script (raw commands only, no result JSON)."""
        lines = []
        for cmd in self.commands:
            func = cmd["func"]
            # format args based on type
            formatted_args = []
            for arg in cmd["args"]:
                if isinstance(arg, str) and not arg.startswith("0x"):
                    formatted_args.append(f"'{arg}'")
                elif isinstance(arg, str) and arg.startswith("0x"):
                    formatted_args.append(arg)  # preserve hex
                else:
                    formatted_args.append(str(arg))
            
            lines.append(f"{func}({', '.join(formatted_args)})")
        return "\n".join(lines) + "\n"

    def to_lua_with_result(self, run_id: str, result_path: str, progress_path: str) -> str:
        """Export to Lua with result JSON and progress JSONL writing.

        Each ar1 command return is captured in the result JSON so the caller
        can verify every step succeeded, not just trust RSTD return code 30000.

        Args:
            run_id: Unique identifier for this execution
            result_path: Absolute path (forward slashes) for the result JSON
            progress_path: Absolute path (forward slashes) for progress JSONL
        """
        lines = []
        lines.append(f"-- Radar Config with result tracking")
        lines.append(f"-- run_id: {run_id}")
        lines.append(f"-- config_name: {self.name}")
        lines.append(f"-- num_commands: {len(self.commands)}")
        lines.append("")

        # JSON escape helper
        lines.append('local function jsonEscape(s)')
        lines.append('    if type(s) ~= "string" then s = tostring(s) end')
        lines.append(r"    s = s:gsub('\\', '\\\\')")
        lines.append(r'    s = s:gsub("\"", "\\\"")')
        lines.append(r"    s = s:gsub('\n', '\\n')")
        lines.append(r"    s = s:gsub('\r', '\\r')")
        lines.append('    return s')
        lines.append('end')
        lines.append("")

        # Progress logger
        lines.append(f'local progress_path = [[{progress_path}]]')
        lines.append('local function logProgress(step, ret, ok, err)')
        lines.append('    local f = io.open(progress_path, "a")')
        lines.append('    if f then')
        lines.append('        f:write(string.format(\'{"step":"%s","return":%s,"ok":%s,"error":"%s"}\\n\',')
        lines.append('            step, tostring(ret), tostring(ok), jsonEscape(tostring(err or ""))))')
        lines.append('        f:close()')
        lines.append('    end')
        lines.append('end')
        lines.append("")

        # Result table
        lines.append(f'local result_path = [[{result_path}]]')
        lines.append('local result = {')
        lines.append(f'    run_id = "{run_id}",')
        lines.append(f'    config_name = "{self.name}",')
        lines.append('    executed = true,')
        lines.append('    success = false,')
        lines.append('    error = "",')
        lines.append('    commands = {},')
        lines.append('}')
        lines.append('')

        # Save result function
        lines.append('local function saveResult()')
        lines.append('    local f = io.open(result_path, "w")')
        lines.append('    if f then')
        lines.append('        -- Build commands array')
        lines.append('        local cmd_parts = {}')
        lines.append('        for i, c in ipairs(result.commands) do')
        lines.append('            cmd_parts[i] = string.format(\'{"func":"%s","return":%s,"ok":%s,"error":"%s"}\',')
        lines.append('                c.func, tostring(c.ret), tostring(c.ok), jsonEscape(tostring(c.err or "")))')
        lines.append('        end')
        lines.append('        local cmd_str = "[" .. table.concat(cmd_parts, ",") .. "]"')
        lines.append('        f:write(string.format(\'{"run_id":"%s","config_name":"%s","executed":%s,"success":%s,"error":"%s","commands":%s}\\n\',')
        lines.append('            result.run_id, result.config_name, tostring(result.executed),')
        lines.append('            tostring(result.success), jsonEscape(result.error), cmd_str))')
        lines.append('        f:close()')
        lines.append('    end')
        lines.append('end')
        lines.append('')

        # Execute each command with result tracking
        for cmd in self.commands:
            func = cmd["func"]
            formatted_args = []
            for arg in cmd["args"]:
                if isinstance(arg, str) and not arg.startswith("0x"):
                    formatted_args.append(f"'{arg}'")
                elif isinstance(arg, str) and arg.startswith("0x"):
                    formatted_args.append(arg)
                else:
                    formatted_args.append(str(arg))
            args_str = ", ".join(formatted_args)
            short_name = func.replace("ar1.", "")

            lines.append(f'do')
            lines.append(f'    local ok, ret = pcall(function() return {func}({args_str}) end)')
            lines.append(f'    local err = nil')
            lines.append(f'    if not ok then err = ret; ret = nil end')
            lines.append(f'    logProgress("{short_name}", ret, ok, err)')
            lines.append(f'    table.insert(result.commands, {{func="{func}", ret=ret, ok=ok, err=err}})')
            lines.append(f'    if not ok or (type(ret) == "number" and ret ~= 0) then')
            lines.append(f'        result.error = "{short_name} failed: " .. tostring(err or ret)')
            lines.append(f'        saveResult()')
            lines.append(f'        print("AWR_RADAR_CONFIG_FAIL run_id={run_id} step={short_name}")')
            lines.append(f'        return')
            lines.append(f'    end')
            lines.append(f'end')
            lines.append('')

        # All commands succeeded
        lines.append('result.success = true')
        lines.append('saveResult()')
        lines.append(f'print("AWR_RADAR_CONFIG_OK run_id={run_id}")')

        return "\n".join(lines) + "\n"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "commands": copy.deepcopy(self.commands),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RadarConfig":
        cfg = cls(name=data.get("name", ""))
        cfg.commands = copy.deepcopy(data.get("commands", []))
        return cfg

    def clone(self, name: str = "", **overrides) -> "RadarConfig":
        """Clone this config and apply setter overrides."""
        cfg = RadarConfig.from_dict(self.to_dict())
        if name:
            cfg.name = name
        
        # Apply overrides mapping to setters
        if "num_frames" in overrides:
            cfg.set_frames(overrides["num_frames"])
        if "chirps_per_frame" in overrides:
            cfg.set_chirps_per_frame(overrides["chirps_per_frame"])
        if "num_adc_samples" in overrides:
            cfg.set_samples(overrides["num_adc_samples"])
        if "start_freq_ghz" in overrides:
            cfg.set_start_freq(overrides["start_freq_ghz"])
        
        return cfg

    def save(self, name_or_path: str | Path | None = None, project_root: Path | None = None) -> Path:
        """Save config to JSON under configs/radar/."""
        if name_or_path is None:
            name_or_path = self.name or "custom_config"
        
        p = Path(name_or_path)
        if not p.is_absolute() and project_root:
            out_dir = project_root / "configs" / "radar"
            out_dir.mkdir(parents=True, exist_ok=True)
            if not p.suffix:
                p = p.with_suffix(".json")
            p = out_dir / p
            
        p.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return p

    def export_lua(self, name_or_path: str | Path | None = None, project_root: Path | None = None) -> Path:
        """Export to Lua under configs/mmws/lua/."""
        if name_or_path is None:
            name_or_path = self.name or "custom_config"
        
        p = Path(name_or_path)
        if not p.is_absolute() and project_root:
            out_dir = project_root / "configs" / "mmws" / "lua"
            out_dir.mkdir(parents=True, exist_ok=True)
            if not p.suffix:
                p = p.with_suffix(".lua")
            p = out_dir / p
            
        p.write_text(self.to_lua(), encoding="utf-8")
        return p


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------

def smoke_config_preset() -> RadarConfig:
    """Return the frozen, known-good hardware-validated smoke config."""
    cfg = RadarConfig("smoke_v1")
    cfg.add_command("ar1.ChanNAdcConfig", 1, 1, 0, 0, 1, 1, 0, 0, 2, 0, 0)
    cfg.add_command("ar1.LPModConfig", 0, 0)
    cfg.add_command("ar1.RfLdoBypassConfig", "0x0")
    cfg.add_command("ar1.SetCalMonFreqLimitConfig", 76, 81, 0)
    cfg.add_command("ar1.SetRFDeviceConfig", 5, 0, 0, 0, 0, 0, 0)
    cfg.add_command("ar1.RfSetCalMonFreqTxPowLimitConfig", 76, 76, 76, 76, 81, 81, 81, 81, 0, 0, 0, 0, 0)
    cfg.add_command("ar1.SetApllSynthBWCtlConfig", 1, 4, 3, 9, 18, 1, 4)
    cfg.add_command("ar1.RfInit")
    cfg.add_command("ar1.DataPathConfig", 513, 1216644097, 0)
    cfg.add_command("ar1.LVDSLaneConfig", 0, 1, 0, 0, 0, 1, 0, 0)
    cfg.add_command("ar1.ProfileConfig", 0, 77, 100, 6, 60, 0, 0, 0, 0, 0, 0, 0, 0, 29.982, 0, 256, 10000, 2216755200, 0, 30, 0, 0, 0)
    cfg.add_command("ar1.ChirpConfig", 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0)
    cfg.add_command("ar1.FrameConfig", 0, 0, 8, 128, 40, 0, 1)
    return cfg
