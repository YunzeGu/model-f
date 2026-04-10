# Logger

`model_f/utils/logger.py`

Records full state snapshots to JSONL (one JSON object per line, one line per tick).

## Usage

```python
from model_f.utils.logger import StateLogger

with StateLogger("logs/run.jsonl") as logger:
    engine.run(2880, tick_callback=logger.log_tick)
```

Or via CLI:
```bash
python main.py --ticks 2880 --log logs/run.jsonl
```

## Output Format

Each line contains:
- `tick`, `hormones`, `drives`, `impulses`, `emotions`, `had_external_input`

## Visualization

Feed the JSONL file to `scripts/plot_run.py` for matplotlib charts of [[Hormone System]] levels, [[Drive System]] vectors, [[Impulse]] events, and [[Emotion Map]] timeline.

## Connects To

- [[Engine]] — provides tick results
- [[Emotion Map]] — emotion labels included in output
