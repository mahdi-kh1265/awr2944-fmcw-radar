function fig = plotRangeDoppler(rdMap, rangeAx, velAx, varargin)
%PLOTRANGEDOPPLER Plot a range-Doppler heatmap with physical axes.
%
%   fig = plotRangeDoppler(rdMap, rangeAx, velAx)
%   fig = plotRangeDoppler(rdMap, rangeAx, velAx, 'DynamicRange', 60, ...)
%
%   rdMap    : double [doppler, range] — power in dB (RX-combined)
%   rangeAx  : double [range, 1] — range axis in meters
%   velAx    : double [doppler, 1] — velocity axis in m/s
%
%   Optional Parameters:
%       'DynamicRange'  — dB below peak to display (default: 60)
%       'Title'         — plot title
%       'SavePath'      — path to save PNG and PDF
%       'Colormap'      — colormap name (default: 'parula')
%       'ConfigLabel'   — annotation string

    p = inputParser;
    addParameter(p, 'DynamicRange', 60, @isnumeric);
    addParameter(p, 'Title', 'Range-Doppler Map', @ischar);
    addParameter(p, 'SavePath', '', @ischar);
    addParameter(p, 'Colormap', 'parula', @ischar);
    addParameter(p, 'ConfigLabel', '', @ischar);
    parse(p, varargin{:});

    dynRange = p.Results.DynamicRange;
    titleStr = p.Results.Title;
    savePath = p.Results.SavePath;
    cmapName = p.Results.Colormap;
    configLabel = p.Results.ConfigLabel;

    vmax = max(rdMap(:));
    vmin = vmax - dynRange;

    % Detect dimension ordering
    [nRows, nCols] = size(rdMap);
    nR = numel(rangeAx);
    nV = numel(velAx);
    if nRows == nR && nCols == nV
        rdMap = rdMap.';  % transpose to [doppler, range]
    end

    fig = figure('Position', [100 100 900 650]);
    imagesc(rangeAx, velAx, rdMap, [vmin vmax]);
    axis xy;
    colormap(cmapName);
    cb = colorbar;
    cb.Label.String = 'Power (dB)';
    xlabel('Range (m)', 'FontSize', 12);
    ylabel('Velocity (m/s)', 'FontSize', 12);
    title(titleStr, 'FontSize', 13);
    set(gca, 'FontSize', 10);

    if ~isempty(configLabel)
        annotation('textbox', [0.02 0.02 0.3 0.05], ...
            'String', configLabel, 'FontSize', 7, ...
            'EdgeColor', 'none', 'Color', [0.5 0.5 0.5]);
    end

    if ~isempty(savePath)
        exportgraphics(fig, [savePath '.png'], 'Resolution', 150);
        exportgraphics(fig, [savePath '.pdf'], 'ContentType', 'vector');
    end
end
