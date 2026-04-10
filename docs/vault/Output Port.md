# Output Port

Abstract interface for consuming [[Model F]] behavioral output.

See [[Pluggable Architecture]] for details.

`model_f/outputs/behavior_vector.py`

## v1 Implementations

- **NullOutput** — discards everything
- **PrintOutput** — prints [[Impulse|impulses]] to console

## Future Implementations

- Unity motor controller — drive vectors → agent movement
- LLM emotion context — emotional state → conversation tone
- [[Logger]] adapter — full state → JSONL file

## Contract

```python
def receive(self, tick: int, drives: np.ndarray, impulses: list[Impulse]) -> None
```

Called every tick with current [[Drive System]] output.
