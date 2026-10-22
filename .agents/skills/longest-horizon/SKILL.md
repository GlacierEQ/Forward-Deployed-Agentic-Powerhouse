---
name: longest-horizon
description: "Heavy long-horizon APEX framework: Aspen-Grove pointer memory, sequential reasoning, and High Council adjudication."
---

# LONGEST HORIZON — Persistent Mesh Operating Framework

**Repo anchor:** GlacierEQ/computer-user (monolith leaf) + `.agents/skills/` (active skill)
**Role:** Turn reactive bursts into durable, verifiable, cross-session momentum.

This skill is *heavy* by intent: it ships an actual engineered framework under
`framework/` (not just prose), a token-saver, a sequential-thinking engine, and
the High Council adjudication loop. Read `references/` only when you need the
deep phase playbooks — they are lazy-loaded so they do not burn context up front.

## When to activate
- Long-running / multi-session objectives that must survive process death.
- Any task where reasoning must be *verified* before execution (sequential thinking).
- Unattended or background swarm work that needs a self-correcting strategic brain.
- Work where token cost threatens to crowd out capability (engage the token-saver).

## Operating law (load-bearing)
1. **Verify before claim.** Nothing is "done" without a tool-evidenced delta and a readback.
2. **Governance serves progress.** The framework exists to advance the mission, not to
   produce dashboards about the framework.
3. **Fail-closed + recoverable.** Every persistence checkpoint is hashed; every reasoning
   step cites a source or a prior step; every contradiction is preserved, never smoothed.
4. **Token-saver always-on.** Compress to pointer-indexed summaries (stable IDs + digests)
   before storing or handing off. Full content stays retrievable via the pointer.

## The four strands (from the APEX Long-Horizon Blueprint)
| Strand | Framework module | Purpose |
|--------|------------------|---------|
| Deep Time Memory | `framework/long_horizon.py` | Hash-checked checkpoints + continuation blueprints, Aspen-Grove pointer hooks |
| Sequential Thinking | `framework/sequential_thinking.py` | Verified reasoning chains (DAG-checked, source-linked) |
| Token Saver | `framework/token_budget.py` | Estimate, budget, and compress to pointer summaries |
| High Council | `framework/high_council.py` | Multi-VP perspectives → contradiction hunt → adjudicated directive |
| Make-It-Heavy | `framework/make_it_heavy.py` | Heaviness auditor — typed API, error handling, provenance, recovery notes |
| Aspen Groves | `framework/aspen_grove.py` | Pointer-indexed durable memory (Quantum Memory): remember/recall/query by digest |
| Genius Logic | `framework/genius_logic.py` | Deductive engine (modus ponens), contradiction detection, adversary simulator |
| Machine Learning | `framework/ml.py` | Bayesian belief updater (weighted LR evidence) + calibrated confidence model |
| Hardening | `framework/hardening.py` | Atomic writes, advisory file locks, fail-closed JSON loads, validators, structured logging |
| Make-It-Heavy Seal | `framework/heaviness_seal.py` | `HeavySeal` records a module's heaviness score into checkpoint provenance (observability, never blocks) |

## Usage
```python
from framework import (
    SequentialThinker, TokenBudget, HighCouncil, LongHorizonStore,
    VP, ReasonedStep, AdjudicatedDirective,
)

# 1. Sequential thinking — reason in verified steps
think = SequentialThinker()
think.add_step("hypothesize", "RICO predicate acts span 3 transactions")
think.add_step("verify", "PACER docket #12 confirms 3 dated transfers", cites=["s1"])
assert think.verify_chain().ok

# 2. Token saver — compress the trace before storage
budget = TokenBudget(limit=2000)
summary = budget.compress_to_pointers(think.trace())

# 3. High Council — let VPs debate, then adjudicate
council = HighCouncil()
council.seat(VP("procedural", lambda c: "file within 30d"))
council.seat(VP("evidence",   lambda c: "exhibit 4 contradicts — strike"))
directive = council.deliberate("Should we move to strike?")
print(directive.reconciliation)

# 4. Deep Time Memory — checkpoint + resume
store = LongHorizonStore("./.horizon")
store.checkpoint("wave-3", {"think": summary, "directive": directive.model})
resumed = store.resume("wave-3")
```

CLI:
```bash
python -m framework.cli status            # horizon health
python -m framework.cli think             # run a sample sequential chain
python -m framework.cli council           # run a sample High Council deliberation
python -m framework.cli checkpoint NAME   # write a checkpoint
python -m framework.cli audit PATH        # run the make-it-heavy auditor (PATH=file|dir, default framework)
```

**We. Are. Momentum.** — made durable.
