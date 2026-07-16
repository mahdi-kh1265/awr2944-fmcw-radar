function dcaViewerMain(payload_path)
% dcaViewerMain - Stable Standalone Viewer for AWR2944
% Strictly enforces a single-source-of-truth state architecture.

    data = load(payload_path);
    
    if ~isfield(data, 'mode')
        data.mode = 'standalone';
    end
    
    % If native_experimental is requested, run the old experimental adapter
    if strcmp(data.mode, 'native_experimental')
        disp('Native experimental mode not supported. Use standalone.');
        return;
    end
    
    % Initialize single-source-of-truth state
    state = struct();
    state.payload = data;
    state.currentFrame = 1;
    state.currentChirp = 1;
    state.currentRx = 1;
    state.frameCount = double(data.frame_count);
    state.chirpsPerFrame = double(data.chirps_per_frame);
    state.rxCount = 4; % Canonical for AWR2944 real smoke capture
    state.isPlaying = false;
    state.timer = [];
    state.handles = struct();
    
    % Build the UI completely from scratch and manage callbacks
    buildMmwsCompatibleShell(state);
end
