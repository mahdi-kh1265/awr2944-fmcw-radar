function mmwsViewer(payload_path)
% mmwsViewer - Classic MATLAB reproduction of mmWave Studio PostProc UI.
% Stage 2: Real Data Integration.

    if nargin < 1
        error('mmwsViewer requires a payload_path to the canonical data .mat file');
    end
    
    data = load(payload_path);
    
    % Verify MATLAB dimensionality
    % Python sends: range_power_db: [range, doppler, frame]
    sz_rpd = size(data.range_power_db);
    assert(length(sz_rpd) >= 2, 'range_power_db shape mismatch');
    
    % Reference mmWS UI dimensions
    layout.referenceWidth = 1151;
    layout.referenceHeight = 582;
    
    plotW = 344;
    plotH = 229;
    ctrlH = 22; % dropdown height
    
    xLeft = 57;
    xRight = 448;
    
    yBottomAxes = 29;
    yBottomCtrl = 258;
    
    yTopAxes = 315;
    yTopCtrl = 544;
    
    layout.topLeftAxes        = [xLeft, yTopAxes, plotW, plotH];
    layout.topLeftHeader      = [xLeft, yTopCtrl, plotW, ctrlH];
    
    layout.topRightAxes       = [xRight, yTopAxes, plotW, plotH];
    layout.topRightHeader     = [xRight, yTopCtrl, plotW, ctrlH];
    
    layout.bottomLeftAxes     = [xLeft, yBottomAxes, plotW, plotH];
    layout.bottomLeftHeader   = [xLeft, yBottomCtrl, plotW, ctrlH];
    
    layout.bottomMiddleAxes   = [xRight, yBottomAxes, plotW, plotH];
    layout.bottomMiddleHeader = [xRight, yBottomCtrl, plotW, ctrlH];
    
    style.figColor = [0.94 0.94 0.94];
    style.fontName = 'Helvetica';
    style.fontSize = 8;
    
    f = figure('Name', 'mmWave Studio PostProc (AWR2944 Clone)', ...
               'NumberTitle', 'off', ...
               'Position', [100, 100, layout.referenceWidth, layout.referenceHeight], ...
               'Color', style.figColor, ...
               'MenuBar', 'none', ...
               'ToolBar', 'figure', ...
               'Resize', 'off', ...
               'CloseRequestFcn', @(src, evt) on_close(src));
           
    plotOptions = { ...
        '<html><b>Basic Plots<html></b>', ...
        '2D FFT amplitude profile', ...
        'Range-Angle plot (per Frame)', ...
        'Detection & Angle estimation Results', ...
        'Chirp Config Picture', ...
        '1D FFT amplitude profile', ...
        'Time domain plot', ...
        '<html><b>CQ metrics<html></b>', ...
        'CQ metrics - DFE Wide-band Energy Monitor', ...
        'CQ metrics - ADC/IF Saturation Indicator', ...
        'CQ metrics - DFE Energy Monitor', ...
        '<html><b>Other Plots<html></b>', ...
        'Phase stability across Chirps', ...
        'Amplitude stability across Chirps'};
        
    chanOptions = {'Common', 'Chan 1', 'Chan 2', 'Chan 3', 'Chan 4'};
    devOptions = {'Dev 1'};

    % Create Axes
    axRD   = axes('Parent', f, 'Units', 'pixels', 'Position', layout.topLeftAxes, 'UserData', layout.topLeftAxes);
    axDet  = axes('Parent', f, 'Units', 'pixels', 'Position', layout.topRightAxes, 'UserData', layout.topRightAxes);
    ax1D   = axes('Parent', f, 'Units', 'pixels', 'Position', layout.bottomLeftAxes, 'UserData', layout.bottomLeftAxes);
    axTime = axes('Parent', f, 'Units', 'pixels', 'Position', layout.bottomMiddleAxes, 'UserData', layout.bottomMiddleAxes);

    handles = guihandles(f);
    handles.axRD = axRD;
    handles.axDet = axDet;
    handles.ax1D = ax1D;
    handles.axTime = axTime;
    handles.style = style;
    handles.data = data;
    
    % Initialize State
    handles.currentFrame = 1;
    handles.currentChirp = 1;
    handles.numFrames = double(data.frame_count);
    handles.numChirps = double(data.chirps_per_frame);
    handles.timerObj = [];

    % Panel 1 Header
    handles.p1 = uicontrol('Parent', f, 'Style', 'popupmenu', 'String', plotOptions, 'Value', 2, ...
              'Units', 'pixels', 'Position', [layout.topLeftHeader(1), layout.topLeftHeader(2), 200, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @(s,e) updatePlot(s, axRD, f));
    handles.ch1 = uicontrol('Parent', f, 'Style', 'popupmenu', 'String', chanOptions, 'Value', 1, ...
              'Units', 'pixels', 'Position', [layout.topLeftHeader(1)+210, layout.topLeftHeader(2), 80, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @(s,e) updatePlot(handles.p1, axRD, f));
    uicontrol('Parent', f, 'Style', 'popupmenu', 'String', devOptions, ...
              'Units', 'pixels', 'Position', [layout.topLeftHeader(1)+300, layout.topLeftHeader(2), 80, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize);
              
    % Panel 2 Header
    handles.p2 = uicontrol('Parent', f, 'Style', 'popupmenu', 'String', plotOptions, 'Value', 4, ...
              'Units', 'pixels', 'Position', [layout.topRightHeader(1), layout.topRightHeader(2), 220, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @(s,e) updatePlot(s, axDet, f));
    handles.ch2 = uicontrol('Parent', f, 'Style', 'popupmenu', 'String', chanOptions, 'Value', 1, ...
              'Units', 'pixels', 'Position', [layout.topRightHeader(1)+230, layout.topRightHeader(2), 70, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @(s,e) updatePlot(handles.p2, axDet, f));
    uicontrol('Parent', f, 'Style', 'popupmenu', 'String', devOptions, ...
              'Units', 'pixels', 'Position', [layout.topRightHeader(1)+310, layout.topRightHeader(2), 70, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize);

    % Panel 3 Header
    handles.p3 = uicontrol('Parent', f, 'Style', 'popupmenu', 'String', plotOptions, 'Value', 6, ...
              'Units', 'pixels', 'Position', [layout.bottomLeftHeader(1), layout.bottomLeftHeader(2), 220, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @(s,e) updatePlot(s, ax1D, f));
    handles.ch3 = uicontrol('Parent', f, 'Style', 'popupmenu', 'String', chanOptions, 'Value', 2, ...
              'Units', 'pixels', 'Position', [layout.bottomLeftHeader(1)+230, layout.bottomLeftHeader(2), 70, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @(s,e) updatePlot(handles.p3, ax1D, f));
    uicontrol('Parent', f, 'Style', 'popupmenu', 'String', devOptions, ...
              'Units', 'pixels', 'Position', [layout.bottomLeftHeader(1)+310, layout.bottomLeftHeader(2), 70, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize);

    % Panel 4 Header
    handles.p4 = uicontrol('Parent', f, 'Style', 'popupmenu', 'String', plotOptions, 'Value', 7, ...
              'Units', 'pixels', 'Position', [layout.bottomMiddleHeader(1), layout.bottomMiddleHeader(2), 220, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @(s,e) updatePlot(s, axTime, f));
    handles.ch4 = uicontrol('Parent', f, 'Style', 'popupmenu', 'String', chanOptions, 'Value', 2, ...
              'Units', 'pixels', 'Position', [layout.bottomMiddleHeader(1)+230, layout.bottomMiddleHeader(2), 70, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @(s,e) updatePlot(handles.p4, axTime, f));
    uicontrol('Parent', f, 'Style', 'popupmenu', 'String', devOptions, ...
              'Units', 'pixels', 'Position', [layout.bottomMiddleHeader(1)+310, layout.bottomMiddleHeader(2), 70, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize);

    % Sliders and Labels
    handles.lblFrame = uicontrol('Parent', f, 'Style', 'text', 'String', sprintf('Frame 1 / %d', handles.numFrames), ...
              'Units', 'pixels', 'Position', [890, 540, 240, 20], ...
              'BackgroundColor', style.figColor, 'HorizontalAlignment', 'left', ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'FontWeight', 'bold');
          
    uicontrol('Parent', f, 'Style', 'pushbutton', 'String', '<', ...
              'Units', 'pixels', 'Position', [890, 515, 20, 20], 'Callback', @(s,e) mod_frame(f, -1));
          
    handles.sldFrame = uicontrol('Parent', f, 'Style', 'slider', 'Min', 1, 'Max', max(2, handles.numFrames), 'Value', 1, ...
              'Units', 'pixels', 'Position', [915, 515, 200, 20], ...
              'SliderStep', [1/max(1, handles.numFrames-1), max(0.1, 1/max(1, handles.numFrames-1))], ...
              'Callback', @(s,e) set_frame(f, round(get(s, 'Value'))));
          
    uicontrol('Parent', f, 'Style', 'pushbutton', 'String', '>', ...
              'Units', 'pixels', 'Position', [1120, 515, 20, 20], 'Callback', @(s,e) mod_frame(f, 1));

    handles.lblChirp = uicontrol('Parent', f, 'Style', 'text', 'String', sprintf('Chirp 1 / %d', handles.numChirps), ...
              'Units', 'pixels', 'Position', [890, 480, 240, 20], ...
              'BackgroundColor', style.figColor, 'HorizontalAlignment', 'left', ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'FontWeight', 'bold');
          
    uicontrol('Parent', f, 'Style', 'pushbutton', 'String', '<', ...
              'Units', 'pixels', 'Position', [890, 455, 20, 20], 'Callback', @(s,e) mod_chirp(f, -1));
          
    handles.sldChirp = uicontrol('Parent', f, 'Style', 'slider', 'Min', 1, 'Max', max(2, handles.numChirps), 'Value', 1, ...
              'Units', 'pixels', 'Position', [915, 455, 200, 20], ...
              'SliderStep', [1/max(1, handles.numChirps-1), max(0.1, 1/max(1, handles.numChirps-1))], ...
              'Callback', @(s,e) set_chirp(f, round(get(s, 'Value'))));
          
    uicontrol('Parent', f, 'Style', 'pushbutton', 'String', '>', ...
              'Units', 'pixels', 'Position', [1120, 455, 20, 20], 'Callback', @(s,e) mod_chirp(f, 1));
          
    handles.btnPlay = uicontrol('Parent', f, 'Style', 'pushbutton', 'String', 'Play', ...
              'Units', 'pixels', 'Position', [890, 410, 250, 30], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @(s,e) toggle_play(f));
          
    uicontrol('Parent', f, 'Style', 'pushbutton', 'String', 'Miscellaneous options', ...
              'Units', 'pixels', 'Position', [890, 370, 250, 30], ...
              'FontName', style.fontName, 'FontSize', style.fontSize);

    uicontrol('Parent', f, 'Style', 'pushbutton', 'String', 'Programmed Parameters', ...
              'Units', 'pixels', 'Position', [890, 330, 125, 25], ...
              'FontWeight', 'bold');
    uicontrol('Parent', f, 'Style', 'pushbutton', 'String', 'Calculated Parameters', ...
              'Units', 'pixels', 'Position', [1015, 330, 125, 25]);
          
    % Populate parameters from data
    param_data = {
        'profileId', '0';
        'freqSlopeConst (MHz/us)', num2str(data.slope_hz_per_s / 1e12, '%.1f');
        'startFreqConst (GHz)', num2str(data.start_frequency_hz / 1e9, '%.1f');
        'idleTimeConst (us)', num2str(data.idle_time_s * 1e6, '%.1f');
        'adcStartTimeConst (us)', 'N/A';
        'rampEndTime (us)', num2str(data.ramp_end_time_s * 1e6, '%.1f');
        'txOutPowerBackoffCode', '0';
        'txPhaseShifter', '0';
        'txStartTime', '0';
        'numAdcSamples', num2str(data.adc_samples);
        'digOutSampleRate (ksps)', num2str(data.sample_rate_hz / 1e3, '%.0f');
        'RX gain (dB)', '30';
        'frame count', num2str(data.frame_count);
        'chirps per frame', num2str(data.chirps_per_frame);
        'frame period (ms)', num2str(data.frame_period_s * 1e3, '%.1f');
        'TX mask', num2str(data.tx_mask);
        'sample format', char(data.sample_format)
    };

    uitable('Parent', f, 'Data', param_data, 'ColumnName', {'Field Names', 'Value'}, ...
            'Units', 'pixels', 'Position', [890, 20, 250, 310], ...
            'ColumnWidth', {140, 90}, 'RowName', [], 'FontName', style.fontName, 'FontSize', style.fontSize);

    guidata(f, handles);

    % Initial Plot Render
    refresh_all_plots(f);
end

function mod_frame(f, delta)
    handles = guidata(f);
    new_frame = max(1, min(handles.numFrames, handles.currentFrame + delta));
    set_frame(f, new_frame);
end

function set_frame(f, val)
    handles = guidata(f);
    handles.currentFrame = val;
    set(handles.sldFrame, 'Value', val);
    set(handles.lblFrame, 'String', sprintf('Frame %d / %d', val, handles.numFrames));
    guidata(f, handles);
    refresh_all_plots(f);
end

function mod_chirp(f, delta)
    handles = guidata(f);
    new_chirp = max(1, min(handles.numChirps, handles.currentChirp + delta));
    set_chirp(f, new_chirp);
end

function set_chirp(f, val)
    handles = guidata(f);
    handles.currentChirp = val;
    set(handles.sldChirp, 'Value', val);
    set(handles.lblChirp, 'String', sprintf('Chirp %d / %d', val, handles.numChirps));
    guidata(f, handles);
    refresh_all_plots(f);
end

function toggle_play(f)
    handles = guidata(f);
    if isempty(handles.timerObj) || ~isvalid(handles.timerObj)
        % Start Playback
        set(handles.btnPlay, 'String', 'Stop');
        handles.timerObj = timer('ExecutionMode', 'fixedRate', 'Period', 0.2, ...
                                 'TimerFcn', @(s,e) step_play(f));
        guidata(f, handles);
        start(handles.timerObj);
    else
        % Stop Playback
        stop(handles.timerObj);
        delete(handles.timerObj);
        handles.timerObj = [];
        set(handles.btnPlay, 'String', 'Play');
        guidata(f, handles);
    end
end

function step_play(f)
    if ~ishandle(f)
        return;
    end
    handles = guidata(f);
    if handles.currentFrame >= handles.numFrames
        toggle_play(f); % Stop at end
    else
        set_frame(f, handles.currentFrame + 1);
    end
end

function on_close(f)
    handles = guidata(f);
    if ~isempty(handles.timerObj) && isvalid(handles.timerObj)
        stop(handles.timerObj);
        delete(handles.timerObj);
    end
    delete(f);
end

function refresh_all_plots(f)
    handles = guidata(f);
    updatePlot(handles.p1, handles.axRD, f);
    updatePlot(handles.p2, handles.axDet, f);
    updatePlot(handles.p3, handles.ax1D, f);
    updatePlot(handles.p4, handles.axTime, f);
end

function rx_idx = get_channel_idx(ch_handle)
    opts = get(ch_handle, 'String');
    val = get(ch_handle, 'Value');
    s = opts{val};
    if strcmp(s, 'Common')
        rx_idx = 1; % Fallback to rx1
    else
        rx_idx = sscanf(s, 'Chan %d');
    end
end

function updatePlot(src, ax, f)
    handles = guidata(f);
    data = handles.data;
    
    % Find which channel dropdown goes with this plot dropdown
    if src == handles.p1
        ch_idx = get_channel_idx(handles.ch1);
    elseif src == handles.p2
        ch_idx = get_channel_idx(handles.ch2);
    elseif src == handles.p3
        ch_idx = get_channel_idx(handles.ch3);
    else
        ch_idx = get_channel_idx(handles.ch4);
    end
    
    opts = get(src, 'String');
    val = get(src, 'Value');
    plotType = strtrim(opts{val});
    
    % Strip HTML
    plotType = regexprep(plotType, '<[^>]*>', '');
    
    cla(ax, 'reset');
    set(ax, 'Color', [1 1 1]);
    
    % Default axes format
    set(ax, 'FontName', handles.style.fontName, 'FontSize', handles.style.fontSize);
    
    frm = handles.currentFrame;
    chp = handles.currentChirp;
    
    switch plotType
        case '2D FFT amplitude profile'
            % doppler_power_db is [range, doppler, frame] from Python transpose
            Z = data.doppler_power_db_raw(:, :, frm);
            imagesc(ax, data.velocity_axis_mps, data.range_axis_m, Z);
            axis(ax, 'xy');
            colormap(ax, 'parula');
            
            if isfield(data, 'display_normalization_mode') && strcmp(data.display_normalization_mode, 'fixed_global')
                caxis(ax, double(data.display_CLim));
            else
                caxis(ax, 'auto');
            end
            
            hold(ax, 'on');
            if isfield(data, 'det_frames') && ~isempty(data.det_frames)
                mask = (data.det_frames == (frm - 1));
                if any(mask)
                    scatter(ax, data.det_velocities(mask), data.det_ranges(mask), 20, 'r', 'filled');
                end
            end
            hold(ax, 'off');
            
            xlabel(ax, 'Velocity - meters/sec');
            ylabel(ax, 'Distance - meters');
            grid(ax, 'on');
            
        case 'Detection & Angle estimation Results'
            text(ax, 0.5, 0.5, 'Angle estimation unavailable for this capture', ...
                 'HorizontalAlignment', 'center', 'FontWeight', 'bold', 'Color', [0.5 0.5 0.5]);
            set(ax, 'XTick', [], 'YTick', []);
            box(ax, 'on');
            
        case '1D FFT amplitude profile'
            sz = size(data.range_power_db);
            if length(sz) == 4
                p_trace = data.range_power_db(:, ch_idx, chp, frm);
                plot(ax, data.range_axis_m, p_trace, 'b-', 'LineWidth', 1);
                xlabel(ax, 'Distance - meters');
                ylabel(ax, 'Relative Power (dBFS)');
                grid(ax, 'on');
                xlim(ax, [min(data.range_axis_m) max(data.range_axis_m)]);
                ylim(ax, [-120 0]);
            else
                text(ax, 0.5, 0.5, 'Error loading 1D FFT', 'HorizontalAlignment', 'center');
            end
            
        case 'Time domain plot'
            % adc_cube_matlab is [sample, rx, chirp, frame]
            sz = size(data.adc_cube_matlab);
            if length(sz) == 4
                real_trace = double(data.adc_cube_matlab(:, ch_idx, chp, frm));
                imag_trace = zeros(size(real_trace)); % Synthesize zero ref for AWR2944 real-only
                hold(ax, 'on');
                plot(ax, data.adc_time_axis_s, real_trace, 'b-', 'LineWidth', 1);
                plot(ax, data.adc_time_axis_s, imag_trace, 'r-', 'LineWidth', 1);
                hold(ax, 'off');
                xlabel(ax, 'Time (sec)');
                ylabel(ax, 'ADC Codes');
                grid(ax, 'on');
                legend(ax, {'Real', 'Imag (Zero Ref)'}, 'Location', 'northeast', ...
                       'FontName', handles.style.fontName, 'FontSize', 8);
            else
                text(ax, 0.5, 0.5, 'Error loading Time Domain', 'HorizontalAlignment', 'center');
            end
            
        otherwise
            % Unsupported plots
            text(ax, 0.5, 0.5, 'Unavailable for this capture', 'HorizontalAlignment', 'center', ...
                 'FontWeight', 'bold', 'Color', [0.5 0.5 0.5]);
            set(ax, 'XTick', [], 'YTick', []);
            title(ax, ['Unsupported: ' plotType], 'Interpreter', 'none');
            box(ax, 'on');
    end
    
    % Explicit pixel layout correction for mmWS parity
    drawnow; % Force render to get accurate extents
    origPos = get(ax, 'UserData');
    if ~isempty(origPos)
        ti = get(ax, 'TightInset');
        pad = 5;
        
        newPos = [origPos(1) + ti(1) + pad, ...
                  origPos(2) + ti(2) + pad, ...
                  origPos(3) - ti(1) - ti(3) - 2*pad, ...
                  origPos(4) - ti(2) - ti(4) - 2*pad];
        
        % Check collision with bottom dropdowns for top axes
        yBottomCtrlTop = 258 + 22; % layout.yBottomCtrl + ctrlH
        if origPos(2) > 300 % Top axes
            minY = yBottomCtrlTop + pad + ti(2);
            if newPos(2) < minY
                shift = minY - newPos(2);
                newPos(2) = newPos(2) + shift;
                newPos(4) = max(10, newPos(4) - shift);
            end
        end
        
        set(ax, 'Position', newPos);
    end
end
