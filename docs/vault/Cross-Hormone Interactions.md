# Cross-Hormone Interactions

One of 4 forces acting on the [[Hormone System]] each tick.

## Mechanism

A 6x6 influence matrix applied each tick:

```
delta_h = interaction_matrix @ current_levels * strength
```

Global strength factor: 0.01 (keeps interactions subtle).

## Interaction Map

```
Cortisol  ──(-0.3)──> Serotonin      stress kills contentment
Cortisol  ──(+0.2)──> Norepinephrine stress raises alertness
Endorphin ──(-0.2)──> Cortisol       endorphins counteract stress
Dopamine  ──(+0.1)──> Norepinephrine motivation raises arousal
Serotonin ──(-0.15)─> Dopamine       satisfaction reduces seeking
Norepinephrine ──(+0.05)──> Dopamine arousal slightly raises motivation
Oxytocin  ──(-0.1)──> Cortisol       social comfort reduces stress
```

## Why This Matters

Without interactions, each hormone would be independent — just 6 parallel oscillators. The interaction matrix creates **emergent cascades**: a cortisol spike doesn't just increase stress, it suppresses serotonin, raises norepinephrine, which raises dopamine slightly, shifting the entire [[Drive System]] profile.

This is where complex, seemingly irrational behavior patterns emerge from simple rules.
