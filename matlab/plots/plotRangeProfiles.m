function fig = plotRangeProfiles(rangeSpectrum, rangeAx, profile, varargin)
%PLOTRANGEPROFILES Plot mean range profiles for each RX channel.
%
%   fig = plotRangeProfiles(rangeSpectrum, rangeAx, profile)
%
%   rangeSpectrum : complex [rangeBins, rx, chirp, frame]
%   rangeAx       : double [rangeBins, 1]
%   profile       : struct from smokeV1Profile()
%
%   Optional:
%       'Frame'    — which frame to plot (default: 1)
%       'SavePath' — path to save

    p = inputParser;
    addParameter(p, 'Frame', 1, @isnumeric);
    addParameter(p, 'SavePath', '', @ischar);
    parse(p, varargin{:});

    frameIdx = p.Results.Frame;
    savePath = p.Results.SavePath;

    nRx = size(rangeSpectrum, 2);
    colors = lines(nRx + 1);

    fig = figure('Position', [100 100 1100 450]);
    hold on;

    for rx = 1:nRx
        % Mean across chirps for this frame
        data = rangeSpectrum(:, rx, :, frameIdx);  % [range, 1, chirps, 1]
        meanMag = mean(abs(data), 3);
        magDb = 20 * log10(max(meanMag, eps));
        plot(rangeAx, magDb, 'LineWidth', 0.8, 'Color', colors(rx,:), ...
            'DisplayName', sprintf('RX%d', rx-1));
    end

    % Noncoherent sum across all RX
    allRx = rangeSpectrum(:, :, :, frameIdx);
    ncPower = mean(sum(abs(allRx).^2, 2), 3);
    ncDb = 10 * log10(max(ncPower, eps));
    plot(rangeAx, ncDb, 'k--', 'LineWidth', 1.2, 'DisplayName', 'NC-Sum');

    hold off;
    xlabel('Range (m)', 'FontSize', 12);
    ylabel('Power (dB)', 'FontSize', 12);
    title(sprintf('Range Profiles — Frame %d', frameIdx-1), 'FontSize', 13);
    legend('Location', 'northeast', 'FontSize', 8);
    grid on;
    set(gca, 'FontSize', 10);

    if ~isempty(savePath)
        exportgraphics(fig, [savePath '.png'], 'Resolution', 150);
    end
end
