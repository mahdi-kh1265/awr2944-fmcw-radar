"""Background subtraction for radar range-Doppler maps.

D. Saved empty-scene background subtraction (power-domain):
    P_clean = max(P_current - alpha * P_background, 0)

E. Exponential adaptive background:
    B_t = (1 - alpha) * B_{t-1} + alpha * P_t
    With target protection to prevent moving targets from contaminating
    the adaptive background.
"""

from __future__ import annotations

import numpy as np

from awr2944_dca.dsp.config import BackgroundConfig, BackgroundMode


def subtract_background(
    power_map: np.ndarray,
    config: BackgroundConfig,
    background: np.ndarray | None = None,
) -> np.ndarray:
    """Apply background subtraction.

    Parameters
    ----------
    power_map : ndarray, float32
        Current power map (linear or dB, but must match background).
    config : BackgroundConfig
    background : ndarray, optional
        Saved or adaptive background. Required for SAVED mode.

    Returns
    -------
    ndarray, float32
        Background-subtracted power map (same shape).
    """
    if config.mode == BackgroundMode.NONE:
        return power_map.copy()
    elif config.mode == BackgroundMode.SAVED:
        if background is None:
            raise ValueError("Background array required for SAVED mode")
        return _saved_subtraction(power_map, background, config.alpha)
    elif config.mode == BackgroundMode.ADAPTIVE:
        # Adaptive requires stateful updates — handled by AdaptiveBackground
        raise ValueError(
            "Use AdaptiveBackground class for adaptive mode. "
            "subtract_background() only supports SAVED mode."
        )
    else:
        raise ValueError(f"Unknown background mode: {config.mode}")


def _saved_subtraction(
    power: np.ndarray,
    background: np.ndarray,
    alpha: float,
) -> np.ndarray:
    """P_clean = max(P_current - alpha * P_background, 0)"""
    return np.maximum(power - alpha * background, 0.0).astype(np.float32)


class AdaptiveBackground:
    """Exponential adaptive background estimator with target protection.

    B_t = (1 - alpha) * B_{t-1} + alpha * P_t

    If protection_mask is True, bins where P_t significantly exceeds B_{t-1}
    are not used to update the background (preventing target contamination).
    """

    def __init__(
        self,
        shape: tuple[int, ...],
        alpha: float = 0.1,
        protection_threshold_db: float = 10.0,
        protect: bool = True,
    ):
        self.background = np.zeros(shape, dtype=np.float32)
        self.alpha = alpha
        self.protection_threshold_db = protection_threshold_db
        self.protect = protect
        self.initialized = False

    def update(self, power_map: np.ndarray) -> np.ndarray:
        """Update background and return cleaned power map.

        Returns
        -------
        ndarray
            Background-subtracted power map.
        """
        if not self.initialized:
            self.background = power_map.copy().astype(np.float32)
            self.initialized = True
            return np.zeros_like(power_map)

        if self.protect:
            # Protection mask: don't update where current >> background
            eps = np.finfo(np.float32).tiny
            ratio_db = 10.0 * np.log10(
                np.maximum(power_map, eps) / np.maximum(self.background, eps)
            )
            mask = ratio_db < self.protection_threshold_db
            alpha_map = np.where(mask, self.alpha, 0.0).astype(np.float32)
        else:
            alpha_map = self.alpha

        self.background = (
            (1.0 - alpha_map) * self.background + alpha_map * power_map
        ).astype(np.float32)

        return np.maximum(power_map - self.background, 0.0).astype(np.float32)
