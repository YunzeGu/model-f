"""Plot Model F simulation logs.

Usage:
    python scripts/plot_run.py logs/run.jsonl
"""
import json
import sys
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("matplotlib is required: pip install matplotlib>=3.5")
    sys.exit(1)

import numpy as np


def load_log(path: str) -> list[dict]:
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def plot(records: list[dict], save_path: str | None = None):
    ticks = [r["tick"] for r in records]

    hormone_names = list(records[0]["hormones"].keys())
    drive_names = list(records[0]["drives"].keys())

    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    # --- Hormones ---
    ax = axes[0]
    for name in hormone_names:
        vals = [r["hormones"][name] for r in records]
        ax.plot(ticks, vals, label=name, linewidth=0.8)
    ax.set_ylabel("Level")
    ax.set_title("Hormone Levels")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)

    # --- Drives ---
    ax = axes[1]
    for name in drive_names:
        vals = [r["drives"][name] for r in records]
        ax.plot(ticks, vals, label=name, linewidth=0.8)
    # Impulse markers
    for r in records:
        for imp in r["impulses"]:
            drive_idx = drive_names.index(imp["drive"])
            ax.scatter(r["tick"], imp["intensity"], marker="^", s=30,
                       color="red", zorder=5)
    ax.set_ylabel("Drive Strength")
    ax.set_title("Behavioral Drives (triangles = impulses)")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)

    # --- Emotion timeline ---
    ax = axes[2]
    emotions = [r["emotions"][0]["name"] if r["emotions"] else "?" for r in records]
    unique_emotions = sorted(set(emotions))
    emotion_to_idx = {e: i for i, e in enumerate(unique_emotions)}
    emotion_indices = [emotion_to_idx[e] for e in emotions]
    confidences = [r["emotions"][0]["confidence"] if r["emotions"] else 0 for r in records]

    ax.scatter(ticks, emotion_indices, c=confidences, cmap="viridis",
               s=2, alpha=0.7)
    ax.set_yticks(range(len(unique_emotions)))
    ax.set_yticklabels(unique_emotions, fontsize=8)
    ax.set_ylabel("Dominant Emotion")
    ax.set_xlabel("Tick")
    ax.set_title("Emotion Timeline (color = confidence)")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Saved to {save_path}")
    else:
        plt.show()


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/plot_run.py <log.jsonl> [output.png]")
        sys.exit(1)

    log_path = sys.argv[1]
    save_path = sys.argv[2] if len(sys.argv) > 2 else None

    records = load_log(log_path)
    print(f"Loaded {len(records)} ticks from {log_path}")
    plot(records, save_path)


if __name__ == "__main__":
    main()
