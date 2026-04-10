from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np


class InputPort(ABC):
    """Abstract base for all input adapters. Produces hormone deltas."""

    @abstractmethod
    def poll(self, tick: int) -> np.ndarray | None:
        """Return hormone delta array, or None if no input this tick."""
        ...


class NullInput(InputPort):
    """No external input. Always returns None."""

    def poll(self, tick: int) -> np.ndarray | None:
        return None
