function profile = smokeV1Profile()
%SMOKEV1PROFILE Return the validated smoke_v1 radar profile parameters.
%
%   profile = awr2944.smokeV1Profile()
%
%   Returns a struct with all parameters matching the Python
%   RadarProfile.from_smoke_v1() factory.

    c = 299792458.0;  % speed of light (m/s)

    profile.start_frequency_hz  = 77e9;
    profile.slope_hz_per_s      = 29.982e12;
    profile.adc_sample_rate_hz  = 10e6;
    profile.adc_samples         = 256;
    profile.idle_time_s         = 100e-6;
    profile.ramp_end_time_s     = 60e-6;
    profile.chirps_per_frame    = 128;
    profile.frame_count         = 8;
    profile.frame_period_s      = 40e-3;
    profile.rx_count            = 4;
    profile.tx_mask             = 3;      % TX0+TX1 simultaneous
    profile.sample_format       = 'real_int16';

    % Derived quantities
    profile.wavelength_m        = c / profile.start_frequency_hz;
    profile.chirp_period_s      = profile.idle_time_s + profile.ramp_end_time_s;
    profile.sampled_bandwidth_hz = profile.slope_hz_per_s * ...
                                   (profile.adc_samples / profile.adc_sample_rate_hz);

    % Range
    profile.range_resolution_m  = c / (2 * profile.sampled_bandwidth_hz);
    profile.max_range_m         = profile.adc_sample_rate_hz * c / ...
                                  (2 * profile.slope_hz_per_s);

    % Velocity (estimates — simultaneous TX, not TDM)
    profile.max_velocity_mps    = profile.wavelength_m / ...
                                  (4 * profile.chirp_period_s);
    profile.velocity_resolution_mps = profile.wavelength_m / ...
                                      (2 * profile.chirps_per_frame * profile.chirp_period_s);
end
