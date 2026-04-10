# Design Evolution

How [[Model F]]'s scope was refined (2026-04-10).

## Iterations

1. **3D cat simulation** — Put a dopamine model into a cat agent in Unity
   - Rejected: requires solving sensory decoding (vision, touch) before the core model is validated

2. **[[Floating Brain]]** — Remove all sensors, just model internal dynamics
   - Accepted: isolates the core problem

3. **Remove LLM/reasoning** — Even simple animals have desires without complex logic
   - Accepted: Model F should work without any rational agent attached

4. **Remove language interaction** — Output is numerical vectors, not text
   - Accepted: pure impulse generation, not conversation

5. **[[Pluggable Architecture]]** — Define ports for future capabilities but connect none in v1
   - Accepted: clean interfaces for memory, LLM, vision, motor control

## Result

A maximally minimal base module: internal hormone dynamics → spontaneous behavioral [[Impulse|impulses]]. Everything else attaches later.
