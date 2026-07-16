"""Public structured profiles for AWR2944."""

from __future__ import annotations
import dataclasses
from typing import Any
import json

class ProfileCompilationNotSupported(Exception):
    """Raised when a profile variant cannot be compiled by the C1 compiler."""
    def __init__(self, message: str, unsupported_fields: list[dict[str, Any]]):
        super().__init__(message)
        self.unsupported_fields = unsupported_fields

@dataclasses.dataclass(frozen=True)
class ChannelConfig:
    rx_mask: int = 15
    tx_mask: int = 7

@dataclasses.dataclass(frozen=True)
class AdcConfig:
    bits: int = 16
    sample_format: str = "real_int16"
    cube_layout: str = "frame_chirp_rx_sample"

@dataclasses.dataclass(frozen=True)
class RfProfileConfig:
    start_frequency_ghz: float = 77.0
    idle_time_us: float = 100.0
    adc_start_time_us: float = 6.0
    ramp_end_time_us: float = 60.0
    slope_mhz_per_us: float = 29.982

@dataclasses.dataclass(frozen=True)
class AdcSamplingConfig:
    samples: int = 256
    sample_rate_msps: float = 10.0

@dataclasses.dataclass(frozen=True)
class ChirpConfig:
    tx_enable_mask: int = 3

@dataclasses.dataclass(frozen=True)
class FrameConfig:
    chirps_per_frame: int = 128
    frame_count: int = 8
    frame_period_ms: float = 40.0

@dataclasses.dataclass(frozen=True)
class LvdsConfig:
    lanes: int = 4
    format: int = 1

@dataclasses.dataclass(frozen=True)
class MonitoringConfig:
    enabled: bool = True

@dataclasses.dataclass(frozen=True)
class CalibrationConfig:
    enabled: bool = True

@dataclasses.dataclass
class ProfileValidationReport:
    success: bool
    errors: list[str]
    warnings: list[str]
    derived: dict[str, Any]

    def summary(self) -> str:
        lines = []
        if self.success:
            lines.append("Profile valid.")
        else:
            lines.append("Profile invalid.")
            for e in self.errors:
                lines.append(f"ERROR: {e}")
        for w in self.warnings:
            lines.append(f"WARNING: {w}")
        return "\n".join(lines)

    def raise_for_errors(self) -> None:
        if not self.success:
            raise ValueError(f"Profile validation failed:\n" + "\n".join(self.errors))

@dataclasses.dataclass(frozen=True)
class RadarProfile:
    """Canonical public structured profile for AWR2944 configurations."""
    name: str = "custom"
    description: str = ""
    channel: ChannelConfig = dataclasses.field(default_factory=ChannelConfig)
    adc: AdcConfig = dataclasses.field(default_factory=AdcConfig)
    rf: RfProfileConfig = dataclasses.field(default_factory=RfProfileConfig)
    sampling: AdcSamplingConfig = dataclasses.field(default_factory=AdcSamplingConfig)
    chirp: ChirpConfig = dataclasses.field(default_factory=ChirpConfig)
    frame: FrameConfig = dataclasses.field(default_factory=FrameConfig)
    lvds: LvdsConfig = dataclasses.field(default_factory=LvdsConfig)
    monitoring: MonitoringConfig = dataclasses.field(default_factory=MonitoringConfig)
    calibration: CalibrationConfig = dataclasses.field(default_factory=CalibrationConfig)

    def with_frame(self, **kwargs) -> 'RadarProfile':
        new_frame = dataclasses.replace(self.frame, **kwargs)
        return dataclasses.replace(self, frame=new_frame)

    def with_rf(self, **kwargs) -> 'RadarProfile':
        new_rf = dataclasses.replace(self.rf, **kwargs)
        return dataclasses.replace(self, rf=new_rf)

    def with_sampling(self, **kwargs) -> 'RadarProfile':
        new_sampling = dataclasses.replace(self.sampling, **kwargs)
        return dataclasses.replace(self, sampling=new_sampling)

    def rename(self, name: str, description: str = "") -> 'RadarProfile':
        return dataclasses.replace(self, name=name, description=description)

    @property
    def adc_start_time_s(self) -> float:
        """ADC start time in SI seconds, derived from rf.adc_start_time_us.
        
        Note: DspRadarProfile does not carry this field, so to_dsp_profile()
        does not include it. It is exposed here for waveform timing analysis
        and will be consumed by the Phase C2 generic compiler.
        """
        return self.rf.adc_start_time_us * 1e-6

    @classmethod
    def smoke_v1(cls) -> 'RadarProfile':
        """The canonical smoke_v1 structured profile defaults."""
        return cls(name="smoke_v1", description="Default validated capture profile")
        
    def to_dsp_profile(self) -> Any:
        """Converts to the internal dsp.config.RadarProfile.
        
        This maps only the fields required by the parser, DSP, and viewer.
        It explicitly drops channel, LVDS, monitoring, and calibration configurations
        that are not required for signal processing.
        """
        from awr2944_dca.dsp.config import RadarProfile as DspRadarProfile
        
        def count_bits(n: int) -> int:
            return bin(n).count('1')
        
        # User requested exact mapping list (adc_start_time_s was listed, but DspRadarProfile lacks it)
        # We map what DspRadarProfile expects exactly.
        return DspRadarProfile(
            start_frequency_hz=self.rf.start_frequency_ghz * 1e9,
            slope_hz_per_s=self.rf.slope_mhz_per_us * 1e12,
            adc_sample_rate_hz=self.sampling.sample_rate_msps * 1e6,
            adc_samples=self.sampling.samples,
            idle_time_s=self.rf.idle_time_us * 1e-6,
            ramp_end_time_s=self.rf.ramp_end_time_us * 1e-6,
            chirps_per_frame=self.frame.chirps_per_frame,
            frame_count=self.frame.frame_count,
            frame_period_s=self.frame.frame_period_ms * 1e-3,
            rx_count=count_bits(self.channel.rx_mask),
            tx_mask=self.chirp.tx_enable_mask,
            sample_format=self.adc.sample_format,
            cube_layout=self.adc.cube_layout
        )
        
    def byte_plan(self, guard_frames: int = 0) -> dict[str, int]:
        """Calculates expected logical, canonical, and native byte counts."""
        from awr2944_dca.awr2944_adc import expected_raw_dca_bytes, active_payload_bytes
        
        internal = self.to_dsp_profile()
        # We provide the total captures frame count including guard frames to the calculator
        total_frames = self.frame.frame_count + guard_frames
        
        logical = internal.adc_samples * internal.rx_count * internal.chirps_per_frame * total_frames * 2
        
        # Native bytes is typically the canonical + packet overhead
        native = expected_raw_dca_bytes(
            total_frames,
            internal.chirps_per_frame,
            internal.rx_count,
            internal.adc_samples
        )
        canonical = active_payload_bytes(
            total_frames,
            internal.chirps_per_frame,
            internal.rx_count,
            internal.adc_samples
        )
        
        return {
            "logical_bytes": logical,
            "native_bytes": native,
            "canonical_bytes": canonical,
        }

    def validate(self) -> ProfileValidationReport:
        errors = []
        warnings = []
        
        if self.sampling.samples <= 0:
            errors.append("adc.samples must be positive")
        if self.frame.frame_count <= 0:
            errors.append("frame.frame_count must be positive")
        
        # Check TDM-MIMO separation capability warning
        # If tx_enable_mask has multiple bits set simultaneously
        tx_bits = bin(self.chirp.tx_enable_mask).count('1')
        if tx_bits > 1:
            warnings.append("Simultaneous multiple-TX operation prevents separable TDM-MIMO angle estimation.")
            
        # Check C1 compiler compatibility (this is just a warning in validate, error in to_sdk_cli)
        smoke = self.smoke_v1()
        if (self.channel != smoke.channel or self.adc != smoke.adc or 
            self.rf != smoke.rf or self.sampling != smoke.sampling or 
            self.chirp != smoke.chirp or self.lvds != smoke.lvds or 
            self.monitoring != smoke.monitoring or self.calibration != smoke.calibration or
            self.frame.frame_period_ms != smoke.frame.frame_period_ms):
            warnings.append("Profile compiles only through smoke-compatible mode (some overrides are unsupported in C1).")

        derived = {}
        if self.sampling.samples > 0 and self.sampling.sample_rate_msps > 0 and self.rf.slope_mhz_per_us > 0:
            internal = self.to_dsp_profile()
            derived = {
                "bandwidth_mhz": internal.sampled_bandwidth_hz / 1e6,
                "range_resolution_m": internal.range_resolution_m,
                "max_unambiguous_range_m": internal.max_unambiguous_range_m,
                "chirp_duration_us": internal.chirp_repetition_interval_s * 1e6,
                "frame_duration_ms": internal.active_frame_duration_s * 1e3,
            }
            
            # Frame period consistency
            if derived["frame_duration_ms"] > self.frame.frame_period_ms:
                errors.append(f"Frame period ({self.frame.frame_period_ms}ms) is too short for active frame duration ({derived['frame_duration_ms']:.2f}ms).")
            
        success = len(errors) == 0
        return ProfileValidationReport(
            success=success,
            errors=errors,
            warnings=warnings,
            derived=derived
        )
        
    def to_sdk_cli(self) -> list[str]:
        smoke = self.smoke_v1()
        
        unsupported = []
        
        if self.channel != smoke.channel:
            unsupported.append({"path": "channel", "expected": smoke.channel, "actual": self.channel})
        if self.adc != smoke.adc:
            unsupported.append({"path": "adc", "expected": smoke.adc, "actual": self.adc})
        if self.rf != smoke.rf:
            unsupported.append({"path": "rf", "expected": smoke.rf, "actual": self.rf})
        if self.sampling != smoke.sampling:
            unsupported.append({"path": "sampling", "expected": smoke.sampling, "actual": self.sampling})
        if self.chirp != smoke.chirp:
            unsupported.append({"path": "chirp", "expected": smoke.chirp, "actual": self.chirp})
        if self.lvds != smoke.lvds:
            unsupported.append({"path": "lvds", "expected": smoke.lvds, "actual": self.lvds})
        if self.monitoring != smoke.monitoring:
            unsupported.append({"path": "monitoring", "expected": smoke.monitoring, "actual": self.monitoring})
        if self.calibration != smoke.calibration:
            unsupported.append({"path": "calibration", "expected": smoke.calibration, "actual": self.calibration})
        if self.frame.frame_period_ms != smoke.frame.frame_period_ms:
            unsupported.append({"path": "frame.frame_period_ms", "expected": smoke.frame.frame_period_ms, "actual": self.frame.frame_period_ms})
            
        if unsupported:
            raise ProfileCompilationNotSupported(
                "Profile relies on unsupported C1 configurations. Only smoke-compatible capture-size variants are supported.",
                unsupported_fields=unsupported
            )
            
        from awr2944_dca.sdk_cli_profile import build_smoke_v1_cli
        return build_smoke_v1_cli(
            frames=self.frame.frame_count,
            chirps_per_frame=self.frame.chirps_per_frame
        )
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "channel": dataclasses.asdict(self.channel),
            "adc": dataclasses.asdict(self.adc),
            "rf": dataclasses.asdict(self.rf),
            "sampling": dataclasses.asdict(self.sampling),
            "chirp": dataclasses.asdict(self.chirp),
            "frame": dataclasses.asdict(self.frame),
            "lvds": dataclasses.asdict(self.lvds),
            "monitoring": dataclasses.asdict(self.monitoring),
            "calibration": dataclasses.asdict(self.calibration),
        }
        
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'RadarProfile':
        d = dict(data)
        
        # Provide fallback to smoke_v1 defaults for minimal schema compatibility
        smoke = cls.smoke_v1()
        
        name = d.get("name", smoke.name)
        desc = d.get("description", smoke.description)
        
        chan = ChannelConfig(**d.get("channel", dataclasses.asdict(smoke.channel)))
        adc = AdcConfig(**d.get("adc", dataclasses.asdict(smoke.adc)))
        rf = RfProfileConfig(**d.get("rf", dataclasses.asdict(smoke.rf)))
        samp = AdcSamplingConfig(**d.get("sampling", dataclasses.asdict(smoke.sampling)))
        chirp = ChirpConfig(**d.get("chirp", dataclasses.asdict(smoke.chirp)))
        frame = FrameConfig(**d.get("frame", dataclasses.asdict(smoke.frame)))
        lvds = LvdsConfig(**d.get("lvds", dataclasses.asdict(smoke.lvds)))
        mon = MonitoringConfig(**d.get("monitoring", dataclasses.asdict(smoke.monitoring)))
        cal = CalibrationConfig(**d.get("calibration", dataclasses.asdict(smoke.calibration)))
        
        return cls(
            name=name,
            description=desc,
            channel=chan,
            adc=adc,
            rf=rf,
            sampling=samp,
            chirp=chirp,
            frame=frame,
            lvds=lvds,
            monitoring=mon,
            calibration=cal
        )
        
    def to_toml(self) -> str:
        # We serialize as dict and then dump to TOML
        import tomli_w
        data = self.to_dict()
        data["schema_version"] = "1.0"
        return tomli_w.dumps(data)
        
    @classmethod
    def from_toml(cls, toml_str: str) -> 'RadarProfile':
        import tomllib
        data = tomllib.loads(toml_str)
        return cls.from_dict(data)
