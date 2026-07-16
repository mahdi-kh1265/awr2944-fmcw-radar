import struct
import threading
import time
import socket
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from awr2944_dca.direct_udp_capture import UdpReceiverThread

def create_packet(seq: int, byte_count: int, payload_len: int) -> bytes:
    # 10 byte header
    seq_bytes = struct.pack('<I', seq & 0xFFFFFFFF)
    # 48 bit byte count
    bc_lower = byte_count & 0xFFFFFFFF
    bc_upper = (byte_count >> 32) & 0xFFFF
    bc_bytes = struct.pack('<I', bc_lower) + struct.pack('<H', bc_upper)
    header = seq_bytes + bc_bytes
    return header + b'\x00' * payload_len

class MockSocket:
    def __init__(self, packets):
        self.packets = packets
        self.idx = 0
        self.closed = False
        
    def recvfrom(self, bufsize):
        if self.idx < len(self.packets):
            p = self.packets[self.idx]
            self.idx += 1
            return p, ('127.0.0.1', 4096)
        # Block forever
        time.sleep(0.1)
        raise socket.timeout()
        
    def setsockopt(self, *args): pass
    def bind(self, *args): pass
    def settimeout(self, *args): pass
    def close(self): self.closed = True

def run_synthetic_capture(tmp_path, packets, expected_bytes=None):
    if expected_bytes is None:
        expected_bytes = sum(len(p)-10 for p in packets)
        
    out_file = tmp_path / "adc_data.bin"
    capture_started_event = threading.Event()
    ready_event = threading.Event()
    
    capture = UdpReceiverThread(
        out_file, 
        expected_bytes, 
        host_ip="127.0.0.1",
        data_port=0,
        capture_started_event=capture_started_event, 
        ready_event=ready_event
    )
    
    # Close the real socket to avoid leaks before swapping in the mock
    if hasattr(capture, 'sock') and capture.sock:
        capture.sock.close()
        
    # Mock socket
    mock_sock = MockSocket(packets)
    capture.sock = mock_sock
    
    try:
        # start in background
        capture.start()
        capture_started_event.set()
        capture.join(timeout=2.0)
    finally:
        capture.stop()
        if hasattr(capture, 'sock') and capture.sock and getattr(capture.sock, 'closed', False) is False:
            capture.sock.close()
        capture.join(timeout=1.0)
        assert not capture.is_alive(), "UdpReceiverThread leaked!"
    
    return capture

def test_pristine_stream(tmp_path):
    packets = [
        create_packet(0, 0, 1456),
        create_packet(1, 1456, 1456),
        create_packet(2, 2912, 1456),
        create_packet(3, 4368, 100), # partial final wire packet
    ]
    cap = run_synthetic_capture(tmp_path, packets)
    assert cap.sequence_gaps == 0
    assert cap.byte_counter_discontinuity_count == 0
    assert cap.missing_payload_bytes == 0
    assert cap.overlap_payload_bytes == 0
    assert cap.received_bytes == 3*1456 + 100

def test_partial_consumption_of_final_packet(tmp_path):
    packets = [
        create_packet(0, 0, 1456),
        create_packet(1, 1456, 1456),
        create_packet(2, 2912, 1456),
    ]
    # We only want 3000 bytes total, so we consume partial of 3rd packet
    cap = run_synthetic_capture(tmp_path, packets, expected_bytes=3000)
    assert cap.sequence_gaps == 0
    assert cap.byte_counter_discontinuity_count == 0
    assert cap.missing_payload_bytes == 0
    assert cap.overlap_payload_bytes == 0
    assert cap.received_bytes == 3000

def test_missing_packet(tmp_path):
    packets = [
        create_packet(0, 0, 1456),
        # missing packet 1 (bc: 1456)
        create_packet(2, 2912, 1456),
    ]
    cap = run_synthetic_capture(tmp_path, packets)
    assert cap.sequence_gaps == 1
    assert cap.byte_counter_discontinuity_count == 1
    assert cap.missing_payload_bytes == 1456
    assert cap.overlap_payload_bytes == 0

def test_duplicate_packet(tmp_path):
    packets = [
        create_packet(0, 0, 1456),
        create_packet(1, 1456, 1456),
        create_packet(1, 1456, 1456), # duplicate
        create_packet(2, 2912, 1456),
    ]
    cap = run_synthetic_capture(tmp_path, packets)
    assert cap.sequence_gaps == 1
    assert cap.byte_counter_discontinuity_count == 1
    assert cap.missing_payload_bytes == 0
    assert cap.overlap_payload_bytes == 1456

def test_out_of_order_packet(tmp_path):
    packets = [
        create_packet(0, 0, 1456),
        create_packet(2, 2912, 1456), # arrived early
        create_packet(1, 1456, 1456), # arrived late
        create_packet(3, 4368, 1456), 
    ]
    cap = run_synthetic_capture(tmp_path, packets)
    # transition 0->2: seq gap, missing = 1456
    # transition 2->1: seq gap (went backwards), overlap = 1456 - (-1456) = 2912 ?
    # Let's trace it:
    # 0->2: seq=2, last_seq=0 -> gap. bc=2912, last_bc=0. delta=2912. exp=1456. actual > exp -> missing += 1456
    # 2->1: seq=1, last_seq=2 -> gap(backward). bc=1456, last_bc=2912. actual_delta = 1456 - 2912 = -1456. exp=1456.
    # actual < exp (-1456 < 1456) -> overlap += 1456 - (-1456) = 2912.
    # 1->3: seq=3, last_seq=1 -> gap. bc=4368, last_bc=1456. delta=2912. exp=1456. missing += 1456.
    
    assert cap.sequence_gaps == 3
    assert cap.byte_counter_discontinuity_count == 3
    assert cap.missing_payload_bytes == 2912
    assert cap.overlap_payload_bytes == 2912

def test_nonzero_starting_byte_counter(tmp_path):
    packets = [
        create_packet(5, 500000, 1456),
        create_packet(6, 501456, 1456),
        create_packet(7, 502912, 100),
    ]
    cap = run_synthetic_capture(tmp_path, packets)
    assert cap.sequence_gaps == 0
    assert cap.byte_counter_discontinuity_count == 0
    assert cap.missing_payload_bytes == 0
    assert cap.overlap_payload_bytes == 0

def test_uint32_sequence_wraparound(tmp_path):
    packets = [
        create_packet(0xFFFFFFFF, 0, 1456),
        create_packet(0, 1456, 1456),
        create_packet(1, 2912, 1456),
    ]
    cap = run_synthetic_capture(tmp_path, packets)
    assert cap.sequence_gaps == 0
    assert cap.byte_counter_discontinuity_count == 0

def test_uint48_byte_counter_wraparound(tmp_path):
    # (1 << 48) - 1456 = 281474976709168
    bc_1 = (1 << 48) - 1456
    bc_2 = 0
    bc_3 = 1456
    
    packets = [
        create_packet(0, bc_1, 1456),
        create_packet(1, bc_2, 1456),
        create_packet(2, bc_3, 1456),
    ]
    cap = run_synthetic_capture(tmp_path, packets)
    assert cap.sequence_gaps == 0
    assert cap.byte_counter_discontinuity_count == 0
    assert cap.missing_payload_bytes == 0
    assert cap.overlap_payload_bytes == 0

def test_smoke_v1_regression(tmp_path):
    # 4,718,592 bytes = 3,240 full packets + 1,152 final bytes
    packets = []
    bc = 0
    for seq in range(3240):
        packets.append(create_packet(seq, bc, 1456))
        bc += 1456
    packets.append(create_packet(3240, bc, 1152))
    
    cap = run_synthetic_capture(tmp_path, packets)
    assert cap.received_bytes == 4718592
    assert cap.sequence_gaps == 0
    assert cap.byte_counter_discontinuity_count == 0
    assert cap.missing_payload_bytes == 0
    assert cap.overlap_payload_bytes == 0
