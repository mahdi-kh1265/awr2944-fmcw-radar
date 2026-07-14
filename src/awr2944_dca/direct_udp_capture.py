"""
Direct UDP Capture logic for DCA1000EVM, bypassing TI's CLI Record executable.
This allows us to maintain Python ownership of the capture buffers and avoid C# bridge / MMWS dependencies.
"""
import socket
import struct
import threading
import time
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class DirectUdpCapture:
    def __init__(self, host_ip: str = "192.168.33.30", dca_ip: str = "192.168.33.180", cmd_port: int = 4096, data_port: int = 4098):
        self.host_ip = host_ip
        self.dca_ip = dca_ip
        self.cmd_port = cmd_port
        self.data_port = data_port

    def send_command(self, cmd_code: int, timeout: float = 2.0) -> bool:
        """Send a direct DCA UDP control command and wait for ack."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind to our command port exactly to receive replies
        try:
            sock.bind((self.host_ip, self.cmd_port))
        except OSError as e:
            logger.error(f"Failed to bind to command port {self.host_ip}:{self.cmd_port} - {e}")
            raise RuntimeError(f"Could not bind to {self.cmd_port}. Is another process using it?") from e
            
        sock.settimeout(timeout)
        
        header = 0xA55A
        footer = 0xEEAA
        length = 0
        cmd_bytes = struct.pack('<H H H H', header, cmd_code, length, footer)
        
        logger.debug(f"Sending DCA command 0x{cmd_code:04X}...")
        sock.sendto(cmd_bytes, (self.dca_ip, self.cmd_port))
        
        try:
            reply, _ = sock.recvfrom(1024)
            logger.debug(f"DCA reply: {reply.hex()}")
            return True
        except socket.timeout:
            logger.error(f"DCA command 0x{cmd_code:04X} timed out")
            return False
        finally:
            sock.close()

    def start_record(self) -> bool:
        """Command 0x0005: Record Start"""
        return self.send_command(0x0005)

    def stop_record(self) -> bool:
        """Command 0x0006: Record Stop"""
        return self.send_command(0x0006)

class UdpReceiverThread(threading.Thread):
    def __init__(
        self,
        output_path: Path | str,
        expected_bytes: int,
        host_ip: str = "192.168.33.30",
        data_port: int = 4098,
        ready_event: threading.Event | None = None,
        capture_started_event: threading.Event | None = None,
        first_packet_timeout: float = 5.0,
        quiet_timeout: float = 2.0,
    ):
        super().__init__()
        self.output_path = output_path
        self.expected_bytes = expected_bytes
        self.host_ip = host_ip
        self.data_port = data_port
        
        self.ready_event = ready_event or threading.Event()
        self.capture_started_event = capture_started_event or threading.Event()
        self.stop_event = threading.Event()
        
        self.first_packet_timeout = first_packet_timeout
        self.quiet_timeout = quiet_timeout
        
        self.received_bytes = 0
        self.first_packet_received = False
        self.capture_complete = False
        self.failure_reason: str | None = None
        self.exception: Exception | None = None
        
        self.sequence_gaps = 0
        self.byte_counter_discontinuity_count = 0
        self.missing_payload_bytes = 0
        self.overlap_payload_bytes = 0
        self.packet_records = []
        self.phase = "ready"
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Increase OS buffer size to prevent dropping packets
        try:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 100 * 1024 * 1024)
        except OSError:
            logger.warning("Could not set 100MB socket receive buffer. Packet loss may occur.")
            
        try:
            self.sock.bind((self.host_ip, self.data_port))
        except OSError as e:
            self.phase = "failed"
            self.exception = e
            self.failure_reason = f"Failed to bind UDP data port: {e}"
            self.sock.close()
            raise

    def run(self):
        logger.info(f"Receiver bound to {self.host_ip}:{self.data_port}, awaiting {self.expected_bytes} bytes.")
        self.ready_event.set()
        
        self.phase = "waiting_trigger"
        
        # Interruptible wait for trigger
        while not self.capture_started_event.wait(timeout=0.1):
            if self.stop_event.is_set():
                self.phase = "stopped"
                self.sock.close()
                return

        self.phase = "waiting_first_packet"
        self.sock.settimeout(self.first_packet_timeout)
        
        last_seq = None
        last_byte_counter = None
        last_wire_payload_len = None
        
        packet_index = 0
        
        try:
            with open(self.output_path, "wb") as f:
                while self.received_bytes < self.expected_bytes and not self.stop_event.is_set():
                    try:
                        data, _ = self.sock.recvfrom(2048)
                        
                        if not self.first_packet_received:
                            self.first_packet_received = True
                            self.phase = "streaming"
                            self.sock.settimeout(self.quiet_timeout)
                        
                        if len(data) < 10:
                            continue
                            
                        # Parse header: seq (uint32), byte_count (uint64, but sent as 48-bit? Actually TI docs say 6 bytes. We use struct unpack if we can)
                        # The packet header is 10 bytes:
                        # Sequence number: 4 bytes (UINT32)
                        # Byte count: 6 bytes (UINT48)
                        seq = struct.unpack('<I', data[0:4])[0]
                        # 48-bit byte count unpacking
                        byte_count = struct.unpack('<I', data[4:8])[0] | (struct.unpack('<H', data[8:10])[0] << 32)
                        
                        wire_payload = data[10:]
                        wire_payload_len = len(wire_payload)
                        
                        remaining = self.expected_bytes - self.received_bytes
                        consumed_payload_len = min(wire_payload_len, remaining)
                        
                        f.write(wire_payload[:consumed_payload_len])
                        self.received_bytes += consumed_payload_len
                        
                        # Check sequence gaps
                        if last_seq is not None:
                            seq_delta = (seq - last_seq) & 0xFFFFFFFF
                            if seq_delta != 1:
                                self.sequence_gaps += 1
                        else:
                            seq_delta = 1 # Initial packet
                            
                        # Check byte counter gaps
                        if last_byte_counter is not None:
                            MASK48 = (1 << 48) - 1
                            actual_delta = (byte_count - last_byte_counter) & MASK48
                            
                            if seq_delta > 0x7FFFFFFF:
                                # Out of order packet, sequence went backwards
                                actual_delta = actual_delta - (1 << 48)
                                
                            expected_delta = last_wire_payload_len
                            
                            if actual_delta != expected_delta:
                                self.byte_counter_discontinuity_count += 1
                                if actual_delta > expected_delta:
                                    self.missing_payload_bytes += actual_delta - expected_delta
                                elif actual_delta < expected_delta:
                                    self.overlap_payload_bytes += expected_delta - actual_delta
                                    
                        classification = "normal"
                        if seq_delta != 1:
                            classification = "sequence_gap"
                        elif last_byte_counter is not None and actual_delta != expected_delta:
                            classification = "byte_gap"
                            
                        # It might also be the last packet
                        if self.received_bytes >= self.expected_bytes:
                            if classification == "normal":
                                classification = "last_packet"
                                
                        self.packet_records.append({
                            "packet_index": packet_index,
                            "sequence_number": seq,
                            "byte_counter": byte_count,
                            "wire_payload_length": wire_payload_len,
                            "consumed_payload_length": consumed_payload_len,
                            "arrival_time_ns": time.perf_counter_ns(),
                            "sequence_delta": seq_delta,
                            "counter_delta": actual_delta if last_byte_counter is not None else 0,
                            "classification": classification,
                        })
                        packet_index += 1

                        last_seq = seq
                        last_byte_counter = byte_count
                        last_wire_payload_len = wire_payload_len
                        
                    except socket.timeout:
                        if not self.first_packet_received:
                            self.failure_reason = f"First packet timeout ({self.first_packet_timeout}s)"
                        else:
                            self.failure_reason = f"Quiet timeout ({self.quiet_timeout}s)"
                        break
                        
        except Exception as e:
            self.exception = e
            self.failure_reason = f"Exception during capture: {e}"
        finally:
            self.sock.close()
            # Write metadata after capture loop exits
            self._write_metadata()
            
            if self.stop_event.is_set():
                self.phase = "stopped"
            elif self.received_bytes == self.expected_bytes:
                self.capture_complete = True
                self.phase = "complete"
            else:
                self.phase = "failed"
                if not self.failure_reason:
                    self.failure_reason = "Exited loop before expected bytes reached"
                    
            logger.info(
                f"Receiver stopped. Phase: {self.phase}. "
                f"Captured: {self.received_bytes}/{self.expected_bytes} bytes. "
                f"Seq Gaps: {self.sequence_gaps}, Byte Discontinuities: {self.byte_counter_discontinuity_count}"
            )

    def _write_metadata(self) -> None:
        if not self.packet_records:
            return
        meta_dir = Path(self.output_path).parent / "metadata"
        meta_dir.mkdir(parents=True, exist_ok=True)
        meta_path = meta_dir / "packet_metadata.jsonl"
        try:
            with open(meta_path, "w") as f:
                for rec in self.packet_records:
                    f.write(json.dumps(rec) + "\n")
        except Exception as e:
            logger.error(f"Failed to write packet metadata: {e}")

    def stop(self):
        self.stop_event.set()
