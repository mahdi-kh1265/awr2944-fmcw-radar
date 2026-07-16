function awrViewerControl(action, token, temp_mat_path, varargin)
% awrViewerControl - DEPRECATED. DO NOT USE.
%
% This helper used synchronous COM (eng.Execute) to dispatch viewer actions.
% It is superseded by the queue-based dispatcher:
%   awrQueueDispatcher.m  — timer lifecycle (start / stop)
%   awrDispatchOneTick.m  — timer callback; safe event-loop execution
%
% Retained for reference and diagnosis until the queued controller passes
% real-MATLAB acceptance testing. Do not call this function at runtime.
%
% Original description:
%   Stateless helper for Python COM automation.
%   Exclusively targets the figure tagged with AWR_SessionToken = token.
%   Does not replot or calculate DSP. Writes results to temp_mat_path.
%
% Changes that were applied before deprecation:
%   wait_ready: drawnow before signalling ready; post-drain revalidation.
%   set_frame:  drawnow before/after callback; bounded retry on
%               MATLAB:graphics:ModificationDuringUpdate; actual frame returned.


    try
        % Find the target figure
        figs = findall(0, 'Type', 'figure');
        target_fig = [];
        for i = 1:length(figs)
            if strcmp(getappdata(figs(i), 'AWR_SessionToken'), token)
                target_fig = figs(i);
                break;
            end
        end

        if isempty(target_fig)
            if strcmp(action, 'wait_ready') || strcmp(action, 'close')
                % wait_ready doesn't error if not found yet, just returns empty
                res = struct('success', true, 'found', false);
                save_result(temp_mat_path, res);
                return;
            else
                error('Figure with SessionToken %s not found.', token);
            end
        end

        % For actions requiring the state
        state = guidata(target_fig);

        res = struct('success', true);

        switch action
            case 'wait_ready'
                % --- Drain initial rendering before signalling ready ---
                % Full drawnow (not limitrate) flushes all deferred property
                % changes and waits for the update traversal to complete.
                drawnow;

                % Revalidate after drain: figure handle, guidata, required
                % handles struct, all four axes, and their initial graphics
                % children must all be intact.
                if ~ishandle(target_fig)
                    error('AWR:wait_ready:figureGone', ...
                          'Figure handle became invalid after drawnow.');
                end
                state = guidata(target_fig);
                if isempty(state)
                    error('AWR:wait_ready:guidataMissing', ...
                          'guidata is empty after drawnow.');
                end
                required_axes = {'axRD', 'axDet', 'ax1D', 'axTime'};
                for k = 1:length(required_axes)
                    ax_name = required_axes{k};
                    if ~isfield(state.handles, ax_name)
                        error('AWR:wait_ready:missingHandle', ...
                              'Required handle %s missing after drawnow.', ax_name);
                    end
                    ax = state.handles.(ax_name);
                    if ~ishandle(ax)
                        error('AWR:wait_ready:axisGone', ...
                              'Axis %s handle invalid after drawnow.', ax_name);
                    end
                    ch = get(ax, 'Children');
                    if isempty(ch)
                        error('AWR:wait_ready:axisEmpty', ...
                              'Axis %s has no graphics children after drawnow.', ax_name);
                    end
                end

                res.found = true;

            case 'list_plots'
                res.plots = {'axRD', 'axDet', 'ax1D', 'axTime'};

            case 'get_frame'
                if isfield(state, 'currentFrame')
                    res.frame = state.currentFrame;
                else
                    res.frame = 1;
                end

            case 'set_frame'
                % Note: Python sends 1-based frame to MATLAB
                frame = str2double(varargin{1});
                if frame >= 1 && frame <= state.frameCount

                    % --- Flush any in-progress rendering before touching state ---
                    drawnow;

                    % Set slider value (triggers no callback itself)
                    set(state.handles.sldFrame, 'Value', frame);

                    % Invoke the existing unchanged callback
                    cb = get(state.handles.sldFrame, 'Callback');
                    invoke_cb(cb, state.handles.sldFrame);

                    % --- Drain the new frame render before returning to Python ---
                    drawnow;

                    % Return the actual frame stored by the callback, not the
                    % requested value, so Python can detect a mismatch.
                    updatedState = guidata(target_fig);
                    res.frame = updatedState.currentFrame;

                else
                    error('Frame %d out of bounds (1 - %d)', frame, state.frameCount);
                end

            case 'get_displayed_plot'
                plot_name = varargin{1}; % 'axRD', 'axDet', etc.
                if ~isfield(state.handles, plot_name)
                    error('Unknown plot name: %s', plot_name);
                end
                ax = state.handles.(plot_name);

                % Extract properties
                ch = get(ax, 'Children');
                if isempty(ch)
                    res.type = 'empty';
                else
                    % Only take the first primary data child
                    obj = ch(end); % Children order is top-to-bottom, so bottom is usually the main plot
                    res.type = get(obj, 'Type');

                    if isprop(obj, 'XData')
                        res.XData = get(obj, 'XData');
                    end
                    if isprop(obj, 'YData')
                        res.YData = get(obj, 'YData');
                    end
                    if isprop(obj, 'CData')
                        res.CData = get(obj, 'CData');
                    end
                end

                % Get axis limits and titles
                if isprop(ax, 'Title') && ~isempty(get(ax, 'Title'))
                    res.Title = get(get(ax, 'Title'), 'String');
                else
                    res.Title = '';
                end
                res.XLim = get(ax, 'XLim');
                res.YLim = get(ax, 'YLim');
                res.CLim = get(ax, 'CLim');

            case 'export_plot'
                plot_name = varargin{1};
                out_path = varargin{2};
                resolution = varargin{3};

                if ~isfield(state.handles, plot_name)
                    error('Unknown plot name: %s', plot_name);
                end
                ax = state.handles.(plot_name);
                exportgraphics(ax, out_path, 'Resolution', str2double(resolution));
                res.exported_path = out_path;

            case 'export_window'
                out_path = varargin{1};
                resolution = varargin{2};
                exportgraphics(target_fig, out_path, 'Resolution', str2double(resolution));
                res.exported_path = out_path;

            case 'save_figure'
                out_path = varargin{1};
                savefig(target_fig, out_path);
                res.exported_path = out_path;

            case 'close'
                close(target_fig);
                res.closed = true;

            otherwise
                error('Unknown action: %s', action);
        end

        save_result(temp_mat_path, res);

    catch ME
        res = struct('success', false, 'error_message', ME.message, 'error_id', ME.identifier);
        save_result(temp_mat_path, res);
    end

end

% ---------------------------------------------------------------------------
% invoke_cb - invoke the existing slider callback with one bounded retry
%             for MATLAB:graphics:ModificationDuringUpdate only.
% ---------------------------------------------------------------------------
function invoke_cb(cb, slider_handle)
    try
        if iscell(cb)
            feval(cb{1}, slider_handle, [], cb{2:end});
        else
            cb(slider_handle, []);
        end
    catch ME
        if strcmp(ME.identifier, 'MATLAB:graphics:ModificationDuringUpdate')
            % Graphics pipeline was still flushing. Drain it and retry once.
            drawnow;
            if iscell(cb)
                feval(cb{1}, slider_handle, [], cb{2:end});
            else
                cb(slider_handle, []);
            end
            drawnow;
        else
            % Any other error propagates immediately — no suppression.
            rethrow(ME);
        end
    end
end

% ---------------------------------------------------------------------------
function save_result(path, res)
    % Write struct to MAT file
    % Save with v6 to avoid issues with Python scipy.io.loadmat
    save(path, 'res', '-v6');
end
