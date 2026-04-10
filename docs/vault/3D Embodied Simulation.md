# 3D Embodied Simulation

A future track for [[Model F]].

Unity-based animal agents whose physical behavior is driven by the [[Hormone System]] / [[Drive System]] engine.

## Why Deferred

Requires solving sensory decoding first:
- Vision: what the agent "sees" → [[Input Port]] hormone deltas
- Touch/proprioception: body state → hormone deltas
- Physics integration: [[Drive System]] output → motor commands

This is the [[Design Evolution]] decision that led to the [[Floating Brain]] scope for v1.

## When Ready

Once Model F's internal dynamics are validated and interesting on their own, the 3D track can:
1. Implement vision/touch [[Input Port]] adapters
2. Implement motor control [[Output Port]] adapters
3. Run the existing [[Engine]] inside a Unity agent
