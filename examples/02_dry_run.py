"""Example 02: Dry-run a capture configuration.

Shows how to load a built-in profile, resolve the configuration,
and inspect the derived parameters without touching hardware.
"""

from awr2944_dca.lab import RadarProject
from awr2944_dca.api.profile import RadarProfile

# Load the built-in smoke test profile
profile = RadarProfile.from_preset("smoke_v1")

print(f"Profile: {profile.name}")
print(f"ADC samples/chirp: {profile.adc_samples}")
print(f"Chirps/frame: {profile.chirps_per_frame}")
print(f"Requested frames: {profile.num_frames}")
print()

# Perform a dry-run resolve (no hardware needed)
resolved = profile.dry_run(frames=8, guard_frames=1)

print("--- Resolved parameters ---")
print(f"  Total frames (with guard): {resolved.total_frames}")
print(f"  Canonical frames: {resolved.canonical_frames}")
print(f"  Expected raw bytes: {resolved.expected_bytes:,}")
