function [cube, meta] = loadCanonicalCube(matFilePath)
%LOADCANONICALCUBE Load the canonical ADC cube exported from Python.
%
%   [cube, meta] = awr2944.loadCanonicalCube(matFilePath)
%
%   The .mat file is produced by Python's dsp.matlab_export.export_to_mat().
%   It contains two copies of the data:
%       adc_cube        — Python order [frame, chirp, rx, sample]
%       adc_cube_matlab — Pre-transposed [sample, rx, chirp, frame]
%
%   This function uses adc_cube_matlab, which has dimensions that match
%   MATLAB's column-major convention (first index varies fastest):
%       cube(sample, rx, chirp, frame) — MATLAB 1-indexed
%
%   Parameters
%   ----------
%   matFilePath : char or string
%       Path to the exported .mat file.
%
%   Returns
%   -------
%   cube : int16 [sample, rx, chirp, frame]
%       ADC data cube.
%   meta : struct
%       All metadata fields from the export.

    data = load(matFilePath);

    % Use the pre-transposed MATLAB-order cube
    if isfield(data, 'adc_cube_matlab')
        cube = data.adc_cube_matlab;
    else
        % Fallback: transpose from Python order
        cube = permute(data.adc_cube, [4 3 2 1]);
        warning('awr2944:loadCanonicalCube', ...
            'adc_cube_matlab not found, transposed from Python order.');
    end

    % Build metadata struct
    meta = struct();
    fieldsToCopy = {'frame_count', 'chirps_per_frame', 'rx_count', 'adc_samples', ...
                    'sample_rate_hz', 'slope_hz_per_s', 'start_frequency_hz', ...
                    'idle_time_s', 'ramp_end_time_s', 'frame_period_s', ...
                    'tx_mask', 'sample_format', 'layout_version', ...
                    'canonical_raw_sha256', 'range_bin_spacing_m', ...
                    'max_range_m', 'velocity_bin_spacing_mps', 'max_velocity_mps', ...
                    'range_axis_m', 'velocity_axis_mps'};

    for i = 1:numel(fieldsToCopy)
        fn = fieldsToCopy{i};
        if isfield(data, fn)
            val = data.(fn);
            if isnumeric(val) && numel(val) == 1
                meta.(fn) = double(val);
            else
                meta.(fn) = val;
            end
        end
    end

    % Verify dimensions match metadata
    [nSamp, nRx, nChirp, nFrame] = size(cube);
    assert(nSamp  == meta.adc_samples,      'Sample count mismatch');
    assert(nRx    == meta.rx_count,          'RX count mismatch');
    assert(nChirp == meta.chirps_per_frame,  'Chirps/frame mismatch');
    assert(nFrame == meta.frame_count,       'Frame count mismatch');

    fprintf('Loaded canonical cube: [%d samples, %d RX, %d chirps, %d frames]\n', ...
        nSamp, nRx, nChirp, nFrame);
end
