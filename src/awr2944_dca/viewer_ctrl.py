"""
COM Automation Controller for the existing MATLAB viewer.

Architecture: Python/COM enqueues JSON requests to a per-session filesystem
queue. A MATLAB-side timer (awrDispatchOneTick, Period=0.1 s, fixedSpacing)
dequeues them on MATLAB's event loop — between graphics update traversals —
executes each action against the existing tagged viewer figure, and writes a
JSON response. Python polls the response file.

Only two synchronous COM calls touch MATLAB:
  1. At launch: addpath + dcaViewerMain + awrQueueDispatcher('start', ...)
  2. At shutdown: awrQueueDispatcher('stop', ...) then eng.Quit()

All viewer figure/guidata/axes/graphics access happens inside the MATLAB
timer callback, never from a synchronous COM call.
"""

from __future__ import annotations

import json
import logging
import shutil
import time
import uuid
from pathlib import Path
from typing import Any, TYPE_CHECKING

import scipy.io as sio

from awr2944_dca.viewer import export_viewer_payload

if TYPE_CHECKING:
    from awr2944_dca.lab import RadarCapture

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Supported export formats and their MATLAB-compatible extensions
# ---------------------------------------------------------------------------
_EXPORT_FORMATS = {"png", "jpeg", "jpg", "tiff", "pdf", "svg"}


def _validate_format(fmt: str) -> str:
    """Normalise and validate an export format string."""
    fmt = fmt.lower().strip()
    if fmt not in _EXPORT_FORMATS:
        raise ValueError(
            f"Unsupported export format '{fmt}'. "
            f"Choose from: {sorted(_EXPORT_FORMATS)}"
        )
    return fmt

# ---------------------------------------------------------------------------
# Polling constants
# ---------------------------------------------------------------------------
_POLL_INTERVAL_S  = 0.05    # 50 ms between filesystem polls
_WAIT_SLEEP_S     = 0.10    # sleep between wait_ready re-enqueues


class ViewerExportUnsupportedError(NotImplementedError):
    """Raised when an automated MATLAB graphics export is attempted."""
    pass


class ViewerData:
    """Read-only access to the generated viewer payload."""

    def __init__(self, capture_dir: Path):
        self._path = capture_dir / "viewer_payload" / "viewer_payload.mat"

    @property
    def path(self) -> Path:
        return self._path

    @property
    def exists(self) -> bool:
        return self._path.exists()

    def load(self) -> dict[str, Any]:
        """Load the existing payload. Does NOT regenerate it."""
        if not self.exists:
            raise FileNotFoundError(f"Viewer payload not found at {self._path}")
        return sio.loadmat(str(self._path), squeeze_me=True, struct_as_record=False)


class ControlledViewer:
    """
    Queue-based controller for the existing MATLAB viewer dashboard.

    Public API mirrors the previous synchronous controller; internals use
    filesystem-based request/response queues so that no COM call ever
    touches the live graphics hierarchy.
    """

    # Map Python human names → MATLAB axes handle names in guidata
    PLOT_MAP = {
        "range_doppler": "axRD",
        "detections":    "axDet",
        "range_profile": "ax1D",
        "time_domain":   "axTime",
    }

    def __init__(
        self,
        capture_id:  str,
        payload_dir: Path,
        control_dir: Path,
        eng:         Any,
        token:       str,
    ):
        self.capture_id  = capture_id
        self.payload_dir = payload_dir
        self.token       = token
        self.eng         = eng

        # Per-session queue subdirectories
        self._ctrl_dir = control_dir
        self._req_dir  = control_dir / "requests"
        self._resp_dir = control_dir / "responses"
        self._data_dir = control_dir / "data"

        # Exports go into payload_dir/exports (unchanged from previous API)
        self.exports_dir = payload_dir / "exports"
        self.exports_dir.mkdir(exist_ok=True)

        self._is_closed = False
        self._failed = False
        # frame_count is populated on first wait_ready (via actual_frame context)
        # and can be explicitly set by open_controlled_viewer after wait_ready.
        self._frame_count: int | None = None

    # ------------------------------------------------------------------
    def __enter__(self) -> ControlledViewer:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self._failed = True
        self.close()

    # ------------------------------------------------------------------
    # Internal queue primitives
    # ------------------------------------------------------------------

    def _enqueue(self, action: str, timeout: float = 30.0, **kwargs) -> dict[str, Any]:
        """
        Write one request JSON atomically and poll for the response.
        Only one request may be in-flight at a time (enforced by caller).
        """
        if self._is_closed:
            raise RuntimeError("Viewer is closed.")

        request_id = uuid.uuid4().hex
        req = {
            "request_id": request_id,
            "token":      self.token,
            "action":     action,
            "args":       kwargs,
        }

        # Atomic write: write to .tmp then rename
        req_file = self._req_dir / f"req_{self.token}_{request_id}.json"
        tmp_file = self._req_dir / f"req_{self.token}_{request_id}.tmp"
        try:
            tmp_file.write_text(json.dumps(req), encoding="utf-8")
            tmp_file.rename(req_file)
        except Exception as exc:
            self._failed = True
            raise RuntimeError(f"Queue protocol error (write failed): {exc}") from exc

        logger.debug("Enqueued %s request_id=%s", action, request_id)
        return self._poll_response(request_id, action, timeout)

    def _poll_response(self, request_id: str, action: str, timeout: float) -> dict[str, Any]:
        """Block-poll for the response JSON file. Reads and deletes it on receipt."""
        resp_file = self._resp_dir / f"resp_{self.token}_{request_id}.json"
        deadline  = time.monotonic() + timeout

        while time.monotonic() < deadline:
            if resp_file.exists():
                try:
                    text = resp_file.read_text(encoding="utf-8")
                    resp = json.loads(text)
                    resp_file.unlink(missing_ok=True)
                except (json.JSONDecodeError, OSError) as exc:
                    if isinstance(exc, json.JSONDecodeError):
                        self._failed = True
                        raise RuntimeError(f"Malformed JSON response from MATLAB: {exc}")
                    time.sleep(_POLL_INTERVAL_S)
                    continue

                if not resp.get("success", False):
                    self._failed = True
                    raise RuntimeError(
                        f"MATLAB Error [{resp.get('error_identifier', '')}]: "
                        f"{resp.get('error_message', 'Unknown error')}"
                    )

                # Load optional .mat data sidecar (large arrays)
                output_path = resp.get("output_path") or ""
                if output_path and output_path.endswith(".mat"):
                    mat_path = Path(output_path)
                    if mat_path.exists():
                        try:
                            data = sio.loadmat(str(mat_path), squeeze_me=True)
                        except Exception as exc:
                            self._failed = True
                            raise RuntimeError(f"Failed to load sidecar .mat: {exc}")
                        mat_path.unlink(missing_ok=True)
                        resp["_data"] = {k: v for k, v in data.items()
                                         if not k.startswith("_")}
                    else:
                        self._failed = True
                        raise RuntimeError(f"Expected sidecar data file missing: {mat_path}")

                return resp

            time.sleep(_POLL_INTERVAL_S)

        # Timed out: clean up the stale request if it was never consumed
        stale = self._req_dir / f"req_{self.token}_{request_id}.json"
        stale.unlink(missing_ok=True)
        self._failed = True
        raise TimeoutError(
            f"No MATLAB response for action='{action}' within {timeout:.1f}s\n"
            f"Session token: {self.token}\n"
            f"Request ID:    {request_id}\n"
            f"Session dir:   {self._ctrl_dir}\n"
            f"Request path:  {stale}\n"
            f"Expected resp: {resp_file}"
        )

    # ------------------------------------------------------------------
    # Public API — signatures unchanged from previous controller
    # ------------------------------------------------------------------

    def wait_ready(self, timeout: float = 60.0) -> None:
        """
        Poll until the MATLAB dashboard is fully rendered and all four axes
        have graphics children. Sends repeated wait_ready requests so that
        MATLAB never blocks inside the timer waiting for the viewer.
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._is_closed:
                raise RuntimeError("Viewer was closed during wait_ready.")
            try:
                resp = self._enqueue("wait_ready", timeout=5.0)
                if resp.get("found"):
                    # Capture frame_count from the first successful ready response
                    if self._frame_count is None and resp.get("frame_count"):
                        self._frame_count = int(resp["frame_count"])
                    logger.info("Viewer ready (frame=%s)", resp.get("actual_frame"))
                    return
            except TimeoutError:
                self._failed = False  # Reset failed flag since this is expected during startup
                
            time.sleep(_WAIT_SLEEP_S)
        raise TimeoutError(f"Viewer did not become ready within {timeout:.1f}s")

    @property
    def frame_count(self) -> int:
        """
        Total number of canonical frames (0-based upper bound exclusive).
        Populated after wait_ready(). Raises RuntimeError if not yet known.
        """
        if self._frame_count is None:
            raise RuntimeError(
                "frame_count is not yet known. Call wait_ready() first."
            )
        return self._frame_count

    def list_plots(self) -> list[str]:
        return list(self.PLOT_MAP.keys())

    def get_frame(self) -> int:
        """Return current frame index (0-based)."""
        resp = self._enqueue("get_frame")
        return int(resp["actual_frame"]) - 1   # MATLAB 1-based → Python 0-based

    def set_frame(self, frame: int) -> None:
        """Set displayed frame (0-based). Validates bounds before enqueueing."""
        # Python-side bounds check (defense-in-depth: MATLAB dispatcher also validates)
        if self._frame_count is not None:
            if frame < 0 or frame >= self._frame_count:
                raise ValueError(
                    f"Frame index {frame} is out of range. "
                    f"Valid frame indices are 0\u2013{self._frame_count - 1}."
                )
        resp = self._enqueue("set_frame", frame=frame + 1)  # Python 0-based → MATLAB 1-based
        actual = int(resp["actual_frame"]) - 1
        if actual != frame:
            raise RuntimeError(
                f"set_frame({frame}) requested but MATLAB reports frame {actual}"
            )

    def get_displayed_plot(self, name: str) -> dict[str, Any]:
        if name not in self.PLOT_MAP:
            raise ValueError(f"Unknown plot '{name}'. Choose from: {list(self.PLOT_MAP)}")
        resp = self._enqueue("get_displayed_plot", plot_name=self.PLOT_MAP[name])
        raw = resp.get("_data", {})
        return self._normalize_plot_data(name, raw)

    @staticmethod
    def _normalize_plot_data(name: str, raw: dict) -> dict[str, Any]:
        """
        Normalise the raw data dict returned by the MATLAB dispatcher into a
        stable Python structure. MATLAB-loaded arrays are left as numpy arrays.
        Absent or None fields are given sensible defaults.
        """
        import numpy as np

        def _str(v) -> str:
            """Coerce MATLAB char arrays / numpy string scalars to str."""
            if v is None:
                return ""
            if isinstance(v, np.ndarray):
                if v.size == 0:
                    return ""
                return str(v.flat[0])
            return str(v)

        def _arr_or_none(v):
            if v is None:
                return None
            arr = np.atleast_1d(v)
            return arr if arr.size > 0 else None

        # Normalise object type string
        raw_type = _str(raw.get("obj_type") or raw.get("type"))
        if "image" in raw_type.lower() or "CData" in raw:
            plot_type = "image"
        elif "line" in raw_type.lower():
            plot_type = "line"
        elif raw_type == "empty" or not raw_type:
            plot_type = "empty"
        else:
            plot_type = raw_type

        return {
            "name":  name,
            "type":  plot_type,
            "title": _str(raw.get("Title")),
            "XData": _arr_or_none(raw.get("XData")),
            "YData": _arr_or_none(raw.get("YData")),
            "CData": _arr_or_none(raw.get("CData")),
            "CLim":  _arr_or_none(raw.get("CLim")),
            "XLim":  _arr_or_none(raw.get("XLim")),
            "YLim":  _arr_or_none(raw.get("YLim")),
        }

    def export_plot(
        self,
        name: str,
        *,
        path: Path | None = None,
        format: str = "png",
        resolution: int = 300,
    ) -> Path:
        """Export a single axes image from the existing MATLAB viewer."""
        raise ViewerExportUnsupportedError(
            "Automated MATLAB graphics export is unavailable in this headless COM environment.\n"
            "Please open the MATLAB dashboard and use the built-in export functionality, "
            "or take an OS screenshot."
        )

    def export_all(
        self,
        *,
        directory: Path | None = None,
        format: str = "png",
        resolution: int = 300,
    ) -> dict[str, Path]:
        """Export all four axes images from the existing MATLAB viewer."""
        raise ViewerExportUnsupportedError(
            "Automated MATLAB graphics export is unavailable in this headless COM environment.\n"
            "Please open the MATLAB dashboard and use the built-in export functionality, "
            "or take an OS screenshot."
        )

    def export_window(
        self,
        *,
        path: Path | None = None,
        format: str = "png",
        resolution: int = 150,
    ) -> Path:
        """Export the full MATLAB dashboard window."""
        raise ViewerExportUnsupportedError(
            "Automated MATLAB graphics export is unavailable in this headless COM environment.\n"
            "Please open the MATLAB dashboard and use the built-in export functionality, "
            "or take an OS screenshot."
        )

    def save_figure(self, *, path: Path | None = None) -> Path:
        """Save the MATLAB figure as a .fig file."""
        raise ViewerExportUnsupportedError(
            "Automated MATLAB .fig saving is unavailable in this headless COM environment.\n"
            "Please open the MATLAB dashboard and use the File -> Save option."
        )

    def close(self) -> None:
        """Close the viewer. Idempotent: safe to call multiple times."""
        if self._is_closed:
            # Already closed — this is success, not an error.
            return
        self._is_closed = True

        # Enqueue the close action — MATLAB timer closes the tagged figure.
        # If the MATLAB instance has already exited this will timeout; treat
        # as non-fatal since the session will be cleaned up regardless.
        try:
            self._enqueue("close", timeout=10.0)
        except Exception as exc:
            logger.debug("close enqueue did not confirm (instance may already be gone): %s", exc)

        # Stop the dispatcher timer via COM (safe: figure is already closed,
        # no graphics traversal can be in progress)
        ctrl_dir_str = str(self._ctrl_dir).replace("\\", "\\\\")
        try:
            self.eng.Execute(
                f"awrQueueDispatcher('stop', '{self.token}', '{ctrl_dir_str}');"
            )
        except Exception as exc:
            self._failed = True
            logger.warning("Timer stop failed: %s", exc)

        # Quit the dedicated MATLAB instance
        try:
            self.eng.Quit()
        except Exception as exc:
            self._failed = True
            logger.warning("eng.Quit() failed: %s", exc)

        # Clean up the session directory on clean shutdown
        if not self._failed:
            try:
                shutil.rmtree(self._ctrl_dir)
                logger.info("Session directory removed: %s", self._ctrl_dir)
            except Exception as exc:
                logger.warning("Could not remove session dir %s: %s", self._ctrl_dir, exc)
        else:
            logger.warning("Session failed. Preserving directory: %s", self._ctrl_dir)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def open_controlled_viewer(
    capture:                "RadarCapture",
    clim_mode:              str   = "fixed_global",
    display_dynamic_range_db: float = 40.0,
) -> ControlledViewer:
    """
    Export the viewer payload, launch the MATLAB dashboard, start the queue
    dispatcher, and return a ControlledViewer.

    Exactly one synchronous COM command is issued to MATLAB before control
    transfers to the queue:

        addpath(...);
        dcaViewerMain('payload.mat');
        awrQueueDispatcher('start', token, queueDir);

    No subsequent COM call touches the viewer figure, guidata, axes, callbacks,
    or graphics properties until awrQueueDispatcher('stop', ...) at shutdown.
    """
    try:
        import win32com.client
    except ImportError:
        raise ImportError(
            "pywin32 is required for the controlled viewer. "
            "Install via `pip install pywin32`."
        )

    # Canonical ADC file required (no guard frames)
    canonical_path = capture.raw.canonical_path
    if canonical_path is None or not canonical_path.exists():
        raise FileNotFoundError(
            "Canonical ADC file (adc_data_canonical.bin) is required. "
            "The native capture includes guard frames and must not be used. "
            f"Expected: {capture.raw.canonical_path}"
        )

    prof = capture._resolve_viewer_profile()
    if prof is None:
        raise ValueError("Could not resolve RadarProfile from manifests.")

    # Output directories
    payload_dir = canonical_path.parent / "viewer_payload"
    payload_dir.mkdir(exist_ok=True)
    payload_path = payload_dir / "viewer_payload.mat"

    # Session-scoped control directory
    token       = uuid.uuid4().hex
    control_dir = payload_dir / ".control" / token
    req_dir     = control_dir / "requests"
    resp_dir    = control_dir / "responses"
    data_dir    = control_dir / "data"
    for d in (control_dir, req_dir, resp_dir, data_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Export viewer payload (unchanged DSP path)
    export_viewer_payload(
        canonical_path,
        payload_path,
        prof,
        clim_mode=clim_mode,
        display_dynamic_range_db=display_dynamic_range_db,
        mode="standalone",
    )

    matlab_dir = (
        Path(__file__).parent.parent.parent / "matlab" / "viewer"
    ).resolve()

    # Paths for MATLAB (escape backslashes)
    def _mpath(p: Path) -> str:
        return str(p).replace("\\", "\\\\")

    # Launch MATLAB COM server
    try:
        eng = win32com.client.DispatchEx("Matlab.Application.Single")
    except Exception as exc:
        raise RuntimeError(f"Failed to start MATLAB COM server: {exc}") from exc

    try:
        # Single compound COM command: addpath + viewer + dispatcher start
        # No further COM calls touch the graphics hierarchy until shutdown.
        launch_cmd = (
            f"addpath('{_mpath(matlab_dir)}'); "
            f"dcaViewerMain('{_mpath(payload_path)}'); "
            f"awrQueueDispatcher('start', '{token}', '{_mpath(control_dir)}');"
        )
        eng.Execute(launch_cmd)

    except Exception:
        try:
            eng.Quit()
        except Exception:
            pass
        raise

    return ControlledViewer(
        capture_id=capture.capture_id,
        payload_dir=payload_dir,
        control_dir=control_dir,
        eng=eng,
        token=token,
    )
