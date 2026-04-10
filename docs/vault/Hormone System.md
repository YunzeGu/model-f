# Hormone System

`model_f/core/hormone_state.py`

Maintains 6 continuous-float hormone levels in [0.0, 1.0], each evolving through 4 superimposed forces per tick.

## The 6 Hormones

| Hormone | Setpoint | Role |
|---------|----------|------|
| [[Dopamine]] | 0.5 | Reward anticipation, motivation |
| [[Serotonin]] | 0.6 | Contentment, impulse inhibition |
| [[Cortisol]] | 0.3 | Stress, alertness, fight-or-flight |
| [[Norepinephrine]] | 0.4 | Arousal, attention, action readiness |
| [[Oxytocin]] | 0.4 | Social bonding, comfort-seeking |
| [[Endorphin]] | 0.3 | Pain suppression, euphoric inertia |

## 4 Forces Per Tick

1. **[[Homeostatic Decay]]** — exponential return toward setpoint
2. **[[Circadian Rhythm]]** — sinusoidal modulation of effective setpoint
3. **[[Cross-Hormone Interactions]]** — 6x6 influence matrix
4. **[[Biological Noise]]** — Gaussian perturbation

## Output

- Raw levels → consumed by [[Drive System]]
- Deviations from setpoint → measure of urgency
- Snapshot → consumed by [[Logger]]

## Input Port

- `inject(deltas)` — additive hormone modification, used by [[Input Port]] adapters
