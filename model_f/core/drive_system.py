"""Drive computation and impulse generation for Model F.

Transforms hormone levels into behavioral drive vectors and discrete
impulse events. No dependency on hormone_state.py — operates purely on
numpy arrays of hormone values.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import exp

import numpy as np


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Impulse:
    """A discrete behavioral impulse emitted when a drive crosses a threshold
    or changes rapidly."""

    tick: int                         # when generated
    drive_name: str                   # which drive dimension
    intensity: float                  # 0.0 to 1.0
    urgency: float                    # rate of change that triggered it
    source_hormones: dict[str, float] # hormone snapshot at generation time


@dataclass
class DriveConfig:
    """Configuration for a single drive dimension."""

    name: str
    hormone_weights: np.ndarray  # shape (6,) — signed weights per hormone
    bias: float = 0.0
    activation: str = "sigmoid"  # "sigmoid", "relu", or "linear"


# ---------------------------------------------------------------------------
# Default drive configurations
# ---------------------------------------------------------------------------
# Hormone index order: dopamine(0), serotonin(1), cortisol(2),
#                      norepinephrine(3), oxytocin(4), endorphin(5)

DEFAULT_DRIVE_CONFIGS: list[DriveConfig] = [
    DriveConfig(
        name="seek_novelty",
        hormone_weights=np.array([1.2, -0.8, 0.0, 0.3, 0.0, 0.0]),
        bias=-0.5,
    ),
    DriveConfig(
        name="withdraw",
        hormone_weights=np.array([0.0, -0.3, 1.0, -0.5, 0.0, 0.0]),
        bias=-0.5,
    ),
    DriveConfig(
        name="engage",
        hormone_weights=np.array([0.6, 0.0, -0.3, 1.0, 0.0, 0.0]),
        bias=-0.5,
    ),
    DriveConfig(
        name="rest",
        hormone_weights=np.array([0.0, 1.0, 0.0, -0.7, 0.0, 0.8]),
        bias=-0.5,
    ),
    DriveConfig(
        name="seek_comfort",
        hormone_weights=np.array([0.0, -0.3, 0.5, 0.0, 1.0, 0.0]),
        bias=-0.5,
    ),
    DriveConfig(
        name="express",
        hormone_weights=np.array([0.8, 0.0, -0.5, 0.7, 0.0, 0.0]),
        bias=-0.5,
    ),
]


# ---------------------------------------------------------------------------
# Activation helpers
# ---------------------------------------------------------------------------

def _sigmoid(raw: float) -> float:
    """Steeper sigmoid scaled by 4 to spread the [0,1] range."""
    return 1.0 / (1.0 + exp(-4.0 * raw))


def _clamped(raw: float) -> float:
    """Clamp to [0, 1]."""
    return min(max(raw, 0.0), 1.0)


_ACTIVATIONS = {
    "sigmoid": _sigmoid,
    "relu": _clamped,
    "linear": _clamped,
}


# ---------------------------------------------------------------------------
# DriveSystem
# ---------------------------------------------------------------------------

class DriveSystem:
    """Computes behavioral drive vectors from hormone levels and emits
    discrete impulse events when drives cross thresholds or change rapidly."""

    def __init__(
        self,
        drive_configs: list[DriveConfig] | None = None,
        impulse_threshold: float = 0.7,
        change_sensitivity: float = 0.15,
        refractory_ticks: int = 10,
    ) -> None:
        self._configs = drive_configs if drive_configs is not None else DEFAULT_DRIVE_CONFIGS
        self._impulse_threshold = impulse_threshold
        self._change_sensitivity = change_sensitivity
        self._refractory_ticks = refractory_ticks

        # Build weight matrix: shape (n_drives, 6)
        self._weight_matrix = np.stack(
            [cfg.hormone_weights for cfg in self._configs]
        )
        self._biases = np.array([cfg.bias for cfg in self._configs])
        self._activation_fns = [
            _ACTIVATIONS[cfg.activation] for cfg in self._configs
        ]

        # Internal state for impulse detection
        self._previous_drives: np.ndarray | None = None
        self._refractory_counters: dict[int, int] = {}  # drive_index -> remaining ticks

    # -- properties ----------------------------------------------------------

    @property
    def drive_names(self) -> list[str]:
        return [cfg.name for cfg in self._configs]

    # -- core computation ----------------------------------------------------

    def compute_drives(self, hormone_levels: np.ndarray) -> np.ndarray:
        """Compute drive vector from hormone levels.

        For each drive: ``raw = weights @ hormones + bias``, then apply
        the configured activation function.

        Parameters
        ----------
        hormone_levels : np.ndarray
            Shape ``(6,)`` hormone values, each in [0, 1].

        Returns
        -------
        np.ndarray
            Shape ``(n_drives,)`` drive values, each in [0, 1].
        """
        raw = self._weight_matrix @ hormone_levels + self._biases
        drives = np.array(
            [fn(r) for fn, r in zip(self._activation_fns, raw)]
        )
        return drives

    def check_impulses(
        self,
        tick: int,
        current_drives: np.ndarray,
        hormone_snapshot: dict[str, float],
    ) -> list[Impulse]:
        """Compare current drives against previous drives and emit impulses.

        An :class:`Impulse` is emitted for a drive dimension when **either**:

        1. **Threshold crossing** — the drive exceeds ``impulse_threshold``
           *and* was at or below the threshold on the previous tick.
        2. **Rapid change** — ``abs(current - previous)`` exceeds
           ``change_sensitivity``.

        Both conditions respect per-drive refractory periods: after an
        impulse fires, the drive is suppressed for ``refractory_ticks``
        ticks.

        Parameters
        ----------
        tick : int
            Current simulation tick.
        current_drives : np.ndarray
            Drive vector from :meth:`compute_drives`.
        hormone_snapshot : dict[str, float]
            Hormone name -> value mapping at this tick.

        Returns
        -------
        list[Impulse]
            Possibly empty list of impulses generated this tick.
        """
        impulses: list[Impulse] = []

        # Decrement refractory counters
        expired = []
        for idx, remaining in self._refractory_counters.items():
            if remaining <= 1:
                expired.append(idx)
            else:
                self._refractory_counters[idx] = remaining - 1
        for idx in expired:
            del self._refractory_counters[idx]

        # First tick — no previous state to compare against
        if self._previous_drives is None:
            self._previous_drives = current_drives.copy()
            return impulses

        for i, cfg in enumerate(self._configs):
            # Skip drives still in refractory period
            if i in self._refractory_counters:
                continue

            prev = self._previous_drives[i]
            curr = current_drives[i]
            change = curr - prev

            fire = False

            # Condition 1: threshold crossing
            if curr > self._impulse_threshold and prev <= self._impulse_threshold:
                fire = True

            # Condition 2: rapid change
            if abs(change) > self._change_sensitivity:
                fire = True

            if fire:
                impulses.append(
                    Impulse(
                        tick=tick,
                        drive_name=cfg.name,
                        intensity=float(curr),
                        urgency=float(change),
                        source_hormones=dict(hormone_snapshot),
                    )
                )
                self._refractory_counters[i] = self._refractory_ticks

        # Store current drives for next comparison
        self._previous_drives = current_drives.copy()

        return impulses

    def step(
        self,
        tick: int,
        hormone_levels: np.ndarray,
        hormone_names: list[str],
    ) -> tuple[np.ndarray, list[Impulse]]:
        """Convenience method: compute drives, check impulses, return both.

        Parameters
        ----------
        tick : int
            Current simulation tick.
        hormone_levels : np.ndarray
            Shape ``(6,)`` hormone values.
        hormone_names : list[str]
            Hormone names in the same order as ``hormone_levels``, used to
            build the snapshot dict stored in each :class:`Impulse`.

        Returns
        -------
        tuple[np.ndarray, list[Impulse]]
            ``(drive_vector, impulses)``
        """
        drives = self.compute_drives(hormone_levels)
        snapshot = {name: float(val) for name, val in zip(hormone_names, hormone_levels)}
        impulses = self.check_impulses(tick, drives, snapshot)
        return drives, impulses
