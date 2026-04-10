# Biological Noise

One of 4 forces acting on the [[Hormone System]] each tick.

## Formula

```
h(t+1) += N(0, sigma)
```

Small Gaussian perturbation applied after all other forces.

## Sigma Per Hormone

| Hormone | sigma |
|---------|-------|
| [[Norepinephrine]] | 0.018 (highest — attention fluctuates most) |
| [[Dopamine]] | 0.015 |
| [[Cortisol]] | 0.012 |
| [[Serotonin]] | 0.010 |
| [[Endorphin]] | 0.010 |
| [[Oxytocin]] | 0.008 (lowest — bonding state is most stable) |

## Why It Matters

Without noise, the [[Floating Brain]] would eventually settle into a perfectly predictable cycle (just [[Homeostatic Decay]] + [[Circadian Rhythm]] + [[Cross-Hormone Interactions]]). Noise introduces the **unpredictability** that makes behavior feel organic.

It's why the same "brain" with the same parameters won't produce the same [[Impulse]] sequence every time (unless you fix the RNG seed).
