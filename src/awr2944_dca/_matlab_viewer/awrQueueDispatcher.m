function awrQueueDispatcher(cmd, token, queue_dir)
% awrQueueDispatcher - Manage the queue-based dispatcher timer.
%
% Called once at startup and once at shutdown via COM. All subsequent
% viewer control is handled by the timer on MATLAB's event loop — no
% further synchronous COM calls touch the viewer figure or graphics tree.
%
% awrQueueDispatcher('start', token, queueDir)
%   Discovers the existing viewer figure by name, tags it with the session
%   token, creates subdirectories, and starts a fixedSpacing timer at 0.1 s.
%
% awrQueueDispatcher('stop', token, queueDir)
%   Stops and deletes the dispatcher timer. Does not close the figure.

    switch cmd
        % ------------------------------------------------------------------
        case 'start'
            fig_name = 'mmWave Studio PostProc (AWR2944 Clone)';
            figs = findall(0, 'Type', 'figure', 'Name', fig_name);
            if isempty(figs)
                error('AWR:dispatcher:figureNotFound', ...
                      'Viewer figure "%s" not found after launch.', fig_name);
            end
            target_fig = figs(1);

            % Tag the figure with the session token so awrDispatchOneTick
            % can find it without relying on the figure name alone.
            setappdata(target_fig, 'AWR_SessionToken', token);

            % Create the per-session queue directories
            for sub = {'requests', 'responses', 'data'}
                d = fullfile(queue_dir, sub{1});
                if ~exist(d, 'dir'), mkdir(d); end
            end

            % Start the dispatcher timer.
            % fixedSpacing: next tick starts 0.1s after the current one ends.
            % BusyMode=drop: if the timer fires while a tick is still running
            %   (shouldn't happen with fixedSpacing, but belt-and-suspenders),
            %   the extra fire is dropped rather than queued.
            t = timer( ...
                'Name',          ['AWR_Dispatcher_' token], ...
                'ExecutionMode', 'fixedSpacing', ...
                'BusyMode',      'drop', ...
                'Period',        0.1, ...
                'TimerFcn',      @(~,~) awrDispatchOneTick(token, queue_dir), ...
                'ErrorFcn',      @(~,e) awr_log_timer_error(token, queue_dir, e), ...
                'UserData',      token ...
            );
            start(t);

        % ------------------------------------------------------------------
        case 'stop'
            timers = timerfind('Name', ['AWR_Dispatcher_' token]);
            for k = 1:length(timers)
                try stop(timers(k));  catch; end
                try delete(timers(k)); catch; end
            end

        % ------------------------------------------------------------------
        otherwise
            error('AWR:dispatcher:unknownCommand', ...
                  'Unknown awrQueueDispatcher command: %s', cmd);
    end
end

function awr_log_timer_error(token, queue_dir, evt)
    try
        log_path = fullfile(queue_dir, 'controller_log.jsonl');
        fid = fopen(log_path, 'a', 'n', 'UTF-8');
        if fid ~= -1
            msg = '';
            if isfield(evt, 'Data') && isa(evt.Data, 'MException')
                msg = getReport(evt.Data, 'extended', 'hyperlinks', 'off');
            elseif isfield(evt, 'Data') && isfield(evt.Data, 'message')
                msg = evt.Data.message;
            end
            log_entry = struct( ...
                'timestamp', datestr(now, 'yyyy-mm-ddTHH:MM:SS.FFF'), ...
                'event', 'timer_error', ...
                'token', token, ...
                'request_id', 'unknown', ...
                'action', 'timer_callback', ...
                'output_path', '', ...
                'error_message', msg ...
            );
            fprintf(fid, '%s\n', jsonencode(log_entry));
            fclose(fid);
        end
    catch
    end
end
