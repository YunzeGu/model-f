# LLM Dialogue

A future track for [[Model F]].

A persistent emotional core for conversational agents that maintains state across sessions and generates spontaneous internal state changes.

## How It Would Work

1. [[Model F]] runs continuously, generating [[Impulse|impulses]] and [[Drive System|drive states]]
2. An [[Output Port]] adapter translates the current emotional state into LLM system prompt context
3. An [[Input Port]] adapter translates conversation events (user anger, praise, topics) into [[Hormone System]] deltas
4. The LLM's responses are colored by the emotional state — not controlled, but influenced

## Why Deferred

[[Model F]] v1 deliberately excludes rational reasoning. The LLM track requires bidirectional integration and careful design to prevent the rational agent from overriding the irrational impulse generator.

## Key Challenge

How to let [[Non-Purposive Autonomy|non-purposive impulses]] influence a goal-oriented LLM without the LLM rationalizing them away.
