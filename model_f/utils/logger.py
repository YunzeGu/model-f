from __future__ import annotations
import json
from pathlib import Path


class StateLogger:
    """Records full state snapshots each tick to a JSONL file."""

    def __init__(self, output_path: str | Path = "logs/run.jsonl"):
        self._path = Path(output_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(self._path, "w", encoding="utf-8")

    def log_tick(self, tick_result: dict) -> None:
        self._file.write(json.dumps(tick_result) + "\n")

    def close(self) -> None:
        self._file.flush()
        self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
