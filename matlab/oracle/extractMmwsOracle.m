function extractMmwsOracle(figPath, outputPrefix)
% extractMmwsOracle Extracts complete object state from a rendered TI .fig
%   extractMmwsOracle(figPath, outputPrefix)

    if nargin < 2
        [folder, name, ~] = fileparts(figPath);
        outputPrefix = fullfile(folder, [name '_oracle']);
    end

    % 1. Open invisibly
    fprintf('Opening %s invisibly...\n', figPath);
    fig = openfig(figPath, 'invisible');
    
    oracle = struct();
    oracle.source_file = figPath;
    oracle.extraction_time = datestr(now);
    
    % FIGURE
    oracle.Figure = struct();
    oracle.Figure.Position = get(fig, 'Position');
    oracle.Figure.Colormap = get(fig, 'Colormap');
    oracle.Figure.Color = get(fig, 'Color');
    oracle.Figure.Renderer = get(fig, 'Renderer');
    
    % 2. Inventory objects
    all_objs = findall(fig);
    
    % AXES
    ax_objs = findall(fig, 'Type', 'axes');
    oracle.Axes = [];
    for i = 1:length(ax_objs)
        ax = ax_objs(i);
        s = struct();
        s.Tag = get(ax, 'Tag');
        s.Position = get(ax, 'Position');
        s.OuterPosition = get(ax, 'OuterPosition');
        s.TightInset = get(ax, 'TightInset');
        s.XLim = get(ax, 'XLim');
        s.YLim = get(ax, 'YLim');
        s.ZLim = get(ax, 'ZLim');
        s.CLim = get(ax, 'CLim');
        s.CLimMode = get(ax, 'CLimMode');
        s.XDir = get(ax, 'XDir');
        s.YDir = get(ax, 'YDir');
        s.XScale = get(ax, 'XScale');
        s.YScale = get(ax, 'YScale');
        s.XGrid = get(ax, 'XGrid');
        s.YGrid = get(ax, 'YGrid');
        s.FontName = get(ax, 'FontName');
        s.FontSize = get(ax, 'FontSize');
        s.LineWidth = get(ax, 'LineWidth');
        s.Box = get(ax, 'Box');
        s.TickDir = get(ax, 'TickDir');
        
        xl = get(ax, 'XLabel'); s.XLabelString = get(xl, 'String'); s.XLabelPosition = get(xl, 'Position');
        yl = get(ax, 'YLabel'); s.YLabelString = get(yl, 'String'); s.YLabelPosition = get(yl, 'Position');
        t = get(ax, 'Title'); s.TitleString = get(t, 'String'); s.TitlePosition = get(t, 'Position');
        
        oracle.Axes = [oracle.Axes; s];
    end
    
    % IMAGES / SURFACES
    img_objs = findall(fig, 'Type', 'image');
    surf_objs = findall(fig, 'Type', 'surface');
    is_objs = [img_objs; surf_objs];
    oracle.ImageSurface = [];
    for i = 1:length(is_objs)
        obj = is_objs(i);
        s = struct();
        s.Type = get(obj, 'Type');
        s.ParentAxesPosition = get(get(obj, 'Parent'), 'Position');
        s.CData = get(obj, 'CData');
        s.CDataMapping = get(obj, 'CDataMapping');
        s.XData = get(obj, 'XData');
        s.YData = get(obj, 'YData');
        s.ZData = get(obj, 'ZData');
        if isprop(obj, 'AlphaData')
            s.AlphaData = get(obj, 'AlphaData');
        else
            s.AlphaData = [];
        end
        oracle.ImageSurface = [oracle.ImageSurface; s];
    end
    
    % LINES
    line_objs = findall(fig, 'Type', 'line');
    oracle.Lines = [];
    for i = 1:length(line_objs)
        obj = line_objs(i);
        s = struct();
        s.ParentAxesPosition = get(get(obj, 'Parent'), 'Position');
        s.XData = get(obj, 'XData');
        s.YData = get(obj, 'YData');
        s.Color = get(obj, 'Color');
        s.LineStyle = get(obj, 'LineStyle');
        s.LineWidth = get(obj, 'LineWidth');
        s.DisplayName = get(obj, 'DisplayName');
        oracle.Lines = [oracle.Lines; s];
    end
    
    % CONTROLS
    ctrl_objs = findall(fig, 'Type', 'uicontrol');
    oracle.Controls = [];
    for i = 1:length(ctrl_objs)
        obj = ctrl_objs(i);
        s = struct();
        s.Tag = get(obj, 'Tag');
        s.Style = get(obj, 'Style');
        str = get(obj, 'String');
        if iscell(str), str = strjoin(str, '|'); end
        s.String = str;
        s.Value = get(obj, 'Value');
        s.Min = get(obj, 'Min');
        s.Max = get(obj, 'Max');
        s.SliderStep = get(obj, 'SliderStep');
        s.Position = get(obj, 'Position');
        cb = get(obj, 'Callback');
        if ischar(cb), s.Callback = cb;
        elseif isa(cb, 'function_handle'), s.Callback = func2str(cb);
        else, s.Callback = 'Other'; end
        s.Visible = get(obj, 'Visible');
        s.Enable = get(obj, 'Enable');
        oracle.Controls = [oracle.Controls; s];
    end
    
    % TABLES
    tbl_objs = findall(fig, 'Type', 'uitable');
    oracle.Tables = [];
    for i = 1:length(tbl_objs)
        obj = tbl_objs(i);
        s = struct();
        s.Tag = get(obj, 'Tag');
        s.Position = get(obj, 'Position');
        s.Data = get(obj, 'Data');
        s.ColumnName = get(obj, 'ColumnName');
        s.RowName = get(obj, 'RowName');
        oracle.Tables = [oracle.Tables; s];
    end

    % 4. Save
    matFile = [outputPrefix '.mat'];
    save(matFile, '-struct', 'oracle');
    fprintf('Saved %s\n', matFile);
    
    jsonFile = [outputPrefix '.json'];
    % For JSON, clear large numeric arrays
    meta_oracle = oracle;
    for i=1:length(meta_oracle.ImageSurface)
        meta_oracle.ImageSurface(i).CData = size(oracle.ImageSurface(i).CData);
        meta_oracle.ImageSurface(i).XData = size(oracle.ImageSurface(i).XData);
        meta_oracle.ImageSurface(i).YData = size(oracle.ImageSurface(i).YData);
        meta_oracle.ImageSurface(i).ZData = size(oracle.ImageSurface(i).ZData);
    end
    for i=1:length(meta_oracle.Lines)
        meta_oracle.Lines(i).XData = size(oracle.Lines(i).XData);
        meta_oracle.Lines(i).YData = size(oracle.Lines(i).YData);
    end
    
    txt = jsonencode(meta_oracle);
    fid = fopen(jsonFile, 'w');
    fprintf(fid, '%s', txt);
    fclose(fid);
    fprintf('Saved %s\n', jsonFile);

    close(fig);
end
