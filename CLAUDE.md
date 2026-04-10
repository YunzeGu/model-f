# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Model F** is the base emotion/hormone state engine — a standalone bionic motivation model that accepts sensory inputs and outputs behavioral drive commands. It is part of a broader research project on animal emotion simulation (see `YunzeGu/humanoid02` for prior work).

Model F is **not coupled to Unity or ML-Agents at this stage**. The goal is a clean, testable Python engine for the internal state model before any simulation environment is integrated.

## Research Context

Two parallel long-term tracks (both share Model F as their emotional core):

1. **3D Embodied Simulation** — Unity-based animal agents whose physical behavior is driven by the hormone/drive state engine
2. **LLM Dialogue Emotion** — A persistent emotional core for conversational agents that maintains state across sessions and generates spontaneous internal state changes without external stimulus

Development notes and research thoughts are tracked in `dev_thoughts.txt`.

**Model F definition and design philosophy** are documented in [`docs/definition.md`](docs/definition.md) — this is the living specification for what Model F is and why it exists. Update it as the concept evolves.

## Environment & Commands

**Python interpreter** (always use full path — do not use system Python):
```
C:\Users\80951\miniconda3\envs\mlagents\python.exe
```

**Run the project:**
```bash
C:\Users\80951\miniconda3\envs\mlagents\python.exe main.py
```

**Install dependencies:**
```bash
C:\Users\80951\miniconda3\envs\mlagents\Scripts\pip.exe install -r requirements.txt
```

## Git Workflow

Commit and push after every meaningful change so the GitHub remote stays in sync with local work. The `.claude/settings.local.json` auto-save hook handles this automatically after every file write or edit.

**Remote:** `https://github.com/YunzeGu/model-f`
**Branch:** `main`

## Architecture

```
main.py                  ← entry point (CLI with --ticks, --seed, --log flags)
model_f/
  engine.py              ← ModelFEngine orchestrator (wires all components)
  core/
    hormone_state.py     ← HormoneState: 6 hormones with decay, noise, circadian, interactions
    drive_system.py      ← DriveSystem: hormone→drive mapping + Impulse generation
    emotion_map.py       ← EmotionMap: cosine-similarity emotion labeling (read-only)
  inputs/
    sensory_adapter.py   ← InputPort ABC + NullInput (capability port for future sensors)
  outputs/
    behavior_vector.py   ← OutputPort ABC + NullOutput/PrintOutput
  utils/
    logger.py            ← StateLogger: JSONL state recording
tests/                   ← pytest test suite (15 tests)
scripts/
  plot_run.py            ← matplotlib visualization of JSONL logs
docs/
  definition.md          ← living conceptual definition
```

## Key Design Principles

- Hormone values are continuous floats with natural decay over time ticks
- Drive urgency is computed from deviation from homeostatic setpoints
- Sensory inputs produce delta changes to hormone state, not direct overrides
- Behavioral output is a weighted priority vector, not a single action command
