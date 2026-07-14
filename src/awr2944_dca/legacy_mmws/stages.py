"""Stage pipeline and allowed-call whitelists for the mmWave Studio backend.

Each stage defines:
- The ar1 calls that belong to it
- Whether execution is currently enabled (allowed_yet)
- A set of calls that are *forbidden* at that stage (for static safety checks)

Safety principle: every call that is not explicitly in a stage's whitelist
is forbidden when generating scripts for that stage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class StageName(str, Enum):
    """Ordered pipeline stages for a full mmWave Studio capture."""

    CONNECTION_ONLY = "connection_only"
    FIRMWARE_LOADING = "firmware_loading"
    DEVICE_BOOT = "device_boot"
    RF_ENABLE_INIT = "rf_enable_init"
    STATIC_CONFIG = "static_config"
    PROFILE_CHIRP_FRAME = "profile_chirp_frame"
    DCA_SETUP = "dca_setup"
    CAPTURE_TRIGGER = "capture_trigger"
    POST_PROCESSING = "post_processing"


@dataclass(frozen=True)
class StageDefinition:
    """Defines one stage of the mmWave Studio pipeline."""

    name: StageName
    display_name: str
    allowed_ar1_calls: frozenset[str]
    allowed_yet: bool
    risk: str  # safe_offline, state_changing, capture_triggering

    def is_call_allowed(self, call_name: str) -> bool:
        """Check whether a specific ar1 call is in this stage's whitelist."""
        return call_name in self.allowed_ar1_calls


# ---------------------------------------------------------------------------
# Stage definitions — ordered pipeline
# ---------------------------------------------------------------------------

STAGES: list[StageDefinition] = [
    StageDefinition(
        name=StageName.CONNECTION_ONLY,
        display_name="Connection-Only",
        allowed_ar1_calls=frozenset({"SOPControl", "Connect", "IsConnected", "Disconnect"}),
        allowed_yet=True,  # <-- only stage currently enabled
        risk="state_changing",
    ),
    StageDefinition(
        name=StageName.FIRMWARE_LOADING,
        display_name="Firmware Loading",
        allowed_ar1_calls=frozenset({"DownloadBSSFw", "DownloadMSSFw"}),
        allowed_yet=False,
        risk="state_changing",
    ),
    StageDefinition(
        name=StageName.DEVICE_BOOT,
        display_name="Device Boot / Power-On",
        allowed_ar1_calls=frozenset({"PowerOn"}),
        allowed_yet=False,
        risk="state_changing",
    ),
    StageDefinition(
        name=StageName.RF_ENABLE_INIT,
        display_name="RF Enable/Init",
        allowed_ar1_calls=frozenset({"RfEnable", "RfInit"}),
        allowed_yet=False,
        risk="state_changing",
    ),
    StageDefinition(
        name=StageName.STATIC_CONFIG,
        display_name="Static ADC/LVDS Config",
        allowed_ar1_calls=frozenset({
            "ChanNAdcConfig", "LPModConfig", "DataPathConfig",
            "LvdsClkConfig", "LVDSLaneConfig",
        }),
        allowed_yet=False,
        risk="safe_with_board_no_rf",
    ),
    StageDefinition(
        name=StageName.PROFILE_CHIRP_FRAME,
        display_name="Profile/Chirp/Frame Config",
        allowed_ar1_calls=frozenset({
            "ProfileConfig", "ChirpConfig", "FrameConfig", "AdvanceFrameConfig",
        }),
        allowed_yet=False,
        risk="safe_with_board_no_rf",
    ),
    StageDefinition(
        name=StageName.DCA_SETUP,
        display_name="DCA1000 Setup",
        allowed_ar1_calls=frozenset({
            "SelectCaptureDevice",
            "CaptureCardConfig_EthInit",
            "CaptureCardConfig_Mode",
            "CaptureCardConfig_PacketDelay",
        }),
        allowed_yet=False,
        risk="state_changing",
    ),
    StageDefinition(
        name=StageName.CAPTURE_TRIGGER,
        display_name="Capture Trigger",
        allowed_ar1_calls=frozenset({
            "CaptureCardConfig_StartRecord", "StartFrame",
        }),
        allowed_yet=False,
        risk="capture_triggering",
    ),
    StageDefinition(
        name=StageName.POST_PROCESSING,
        display_name="Post-Processing",
        allowed_ar1_calls=frozenset({"StartMatlabPostProc"}),
        allowed_yet=False,
        risk="safe_offline",
    ),
]


def get_stage(name: StageName) -> StageDefinition:
    """Look up a stage definition by name."""
    for s in STAGES:
        if s.name == name:
            return s
    raise KeyError(f"Unknown stage: {name}")


def get_all_allowed_calls(stage: StageName) -> frozenset[str]:
    """Return the set of ar1 calls allowed for a specific stage."""
    return get_stage(stage).allowed_ar1_calls


def get_all_forbidden_calls(stage: StageName) -> frozenset[str]:
    """Return every ar1 call that is NOT in this stage's whitelist.

    Constructed from the union of all other stages' allowed calls.
    """
    allowed = get_all_allowed_calls(stage)
    all_calls: set[str] = set()
    for s in STAGES:
        all_calls |= s.allowed_ar1_calls
    return frozenset(all_calls - allowed)


# Convenience: all known ar1 calls across all stages
ALL_KNOWN_CALLS: frozenset[str] = frozenset().union(
    *(s.allowed_ar1_calls for s in STAGES)
)

# Static config ar1 calls mapped to their capture.yaml source fields
STATIC_CONFIG_FIELD_MAP: dict[str, list[str]] = {
    "ChanNAdcConfig": ["hardware.rx_enabled", "hardware.tx_enabled", "adc.bits", "adc.is_complex"],
    "LPModConfig": ["adc.is_complex"],
    "DataPathConfig": ["adc.is_complex", "adc.channel_interleave"],
    "LvdsClkConfig": ["adc.num_lvds_lanes"],
    "LVDSLaneConfig": ["adc.num_lvds_lanes"],
}

# Profile/chirp/frame config ar1 calls mapped to capture.yaml source fields
SENSOR_CONFIG_FIELD_MAP: dict[str, list[str]] = {
    "ProfileConfig": [
        "profile.start_freq_ghz", "profile.slope_mhz_per_us",
        "profile.idle_time_us", "profile.ramp_end_time_us",
        "profile.sample_rate_ksps", "adc.samples_per_chirp",
    ],
    "ChirpConfig": ["hardware.tx_enabled"],
    "FrameConfig": [
        "frame.chirps_per_frame", "frame.num_frames", "frame.frame_period_ms",
    ],
}
