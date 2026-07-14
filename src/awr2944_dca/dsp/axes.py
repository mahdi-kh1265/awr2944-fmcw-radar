"""Physical axis construction for range and velocity.

Range axis for real-ADC rfft:
    f_b[k] = k * fs / NFFT
    R[k]   = c * f_b[k] / (2 * S) = c * k * fs / (2 * S * NFFT)

Velocity axis for Doppler FFT:
    f_d[k] = (k - N/2) * (1 / (N * Tc))     after fftshift
    v[k]   = lambda * f_d[k] / 2

All axes in SI units (meters, m/s).
"""

from __future__ import annotations

import numpy as np

from awr2944_dca.dsp.config import C_MPS, RadarProfile


def range_axis(profile: RadarProfile, nfft: int | None = None) -> np.ndarray:
    """Compute the range axis for rfft output bins.

    Parameters
    ----------
    profile : RadarProfile
    nfft : int, optional
        FFT length. Defaults to profile.adc_samples.

    Returns
    -------
    ndarray, float64, shape (nfft//2 + 1,)
        Range in meters for each rfft bin.
    """
    n = nfft or profile.adc_samples
    num_bins = n // 2 + 1
    k = np.arange(num_bins, dtype=np.float64)
    return C_MPS * k * profile.adc_sample_rate_hz / (
        2.0 * profile.slope_hz_per_s * n
    )


def range_bin_spacing_m(profile: RadarProfile, nfft: int | None = None) -> float:
    """Range spacing between adjacent FFT bins (meters)."""
    n = nfft or profile.adc_samples
    return C_MPS * profile.adc_sample_rate_hz / (
        2.0 * profile.slope_hz_per_s * n
    )


def velocity_axis(
    profile: RadarProfile,
    ndoppler: int | None = None,
) -> np.ndarray:
    """Compute the velocity axis for fftshift-ed Doppler bins.

    Parameters
    ----------
    profile : RadarProfile
    ndoppler : int, optional
        Doppler FFT length. Defaults to profile.chirps_per_frame.

    Returns
    -------
    ndarray, float64, shape (ndoppler,)
        Velocity in m/s for each Doppler bin (centered at 0 m/s).
    """
    n = ndoppler or profile.chirps_per_frame
    tc = profile.chirp_repetition_interval_s
    lam = profile.wavelength_m

    # After fftshift, bin indices map to: k - N/2
    k = np.arange(n, dtype=np.float64) - n / 2
    f_d = k / (n * tc)
    return lam * f_d / 2.0


def velocity_bin_spacing_mps(
    profile: RadarProfile,
    ndoppler: int | None = None,
) -> float:
    """Velocity spacing between adjacent Doppler bins (m/s)."""
    n = ndoppler or profile.chirps_per_frame
    tc = profile.chirp_repetition_interval_s
    return profile.wavelength_m / (2.0 * n * tc)


def range_resolution_m(profile: RadarProfile) -> float:
    """Physical range resolution: c / (2 × B_sampled).

    This is determined by the sampled bandwidth, NOT the FFT length.
    Zero-padding does not improve physical resolution.
    """
    return profile.range_resolution_m


def velocity_resolution_mps(profile: RadarProfile) -> float:
    """Physical velocity resolution: λ / (2 × N_chirps × Tc)."""
    return profile.velocity_resolution_mps
