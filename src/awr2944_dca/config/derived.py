"""Derived radar parameters computed from a RadarConfig.

All formulas are sourced from TI reference documents:
- mmwaveSensing-FMCW-offlineviewing_0.pdf (TI FMCW offline viewing deck)
- SWRA581B ADC raw data capture app report

Formula references are annotated inline.  When a formula cannot be found in
the provided TI documents, it is marked TODO or "estimate."
"""

from __future__ import annotations

from dataclasses import dataclass

from awr2944_dca.config.schema import AntennaMode, RadarConfig

# Speed of light (m/s)
C_MPS = 299_792_458.0


@dataclass(frozen=True)
class DerivedParams:
    """Derived radar performance parameters.

    Attributes marked with 'estimate' require further validation
    (e.g., exact chirp timing with TDM-MIMO sequencing).
    """

    # File expectations
    expected_file_size_bytes: int

    # RF / chirp
    bandwidth_mhz: float
    wavelength_m: float
    chirp_period_us: float

    # Range — Ref: TI FMCW deck: d_res = c / (2B), d_max = Fs·c / (2S)
    range_resolution_m: float
    max_range_m: float

    # Velocity — Ref: TI FMCW deck: v_max = λ / (4Tc), v_res = λ / (2Tf)
    # These are estimates: TDM-MIMO and multi-TX sequencing affect Tc.
    max_velocity_mps: float  # estimate
    velocity_resolution_mps: float  # estimate

    # Virtual antennas (TDM-MIMO)
    num_virtual_antennas: int  # estimate — requires validated array geometry

    # Timing
    capture_duration_s: float
    expected_disk_mb: float

    # Labels for uncertain quantities
    velocity_is_estimate: bool = True
    angle_is_estimate: bool = True


def compute_derived(cfg: RadarConfig) -> DerivedParams:
    """Compute derived radar parameters from a validated config.

    Range formulas (from TI FMCW offline viewing deck):
        d_res = c / (2 * B)              where B = bandwidth in Hz
        d_max = Fs * c / (2 * S)         where Fs = sample rate in Hz, S = slope in Hz/s

    Velocity formulas (from TI FMCW deck, labeled as estimates):
        v_max = λ / (4 * Tc)             where Tc = chirp period
        v_res = λ / (2 * Tf)             where Tf = frame active time

    Note: In TDM-MIMO mode, the effective Tc for velocity is num_tx × chirp_period
    because each TX fires sequentially.  This is applied as a correction factor.
    """
    # --- Bandwidth ---
    bandwidth_mhz = cfg.profile.bandwidth_mhz
    bandwidth_hz = bandwidth_mhz * 1e6

    # --- Wavelength ---
    freq_hz = cfg.profile.start_freq_ghz * 1e9
    wavelength_m = C_MPS / freq_hz

    # --- Chirp timing ---
    chirp_period_us = cfg.profile.chirp_period_us
    chirp_period_s = chirp_period_us * 1e-6

    # For TDM-MIMO, effective chirp period is num_tx × single chirp period
    num_tx = cfg.hardware.num_tx
    if cfg.hardware.antenna_mode == AntennaMode.TDM_MIMO:
        effective_chirp_period_s = num_tx * chirp_period_s
    else:
        effective_chirp_period_s = chirp_period_s

    # --- Range ---
    # d_res = c / (2B)  — TI FMCW deck
    range_resolution_m = C_MPS / (2.0 * bandwidth_hz)

    # d_max = Fs * c / (2S)  — TI FMCW deck
    sample_rate_hz = cfg.profile.sample_rate_ksps * 1e3
    slope_hz_per_s = cfg.profile.slope_mhz_per_us * 1e12  # MHz/μs → Hz/s
    max_range_m = sample_rate_hz * C_MPS / (2.0 * slope_hz_per_s)

    # --- Velocity (estimates) ---
    # v_max = λ / (4 * Tc_eff)  — TI FMCW deck
    max_velocity_mps = wavelength_m / (4.0 * effective_chirp_period_s)

    # v_res = λ / (2 * Tf)  where Tf = chirps_per_frame × Tc_eff
    # For TDM-MIMO with N_TX transmitters and chirps_per_frame total chirps,
    # the number of Doppler chirps per TX is chirps_per_frame / num_tx.
    if cfg.hardware.antenna_mode == AntennaMode.TDM_MIMO:
        doppler_chirps = cfg.frame.chirps_per_frame // num_tx
    else:
        doppler_chirps = cfg.frame.chirps_per_frame
    frame_active_time_s = doppler_chirps * effective_chirp_period_s
    velocity_resolution_mps = wavelength_m / (2.0 * frame_active_time_s)

    # --- Virtual antennas ---
    num_rx = cfg.hardware.num_rx
    if cfg.hardware.antenna_mode == AntennaMode.TDM_MIMO:
        num_virtual_antennas = num_tx * num_rx
    else:
        num_virtual_antennas = num_rx

    # --- Expected file size ---
    # Delegate to layout-aware computation.
    # Generic formula: samples × rx × chirps × frames × bytes_per_sample_per_rx
    expected_bytes = (
        cfg.adc.samples_per_chirp
        * num_rx
        * cfg.frame.chirps_per_frame
        * cfg.frame.num_frames
        * cfg.adc.bytes_per_sample_per_rx
    )

    # --- Timing ---
    frame_period_s = cfg.frame.frame_period_ms * 1e-3
    capture_duration_s = cfg.frame.num_frames * frame_period_s
    expected_disk_mb = expected_bytes / (1024.0 * 1024.0)

    return DerivedParams(
        expected_file_size_bytes=expected_bytes,
        bandwidth_mhz=bandwidth_mhz,
        wavelength_m=wavelength_m,
        chirp_period_us=chirp_period_us,
        range_resolution_m=range_resolution_m,
        max_range_m=max_range_m,
        max_velocity_mps=max_velocity_mps,
        velocity_resolution_mps=velocity_resolution_mps,
        num_virtual_antennas=num_virtual_antennas,
        capture_duration_s=capture_duration_s,
        expected_disk_mb=expected_disk_mb,
    )
