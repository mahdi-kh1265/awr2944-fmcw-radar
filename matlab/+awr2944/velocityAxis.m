function vAxis = velocityAxis(profile, nDoppler)
%VELOCITYAXIS Compute centered velocity axis for Doppler bins.
%
%   vAxis = awr2944.velocityAxis(profile)
%   vAxis = awr2944.velocityAxis(profile, nDoppler)
%
%   v(k) = lambda * f_d(k) / 2
%   f_d(k) = (k - N/2) / (N * Tc)    after fftshift
%
%   profile  : struct from smokeV1Profile()
%   nDoppler : Doppler FFT length (default: profile.chirps_per_frame)
%
%   Returns vAxis : double [nDoppler, 1] — velocity in m/s

    if nargin < 2
        nDoppler = profile.chirps_per_frame;
    end

    c = 299792458.0;
    lambda = c / profile.start_frequency_hz;
    Tc = profile.chirp_period_s;

    k = (0:nDoppler-1)' - nDoppler/2;
    fd = k / (nDoppler * Tc);
    vAxis = lambda * fd / 2;
end
