# Circadian Rhythm

One of 4 forces acting on the [[Hormone System]] each tick.

## Formula

```
effective_setpoint(t) = base_setpoint + amplitude * sin(2*pi*t / period + phase)
```

Default period: 1440 ticks (= 1 simulated day).

## Meaning

The setpoint itself oscillates over a day/night cycle. This means even without any external input, the [[Floating Brain]] experiences different baseline states at different times of "day".

## Per-Hormone Settings

| Hormone | Amplitude | Phase | Effect |
|---------|-----------|-------|--------|
| [[Cortisol]] | 0.15 | -pi/3 | Peaks in "morning" |
| [[Serotonin]] | 0.10 | pi/2 | Peaks in "afternoon" |
| [[Dopamine]] | 0.08 | 0.0 | Moderate cycle |
| [[Norepinephrine]] | 0.06 | pi/6 | Slight morning bias |
| [[Oxytocin]] | 0.05 | pi/4 | Slight afternoon bias |
| [[Endorphin]] | 0.04 | pi/3 | Weak cycle |

## Emergent Behavior

The [[Floating Brain]] naturally becomes more stressed/alert in the "morning" ([[Cortisol]] peak) and more content/restful in the "evening" ([[Serotonin]] dominance), purely from internal dynamics.
