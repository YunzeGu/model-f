"""Hormone state engine — maintains internal hormone levels and evolves them each tick."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


@dataclass
class HormoneConfig:
    """Configuration for a single hormone."""

    name: str
    setpoint: float
    decay_rate: float
    noise_sigma: float
    circadian_amplitude: float
    circadian_phase: float
    initial_value: float | None = None


DEFAULT_HORMONE_CONFIGS: list[HormoneConfig] = [
    HormoneConfig(
        name="dopamine",
        setpoint=0.5,
        decay_rate=0.05,
        noise_sigma=0.015,
        circadian_amplitude=0.08,
        circadian_phase=0.0,
    ),
    HormoneConfig(
        name="serotonin",
        setpoint=0.6,
        decay_rate=0.03,
        noise_sigma=0.010,
        circadian_amplitude=0.10,
        circadian_phase=math.pi / 2,
    ),
    HormoneConfig(
        name="cortisol",
        setpoint=0.3,
        decay_rate=0.02,
        noise_sigma=0.012,
        circadian_amplitude=0.15,
        circadian_phase=-math.pi / 3,
    ),
    HormoneConfig(
        name="norepinephrine",
        setpoint=0.4,
        decay_rate=0.04,
        noise_sigma=0.018,
        circadian_amplitude=0.06,
        circadian_phase=math.pi / 6,
    ),
    HormoneConfig(
        name="oxytocin",
        setpoint=0.4,
        decay_rate=0.03,
        noise_sigma=0.008,
        circadian_amplitude=0.05,
        circadian_phase=math.pi / 4,
    ),
    HormoneConfig(
        name="endorphin",
        setpoint=0.3,
        decay_rate=0.02,
        noise_sigma=0.010,
        circadian_amplitude=0.04,
        circadian_phase=math.pi / 3,
    ),
]


@dataclass
class HormoneInteractions:
    """Cross-hormone interaction matrix."""

    matrix: np.ndarray
    strength: float = 0.01


def _build_default_interaction_matrix() -> np.ndarray:
    """Build the 6x6 default interaction matrix.

    Row i represents influences ON hormone i FROM all other hormones.
    Index mapping: 0=dopamine, 1=serotonin, 2=cortisol,
                   3=norepinephrine, 4=oxytocin, 5=endorphin
    """
    m = np.zeros((6, 6), dtype=np.float64)

    # High cortisol suppresses serotonin: row=serotonin(1), col=cortisol(2)
    m[1, 2] = -0.3

    # High cortisol raises norepinephrine: row=norepinephrine(3), col=cortisol(2)
    m[3, 2] = 0.2

    # High endorphin suppresses cortisol: row=cortisol(2), col=endorphin(5)
    m[2, 5] = -0.2

    # High dopamine slightly raises norepinephrine: row=norepinephrine(3), col=dopamine(0)
    m[3, 0] = 0.1

    # High serotonin slightly suppresses dopamine: row=dopamine(0), col=serotonin(1)
    m[0, 1] = -0.15

    # High norepinephrine slightly raises dopamine: row=dopamine(0), col=norepinephrine(3)
    m[0, 3] = 0.05

    # High oxytocin slightly suppresses cortisol: row=cortisol(2), col=oxytocin(4)
    m[2, 4] = -0.1

    return m


DEFAULT_INTERACTIONS = HormoneInteractions(matrix=_build_default_interaction_matrix())


class HormoneState:
    """Maintains hormone levels and evolves them each tick via decay, interactions,
    circadian modulation, and biological noise."""

    def __init__(
        self,
        configs: list[HormoneConfig] | None = None,
        interactions: HormoneInteractions | None = None,
        circadian_period: int = 1440,
        rng_seed: int | None = None,
    ) -> None:
        self._configs = configs if configs is not None else DEFAULT_HORMONE_CONFIGS
        self._interactions = interactions if interactions is not None else DEFAULT_INTERACTIONS
        self._circadian_period = circadian_period
        self._rng = np.random.default_rng(rng_seed)
        self._tick = 0

        n = len(self._configs)
        self._name_to_idx: dict[str, int] = {c.name: i for i, c in enumerate(self._configs)}
        self._setpoints = np.array([c.setpoint for c in self._configs], dtype=np.float64)
        self._decay_rates = np.array([c.decay_rate for c in self._configs], dtype=np.float64)
        self._noise_sigmas = np.array([c.noise_sigma for c in self._configs], dtype=np.float64)
        self._circadian_amplitudes = np.array(
            [c.circadian_amplitude for c in self._configs], dtype=np.float64
        )
        self._circadian_phases = np.array(
            [c.circadian_phase for c in self._configs], dtype=np.float64
        )

        self._levels = np.array(
            [c.initial_value if c.initial_value is not None else c.setpoint for c in self._configs],
            dtype=np.float64,
        )

    @property
    def levels(self) -> np.ndarray:
        return self._levels.copy()

    @property
    def names(self) -> list[str]:
        return [c.name for c in self._configs]

    def level(self, name: str) -> float:
        return float(self._levels[self._name_to_idx[name]])

    @property
    def tick(self) -> int:
        return self._tick

    def _effective_setpoints(self) -> np.ndarray:
        phase = 2.0 * math.pi * self._tick / self._circadian_period + self._circadian_phases
        return self._setpoints + self._circadian_amplitudes * np.sin(phase)

    def update(self) -> np.ndarray:
        """Advance one tick. Apply in order:
        1. Effective setpoints (base + circadian)
        2. Homeostatic decay toward effective setpoint
        3. Cross-hormone interactions
        4. Biological noise
        5. Clamp to [0.0, 1.0]
        6. Increment tick counter
        """
        effective = self._effective_setpoints()

        # Homeostatic decay
        self._levels += self._decay_rates * (effective - self._levels)

        # Cross-hormone interactions
        interaction_deltas = self._interactions.matrix @ self._levels
        self._levels += self._interactions.strength * interaction_deltas

        # Biological noise
        self._levels += self._rng.normal(0.0, self._noise_sigmas)

        # Clamp
        np.clip(self._levels, 0.0, 1.0, out=self._levels)

        # Advance tick
        self._tick += 1

        return self._levels.copy()

    def get_deviations(self) -> np.ndarray:
        return self._levels - self._effective_setpoints()

    def snapshot(self) -> dict:
        effective = self._effective_setpoints()
        deviations = self._levels - effective
        names = self.names
        return {
            "tick": self._tick,
            "levels": {names[i]: float(self._levels[i]) for i in range(len(names))},
            "effective_setpoints": {names[i]: float(effective[i]) for i in range(len(names))},
            "deviations": {names[i]: float(deviations[i]) for i in range(len(names))},
        }

    def inject(self, deltas: np.ndarray) -> None:
        """Apply external deltas (additive). Does NOT advance tick. Clamps after."""
        self._levels += deltas
        np.clip(self._levels, 0.0, 1.0, out=self._levels)
