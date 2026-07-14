function noiseDb = estimateNoiseFloor(spectrumDb, method)
%ESTIMATENOISEFLOOR Estimate noise floor from a power spectrum.
%
%   noiseDb = awr2944.estimateNoiseFloor(spectrumDb)
%   noiseDb = awr2944.estimateNoiseFloor(spectrumDb, 'median')
%
%   spectrumDb : double — power spectrum in dB (any dimensions)
%   method     : 'median' (default) or 'percentile25'
%
%   Returns noiseDb : scalar double

    if nargin < 2
        method = 'median';
    end

    vals = spectrumDb(:);
    vals = vals(isfinite(vals));

    switch lower(method)
        case 'median'
            noiseDb = median(vals);
        case 'percentile25'
            noiseDb = prctile(vals, 25);
        otherwise
            error('awr2944:estimateNoiseFloor', 'Unknown method: %s', method);
    end
end
