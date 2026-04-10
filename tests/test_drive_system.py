import numpy as np
import pytest

from model_f.core.drive_system import DriveSystem, DriveConfig, DEFAULT_DRIVE_CONFIGS, Impulse


class TestDriveSystem:
    def test_drive_bounds(self):
        """All drive outputs should be in [0, 1] for random hormone inputs."""
        ds = DriveSystem()
        rng = np.random.default_rng(0)
        for _ in range(20):
            hormones = rng.random(6)
            drives = ds.compute_drives(hormones)
            assert np.all(drives >= 0.0) and np.all(drives <= 1.0), (
                f"Drives out of bounds: {drives}"
            )

    def test_seek_novelty_high_dopamine(self):
        """With dopamine=1.0, serotonin=0.0, others at 0.5, seek_novelty
        should be > 0.7."""
        ds = DriveSystem()
        hormones = np.array([1.0, 0.0, 0.5, 0.5, 0.5, 0.5])
        drives = ds.compute_drives(hormones)

        # seek_novelty is the first drive (index 0)
        seek_novelty = drives[0]
        assert seek_novelty > 0.7, (
            f"seek_novelty should be > 0.7 with high dopamine, got {seek_novelty:.4f}"
        )

    def test_impulse_threshold(self):
        """Gradually increasing dopamine from 0.0 to 1.0 should cause at least
        one impulse to fire when a drive crosses the threshold."""
        ds = DriveSystem()
        hormone_names = ["dopamine", "serotonin", "cortisol",
                         "norepinephrine", "oxytocin", "endorphin"]
        all_impulses = []

        for i in range(50):
            dopamine = i / 49.0  # 0.0 to 1.0
            hormones = np.array([dopamine, 0.5, 0.5, 0.5, 0.5, 0.5])
            drives, impulses = ds.step(tick=i, hormone_levels=hormones,
                                       hormone_names=hormone_names)
            all_impulses.extend(impulses)

        assert len(all_impulses) > 0, (
            "At least one impulse should fire when drives cross threshold"
        )

    def test_refractory_period(self):
        """After an impulse fires, no impulse should fire for the same drive
        during the refractory period, then it can fire again."""
        refractory_ticks = 5
        ds = DriveSystem(refractory_ticks=refractory_ticks,
                         change_sensitivity=0.05)
        hormone_names = ["dopamine", "serotonin", "cortisol",
                         "norepinephrine", "oxytocin", "endorphin"]

        # Tick 0: baseline with low drives (first tick -- no impulses)
        low_hormones = np.array([0.0, 0.5, 0.5, 0.5, 0.5, 0.5])
        ds.step(tick=0, hormone_levels=low_hormones, hormone_names=hormone_names)

        # Tick 1: spike to trigger impulse via rapid change
        high_hormones = np.array([1.0, 0.0, 0.5, 1.0, 0.5, 0.5])
        _, impulses_fire = ds.step(tick=1, hormone_levels=high_hormones,
                                   hormone_names=hormone_names)
        assert len(impulses_fire) > 0, "An impulse should fire on the spike"

        fired_drive = impulses_fire[0].drive_name

        # Ticks 2 through refractory_ticks+1: keep same high hormones, no
        # impulse for the fired drive should occur during refractory period
        for t in range(2, 2 + refractory_ticks):
            _, impulses_ref = ds.step(tick=t, hormone_levels=high_hormones,
                                      hormone_names=hormone_names)
            refractory_impulse_names = [imp.drive_name for imp in impulses_ref]
            assert fired_drive not in refractory_impulse_names, (
                f"Drive '{fired_drive}' should not fire during refractory at tick {t}"
            )

        # After the refractory expires, verify the drive CAN fire again.
        # The rapid change from high->low at this tick should itself trigger
        # the fired drive -- which proves refractory has ended.
        t_after = 2 + refractory_ticks
        _, impulses_after = ds.step(tick=t_after, hormone_levels=low_hormones,
                                    hormone_names=hormone_names)
        after_names = [imp.drive_name for imp in impulses_after]
        assert fired_drive in after_names, (
            f"Drive '{fired_drive}' should be able to fire again after refractory period"
        )

    def test_first_tick_no_impulses(self):
        """On the very first step() call, no impulses should fire."""
        ds = DriveSystem()
        hormone_names = ["dopamine", "serotonin", "cortisol",
                         "norepinephrine", "oxytocin", "endorphin"]
        # Use extreme hormones to maximize chance of threshold crossing
        hormones = np.array([1.0, 0.0, 1.0, 1.0, 0.0, 0.0])
        _, impulses = ds.step(tick=0, hormone_levels=hormones,
                              hormone_names=hormone_names)
        assert len(impulses) == 0, (
            f"No impulses should fire on first tick, got {len(impulses)}"
        )
