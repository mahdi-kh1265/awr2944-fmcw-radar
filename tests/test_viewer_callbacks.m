function test_viewer_callbacks()
    disp('=== Starting Viewer Callback Test ===');
    
    % 1. Create a minimal dummy payload to bypass DSP parsing
    data.mode = 'standalone';
    data.frame_count = 8;
    data.chirps_per_frame = 128;
    data.adc_samples = 256;
    data.slope_hz_per_s = 29.982e12;
    data.start_frequency_hz = 77e9;
    data.idle_time_s = 100e-6;
    data.adc_start_time_s = 6e-6;
    data.ramp_end_time_s = 60e-6;
    data.sample_rate_hz = 10e6;
    data.frame_period_s = 40e-3;
    data.tx_mask = 3;
    data.sample_format = 'Real';
    
    data.range_axis_m = linspace(0, 10, 256);
    data.velocity_axis_mps = linspace(-10, 10, 128);
    data.adc_time_axis_s = linspace(0, 25.6e-6, 256);
    
    data.doppler_power_db_raw = rand(256, 128, 8) * 140;
    data.range_power_db = rand(256, 4, 128, 8) * -60;
    data.adc_cube_matlab = rand(256, 4, 128, 8) * 1000;
    
    payload_path = fullfile(tempdir, 'test_payload.mat');
    save(payload_path, '-struct', 'data');
    
    % 2. Launch Viewer
    addpath(fullfile(pwd, 'matlab', 'viewer'));
    dcaViewerMain(payload_path);
    f = gcf;
    pause(1); % Let it render
    
    state = guidata(f);
    h = state.handles;
    
    try
        % Test 1: Frame next
        disp('Testing Frame Next...');
        h.btnNextFrame.Callback(h.btnNextFrame, []);
        state = guidata(f);
        assert(state.currentFrame == 2, 'Frame did not increment');
        assert(strcmp(get(h.lblFrame, 'String'), 'Frame 2/8'), 'Frame label incorrect');
        
        % Test 2: Frame previous
        disp('Testing Frame Prev...');
        h.btnPrevFrame.Callback(h.btnPrevFrame, []);
        state = guidata(f);
        assert(state.currentFrame == 1, 'Frame did not decrement');
        
        % Test 3: Frame slider
        disp('Testing Frame Slider...');
        set(h.sldFrame, 'Value', 8);
        h.sldFrame.Callback(h.sldFrame, []);
        state = guidata(f);
        assert(state.currentFrame == 8, 'Frame slider failed');
        assert(strcmp(get(h.lblFrame, 'String'), 'Frame 8/8'), 'Frame slider label failed');
        
        % Test 4: Chirp next
        disp('Testing Chirp Next...');
        h.btnNextChirp.Callback(h.btnNextChirp, []);
        state = guidata(f);
        assert(state.currentChirp == 2, 'Chirp did not increment');
        assert(strcmp(get(h.lblChirp, 'String'), 'Chirp 2/128'), 'Chirp label incorrect');
        
        % Test 5: Chirp slider
        disp('Testing Chirp Slider...');
        set(h.sldChirp, 'Value', 128);
        h.sldChirp.Callback(h.sldChirp, []);
        state = guidata(f);
        assert(state.currentChirp == 128, 'Chirp slider failed');
        assert(strcmp(get(h.lblChirp, 'String'), 'Chirp 128/128'), 'Chirp slider label failed');
        
        % Test 6: Channel selector
        disp('Testing Channel Select...');
        set(h.ch1, 'Value', 5); % Chan 4
        h.ch1.Callback(h.ch1, []);
        
        % Test 7: Plot Selectors
        disp('Testing Plot Selectors...');
        set(h.p1, 'Value', 4); % Detection & Angle (Unsupported)
        h.p1.Callback(h.p1, []);
        set(h.p1, 'Value', 2); % 2D FFT
        h.p1.Callback(h.p1, []);
        
        % Test 8: Play
        disp('Testing Playback...');
        state.currentFrame = 1;
        guidata(f, state);
        
        % Just click play.
        h.btnPlay.Callback(h.btnPlay, []);
        pause(1.5); % Let timer tick a few times
        state = guidata(f);
        assert(state.currentFrame > 1, 'Timer did not advance frames');
        assert(strcmp(get(h.btnPlay, 'String'), 'Stop'), 'Play button did not switch to Stop');
        
        % Stop
        h.btnPlay.Callback(h.btnPlay, []);
        state = guidata(f);
        assert(~state.isPlaying, 'Timer did not stop');
        assert(strcmp(get(h.btnPlay, 'String'), 'Play'), 'Stop button did not switch back to Play');
        
        % Test 9: Parameter Tabs
        disp('Testing Param Tabs...');
        % 890, 330 is Prog, 1015, 330 is Calc
        btns = findobj(f, 'Style', 'pushbutton');
        prog_btn = btns(strcmp(get(btns, 'String'), 'Programmed Parameters'));
        calc_btn = btns(strcmp(get(btns, 'String'), 'Calculated Parameters'));
        
        calc_btn.Callback(calc_btn, []);
        prog_btn.Callback(prog_btn, []);
        
        % Test 10: Close during playback
        disp('Testing Close During Playback...');
        h.btnPlay.Callback(h.btnPlay, []);
        pause(0.5);
        close(f);
        
        disp('VIEWER_CALLBACK_TEST_PASS');
    catch ME
        disp('Error during callback testing:');
        disp(ME.message);
        if ishandle(f)
            close(f);
        end
        rethrow(ME);
    end
end
