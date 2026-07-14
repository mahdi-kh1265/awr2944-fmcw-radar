function fig = plotRangeDopplerSurface(rdMap, rangeAx, velAx, varargin)
%PLOTRANGEDOPPLERSURFACE 3D surface of range-Doppler map.
%
%   fig = plotRangeDopplerSurface(rdMap, rangeAx, velAx)
%
%   rdMap    : double [doppler, range] — power in dB
%   rangeAx  : double [range, 1]
%   velAx    : double [doppler, 1]

    p = inputParser;
    addParameter(p, 'DynamicRange', 60, @isnumeric);
    addParameter(p, 'Title', 'Range-Doppler Surface', @ischar);
    addParameter(p, 'SavePath', '', @ischar);
    addParameter(p, 'ViewAngle', [-37.5, 30], @isnumeric);
    parse(p, varargin{:});

    dynRange = p.Results.DynamicRange;
    titleStr = p.Results.Title;
    savePath = p.Results.SavePath;
    viewAngle = p.Results.ViewAngle;

    [nRows, nCols] = size(rdMap);

    % Detect dimension ordering by matching axis lengths
    nR = numel(rangeAx);
    nV = numel(velAx);

    if nRows == nR && nCols == nV
        % rdMap is [range, doppler] — transpose for surf
        rdMap = rdMap.';
    elseif nRows == nV && nCols == nR
        % rdMap is [doppler, range] — expected
    else
        % Best effort: trim axes to match
    end

    [nDop, nRange] = size(rdMap);
    rangeAx = rangeAx(1:min(nRange, numel(rangeAx)));
    velAx = velAx(1:min(nDop, numel(velAx)));

    [R, V] = meshgrid(rangeAx, velAx);

    vmax = max(rdMap(:));
    vmin = vmax - dynRange;
    rdClamped = max(rdMap, vmin);

    fig = figure('Position', [100 100 1000 700]);
    surf(R, V, rdClamped, 'EdgeColor', 'none');
    view(viewAngle);
    colormap parula;
    cb = colorbar;
    cb.Label.String = 'Power (dB)';
    xlabel('Range (m)', 'FontSize', 12);
    ylabel('Velocity (m/s)', 'FontSize', 12);
    zlabel('Power (dB)', 'FontSize', 12);
    title(titleStr, 'FontSize', 13);
    lighting gouraud;
    camlight('headlight');
    set(gca, 'FontSize', 10);

    if ~isempty(savePath)
        exportgraphics(fig, [savePath '.png'], 'Resolution', 150);
        exportgraphics(fig, [savePath '.pdf'], 'ContentType', 'vector');
    end
end
