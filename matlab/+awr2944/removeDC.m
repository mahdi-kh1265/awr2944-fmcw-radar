function result = removeDC(cube, mode)
%REMOVEDC Remove DC offset from ADC data.
%
%   result = awr2944.removeDC(cube, mode)
%
%   cube : double or single [sample, rx, chirp, frame]
%   mode : 'per_chirp' | 'per_rx_global' | 'none'
%
%   Returns result with same dimensions.

    if nargin < 2
        mode = 'per_chirp';
    end

    cube = double(cube);

    switch mode
        case 'none'
            result = cube;

        case 'per_chirp'
            % Subtract mean along sample axis (dim 1) per chirp
            result = cube - mean(cube, 1);

        case 'per_rx_global'
            % Subtract global mean across all frames/chirps per RX
            % Mean over dim 1 (sample), dim 3 (chirp), dim 4 (frame)
            result = cube - mean(cube, [1 3 4]);

        otherwise
            error('awr2944:removeDC', 'Unknown DC removal mode: %s', mode);
    end
end
