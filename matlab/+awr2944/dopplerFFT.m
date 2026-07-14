function [dopplerSpectrum, velAxis] = dopplerFFT(rangeCube, profile, varargin)
%DOPPLERFFT Doppler FFT on complex range spectrum.
%
%   [dopplerSpectrum, velAxis] = awr2944.dopplerFFT(rangeCube, profile)
%
%   rangeCube : complex double [rangeBins, rx, chirp, frame]
%   profile   : struct from smokeV1Profile()
%
%   Optional Parameters:
%       'Window'    — 'rectangular', 'hann', 'hamming' (default: 'hann')
%       'NFFT'      — Doppler FFT length (default: profile.chirps_per_frame)
%       'Clutter'   — 'none', 'slow_time_mean' (default: 'slow_time_mean')
%       'Normalize' — coherent gain normalization (default: true)
%
%   Returns:
%       dopplerSpectrum : complex double [rangeBins, rx, doppler, frame]
%       velAxis         : double [doppler, 1] — velocity in m/s (centered)

    p = inputParser;
    addParameter(p, 'Window', 'hann', @ischar);
    addParameter(p, 'NFFT', profile.chirps_per_frame, @isnumeric);
    addParameter(p, 'Clutter', 'slow_time_mean', @ischar);
    addParameter(p, 'Normalize', true, @islogical);
    parse(p, varargin{:});

    windowType = p.Results.Window;
    nfft       = p.Results.NFFT;
    clutterMode = p.Results.Clutter;
    normalize  = p.Results.Normalize;

    [nRange, nRx, nChirp, nFrame] = size(rangeCube);

    cube = rangeCube;

    % 1. Clutter removal
    switch lower(clutterMode)
        case 'none'
            % no-op
        case 'slow_time_mean'
            % Subtract mean across chirps (dim 3) per (range, rx, frame)
            cube = cube - mean(cube, 3);
        otherwise
            error('awr2944:dopplerFFT', 'Unknown clutter mode: %s', clutterMode);
    end

    % 2. Doppler window along chirp axis (dim 3)
    switch lower(windowType)
        case 'rectangular'
            win = ones(nChirp, 1);
        case 'hann'
            win = hann(nChirp, 'periodic');
        case 'hamming'
            win = hamming(nChirp, 'periodic');
        otherwise
            error('awr2944:dopplerFFT', 'Unknown window: %s', windowType);
    end

    if normalize
        win = win / mean(win);
    end

    % Reshape for broadcasting: [1, 1, nChirp, 1]
    win4d = reshape(win, 1, 1, [], 1);
    cube = cube .* win4d;

    % 3. FFT along chirp axis (dim 3)
    dopplerSpectrum = fft(cube, nfft, 3);

    % 4. fftshift along Doppler axis
    dopplerSpectrum = fftshift(dopplerSpectrum, 3);

    % 5. Velocity axis
    c = 299792458.0;
    lambda = c / profile.start_frequency_hz;
    Tc = profile.chirp_period_s;
    k = (0:nfft-1)' - nfft/2;
    fd = k / (nfft * Tc);
    velAxis = lambda * fd / 2;
end
