import numpy as np
import pytest

from model_f.engine import ModelFEngine
from model_f.core.hormone_state import HormoneState, HormoneConfig, DEFAULT_HORMONE_CONFIGS
from model_f.inputs.sensory_adapter import InputPort
from model_f.outputs.behavior_vector import OutputPort


class MockInputPort(InputPort):
    """Injects +0.3 to dopamine (index 0) at a specified tick."""

    def __init__(self, inject_tick: int = 50):
        self._inject_tick = inject_tick

    def poll(self, tick: int) -> np.ndarray | None:
        if tick == self._inject_tick:
            delta = np.zeros(6)
            delta[0] = 0.3  # dopamine
            return delta
        return None


class MockOutputPort(OutputPort):
    """Counts how many times receive() is called."""

    def __init__(self):
        self.call_count = 0

    def receive(self, tick, drives, impulses) -> None:
        self.call_count += 1


class TestModelFEngine:
    def test_default_runs(self):
        """Engine with default args should run 100 ticks without errors."""
        engine = ModelFEngine()
        engine.run(100)

    def test_custom_input_port(self):
        """A mock InputPort injecting dopamine at tick 50 should produce a
        visible increase in dopamine level after that tick.

        We use zero noise so the injection signal is not overwhelmed by
        stochastic fluctuations.
        """
        zero_noise_configs = [
            HormoneConfig(
                name=c.name, setpoint=c.setpoint, decay_rate=c.decay_rate,
                noise_sigma=0.0, circadian_amplitude=c.circadian_amplitude,
                circadian_phase=c.circadian_phase, initial_value=c.initial_value,
            )
            for c in DEFAULT_HORMONE_CONFIGS
        ]
        hormone_state = HormoneState(configs=zero_noise_configs)
        mock_input = MockInputPort(inject_tick=50)
        engine = ModelFEngine(hormone_state=hormone_state, inputs=[mock_input])

        dopamine_levels = {}

        def callback(result):
            dopamine_levels[result["tick"]] = result["hormones"]["dopamine"]

        engine.run(100, tick_callback=callback)

        # Tick 50 is when injection happens (before update), so tick 50's
        # result should show the boosted level vs tick 49
        assert dopamine_levels[50] > dopamine_levels[49], (
            f"Dopamine at tick 50 ({dopamine_levels[50]:.4f}) should be higher "
            f"than at tick 49 ({dopamine_levels[49]:.4f})"
        )

    def test_output_receives(self):
        """A mock OutputPort should have receive() called once per tick."""
        mock_output = MockOutputPort()
        engine = ModelFEngine(outputs=[mock_output])
        engine.run(100)

        assert mock_output.call_count == 100, (
            f"receive() should be called 100 times, got {mock_output.call_count}"
        )

    def test_tick_result_keys(self):
        """A single tick result should have all expected keys."""
        engine = ModelFEngine()
        result = engine.tick()

        expected_keys = {"tick", "hormones", "drives", "impulses", "emotions",
                         "had_external_input"}
        assert set(result.keys()) == expected_keys, (
            f"Expected keys {expected_keys}, got {set(result.keys())}"
        )
