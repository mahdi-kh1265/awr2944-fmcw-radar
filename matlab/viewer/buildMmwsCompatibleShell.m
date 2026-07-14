function f = buildMmwsCompatibleShell(initial_state)
% buildMmwsCompatibleShell - Constructs the UI and manages all viewer state
% Strictly avoids all TI mmWave Studio callbacks.

    layout.referenceWidth = 1151;
    layout.referenceHeight = 582;
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
               'CloseRequestFcn', @on_close);
               
    % Initialize handles struct
    handles = struct();
    handles.style = style;
    
    % Axis Layout
    plotW = 344; plotH = 229; ctrlH = 22;
    xLeft = 57; xRight = 448;
    yBottomAxes = 29; yBottomCtrl = 258;
    yTopAxes = 315; yTopCtrl = 544;
    
    handles.axRD = axes('Parent', f, 'Units', 'pixels', 'Position', [xLeft, yTopAxes, plotW, plotH]);
    handles.axDet = axes('Parent', f, 'Units', 'pixels', 'Position', [xRight, yTopAxes, plotW, plotH]);
    handles.ax1D = axes('Parent', f, 'Units', 'pixels', 'Position', [xLeft, yBottomAxes, plotW, plotH]);
    handles.axTime = axes('Parent', f, 'Units', 'pixels', 'Position', [xRight, yBottomAxes, plotW, plotH]);
    
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
    
    % Panel 1 Header (Top Left)
    handles.p1 = uicontrol('Parent', f, 'Style', 'popupmenu', 'String', plotOptions, 'Value', 2, ...
              'Units', 'pixels', 'Position', [xLeft, yTopCtrl, 200, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @on_plot_change);
    handles.ch1 = uicontrol('Parent', f, 'Style', 'popupmenu', 'String', chanOptions, 'Value', 1, ...
              'Units', 'pixels', 'Position', [xLeft+210, yTopCtrl, 80, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @on_chan_change);
    uicontrol('Parent', f, 'Style', 'popupmenu', 'String', devOptions, ...
              'Units', 'pixels', 'Position', [xLeft+300, yTopCtrl, 80, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize);

    % Panel 2 Header (Top Right)
    handles.p2 = uicontrol('Parent', f, 'Style', 'popupmenu', 'String', plotOptions, 'Value', 4, ...
              'Units', 'pixels', 'Position', [xRight, yTopCtrl, 220, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @on_plot_change);
    handles.ch2 = uicontrol('Parent', f, 'Style', 'popupmenu', 'String', chanOptions, 'Value', 1, ...
              'Units', 'pixels', 'Position', [xRight+230, yTopCtrl, 70, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @on_chan_change);
    uicontrol('Parent', f, 'Style', 'popupmenu', 'String', devOptions, ...
              'Units', 'pixels', 'Position', [xRight+310, yTopCtrl, 70, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize);

    % Panel 3 Header (Bottom Left)
    handles.p3 = uicontrol('Parent', f, 'Style', 'popupmenu', 'String', plotOptions, 'Value', 6, ...
              'Units', 'pixels', 'Position', [xLeft, yBottomCtrl, 220, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @on_plot_change);
    handles.ch3 = uicontrol('Parent', f, 'Style', 'popupmenu', 'String', chanOptions, 'Value', 2, ...
              'Units', 'pixels', 'Position', [xLeft+230, yBottomCtrl, 70, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @on_chan_change);
    uicontrol('Parent', f, 'Style', 'popupmenu', 'String', devOptions, ...
              'Units', 'pixels', 'Position', [xLeft+310, yBottomCtrl, 70, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize);

    % Panel 4 Header (Bottom Right)
    handles.p4 = uicontrol('Parent', f, 'Style', 'popupmenu', 'String', plotOptions, 'Value', 7, ...
              'Units', 'pixels', 'Position', [xRight, yBottomCtrl, 220, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @on_plot_change);
    handles.ch4 = uicontrol('Parent', f, 'Style', 'popupmenu', 'String', chanOptions, 'Value', 2, ...
              'Units', 'pixels', 'Position', [xRight+230, yBottomCtrl, 70, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @on_chan_change);
    uicontrol('Parent', f, 'Style', 'popupmenu', 'String', devOptions, ...
              'Units', 'pixels', 'Position', [xRight+310, yBottomCtrl, 70, ctrlH], ...
              'FontName', style.fontName, 'FontSize', style.fontSize);

    % Frame Controls
    handles.lblFrame = uicontrol('Parent', f, 'Style', 'text', 'String', sprintf('Frame 1/%d', initial_state.frameCount), ...
              'Units', 'pixels', 'Position', [890, 540, 240, 20], ...
              'BackgroundColor', style.figColor, 'HorizontalAlignment', 'left', ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'FontWeight', 'bold');
          
    handles.btnPrevFrame = uicontrol('Parent', f, 'Style', 'pushbutton', 'String', '<', ...
              'Units', 'pixels', 'Position', [890, 515, 20, 20], 'Callback', @on_prev_frame);
          
    f_step = [1/max(1, initial_state.frameCount-1), 10/max(1, initial_state.frameCount-1)];
    handles.sldFrame = uicontrol('Parent', f, 'Style', 'slider', 'Min', 1, 'Max', max(2, initial_state.frameCount), 'Value', 1, ...
              'Units', 'pixels', 'Position', [915, 515, 200, 20], ...
              'SliderStep', f_step, 'Callback', @on_slide_frame);
          
    handles.btnNextFrame = uicontrol('Parent', f, 'Style', 'pushbutton', 'String', '>', ...
              'Units', 'pixels', 'Position', [1120, 515, 20, 20], 'Callback', @on_next_frame);

    % Chirp Controls
    handles.lblChirp = uicontrol('Parent', f, 'Style', 'text', 'String', sprintf('Chirp 1/%d', initial_state.chirpsPerFrame), ...
              'Units', 'pixels', 'Position', [890, 480, 240, 20], ...
              'BackgroundColor', style.figColor, 'HorizontalAlignment', 'left', ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'FontWeight', 'bold');
          
    handles.btnPrevChirp = uicontrol('Parent', f, 'Style', 'pushbutton', 'String', '<', ...
              'Units', 'pixels', 'Position', [890, 455, 20, 20], 'Callback', @on_prev_chirp);
          
    c_step = [1/max(1, initial_state.chirpsPerFrame-1), 10/max(1, initial_state.chirpsPerFrame-1)];
    handles.sldChirp = uicontrol('Parent', f, 'Style', 'slider', 'Min', 1, 'Max', max(2, initial_state.chirpsPerFrame), 'Value', 1, ...
              'Units', 'pixels', 'Position', [915, 455, 200, 20], ...
              'SliderStep', c_step, 'Callback', @on_slide_chirp);
          
    handles.btnNextChirp = uicontrol('Parent', f, 'Style', 'pushbutton', 'String', '>', ...
              'Units', 'pixels', 'Position', [1120, 455, 20, 20], 'Callback', @on_next_chirp);

    % Playback and Options
    handles.btnPlay = uicontrol('Parent', f, 'Style', 'pushbutton', 'String', 'Play', ...
              'Units', 'pixels', 'Position', [890, 410, 250, 30], ...
              'FontName', style.fontName, 'FontSize', style.fontSize, 'Callback', @on_play);
          
    uicontrol('Parent', f, 'Style', 'pushbutton', 'String', 'Miscellaneous options', ...
              'Units', 'pixels', 'Position', [890, 370, 250, 30], ...
              'FontName', style.fontName, 'FontSize', style.fontSize);

    uicontrol('Parent', f, 'Style', 'pushbutton', 'String', 'Programmed Parameters', ...
              'Units', 'pixels', 'Position', [890, 330, 125, 25], ...
              'FontWeight', 'bold', 'Callback', @on_param_tab);
    uicontrol('Parent', f, 'Style', 'pushbutton', 'String', 'Calculated Parameters', ...
              'Units', 'pixels', 'Position', [1015, 330, 125, 25], 'Callback', @on_param_tab);
              
    % Parameter Table
    data = initial_state.payload;
    handles.param_data_prog = {
        'profileId', '0';
        'freqSlopeConst (MHz/us)', num2str(data.slope_hz_per_s / 1e12, '%.3f');
        'startFreqConst (GHz)', num2str(data.start_frequency_hz / 1e9, '%.1f');
        'idleTimeConst (us)', num2str(data.idle_time_s * 1e6, '%.1f');
        'adcStartTimeConst (us)', '0.0';
        'rampEndTime (us)', num2str(data.ramp_end_time_s * 1e6, '%.1f');
        'txOutPowerBackoffCode', '0';
        'txPhaseShifter', '0';
        'txStartTime', '0';
        'numAdcSamples', num2str(data.adc_samples);
        'digOutSampleRate (MHz)', num2str(data.sample_rate_hz / 1e6, '%.1f');
        'RX gain (dB)', '30';
        'frame count', num2str(data.frame_count);
        'chirps per frame', num2str(data.chirps_per_frame);
        'frame period (ms)', num2str(data.frame_period_s * 1e3, '%.1f');
        'TX mask', num2str(data.tx_mask);
        'sample format', char(data.sample_format)
    };
    
    handles.param_data_calc = {
        'sampled bandwidth (MHz)', num2str((data.adc_samples / data.sample_rate_hz) * data.slope_hz_per_s / 1e6, '%.3f');
        'range-bin spacing (m)', 'N/A';
        'nominal maximum range (m)', 'N/A';
        'chirp repetition interval (us)', 'N/A';
        'velocity-bin spacing (m/s)', 'N/A';
        'nominal maximum velocity (m/s)', 'N/A';
        'active chirp-train duration (ms)', 'N/A';
        'total frame sequence duration (ms)', num2str(data.frame_count * data.frame_period_s * 1e3, '%.1f');
    };

    handles.tblParams = uitable('Parent', f, 'Data', handles.param_data_prog, 'ColumnName', {'Field Names', 'Value'}, ...
            'Units', 'pixels', 'Position', [890, 20, 250, 310], ...
            'ColumnWidth', {140, 90}, 'RowName', [], 'FontName', style.fontName, 'FontSize', style.fontSize);

    % Save initial state
    initial_state.handles = handles;
    guidata(f, initial_state);
    
    % Assert no stale TI callbacks
    all_objs = findall(f);
    for i = 1:length(all_objs)
        try
            cb = get(all_objs(i), 'Callback');
            if ischar(cb) && ~isempty(cb)
                if contains(cb, 'play_from_current_point_onwards') || ...
                   contains(cb, 'chirp_slider') || ...
                   contains(cb, 'frame_slider') || ...
                   contains(cb, 'options_gui') || ...
                   contains(cb, 'MatlabPostProcGui')
                    error('Stale TI callback found on UI element.');
                end
            end
        catch
        end
    end
    
    refreshViewer(f);

    % --- Local Callback Functions ---
    
    function on_close(src, ~)
        state = guidata(src);
        if ~isempty(state) && isfield(state, 'timer')
            if ~isempty(state.timer) && isvalid(state.timer)
                stop(state.timer);
                delete(state.timer);
            end
        end
        delete(src);
    end

    function on_prev_frame(~, ~)
        state = guidata(f);
        state.currentFrame = max(1, state.currentFrame - 1);
        guidata(f, state);
        refreshViewer(f);
    end

    function on_next_frame(~, ~)
        state = guidata(f);
        state.currentFrame = min(state.frameCount, state.currentFrame + 1);
        guidata(f, state);
        refreshViewer(f);
    end

    function on_slide_frame(src, ~)
        state = guidata(f);
        val = round(get(src, 'Value'));
        val = max(1, min(state.frameCount, val));
        state.currentFrame = val;
        guidata(f, state);
        refreshViewer(f);
    end

    function on_prev_chirp(~, ~)
        state = guidata(f);
        state.currentChirp = max(1, state.currentChirp - 1);
        guidata(f, state);
        refreshViewer(f);
    end

    function on_next_chirp(~, ~)
        state = guidata(f);
        state.currentChirp = min(state.chirpsPerFrame, state.currentChirp + 1);
        guidata(f, state);
        refreshViewer(f);
    end

    function on_slide_chirp(src, ~)
        state = guidata(f);
        val = round(get(src, 'Value'));
        val = max(1, min(state.chirpsPerFrame, val));
        state.currentChirp = val;
        guidata(f, state);
        refreshViewer(f);
    end

    function on_play(~, ~)
        state = guidata(f);
        if state.isPlaying
            % Stop
            state.isPlaying = false;
            set(state.handles.btnPlay, 'String', 'Play');
            if ~isempty(state.timer) && isvalid(state.timer)
                stop(state.timer);
                delete(state.timer);
            end
            state.timer = [];
            guidata(f, state);
        else
            % Play
            state.isPlaying = true;
            set(state.handles.btnPlay, 'String', 'Stop');
            state.timer = timer('ExecutionMode', 'fixedRate', 'Period', 0.2, ...
                                'TimerFcn', @(~,~) on_timer_tick(f));
            guidata(f, state);
            start(state.timer);
        end
    end

    function on_timer_tick(f)
        if ~ishandle(f)
            return;
        end
        state = guidata(f);
        if state.currentFrame >= state.frameCount
            % Stop playback
            state.isPlaying = false;
            set(state.handles.btnPlay, 'String', 'Play');
            stop(state.timer);
            delete(state.timer);
            state.timer = [];
            guidata(f, state);
        else
            state.currentFrame = state.currentFrame + 1;
            guidata(f, state);
            refreshViewer(f);
        end
    end

    function on_plot_change(~, ~)
        refreshViewer(f);
    end

    function on_chan_change(~, ~)
        refreshViewer(f);
    end

    function on_param_tab(src, ~)
        state = guidata(f);
        str = get(src, 'String');
        if contains(str, 'Programmed')
            set(state.handles.tblParams, 'Data', state.handles.param_data_prog);
        else
            set(state.handles.tblParams, 'Data', state.handles.param_data_calc);
        end
    end

    function refreshViewer(f)
        state = guidata(f);
        h = state.handles;
        data = state.payload;
        
        % Update UI controls to match state
        set(h.sldFrame, 'Value', state.currentFrame);
        set(h.lblFrame, 'String', sprintf('Frame %d/%d', state.currentFrame, state.frameCount));
        
        set(h.sldChirp, 'Value', state.currentChirp);
        set(h.lblChirp, 'String', sprintf('Chirp %d/%d', state.currentChirp, state.chirpsPerFrame));
        
        % Redraw plots
        drawPlot(h.p1, h.ch1, h.axRD, state, data, h.style);
        drawPlot(h.p2, h.ch2, h.axDet, state, data, h.style);
        drawPlot(h.p3, h.ch3, h.ax1D, state, data, h.style);
        drawPlot(h.p4, h.ch4, h.axTime, state, data, h.style);
    end

    function drawPlot(p_handle, ch_handle, ax, state, data, style)
        % Get plot type and channel
        opts = get(p_handle, 'String');
        if ~iscell(opts), opts = cellstr(opts); end
        val = get(p_handle, 'Value');
        plotType = strtrim(opts{val});
        plotType = regexprep(plotType, '<[^>]*>', '');
        
        c_opts = get(ch_handle, 'String');
        if ~iscell(c_opts), c_opts = cellstr(c_opts); end
        c_val = get(ch_handle, 'Value');
        c_str = c_opts{c_val};
        if strcmp(c_str, 'Common')
            ch_idx = 1;
        else
            ch_idx = sscanf(c_str, 'Chan %d');
        end
        
        cla(ax, 'reset');
        set(ax, 'Color', [1 1 1], 'FontName', style.fontName, 'FontSize', style.fontSize);
        
        frm = state.currentFrame;
        chp = state.currentChirp;
        
        switch plotType
            case '2D FFT amplitude profile'
                if isfield(data, 'doppler_power_db_raw')
                    Z = data.doppler_power_db_raw(:, :, frm);
                    imagesc(ax, data.velocity_axis_mps, data.range_axis_m, Z);
                    axis(ax, 'xy');
                    colormap(ax, 'parula');
                    
                    max_val = max(Z(:));
                    caxis(ax, [max_val - 80, max_val]);
                    
                    xlabel(ax, 'Velocity - meters/sec');
                    ylabel(ax, 'Distance - meters');
                    grid(ax, 'on');
                else
                    text(ax, 0.5, 0.5, '2D FFT unavailable', 'HorizontalAlignment', 'center');
                end
                
            case 'Detection & Angle estimation Results'
                text(ax, 0.5, 0.5, 'Angle estimation unavailable for this capture', ...
                     'HorizontalAlignment', 'center', 'FontWeight', 'bold', 'Color', [0.5 0.5 0.5]);
                set(ax, 'XTick', [], 'YTick', []);
                box(ax, 'on');
                
            case '1D FFT amplitude profile'
                if isfield(data, 'range_power_db')
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
                if isfield(data, 'adc_cube_matlab')
                    real_trace = double(data.adc_cube_matlab(:, ch_idx, chp, frm));
                    imag_trace = zeros(size(real_trace)); % Synthesize zero ref for real-only
                    hold(ax, 'on');
                    plot(ax, data.adc_time_axis_s, real_trace, 'b-', 'LineWidth', 1);
                    plot(ax, data.adc_time_axis_s, imag_trace, 'r-', 'LineWidth', 1);
                    hold(ax, 'off');
                    xlabel(ax, 'Time (sec)');
                    ylabel(ax, 'ADC Codes');
                    grid(ax, 'on');
                    legend(ax, {'Real', 'Imag (Zero Ref)'}, 'Location', 'northeast', ...
                           'FontName', style.fontName, 'FontSize', 8);
                else
                    text(ax, 0.5, 0.5, 'Error loading Time Domain', 'HorizontalAlignment', 'center');
                end
                
            otherwise
                text(ax, 0.5, 0.5, 'Unavailable for this capture', 'HorizontalAlignment', 'center', ...
                     'FontWeight', 'bold', 'Color', [0.5 0.5 0.5]);
                set(ax, 'XTick', [], 'YTick', []);
                title(ax, ['Unsupported: ' plotType], 'Interpreter', 'none');
                box(ax, 'on');
        end
    end
end
