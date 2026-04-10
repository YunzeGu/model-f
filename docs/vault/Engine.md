# Engine

`model_f/engine.py`

The tick-based orchestrator that wires all components together.

## Tick Pipeline

Each tick executes in order:

1. Poll all [[Input Port|input ports]] → collect hormone deltas
2. Apply deltas via [[Hormone System]] `inject()`
3. Advance [[Hormone System]] `update()` (decay, circadian, interactions, noise)
4. Compute drives and [[Impulse|impulses]] via [[Drive System]]
5. Label emotions via [[Emotion Map]]
6. Dispatch to all [[Output Port|output ports]]
7. Return full state dict

## Time Model

- **Tick-based**, not continuous
- 1 tick = 1 simulated minute (default)
- 1440 ticks = 1 simulated day (one [[Circadian Rhythm]] cycle)
- Deterministic with a given RNG seed

## Composition

All components are injected via constructor — defaults are provided:

```python
ModelFEngine(
    hormone_state=HormoneState(),
    drive_system=DriveSystem(),
    emotion_map=EmotionMap(),
    inputs=[NullInput()],       # no external input in v1
    outputs=[NullOutput()],     # or PrintOutput() for console
)
```
