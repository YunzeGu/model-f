import argparse
import sys

from model_f.engine import ModelFEngine
from model_f.core.hormone_state import HormoneState
from model_f.core.drive_system import DriveSystem
from model_f.core.emotion_map import EmotionMap
from model_f.outputs.behavior_vector import PrintOutput
from model_f.utils.logger import StateLogger


def make_summary_callback(drive_names: list[str], every_n: int = 60):
    """Returns a callback that prints a summary line every N ticks."""
    def callback(result: dict):
        tick = result["tick"]
        if tick % every_n != 0:
            return
        h = result["hormones"]
        d = result["drives"]
        emo = result["emotions"][0] if result["emotions"] else {"name": "?", "confidence": 0}
        hstr = " ".join(f"{k[:3]}={v:.2f}" for k, v in h.items())
        dstr = " ".join(f"{k[:4]}={v:.2f}" for k, v in d.items())
        print(f"[tick {tick:04d}] hormones: {hstr}")
        print(f"           drives:   {dstr}")
        print(f"           emotion:  {emo['name']} ({emo['confidence']:.2f})")
    return callback


def main():
    parser = argparse.ArgumentParser(description="Model F - Bionic Impulse Engine")
    parser.add_argument("--ticks", type=int, default=2880, help="Number of ticks to run (default: 2880 = 2 days)")
    parser.add_argument("--seed", type=int, default=None, help="RNG seed for reproducibility")
    parser.add_argument("--summary-interval", type=int, default=60, help="Print summary every N ticks")
    parser.add_argument("--log", type=str, default=None, help="Path to JSONL log file (e.g. logs/run.jsonl)")
    args = parser.parse_args()

    hs = HormoneState(rng_seed=args.seed)
    ds = DriveSystem()
    em = EmotionMap()
    outputs = [PrintOutput(drive_names=ds.drive_names)]

    engine = ModelFEngine(
        hormone_state=hs,
        drive_system=ds,
        emotion_map=em,
        outputs=outputs,
    )

    logger = None
    if args.log:
        logger = StateLogger(args.log)

    summary_cb = make_summary_callback(ds.drive_names, every_n=args.summary_interval)

    def combined_callback(result):
        summary_cb(result)
        if logger:
            logger.log_tick(result)

    print(f"Model F — running {args.ticks} ticks (seed={args.seed})")
    print(f"{'=' * 60}")

    try:
        engine.run(args.ticks, tick_callback=combined_callback)
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        if logger:
            logger.close()
            print(f"\nLog saved to {args.log}")

    print(f"{'=' * 60}")
    print("Done.")


if __name__ == "__main__":
    main()
