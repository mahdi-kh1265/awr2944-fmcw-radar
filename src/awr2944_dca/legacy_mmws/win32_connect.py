"""Win32 API backend for mmWave Studio GUI automation."""

from __future__ import annotations

import time
import ctypes
from pathlib import Path
from typing import Callable, Any, Optional

from awr2944_dca.legacy_mmws.gui_connect import attach_mmwave_studio, ClickFlowResult, ProgressLogger, read_device_status, inspect_connection_tab

try:
    import win32gui  # type: ignore
    import win32con  # type: ignore
    import win32api  # type: ignore
except ImportError:
    pass

def dump_win32_tree(hwnd: int, indent: int = 0, lines: list[str] | None = None) -> list[str]:
    """Recursively dump the win32 HWND tree."""
    if lines is None:
        lines = []

    try:
        class_name = win32gui.GetClassName(hwnd)
        text = win32gui.GetWindowText(hwnd)
        ctrl_id = win32gui.GetDlgCtrlID(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        is_visible = win32gui.IsWindowVisible(hwnd)
        
        prefix = "  " * indent
        lines.append(f"{prefix}HWND={hwnd} ID={ctrl_id} Class={class_name!r} Text={text!r} Rect={rect} Visible={is_visible}")
        
        def enum_child(child_hwnd, _):
            dump_win32_tree(child_hwnd, indent + 1, lines)
        
        win32gui.EnumChildWindows(hwnd, enum_child, None)
    except Exception as e:
        lines.append(f"{'  ' * indent}Error processing HWND {hwnd}: {e}")
        
    return lines


def inspect_win32(
    pid: int | None = None,
    title_regex: str | None = None,
    probe_dir: Path | None = None,
    verbose_log: Callable[[str], None] | None = None,
) -> None:
    """Dump the Win32 window tree to a file."""
    vlog = verbose_log or (lambda s: None)
    
    if probe_dir is None:
        probe_dir = Path("ti") / "probe_logs"
    probe_dir.mkdir(parents=True, exist_ok=True)
    
    app, window = attach_mmwave_studio(pid, title_regex, probe_dir, vlog)
    
    hwnd = window.wrapper_object().handle
    vlog(f"Starting Win32 inspection from Top HWND: {hwnd}")
    
    lines = dump_win32_tree(hwnd)
    
    out_path = probe_dir / "win32_inspect_tree.txt"
    out_path.write_text("\\n".join(lines), encoding="utf-8")
    vlog(f"Wrote {len(lines)} HWND nodes to {out_path}")


def find_hwnd_by_text(parent_hwnd: int, text_match: str, class_match: str = "") -> int:
    """Find a child HWND by partial text match and optional class match."""
    found_hwnd = 0
    
    def enum_child(child_hwnd, _):
        nonlocal found_hwnd
        if found_hwnd != 0:
            return
            
        try:
            text = win32gui.GetWindowText(child_hwnd)
            class_name = win32gui.GetClassName(child_hwnd)
            
            if text_match in text:
                if not class_match or class_match in class_name:
                    found_hwnd = child_hwnd
        except Exception:
            pass
            
    win32gui.EnumChildWindows(parent_hwnd, enum_child, None)
    return found_hwnd


def send_bm_click(hwnd: int):
    """Send BM_CLICK message to a button/radio."""
    win32api.SendMessage(hwnd, win32con.BM_CLICK, 0, 0)


def select_combobox_string(hwnd: int, text: str) -> bool:
    """Select a string in a combobox using CB_SELECTSTRING."""
    # CB_SELECTSTRING = 0x014D
    res = win32api.SendMessage(hwnd, 0x014D, -1, text)
    if res != -1:  # CB_ERR
        # Also send CBN_SELCHANGE (1) to parent via WM_COMMAND (0x0111)
        parent = win32gui.GetParent(hwnd)
        ctrl_id = win32gui.GetDlgCtrlID(hwnd)
        # MAKEWPARAM(ctrl_id, CBN_SELCHANGE) -> (1 << 16) | (ctrl_id & 0xFFFF)
        wparam = (1 << 16) | (ctrl_id & 0xFFFF)
        win32api.SendMessage(parent, win32con.WM_COMMAND, wparam, hwnd)
        return True
    return False


def click_flow_win32(
    pid: int | None = None,
    title_regex: str | None = None,
    com_port: str = "COM6",
    baud: int = 115200,
    probe_dir: Path | None = None,
    verbose_log: Callable[[str], None] | None = None,
) -> ClickFlowResult:
    """Execute the Connection tab flow using Win32 API messages."""
    vlog = verbose_log or (lambda s: None)
    
    if probe_dir is None:
        probe_dir = Path("ti") / "probe_logs"
    probe_dir.mkdir(parents=True, exist_ok=True)
    
    progress = ProgressLogger(probe_dir / "win32_click_flow_progress.jsonl")
    progress.log("win32_click_flow_started")
    
    app, window = attach_mmwave_studio(pid, title_regex, probe_dir, vlog)
    
    # We will use pywinauto just to find the rich-client control wrappers for 
    # things that are hard to find via pure HWND text (since WinForms heavily relies on UIA/AutomationId)
    controls = inspect_connection_tab(window, verbose_log=vlog)
    
    def get_hwnd(ctrl) -> Optional[int]:
        if ctrl is None: return None
        try:
            return ctrl.wrapper_object().handle
        except Exception:
            return None

    hwnd_77ghz = get_hwnd(controls.frequency_radio)
    hwnd_dev = get_hwnd(controls.device_variant_radio)
    hwnd_set = get_hwnd(controls.set_button)
    hwnd_com = get_hwnd(controls.com_combo)
    hwnd_baud = get_hwnd(controls.baud_combo)
    hwnd_conn = get_hwnd(controls.rs232_connect_button)
    
    if not (hwnd_77ghz and hwnd_dev and hwnd_set and hwnd_com and hwnd_baud and hwnd_conn):
        progress.log("hwnds_missing")
        return ClickFlowResult(status="HWNDS_MISSING", error="Could not resolve HWNDs for all required controls.")
        
    # 1. 77 GHz
    progress.log("win32_click_77ghz")
    send_bm_click(hwnd_77ghz)
    time.sleep(0.5)
    
    # 2. Device Variant
    progress.log("win32_click_device_variant")
    send_bm_click(hwnd_dev)
    time.sleep(0.5)
    
    # 3. Set(1)
    progress.log("win32_click_set1")
    send_bm_click(hwnd_set)
    
    # Wait for Set(1) in output
    progress.log("win32_wait_set1")
    set_ok = False
    for _ in range(30):
        time.sleep(1.0)
        try:
            out_doc = controls.output_document
            if out_doc is not None:
                doc_text = out_doc.window_text()
                if "SOPControl" in doc_text or "FullReset" in doc_text:
                    set_ok = True
                    break
        except Exception:
            pass
            
    if not set_ok:
        progress.log("win32_set1_timeout")
        return ClickFlowResult(status="SET1_NOT_CONFIRMED", error="Win32 Set(1) action timed out.")
        
    # 4. COM / Baud
    progress.log("win32_set_com", com_port)
    if not select_combobox_string(hwnd_com, com_port):
        progress.log("win32_com_select_failed")
        return ClickFlowResult(status="COM_PORT_NOT_AVAILABLE", error=f"Could not select {com_port} via CB_SELECTSTRING")
        
    progress.log("win32_set_baud", str(baud))
    select_combobox_string(hwnd_baud, str(baud))
    
    time.sleep(0.5)
    
    # 5. Connect
    progress.log("win32_click_connect")
    send_bm_click(hwnd_conn)
    
    # 6. Poll status
    progress.log("win32_poll_device_status")
    device_status: dict[str, Any] = {}
    for _ in range(15):
        time.sleep(1.0)
        device_status = read_device_status(window, controls, vlog)
        if device_status.get("valid"):
            break
            
    if device_status.get("valid"):
        progress.log("win32_connection_success", device_status.get("raw_text", ""))
        return ClickFlowResult(
            status="CONNECTION_WIN32_SUCCESS",
            device_status_text=device_status.get("raw_text", ""),
            details=device_status,
        )
        
    raw_text = device_status.get("raw_text", "")
    progress.log("win32_connection_failed", raw_text)
    return ClickFlowResult(
        status="DEVICE_STATUS_NOT_VALID",
        device_status_text=raw_text,
        details=device_status,
        error=f"Device Status does not contain expected AWR2944/GP/SOP:2: {raw_text!r}",
    )
