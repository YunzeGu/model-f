# Input Port

Abstract interface for feeding external data into [[Model F]].

See [[Pluggable Architecture]] for details.

`model_f/inputs/sensory_adapter.py`

## v1 Implementations

- **NullInput** — returns None every tick (no external input)

## Future Implementations

- Vision adapter — image features → hormone deltas
- Memory adapter — recalled experiences → hormone deltas
- Social adapter — other agents' emotional states → hormone deltas
- Physical adapter — simulated body state → hormone deltas

## Contract

```python
def poll(self, tick: int) -> np.ndarray | None
```

Returns a hormone delta array (same shape as [[Hormone System]] levels), or None if no input this tick. Applied via `inject()`.
