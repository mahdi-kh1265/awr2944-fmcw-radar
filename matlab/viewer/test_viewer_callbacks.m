function test_viewer_callbacks(payload_path)
    if nargin < 1
        payload_path = 'C:\Users\khams008\Documents\awr2944-fmcw-radar\captures\e2e_direct_001\viewer_payload.mat';
    end
    
    disp('=== 6. DSP AND VIEWER VALIDATION ===');
    disp(['1. Opening dcaViewerMain with: ', payload_path]);
    dcaViewerMain(payload_path);
    drawnow;
    pause(1);
    
    fig = gcf;
    state = guidata(fig);
    h = state.handles;
    
    disp('2. Testing frame slider iteration...');
    num_frames = state.payload.frame_count;
    for i = 1:num_frames
        set(h.sldFrame, 'Value', i);
        cb = get(h.sldFrame, 'Callback');
        cb(h.sldFrame, []);
        drawnow;
        pause(0.2);
    end
    
    disp('3. Testing plot mode switching...');
    % Switch Panel 1 to Range-Doppler (Value 2)
    set(h.p1, 'Value', 2);
    cb = get(h.p1, 'Callback');
    cb(h.p1, []);
    drawnow;
    pause(1.0);
    
    % Switch back to Raw ADC (Value 1)
    set(h.p1, 'Value', 1);
    cb(h.p1, []);
    drawnow;
    pause(0.5);
    
    disp('4. Testing Playback...');
    cb = get(h.btnPlay, 'Callback');
    cb(h.btnPlay, []);
    pause(2.0); % Let it play for a bit
    
    % Click pause (the same button handles pause if state.isPlaying == true)
    cb(h.btnPlay, []);
    drawnow;
    
    disp('5. Closing viewer cleanly...');
    close(fig);
    
    disp('=== END_TO_END_HARDWARE_VIEWER_PASS ===');
end
