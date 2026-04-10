# Drive System

`model_f/core/drive_system.py`

Transforms [[Hormone System|hormone levels]] into behavioral drive vectors and detects [[Impulse|impulses]].

## The 6 Drives

| Drive | Primary Hormones | Meaning |
|-------|-----------------|---------|
| [[Seek Novelty]] | [[Dopamine]] +, [[Serotonin]] - | Urge to explore |
| [[Withdraw]] | [[Cortisol]] +, [[Norepinephrine]] - | Desire to retreat |
| [[Engage]] | [[Norepinephrine]] +, [[Dopamine]] + | Readiness to act |
| [[Rest]] | [[Serotonin]] +, [[Endorphin]] + | Desire to stop |
| [[Seek Comfort]] | [[Oxytocin]] +, [[Cortisol]] + | Urge to find safety |
| [[Express]] | [[Dopamine]] +, [[Norepinephrine]] + | Urge to externalize |

## How It Works

1. **Weight matrix multiplication**: each drive has a signed weight vector over the 6 hormones
2. **Sigmoid activation**: raw value → [0, 1] through a steep sigmoid
3. **[[Impulse]] detection**: threshold crossing or rapid change triggers a discrete impulse event

## Connects To

- Input: [[Hormone System]] levels
- Output: drive vector + [[Impulse]] list → [[Output Port]]
- Labels: [[Emotion Map]] reads drive vectors for labeling
