# Emotion Map

`model_f/core/emotion_map.py`

A **read-only** labeling layer that maps [[Drive System|drive vectors]] to human-readable emotion names. Does NOT affect system dynamics.

## Method

Cosine similarity between current drive vector and 10 prototype vectors.

## 10 Emotion Prototypes

| Emotion | Dominant Drives |
|---------|----------------|
| Restless | [[Seek Novelty]], [[Engage]], [[Express]] |
| Anxious | [[Withdraw]], [[Seek Comfort]] |
| Content | [[Rest]], [[Seek Comfort]] |
| Excited | [[Seek Novelty]], [[Engage]], [[Express]] |
| Melancholic | [[Withdraw]], [[Seek Comfort]], [[Rest]] |
| Energized | [[Engage]], [[Express]] |
| Calm | [[Rest]], [[Seek Comfort]] |
| Fearful | [[Withdraw]], [[Seek Comfort]] |
| Curious | [[Seek Novelty]], [[Engage]] |
| Lethargic | [[Rest]], [[Withdraw]] |

## Design Decision

This is purely observational — a debugging/logging tool. The [[Hormone System]] and [[Drive System]] are the real dynamics. Emotion labels are human projections onto the drive space, not causal factors.
