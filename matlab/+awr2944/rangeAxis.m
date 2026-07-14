function rAxis = rangeAxis(profile, nfft)
%RANGEAXIS Compute range axis for rfft bins.
%
%   rAxis = awr2944.rangeAxis(profile)
%   rAxis = awr2944.rangeAxis(profile, nfft)
%
%   R(k) = c * (k-1) * fs / (2 * S * NFFT) — 1-indexed
%
%   profile : struct from smokeV1Profile()
%   nfft    : FFT length (default: profile.adc_samples)
%
%   Returns rAxis : double [nfft/2+1, 1] — range in meters

    if nargin < 2
        nfft = profile.adc_samples;
    end

    c = 299792458.0;
    nBins = floor(nfft/2) + 1;
    k = (0:nBins-1)';
    rAxis = c * k * profile.adc_sample_rate_hz / ...
            (2 * profile.slope_hz_per_s * nfft);
end
