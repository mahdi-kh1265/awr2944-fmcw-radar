# Implementation Plan: Restoring the Stable Standalone Viewer

## Objective
Abandon the brittle `adc_data.fig` UI shell (native adapter) and fully establish our own `buildMmwsCompatibleShell.m` as the stable production viewer. The standalone viewer will visually approximate mmWave Studio while strictly enforcing code correctness, single-source-of-truth state management, and robust UI interactions (playback, sliders, plot toggling).

## Phase A & B: Independent Viewer & State Management
- In Python, change the default viewer launch mode to `"standalone"`.
- Keep `"native"` as `"native_experimental"` to preserve our work for future TI debugging.
- In `dcaViewerMain.m` and `buildMmwsCompatibleShell.m`, replace ad-hoc `handles` properties with a strictly canonical `state` structure:
  - `state.payload`
  - `state.currentFrame`, `state.currentChirp`, `state.currentRx`
  - `state.frameCount`, `state.chirpsPerFrame`, `state.rxCount`
  - `state.isPlaying`, `state.timer`
  - `state.handles`
- Replace any scattered plot updates with a single `refreshViewer(fig)` that reads `state = guidata(fig)` and routes updates correctly.

## Phase C & D: UI Construction & Validation
- Fully populate `buildMmwsCompatibleShell.m` to generate:
  - Frame & Chirp controls (slider, < button, > button, label).
  - Play/Stop button.
  - Four plot-type dropdowns (Top-Left, Top-Right, Bottom-Left, Bottom-Right).
  - Channel selectors (`Chan 1` to `Chan 4`).
  - Programmed and Calculated parameter tables.
- All sliders will enforce integer limits and steps (`[1/max, 10/max]`).
- Validate that zero TI callback names (`play_from_current_point_onwards`, `chirp_slider`, etc.) are attached to *any* object in the figure.

## Phase E: Playback Implementation
- `toggle_play(fig)` will create a single MATLAB `timer` running at 5 Hz (0.2s period).
- On each tick, it advances `state.currentFrame` and wraps around or stops cleanly.
- `on_close` will trap figure closure, stop/delete the timer safely, and prevent any stack trace warnings.

## Phase F & G: Plotting and Parameters
- **Top Left:** 2D Range-Doppler map (Raw, no CFAR red stripe).
- **Bottom Left:** 1D Range Profile (Distance vs dBFS).
- **Bottom Middle:** Time Domain Trace (Blue=Real, Red=Zeros for AWR2944 real-only).
- **Top Right:** Hardcoded "Angle estimation unavailable for this capture".
- **Parameter Table:** Programmed and Calculated values derived purely from `state.payload.profile` (Real format, 8 frames, 128 chirps, 256 samples).

## Phase H: Direct Callback Tests
- Write `test_viewer_callbacks.m` to open the viewer with a dummy `viewer_payload.mat` payload.
- Programmatically invoke the function handles assigned to the buttons, sliders, and dropdowns.
- Assert that `state` updates correctly and plots refresh without throwing *any* MATLAB errors.

## Phase I & J: End-to-End Hardware Validation
- After MATLAB tests pass, perform a genuine Python UDP capture of 9 frames (with 1 frame dropped as guard) -> 8 frame canonical dataset.
- Confirm exactly `4,718,592` bytes received, parsing cleanly to `[8, 128, 4, 256]` int16 array.
- Process via `run_pipeline`, dump to `viewer_payload.mat`, and launch the new standalone viewer.
- Validate interaction visually.

## User Feedback Required
> [!NOTE]
> Please approve this plan. It shifts priority entirely to reliability by discarding the buggy `.fig` extraction. I will implement the MATLAB scripts, run the callback tests, perform the live capture, and document the final viewer behavior in the walkthrough.
