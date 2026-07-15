function awrDispatchOneTick(token, queue_dir)
% awrDispatchOneTick - Timer callback for the queue-based dispatcher.
%
% Runs on MATLAB's event loop (between update traversals). Dequeues exactly
% one pending request, executes it against the existing tagged viewer figure,
% and writes a JSON response. BusyMode='drop' on the parent timer prevents
% concurrent invocations.
%
% This function must not:
%   - Recalculate DSP or replot data
%   - Create replacement axes or modify viewer callbacks
%   - Touch capture files or radar hardware

    req_dir  = fullfile(queue_dir, 'requests');
    resp_dir = fullfile(queue_dir, 'responses');
    data_dir = fullfile(queue_dir, 'data');
    log_path = fullfile(queue_dir, 'controller_log.jsonl');

    % Find the oldest pending request for this session token
    pattern = fullfile(req_dir, ['req_' token '_*.json']);
    entries = dir(pattern);
    if isempty(entries)
        return;
    end

    [~, order] = sort([entries.datenum]);
    req_file = fullfile(req_dir, entries(order(1)).name);
    
    % Request discovered but not yet read
    awr_log_event(log_path, 'request_discovered', token, 'unknown', 'unknown', '', '');

    % Parse the request — delete file immediately to prevent reprocessing
    req_id = 'unknown';
    action = 'unknown';
    try
        req_text = fileread(req_file);
        req = jsondecode(req_text);
        req_id = req.request_id;
        action = req.action;
    catch ME
        awr_delete(req_file);
        ext_rep = getReport(ME, 'extended', 'hyperlinks', 'off');
        awr_log_event(log_path, 'action_failed', token, req_id, 'unknown', '', ext_rep);
        awr_write_response(resp_dir, token, req_id, log_path, ...
            awr_error_resp('unknown', 'AWR:dispatcher:malformedRequest', ME.message, ext_rep));
        return;
    end
    awr_delete(req_file);
    awr_log_event(log_path, 'request_dequeued', token, req_id, action, '', '');

    % Find the tagged viewer figure
    target_fig = awr_find_figure(token);

    % Execute
    awr_log_event(log_path, 'action_started', token, req_id, action, '', '');
    try
        [resp, mat_payload] = awr_execute(action, req, target_fig, data_dir, token, req_id, log_path);

        % Write large array payload to .mat sidecar if present
        if ~isempty(mat_payload) && isstruct(mat_payload)
            data_path = fullfile(data_dir, ['data_' token '_' req_id '.mat']);
            tmp_path  = [data_path '.tmp'];
            save(tmp_path, '-struct', 'mat_payload', '-v7');
            movefile(tmp_path, data_path);
            resp.output_path = data_path;
        end

    catch ME
        ext_rep = getReport(ME, 'extended', 'hyperlinks', 'off');
        awr_log_event(log_path, 'action_failed', token, req_id, action, '', ext_rep);
        resp = awr_error_resp(action, ME.identifier, ME.message, ext_rep);
    end

    awr_log_event(log_path, 'response_write_started', token, req_id, action, resp.output_path, '');
    awr_write_response(resp_dir, token, req_id, log_path, resp);
    awr_log_event(log_path, 'response_written', token, req_id, action, resp.output_path, '');
end


% ===========================================================================
% Action dispatcher
% ===========================================================================
function [resp, mat_payload] = awr_execute(action, req, target_fig, data_dir, token, req_id, log_path)
    mat_payload = [];

    switch action

        % ------------------------------------------------------------------
        case 'wait_ready'
            if isempty(target_fig)
                resp = awr_resp(action, 'found', false);
                return;
            end
            state = guidata(target_fig);
            if isempty(state)
                resp = awr_resp(action, 'found', false);
                return;
            end
            required = {'axRD', 'axDet', 'ax1D', 'axTime'};
            for k = 1:length(required)
                nm = required{k};
                if ~isfield(state.handles, nm) || ...
                   ~isgraphics(state.handles.(nm), 'axes') || ...
                   isempty(get(state.handles.(nm), 'Children'))
                    resp = awr_resp(action, 'found', false);
                    return;
                end
            end
            resp = awr_resp(action, 'found', true, 'actual_frame', state.currentFrame, ...
                            'frame_count', state.frameCount);

        % ------------------------------------------------------------------
        case 'get_frame'
            state = guidata(target_fig);
            frm = 1;
            if isfield(state, 'currentFrame'), frm = state.currentFrame; end
            resp = awr_resp(action, 'actual_frame', frm);

        % ------------------------------------------------------------------
        case 'set_frame'
            frm   = req.args.frame;   % 1-based
            state = guidata(target_fig);
            if frm < 1 || frm > state.frameCount
                error('AWR:dispatcher:outOfBounds', ...
                      'Frame %d out of range (1-%d)', frm, state.frameCount);
            end
            set(state.handles.sldFrame, 'Value', frm);
            cb = get(state.handles.sldFrame, 'Callback');
            awr_invoke_cb(cb, state.handles.sldFrame);   % bounded retry inside
            updated = guidata(target_fig);
            resp = awr_resp(action, 'actual_frame', updated.currentFrame);

        % ------------------------------------------------------------------
        case 'get_displayed_plot'
            plot_name = req.args.plot_name;
            state = guidata(target_fig);
            if ~isfield(state.handles, plot_name)
                error('AWR:dispatcher:unknownPlot', 'Unknown plot: %s', plot_name);
            end
            ax = state.handles.(plot_name);
            ch = get(ax, 'Children');

            mat_payload = struct();
            if ~isempty(ch)
                obj = ch(end);
                mat_payload.obj_type = get(obj, 'Type');
                if isprop(obj, 'XData'), mat_payload.XData = get(obj, 'XData'); end
                if isprop(obj, 'YData'), mat_payload.YData = get(obj, 'YData'); end
                if isprop(obj, 'CData'), mat_payload.CData = get(obj, 'CData'); end
            else
                mat_payload.obj_type = 'empty';
            end
            mat_payload.XLim = get(ax, 'XLim');
            mat_payload.YLim = get(ax, 'YLim');
            mat_payload.CLim = get(ax, 'CLim');
            if isprop(ax, 'Title') && ~isempty(get(ax, 'Title'))
                mat_payload.Title = get(get(ax, 'Title'), 'String');
            else
                mat_payload.Title = '';
            end
            resp = awr_resp(action, 'actual_frame', guidata(target_fig).currentFrame);



        % ------------------------------------------------------------------
        case 'close'
            if ~isempty(target_fig) && isgraphics(target_fig, 'figure')
                close(target_fig);
            end
            resp = awr_resp(action);

        % ------------------------------------------------------------------
        otherwise
            error('AWR:dispatcher:unknownAction', 'Unknown action: %s', action);
    end
end


% ===========================================================================
% Helpers
% ===========================================================================

function fig = awr_find_figure(token)
    fig = [];
    figs = findall(0, 'Type', 'figure');
    for i = 1:length(figs)
        tok = getappdata(figs(i), 'AWR_SessionToken');
        if ischar(tok) && strcmp(tok, token)
            fig = figs(i);
            return;
        end
    end
end


function awr_invoke_cb(cb, slider_handle)
% Invoke the existing slider callback. Bounded retry on
% MATLAB:graphics:ModificationDuringUpdate only.
    try
        if iscell(cb)
            feval(cb{1}, slider_handle, [], cb{2:end});
        else
            cb(slider_handle, []);
        end
    catch ME
        if strcmp(ME.identifier, 'MATLAB:graphics:ModificationDuringUpdate')
            % Drain the traversal and retry exactly once
            drawnow;
            if iscell(cb)
                feval(cb{1}, slider_handle, [], cb{2:end});
            else
                cb(slider_handle, []);
            end
        else
            rethrow(ME);   % all other errors propagate immediately
        end
    end
end


function resp = awr_resp(action, varargin)
% Build a success response struct. Extra fields via key-value pairs.
    resp = struct( ...
        'success',          true, ...
        'action',           action, ...
        'actual_frame',     [], ...
        'frame_count',      [], ...
        'output_path',      '', ...
        'error_identifier', '', ...
        'error_message',    '' ...
    );
    for k = 1:2:length(varargin)
        resp.(varargin{k}) = varargin{k+1};
    end
end


function resp = awr_error_resp(action, identifier, message, report)
    if nargin < 4
        report = '';
    end
    resp = struct( ...
        'success',          false, ...
        'action',           action, ...
        'actual_frame',     [], ...
        'output_path',      '', ...
        'error_identifier', identifier, ...
        'error_message',    message, ...
        'error_report',     report ...
    );
end


function awr_write_response(resp_dir, token, req_id, log_path, resp)
    try
        tmp_path  = fullfile(resp_dir, ['resp_' token '_' req_id '.tmp']);
        resp_path = fullfile(resp_dir, ['resp_' token '_' req_id '.json']);
        
        % Ensure we don't clobber an existing response (should not happen)
        if exist(resp_path, 'file')
            awr_delete(resp_path);
        end
        
        fid = fopen(tmp_path, 'w', 'n', 'UTF-8');
        if fid == -1
            error('AWR:dispatcher:fileOpenError', 'Could not open tmp response file');
        end
        
        json = jsonencode(resp);
        fwrite(fid, json, 'char');
        fclose(fid);
        
        movefile(tmp_path, resp_path);
    catch ME
        ext_rep = getReport(ME, 'extended', 'hyperlinks', 'off');
        awr_log_event(log_path, 'action_failed', token, req_id, resp.action, '', ext_rep);
        try
            if exist('fid', 'var') && fid ~= -1
                fclose(fid);
            end
        catch; end
    end
end

function awr_delete(file_path)
    try
        if exist(file_path, 'file')
            delete(file_path);
        end
    catch
    end
end

function awr_log_event(log_path, event_name, token, req_id, action, out_path, err_msg)
    try
        fid = fopen(log_path, 'a', 'n', 'UTF-8');
        if fid ~= -1
            log_entry = struct( ...
                'timestamp', datestr(now, 'yyyy-mm-ddTHH:MM:SS.FFF'), ...
                'event', event_name, ...
                'token', token, ...
                'request_id', req_id, ...
                'action', action, ...
                'output_path', out_path, ...
                'error_message', err_msg ...
            );
            fprintf(fid, '%s\n', jsonencode(log_entry));
            fclose(fid);
        end
    catch
    end
end
