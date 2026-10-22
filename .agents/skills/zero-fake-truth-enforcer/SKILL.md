---
name: zero-fake-truth-enforcer
description: Zero fake execution — every claim must be evidence-backed.
---
# Zero Fake Truth Enforcer

## Prohibited Patterns (Hard Blocks)
1. Sleep-based simulated completion.
2. Mocked integration presented as live.
3. Hard-coded "VERIFIED" state without actual verification.
4. Placeholder adapters presented as implemented.
5. Success logs emitted before work actually succeeds.
6. Demo-only routes described as production.
7. Silent exception swallowing.
8. Synthetic evidence presented as source evidence.

## Enforcement
Before any claim of completion, the agent MUST:
1. Show the tool call that performed the work.
2. Show the tool output confirming success.
3. If applicable, show a readback verifying the state change persisted.

Violations are treated as integrity failures.
