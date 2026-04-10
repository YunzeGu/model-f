import numpy as np
import pytest

from model_f.core.hormone_state import (
    HormoneState,
    HormoneConfig,
    DEFAULT_HORMONE_CONFIGS,
    HormoneInteractions,
    DEFAULT_INTERACTIONS,
)


def _zero_noise_configs():
    return [
        HormoneConfig(
            name=c.name,
            setpoint=c.setpoint,
            decay_rate=c.decay_rate,
            noise_sigma=0.0,
            circadian_amplitude=c.circadian_amplitude,
            circadian_phase=c.circadian_phase,
            initial_value=c.initial_value,
        )
        for c in DEFAULT_HORMONE_CONFIGS
    ]


class TestHormoneState:
    def test_homeostatic_convergence(self):
        """Dopamine starts at 1.0 (far from setpoint 0.5), should converge
        within 0.01 of setpoint after 500 ticks with zero noise."""
        configs = _zero_noise_configs()
        # Override dopamine initial value to 1.0
        configs[0] = HormoneConfig(
            name=configs[0].name,
            setpoint=configs[0].setpoint,
            decay_rate=configs[0].decay_rate,
            noise_sigma=0.0,
            circadian_amplitude=configs[0].circadian_amplitude,
            circadian_phase=configs[0].circadian_phase,
            initial_value=1.0,
        )
        state = HormoneState(configs=configs, interactions=DEFAULT_INTERACTIONS)

        for _ in range(500):
            state.update()

        dopamine_level = state.level("dopamine")
        assert abs(dopamine_level - 0.5) < 0.01, (
            f"Dopamine should converge near setpoint 0.5, got {dopamine_level}"
        )

    def test_clamping(self):
        """Injecting massive positive deltas should clamp at 1.0;
        massive negative deltas should clamp at 0.0."""
        state = HormoneState()

        # Inject large positive delta
        state.inject(np.full(6, 5.0))
        levels = state.levels
        assert np.all(levels <= 1.0), f"All levels should be <= 1.0, got {levels}"

        # Inject large negative delta
        state.inject(np.full(6, -10.0))
        levels = state.levels
        assert np.all(levels >= 0.0), f"All levels should be >= 0.0, got {levels}"

    def test_reproducibility(self):
        """Two HormoneState instances with the same seed should produce
        identical levels after 100 ticks."""
        state_a = HormoneState(rng_seed=42)
        state_b = HormoneState(rng_seed=42)

        for _ in range(100):
            state_a.update()
            state_b.update()

        assert np.allclose(state_a.levels, state_b.levels), (
            f"Levels should be identical:\n  A: {state_a.levels}\n  B: {state_b.levels}"
        )

    def test_circadian_periodicity(self):
        """Over 2 full circadian periods (2880 ticks), cortisol at tick 2880
        should be closer to tick 0 than tick 1440 is (half-period shift)."""
        configs = _zero_noise_configs()
        state = HormoneState(configs=configs, interactions=DEFAULT_INTERACTIONS)

        level_at_0 = state.level("cortisol")

        for _ in range(1440):
            state.update()
        level_at_1440 = state.level("cortisol")

        for _ in range(1440):
            state.update()
        level_at_2880 = state.level("cortisol")

        diff_half = abs(level_at_1440 - level_at_0)
        diff_full = abs(level_at_2880 - level_at_0)

        assert diff_full < diff_half, (
            f"Level at 2880 should be closer to tick 0 than tick 1440 is. "
            f"|tick1440 - tick0| = {diff_half:.6f}, |tick2880 - tick0| = {diff_full:.6f}"
        )

    def test_cross_hormone_interaction(self):
        """High cortisol should suppress serotonin below its setpoint over time."""
        configs = _zero_noise_configs()
        state = HormoneState(configs=configs, interactions=DEFAULT_INTERACTIONS)

        # Record initial serotonin level (at setpoint 0.6)
        initial_serotonin = state.level("serotonin")

        # Inject cortisol to 1.0
        deltas = np.zeros(6)
        deltas[2] = 1.0  # cortisol index
        state.inject(deltas)

        # Run 50 ticks
        for _ in range(50):
            state.update()

        final_serotonin = state.level("serotonin")
        assert final_serotonin < initial_serotonin, (
            f"Serotonin should decrease under high cortisol. "
            f"Initial: {initial_serotonin:.4f}, Final: {final_serotonin:.4f}"
        )

    def test_snapshot_types(self):
        """snapshot() should return only plain Python types, not numpy types."""
        state = HormoneState()
        state.update()
        snap = state.snapshot()

        def _check_plain(obj, path="root"):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    assert isinstance(k, (str, int, float)), (
                        f"Key at {path}.{k} is {type(k).__name__}, not a plain type"
                    )
                    _check_plain(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    _check_plain(v, f"{path}[{i}]")
            else:
                assert isinstance(obj, (int, float, str, bool, type(None))), (
                    f"Value at {path} is {type(obj).__name__} ({obj!r}), not a plain Python type"
                )

        _check_plain(snap)
