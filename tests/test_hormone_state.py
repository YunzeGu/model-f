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
        close to its setpoint after 500 ticks with zero noise.

        We use zero circadian amplitude to isolate the decay behaviour and
        a zero-interaction matrix so cross-hormone effects don't shift the
        equilibrium.
        """
        configs = [
            HormoneConfig(
                name=c.name,
                setpoint=c.setpoint,
                decay_rate=c.decay_rate,
                noise_sigma=0.0,
                circadian_amplitude=0.0,
                circadian_phase=c.circadian_phase,
                initial_value=1.0 if c.name == "dopamine" else c.setpoint,
            )
            for c in DEFAULT_HORMONE_CONFIGS
        ]
        no_interactions = HormoneInteractions(
            matrix=np.zeros((6, 6), dtype=np.float64), strength=0.0
        )
        state = HormoneState(configs=configs, interactions=no_interactions)

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
        """After the system settles into its orbital cycle, cortisol should
        return to roughly the same level after one full circadian period
        (1440 ticks).

        We let the system warm up for 2 full periods so transients die out,
        then sample at the start and end of a third period.  The value at
        the end of the full period should be closer to the start than the
        half-period value is.
        """
        configs = _zero_noise_configs()
        # Disable cross-hormone interactions for a clean circadian signal
        no_interactions = HormoneInteractions(
            matrix=np.zeros((6, 6), dtype=np.float64), strength=0.0
        )
        state = HormoneState(configs=configs, interactions=no_interactions)

        # Warm up: run 2 full periods (2880 ticks) to settle into orbit
        for _ in range(2880):
            state.update()

        # Now sample the orbital cycle
        level_start = state.level("cortisol")

        for _ in range(720):  # half period
            state.update()
        level_half = state.level("cortisol")

        for _ in range(720):  # complete the period
            state.update()
        level_full = state.level("cortisol")

        diff_half = abs(level_half - level_start)
        diff_full = abs(level_full - level_start)

        assert diff_full < diff_half, (
            f"After warm-up, level at full period should be closer to start than half period. "
            f"|half - start| = {diff_half:.6f}, |full - start| = {diff_full:.6f}"
        )

    def test_cross_hormone_interaction(self):
        """High cortisol should suppress serotonin below its setpoint over time.

        We disable circadian modulation so the only forces at play are
        homeostatic decay and the cross-hormone interaction.  We repeatedly
        inject cortisol each tick to keep it elevated and track serotonin's
        trajectory.
        """
        configs = [
            HormoneConfig(
                name=c.name,
                setpoint=c.setpoint,
                decay_rate=c.decay_rate,
                noise_sigma=0.0,
                circadian_amplitude=0.0,
                circadian_phase=0.0,
                initial_value=c.initial_value,
            )
            for c in DEFAULT_HORMONE_CONFIGS
        ]
        state = HormoneState(configs=configs, interactions=DEFAULT_INTERACTIONS)

        # Record initial serotonin level (at setpoint 0.6)
        initial_serotonin = state.level("serotonin")

        # Keep cortisol high by re-injecting each tick
        for _ in range(50):
            deltas = np.zeros(6)
            deltas[2] = 0.5  # cortisol boost each tick
            state.inject(deltas)
            state.update()

        final_serotonin = state.level("serotonin")
        assert final_serotonin < initial_serotonin, (
            f"Serotonin should decrease under sustained high cortisol. "
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
