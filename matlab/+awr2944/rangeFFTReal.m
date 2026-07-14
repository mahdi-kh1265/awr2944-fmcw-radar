function [rangeSpectrum, rangeAxis] = rangeFFTReal(cube, profile, varargin)
%RANGEFFTREAL Range FFT for real-valued ADC data.
%
%   [rangeSpectrum, rangeAxis] = awr2944.rangeFFTReal(cube, profile)
%   [rangeSpectrum, rangeAxis] = awr2944.rangeFFTReal(cube, profile, 'Window', 'hann', 'NFFT', 256)
%
%   cube    : double [sample, rx, chirp, frame] — after DC removal
%   profile : struct from smokeV1Profile()
%
%   Optional Parameters:
%       'Window'  — 'rectangular', 'hann', 'hamming', 'blackman' (default: 'hann')
%       'NFFT'    — FFT length (default: profile.adc_samples)
%       'Normalize' — true/false for coherent-gain normalization (default: true)
%
%   Returns:
%       rangeSpectrum : complex double [NFFT/2+1, rx, chirp, frame]
%       rangeAxis     : double [NFFT/2+1, 1] — range in meters

    p = inputParser;
    addParameter(p, 'Window', 'hann', @ischar);
    addParameter(p, 'NFFT', profile.adc_samples, @isnumeric);
    addParameter(p, 'Normalize', true, @islogical);
    parse(p, varargin{:});

    windowType = p.Results.Window;
    nfft       = p.Results.NFFT;
    normalize  = p.Results.Normalize;

    [nSamp, nRx, nChirp, nFrame] = size(cube);

    % Generate window
    switch lower(windowType)
        case 'rectangular'
            win = ones(nSamp, 1);
        case 'hann'
            win = hann(nSamp, 'periodic');
        case 'hamming'
            win = hamming(nSamp, 'periodic');
        case 'blackman'
            win = blackman(nSamp, 'periodic');
        otherwise
            error('awr2944:rangeFFTReal', 'Unknown window: %s', windowType);
    end

    % Coherent gain normalization
    if normalize
        win = win / mean(win);
    end

    % Apply window (broadcast across rx, chirp, frame)
    windowed = cube .* win;

    % FFT along sample axis (dim 1)
    fullSpectrum = fft(windowed, nfft, 1);

    % Extract positive frequencies only (rfft equivalent)
    nBins = floor(nfft/2) + 1;
    rangeSpectrum = fullSpectrum(1:nBins, :, :, :);

    % Range axis: R(k) = c * (k-1) * fs / (2 * S * NFFT)
    c = 299792458.0;
    k = (0:nBins-1)';
    rangeAxis = c * k * profile.adc_sample_rate_hz / ...
                (2 * profile.slope_hz_per_s * nfft);
end
