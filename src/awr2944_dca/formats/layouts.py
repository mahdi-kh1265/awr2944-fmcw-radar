"""Binary layout abstraction for DCA1000 ADC captures.

Each layout encodes how raw int16 samples in adc_data.bin are interleaved
across LVDS lanes, RX channels, and I/Q components.

Layout status flags:
    swra581b_reference  — Implementation is derived from TI SWRA581B app note
                          MATLAB snippets and data-format diagrams.
    lab_validated       — Implementation has been tested against real hardware
                          captures from our exact setup and confirmed correct.

IMPORTANT: No layout is "validated" until it has been tested against a real
capture from the specific device + DCA1000 setup.  The SWRA581B app note
gives reference examples for older xWR12xx/xWR14xx/xWR16xx/IWR6843 devices
but does not explicitly cover AWR2944.
"""

from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from typing import ClassVar

import numpy as np

from awr2944_dca.config.schema import RadarConfig


class BinaryLayout(ABC):
    """Abstract base class for DCA1000 binary data layouts.

    Subclasses must implement:
        - reshape_samples(): convert flat int16 array → radar cube
        - expected_file_size(): compute expected file size for a config
    """

    name: ClassVar[str]
    description: ClassVar[str]

    # Status flags — see module docstring for definitions
    swra581b_reference: ClassVar[bool] = False
    lab_validated: ClassVar[bool] = False
    requires_real_capture_validation: ClassVar[bool] = False
    source: ClassVar[str] = ""

    def warn_if_unvalidated(self) -> None:
        """Emit a warning if this layout has not been validated on real hardware."""
        if not self.lab_validated:
            warnings.warn(
                f"Layout '{self.name}' has NOT been validated against real hardware captures. "
                f"Parse results may be incorrect.  Validation checklist: file size, RX order, "
                f"IQ/real mode, chirp ordering, frame ordering, LVDS lane mapping, "
                f"TDM-MIMO virtual antenna ordering, Doppler sign convention.",
                UserWarning,
                stacklevel=3,
            )

    @abstractmethod
    def reshape_samples(
        self,
        raw: np.ndarray,
        config: RadarConfig,
    ) -> np.ndarray:
        """Reshape a flat int16 sample array into a radar cube.

        Args:
            raw: Flat array of int16 samples read from adc_data.bin.
            config: Validated radar configuration.

        Returns:
            For real ADC:    float32 array with shape [frames, chirps, rx, samples]
            For complex ADC: complex64 array with shape [frames, chirps, rx, samples]
        """

    @abstractmethod
    def expected_file_size(self, config: RadarConfig) -> int:
        """Compute the expected adc_data.bin file size in bytes for a config."""

    @abstractmethod
    def pack_cube(
        self,
        cube: np.ndarray,
        config: RadarConfig,
    ) -> np.ndarray:
        """Pack a radar cube back into flat int16 samples (for synthetic tests).

        Args:
            cube: Radar cube [frames, chirps, rx, samples], float32 or complex64.
            config: Validated radar configuration.

        Returns:
            Flat int16 array matching the binary layout format.
        """


# ---------------------------------------------------------------------------
# SWRA581B reference layouts
# ---------------------------------------------------------------------------


class Xwr14xxComplex4Lane(BinaryLayout):
    """xWR12xx/xWR14xx DCA1000: 4 LVDS lanes, complex (I+Q), 4 RX.

    From SWRA581B Section 3.2.1 / Figure 6 / MATLAB readDCA1000.m:
    Data is interleaved across 4 lanes (one per RX).  Within each lane,
    I and Q samples alternate: [I0, Q0, I1, Q1, ...].

    The MATLAB code reshapes as:
        fileData = reshape(adcData, numLanes, []);
        for i = 1:numLanes
            retVal(i,:) = fileData(i, 1:2:end) + 1j*fileData(i, 2:2:end);
    """

    name = "xwr14xx_complex_4lane"
    description = (
        "xWR12xx/xWR14xx DCA1000 4-lane complex layout (SWRA581B reference). "
        "4 LVDS lanes, 4 RX, I+Q interleaved per lane."
    )
    swra581b_reference = True
    lab_validated = False  # Not validated on our hardware

    def reshape_samples(
        self,
        raw: np.ndarray,
        config: RadarConfig,
    ) -> np.ndarray:
        self.warn_if_unvalidated()

        num_rx = config.hardware.num_rx
        num_lanes = 4
        samples_per_chirp = config.adc.samples_per_chirp
        chirps_per_frame = config.frame.chirps_per_frame
        num_frames = config.frame.num_frames

        # Reshape to [lanes, total_samples_per_lane]
        lane_data = raw.reshape(num_lanes, -1, order="F")
        # Deinterleave I and Q within each lane
        # lane_data shape: [num_lanes, total_iq_pairs * 2]
        i_data = lane_data[:, 0::2].astype(np.float32)
        q_data = lane_data[:, 1::2].astype(np.float32)
        complex_data = i_data + 1j * q_data

        # Now complex_data shape: [num_rx, total_complex_samples]
        # Reshape to [num_rx, num_frames * chirps * samples]
        # Then to [frames, chirps, rx, samples]
        complex_data = complex_data.reshape(
            num_rx, num_frames, chirps_per_frame, samples_per_chirp
        )
        # Transpose from [rx, frame, chirp, sample] → [frame, chirp, rx, sample]
        cube = complex_data.transpose(1, 2, 0, 3)
        return cube

    def expected_file_size(self, config: RadarConfig) -> int:
        # Complex: 2 int16 per sample (I + Q) per RX
        return (
            config.adc.samples_per_chirp
            * config.hardware.num_rx
            * config.frame.chirps_per_frame
            * config.frame.num_frames
            * 4  # 2 bytes I + 2 bytes Q
        )

    def pack_cube(
        self,
        cube: np.ndarray,
        config: RadarConfig,
    ) -> np.ndarray:
        # cube: [frames, chirps, rx, samples] complex64
        # → [rx, frames, chirps, samples]
        data = cube.transpose(2, 0, 1, 3)
        num_rx = config.hardware.num_rx
        # Flatten to [rx, total_samples]
        data = data.reshape(num_rx, -1)
        # Interleave I and Q
        total_samples = data.shape[1]
        interleaved = np.empty((num_rx, total_samples * 2), dtype=np.float32)
        interleaved[:, 0::2] = data.real
        interleaved[:, 1::2] = data.imag
        # Reshape to flat using Fortran order (column-major = lane interleave)
        flat = interleaved.reshape(-1, order="F").astype(np.int16)
        return flat


class Xwr16xxComplex2Lane(BinaryLayout):
    """xWR16xx/IWR6843 DCA1000: 2 LVDS lanes, complex, 4 RX.

    From SWRA581B Section 3.2.2 / MATLAB readDCA1000.m:
    2 LVDS lanes carry 4 RX channels.  Each lane carries 2 RX with I/Q
    interleaved.  Data order: [L1_I0, L2_I0, L1_Q0, L2_Q0, L1_I1, ...].
    """

    name = "xwr16xx_complex_2lane"
    description = (
        "xWR16xx/IWR6843 DCA1000 2-lane complex layout (SWRA581B reference). "
        "2 LVDS lanes, 4 RX packed into 2 lanes, I+Q interleaved."
    )
    swra581b_reference = True
    lab_validated = False

    def reshape_samples(
        self,
        raw: np.ndarray,
        config: RadarConfig,
    ) -> np.ndarray:
        self.warn_if_unvalidated()

        num_rx = config.hardware.num_rx
        samples_per_chirp = config.adc.samples_per_chirp
        chirps_per_frame = config.frame.chirps_per_frame
        num_frames = config.frame.num_frames

        # SWRA581B 2-lane complex: 4 values interleaved per "group"
        # [L1_I, L2_I, L1_Q, L2_Q] for each sample index
        # Reshape: take groups of 4 across 2 lanes
        lane_data = raw.reshape(4, -1, order="F")
        # lane_data rows: [L1_I, L2_I, L1_Q, L2_Q]
        # RX0 = L1_I + j*L1_Q, RX1 = L2_I + j*L2_Q
        # For 4 RX: L1 carries RX0,RX1 and L2 carries RX2,RX3
        # The exact mapping depends on the device — using SWRA581B convention

        # Build complex per-RX data
        rx_data = np.empty((num_rx, lane_data.shape[1]), dtype=np.complex64)
        rx_data[0] = lane_data[0].astype(np.float32) + 1j * lane_data[2].astype(np.float32)
        rx_data[1] = lane_data[1].astype(np.float32) + 1j * lane_data[3].astype(np.float32)

        if num_rx > 2:
            # For 4-RX: additional RX channels interleaved in subsequent samples
            # This is a simplified model — real 2-lane 4-RX packing is more complex
            # and device-specific. Mark as requiring validation.
            warnings.warn(
                "xWR16xx 2-lane with >2 RX: interleave pattern may need adjustment. "
                "Only 2-RX mapping is directly from SWRA581B.",
                UserWarning,
                stacklevel=2,
            )

        # Use only the RX channels we can confidently parse
        actual_rx = min(num_rx, 2)
        data = rx_data[:actual_rx]

        data = data.reshape(actual_rx, num_frames, chirps_per_frame, samples_per_chirp)
        cube = data.transpose(1, 2, 0, 3)
        return cube

    def expected_file_size(self, config: RadarConfig) -> int:
        return (
            config.adc.samples_per_chirp
            * config.hardware.num_rx
            * config.frame.chirps_per_frame
            * config.frame.num_frames
            * 4  # complex: 2 bytes I + 2 bytes Q
        )

    def pack_cube(
        self,
        cube: np.ndarray,
        config: RadarConfig,
    ) -> np.ndarray:
        # Simplified 2-RX packing
        data = cube.transpose(2, 0, 1, 3)  # [rx, frame, chirp, sample]
        num_rx = data.shape[0]
        data = data.reshape(num_rx, -1)
        total_samples = data.shape[1]

        # Interleave as [L1_I, L2_I, L1_Q, L2_Q]
        interleaved = np.empty((4, total_samples), dtype=np.float32)
        interleaved[0] = data[0].real
        interleaved[1] = data[1].real if num_rx > 1 else np.zeros(total_samples)
        interleaved[2] = data[0].imag
        interleaved[3] = data[1].imag if num_rx > 1 else np.zeros(total_samples)

        flat = interleaved.reshape(-1, order="F").astype(np.int16)
        return flat


# ---------------------------------------------------------------------------
# AWR2944 layout (unvalidated)
# ---------------------------------------------------------------------------


class Awr2944Real2LaneInterleavedCandidate(BinaryLayout):
    """AWR2944 DCA1000: 2 LVDS lanes, real ADC, 4 RX.
    
    Candidate A: Interleaved (ch_interleave = 0)
    
    Expected binary format:
    With 2 LVDS lanes and 4 RX in real mode, data is interleaved across
    lanes with 2 RX per lane per sample clock:
        [L1_RX0, L2_RX2, L1_RX1, L2_RX3, L1_RX0, L2_RX2, ...]
    """
    
    name = "awr2944_real_2lane_interleaved_candidate"
    description = (
        "AWR2944 2-lane real ADC (Candidate A: Interleaved). "
        "RX channels cycle per sample clock."
    )
    swra581b_reference = False
    lab_validated = False
    requires_real_capture_validation = True
    source = "TI install audit; AWR2944-specific parser not found locally"

    def reshape_samples(
        self,
        raw: np.ndarray,
        config: RadarConfig,
    ) -> np.ndarray:
        self.warn_if_unvalidated()

        num_rx = config.hardware.num_rx
        samples_per_chirp = config.adc.samples_per_chirp
        chirps_per_frame = config.frame.chirps_per_frame
        num_frames = config.frame.num_frames

        # Reshape: de-interleave lanes using Fortran order (column-major)
        lane_data = raw.reshape(num_rx, -1, order="F")

        # Convert to float32 (real-valued cube)
        real_data = lane_data.astype(np.float32)

        # Reshape to [rx, frames, chirps, samples]
        real_data = real_data.reshape(
            num_rx, num_frames, chirps_per_frame, samples_per_chirp
        )

        # Transpose to canonical order [frame, chirp, rx, sample]
        cube = real_data.transpose(1, 2, 0, 3)
        return cube

    def expected_file_size(self, config: RadarConfig) -> int:
        return (
            config.adc.samples_per_chirp
            * config.hardware.num_rx
            * config.frame.chirps_per_frame
            * config.frame.num_frames
            * 2
        )

    def pack_cube(
        self,
        cube: np.ndarray,
        config: RadarConfig,
    ) -> np.ndarray:
        data = cube.transpose(2, 0, 1, 3)
        num_rx = config.hardware.num_rx
        data = data.reshape(num_rx, -1)
        flat = data.reshape(-1, order="F").astype(np.int16)
        return flat


class Awr2944Real2LaneNoninterleavedCandidate(BinaryLayout):
    """AWR2944 DCA1000: 2 LVDS lanes, real ADC, 4 RX.
    
    Candidate B: Non-Interleaved (ch_interleave = 1)
    
    Expected binary format:
    All samples for RX0, then all samples for RX1, etc.
        [RX0_s0, RX0_s1, ..., RX0_sN, RX1_s0, RX1_s1, ...]
    
    This matches TI's rawDataReader.m assumption for known 2-lane devices.
    """
    
    name = "awr2944_real_2lane_noninterleaved_candidate"
    description = (
        "AWR2944 2-lane real ADC (Candidate B: Non-Interleaved). "
        "All samples per RX arrive contiguously per chirp."
    )
    swra581b_reference = False
    lab_validated = False
    requires_real_capture_validation = True
    source = "TI install audit; AWR2944-specific parser not found locally"

    def reshape_samples(
        self,
        raw: np.ndarray,
        config: RadarConfig,
    ) -> np.ndarray:
        self.warn_if_unvalidated()

        num_rx = config.hardware.num_rx
        samples_per_chirp = config.adc.samples_per_chirp
        chirps_per_frame = config.frame.chirps_per_frame
        num_frames = config.frame.num_frames

        # Reshape directly to [frame, chirp, rx, sample] using C order
        real_data = raw.reshape(
            num_frames, chirps_per_frame, num_rx, samples_per_chirp, order="C"
        )
        cube = real_data.astype(np.float32)
        return cube

    def expected_file_size(self, config: RadarConfig) -> int:
        return (
            config.adc.samples_per_chirp
            * config.hardware.num_rx
            * config.frame.chirps_per_frame
            * config.frame.num_frames
            * 2
        )

    def pack_cube(
        self,
        cube: np.ndarray,
        config: RadarConfig,
    ) -> np.ndarray:
        # Cube is already [frame, chirp, rx, sample]
        # Non-interleaved writes RX sequentially within each chirp.
        # So we just flatten the whole cube in C order!
        flat = cube.reshape(-1, order="C").astype(np.int16)
        return flat


# ---------------------------------------------------------------------------
# Layout registry
# ---------------------------------------------------------------------------

_LAYOUT_REGISTRY: dict[str, BinaryLayout] = {}


def _register_defaults() -> None:
    """Register the built-in layouts."""
    for layout_cls in [
        Xwr14xxComplex4Lane,
        Xwr16xxComplex2Lane,
        Awr2944Real2LaneInterleavedCandidate,
        Awr2944Real2LaneNoninterleavedCandidate,
    ]:
        layout = layout_cls()
        _LAYOUT_REGISTRY[layout.name] = layout


_register_defaults()


def get_layout(name: str) -> BinaryLayout:
    """Look up a layout by name.

    Raises:
        KeyError: If the layout name is not registered.
    """
    if name not in _LAYOUT_REGISTRY:
        available = ", ".join(sorted(_LAYOUT_REGISTRY.keys()))
        raise KeyError(
            f"Unknown layout '{name}'.  Available layouts: {available}"
        )
    return _LAYOUT_REGISTRY[name]


def list_layouts() -> list[str]:
    """Return the names of all registered layouts."""
    return sorted(_LAYOUT_REGISTRY.keys())


def register_layout(layout: BinaryLayout) -> None:
    """Register a custom layout."""
    _LAYOUT_REGISTRY[layout.name] = layout
