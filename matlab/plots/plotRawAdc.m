function fig = plotRawAdc(cube, profile, varargin)
%PLOTRAWADC Plot raw ADC traces in a tiled layout.
%
%   fig = plotRawAdc(cube, profile)
%
%   cube    : int16 or double [sample, rx, chirp, frame]
%   profile : struct
%
%   Optional:
%       'Frame' — frame index, 1-indexed (default: 1)
%       'Chirp' — chirp index, 1-indexed (default: 1)
%       'SavePath' — path to save

    p = inputParser;
    addParameter(p, 'Frame', 1, @isnumeric);
    addParameter(p, 'Chirp', 1, @isnumeric);
    addParameter(p, 'SavePath', '', @ischar);
    parse(p, varargin{:});

    frameIdx = p.Results.Frame;
    chirpIdx = p.Results.Chirp;
    savePath = p.Results.SavePath;

    nRx = min(size(cube, 2), 4);

    fig = figure('Position', [100 100 1200 700]);
    t = tiledlayout(2, 2, 'TileSpacing', 'compact', 'Padding', 'compact');
    title(t, sprintf('Raw ADC — Frame %d, Chirp %d', frameIdx-1, chirpIdx-1), ...
        'FontSize', 13);

    colors = lines(4);
    for rx = 1:nRx
        nexttile;
        data = double(cube(:, rx, chirpIdx, frameIdx));
        plot(0:numel(data)-1, data, 'LineWidth', 0.6, 'Color', colors(rx,:));
        title(sprintf('RX%d', rx-1), 'FontSize', 10);
        ylabel('ADC (int16)');
        if rx >= 3
            xlabel('Sample Index');
        end
        grid on;
        set(gca, 'FontSize', 9);
    end

    if ~isempty(savePath)
        exportgraphics(fig, [savePath '.png'], 'Resolution', 150);
    end
end
