# Pluggable Architecture

[[Model F]] is designed as a base module that future capabilities can plug into.

## Port Interfaces

### [[Input Port]] (`model_f/inputs/sensory_adapter.py`)

```python
class InputPort(ABC):
    def poll(self, tick: int) -> np.ndarray | None:
        """Return hormone deltas, or None."""
```

Converts external signals into [[Hormone System]] deltas. v1 has only `NullInput`.

### [[Output Port]] (`model_f/outputs/behavior_vector.py`)

```python
class OutputPort(ABC):
    def receive(self, tick: int, drives: np.ndarray, impulses: list[Impulse]) -> None:
        """Consume drive state and impulses."""
```

Sends [[Drive System]] output to downstream consumers. v1 has `NullOutput` and `PrintOutput`.

## Future Capability Plugins

| Capability | Port Type | Would Do |
|-----------|-----------|----------|
| Vision model | [[Input Port]] | Visual stimuli → hormone deltas |
| Memory system | [[Input Port]] | Memory recall → hormone deltas |
| LLM reasoning | [[Input Port]] + [[Output Port]] | Bidirectional emotional context |
| Motor control | [[Output Port]] | Drive vectors → physical movement |
| Social system | [[Input Port]] | Other agents' states → hormone deltas |

## Design Principle

**Core never imports from ports.** Ports import from core. The [[Hormone System]] exposes `inject()` for input, and `levels`/`snapshot()` for output. This keeps the core dependency-free.
