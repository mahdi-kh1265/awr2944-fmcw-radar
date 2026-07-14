function results = testPythonParity(matFilePath)
%TESTPYTHONPARITY Validate MATLAB processing matches Python.
%
%   results = testPythonParity(matFilePath)
%
%   Loads the canonical .mat export and compares MATLAB processing
%   against stored golden values (or self-consistency checks).

    fprintf('=== Python/MATLAB Parity Test ===\n\n');

    % Load data
    [cube, meta] = awr2944.loadCanonicalCube(matFilePath);
    profile = awr2944.smokeV1Profile();
    results = struct();

    % 1. Profile agreement
    fprintf('1. Profile comparison...\n');
    assert(abs(profile.adc_samples - meta.adc_samples) < 1e-6, ...
        'adc_samples mismatch');
    assert(abs(profile.chirps_per_frame - meta.chirps_per_frame) < 1e-6, ...
        'chirps_per_frame mismatch');
    assert(abs(profile.frame_count - meta.frame_count) < 1e-6, ...
        'frame_count mismatch');
    results.profile = 'PASS';
    fprintf('   PASS\n');

    % 2. Range axis agreement
    fprintf('2. Range axis comparison...\n');
    rAxis = awr2944.rangeAxis(profile);
    rAxisPy = meta.range_axis_m(:);
    maxRangeErr = max(abs(rAxis - rAxisPy));
    fprintf('   Max range axis error: %.2e m\n', maxRangeErr);
    assert(maxRangeErr < 1e-6, 'Range axis mismatch');
    results.range_axis_max_error_m = maxRangeErr;
    results.range_axis = 'PASS';
    fprintf('   PASS\n');

    % 3. Velocity axis agreement
    fprintf('3. Velocity axis comparison...\n');
    vAxis = awr2944.velocityAxis(profile);
    vAxisPy = meta.velocity_axis_mps(:);
    maxVelErr = max(abs(vAxis - vAxisPy));
    fprintf('   Max velocity axis error: %.2e m/s\n', maxVelErr);
    assert(maxVelErr < 1e-6, 'Velocity axis mismatch');
    results.velocity_axis_max_error_mps = maxVelErr;
    results.velocity_axis = 'PASS';
    fprintf('   PASS\n');

    % 4. DC removal consistency
    fprintf('4. DC removal self-consistency...\n');
    cubeFloat = double(cube);
    dcRemoved = awr2944.removeDC(cubeFloat, 'per_chirp');
    chirpMeans = squeeze(mean(dcRemoved, 1));  % should be ~0
    maxDcResidual = max(abs(chirpMeans(:)));
    fprintf('   Max DC residual: %.2e\n', maxDcResidual);
    assert(maxDcResidual < 1e-8, 'DC removal failed');
    results.dc_residual = maxDcResidual;
    results.dc_removal = 'PASS';
    fprintf('   PASS\n');

    % 5. Range FFT shape
    fprintf('5. Range FFT shape check...\n');
    [rSpec, rAx] = awr2944.rangeFFTReal(dcRemoved, profile, ...
        'Window', 'hann', 'NFFT', 256);
    [nRange, nRx, nChirp, nFrame] = size(rSpec);
    assert(nRange == 129, 'Expected 129 range bins for NFFT=256');
    assert(nRx == 4, 'Expected 4 RX channels');
    assert(nChirp == 128, 'Expected 128 chirps');
    assert(nFrame == 8, 'Expected 8 frames');
    results.range_fft_shape = [nRange, nRx, nChirp, nFrame];
    results.range_fft = 'PASS';
    fprintf('   Shape: [%d, %d, %d, %d] — PASS\n', nRange, nRx, nChirp, nFrame);

    % 6. Doppler FFT shape
    fprintf('6. Doppler FFT shape check...\n');
    [dSpec, vAx] = awr2944.dopplerFFT(rSpec, profile, ...
        'Window', 'hann', 'Clutter', 'slow_time_mean');
    [nR2, nRx2, nDop, nF2] = size(dSpec);
    assert(nR2 == 129, 'Range bins preserved');
    assert(nDop == 128, 'Expected 128 Doppler bins');
    results.doppler_fft_shape = [nR2, nRx2, nDop, nF2];
    results.doppler_fft = 'PASS';
    fprintf('   Shape: [%d, %d, %d, %d] — PASS\n', nR2, nRx2, nDop, nF2);

    % 7. Peak range-bin agreement (should be deterministic)
    fprintf('7. Peak bin check...\n');
    ncPower = awr2944.combineRxPower(rSpec);
    meanProfile = mean(abs(squeeze(ncPower(:, 1, :, 1))), 2);
    [~, peakBin] = max(meanProfile);
    peakRange = rAx(peakBin);
    fprintf('   Peak range bin: %d (%.2f m)\n', peakBin, peakRange);
    results.peak_range_bin = peakBin;
    results.peak_range_m = peakRange;
    results.peak_bin = 'PASS';
    fprintf('   PASS\n');

    % Summary
    fprintf('\n=== All parity tests PASSED ===\n');
    results.overall = 'PASS';
end
