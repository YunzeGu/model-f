from __future__ import annotations
from typing import Callable
import numpy as np

from model_f.core.hormone_state import HormoneState
from model_f.core.drive_system import DriveSystem
from model_f.core.emotion_map import EmotionMap
from model_f.inputs.sensory_adapter import InputPort, NullInput
from model_f.outputs.behavior_vector import OutputPort, NullOutput


class ModelFEngine:
    """Main simulation engine orchestrating all components."""

    def __init__(
        self,
        hormone_state: HormoneState | None = None,
        drive_system: DriveSystem | None = None,
        emotion_map: EmotionMap | None = None,
        inputs: list[InputPort] | None = None,
        outputs: list[OutputPort] | None = None,
    ):
        self._hormone_state = hormone_state or HormoneState()
        self._drive_system = drive_system or DriveSystem()
        self._emotion_map = emotion_map or EmotionMap()
        self._inputs = inputs if inputs is not None else [NullInput()]
        self._outputs = outputs if outputs is not None else [NullOutput()]

    def tick(self) -> dict:
        """
        Execute one simulation tick:
        1. Poll all input ports, accumulate hormone deltas
        2. If any deltas, apply via inject()
        3. Advance hormone state (update)
        4. Compute drives and impulses
        5. Label emotions
        6. Dispatch to all output ports
        7. Return full tick result dict
        """
        # 1-2: gather and apply input deltas
        n = len(self._hormone_state.names)
        total_delta = np.zeros(n)
        has_input = False
        for inp in self._inputs:
            delta = inp.poll(self._hormone_state.tick)
            if delta is not None:
                total_delta += delta
                has_input = True
        if has_input:
            self._hormone_state.inject(total_delta)

        # 3: advance hormone state
        levels = self._hormone_state.update()

        # 4: compute drives and impulses
        drives, impulses = self._drive_system.step(
            self._hormone_state.tick,
            levels,
            self._hormone_state.names,
        )

        # 5: label emotions
        labels = self._emotion_map.label(drives, top_k=3)

        # 6: dispatch to outputs
        for out in self._outputs:
            out.receive(self._hormone_state.tick, drives, impulses)

        # 7: build result
        result = {
            "tick": self._hormone_state.tick,
            "hormones": dict(zip(self._hormone_state.names, levels.tolist())),
            "drives": dict(zip(self._drive_system.drive_names, drives.tolist())),
            "impulses": [
                {
                    "drive": imp.drive_name,
                    "intensity": imp.intensity,
                    "urgency": imp.urgency,
                }
                for imp in impulses
            ],
            "emotions": [
                {"name": lbl.name, "confidence": round(lbl.confidence, 4)}
                for lbl in labels
            ],
            "had_external_input": has_input,
        }
        return result

    def run(self, n_ticks: int, tick_callback: Callable[[dict], None] | None = None) -> None:
        """Run simulation for n_ticks. Optional callback per tick."""
        for _ in range(n_ticks):
            result = self.tick()
            if tick_callback is not None:
                tick_callback(result)

    @property
    def state(self) -> dict:
        """Current full state snapshot."""
        return self._hormone_state.snapshot()
