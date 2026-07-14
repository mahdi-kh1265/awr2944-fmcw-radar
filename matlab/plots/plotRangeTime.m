function fig = plotRangeTime(rangeSpectrum, rangeAx, profile, varargin)
%PLOTRANGETIME Range-time heatmap (mean across chirps per frame).
%
%   rangeSpectrum : complex [rangeBins, rx, chirps, frames]
%   rangeAx : [rangeBins, 1]
%   profile : struct

    p = inputParser;
    addParameter(p, 'RX', 1, @isnumeric);
    addParameter(p, 'DynamicRange', 60, @isnumeric);
    addParameter(p, 'SavePath', '', @ischar);
    parse(p, varargin{:});

    rx = p.Results.RX;
    dynRange = p.Results.DynamicRange;
    savePath = p.Results.SavePath;

    nFrames = size(rangeSpectrum, 4);
    timeAxis = (0:nFrames-1) * profile.frame_period_s * 1000;  % ms

    % Mean magnitude across chirps for each frame
    rtMap = zeros(numel(rangeAx), nFrames);
    for f = 1:nFrames
        rtMap(:, f) = mean(abs(rangeSpectrum(:, rx, :, f)), 3);
    end
    rtDb = 20 * log10(max(rtMap, eps));

    vmax = max(rtDb(:));
    vmin = vmax - dynRange;

    fig = figure('Position', [100 100 1100 450]);
    imagesc(timeAxis, rangeAx, rtDb, [vmin vmax]);
    axis xy;
    colormap parula;
    cb = colorbar;
    cb.Label.String = 'Power (dB)';
    xlabel('Time (ms)', 'FontSize', 12);
    ylabel('Range (m)', 'FontSize', 12);
    title(sprintf('Range-Time Heatmap — RX%d', rx-1), 'FontSize', 13);
    set(gca, 'FontSize', 10);

    if ~isempty(savePath)
        exportgraphics(fig, [savePath '.png'], 'Resolution', 150);
    end
end
