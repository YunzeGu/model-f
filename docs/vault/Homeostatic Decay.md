# Homeostatic Decay

One of 4 forces acting on the [[Hormone System]] each tick.

## Formula

```
h(t+1) = h(t) + alpha * (setpoint - h(t))
```

Where `alpha` is the decay rate (0.0–1.0), different per hormone.

## Meaning

Every hormone "wants" to return to its setpoint. The further it is from setpoint, the stronger the pull back. This is the biological homeostasis principle — the body actively regulates internal state toward equilibrium.

## Decay Rates

| Hormone | alpha | Speed |
|---------|-------|-------|
| [[Dopamine]] | 0.05 | Fast — spikes are short-lived |
| [[Norepinephrine]] | 0.04 | Moderate |
| [[Serotonin]] | 0.03 | Slow — mood shifts gradually |
| [[Oxytocin]] | 0.03 | Slow |
| [[Cortisol]] | 0.02 | Very slow — stress lingers |
| [[Endorphin]] | 0.02 | Very slow — euphoria fades slowly |
