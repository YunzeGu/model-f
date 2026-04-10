from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np
from model_f.core.drive_system import Impulse


class OutputPort(ABC):
    """Abstract base for all output consumers."""

    @abstractmethod
    def receive(self, tick: int, drives: np.ndarray, impulses: list[Impulse]) -> None:
        ...


class NullOutput(OutputPort):
    """Discards output."""

    def receive(self, tick: int, drives: np.ndarray, impulses: list[Impulse]) -> None:
        pass


class PrintOutput(OutputPort):
    """Prints impulses to stdout."""

    def __init__(self, drive_names: list[str] | None = None):
        self._drive_names = drive_names

    def receive(self, tick: int, drives: np.ndarray, impulses: list[Impulse]) -> None:
        for imp in impulses:
            print(f"[tick {tick:04d}] IMPULSE: {imp.drive_name} "
                  f"intensity={imp.intensity:.3f} urgency={imp.urgency:.3f}")
