# Scale FDE End-to-End Mastery — Research → Execution

Mission: `SCALE-FDE-DEMO-001`

This document converts current Scale role requirements and 2026 agent-systems research into executable engineering invariants for the GlacierEQ demonstration. It is not a reading list. Every research finding below maps to a concrete runtime, evaluation, or evidence requirement.

## 1. What the job actually is

Scale's current Forward Deployed Software Engineer, Public Sector role says the engineer embeds with mission users, owns delivery from prototype through stable production, builds backend/data integrations, and turns field-learned patterns into reusable platform capability.

Source: https://scale.com/careers/4481921005

The Frontier Agents Engineer role expands that lifecycle across agent runtime, orchestration, context pipelines, tool integrations, evaluation, observability, deployment, experimentation, and continuous improvement.

Source: https://scale.com/careers/4694861005

**GlacierEQ invariant:** a successful demo must not stop at architecture, local tests, or an agent answer. It must cross the whole loop:

```
mission ambiguity
→ mission understanding
→ capability discovery
→ architecture
→ dependency-aware execution
→ provider mutation
→ provider readback
→ evaluation
→ deployment-readiness decision
→ reusable capability extraction
→ second-run reuse
→ operational evidence
```

## 2. Ambiguity: investigate first, escalate selectively

HiL-Bench shows that strong agents collapse when decision-critical information is missing and they must decide whether to ask for help. The failure mode is silent guessing, not tool incapability.

Sources:
- https://scale.com/blog/hil
- https://labs.scale.com/papers/hil

**System rule:** distinguish:
1. unknown but discoverable,
2. unknown but inferable with evidence,
3. decision-critical ambiguity that cannot be safely resolved internally.

Only class 3 triggers human escalation. Measure selective-escalation precision/recall instead of rewarding either silent guessing or question spam.

## 3. Multi-agent execution: spine owns mutable state

Scale's Spine-Branch work models a physical constraint we must treat as architectural: parallel VM states do not merge. A persistent spine carries the main state; branch workers collect bounded information and return artifacts/evidence.

Source: https://labs.scale.com/papers/spine-branch-coordination

**System rule:**
- Runtime B owns the mutable mission spine.
- A discovery workers and other parallel branches are bounded and return immutable evidence.
- Branch workers do not independently mutate shared mission state.
- State merge attempts are a verification failure.
- Handoffs are typed, content-addressed, and receipt-bound.

## 4. Deployment readiness is not benchmark accuracy

READY defines deployment qualification as reliability at a stated target, human oversight burden, and total cost for a concrete workflow, followed by held-out validation.

Sources:
- https://labs.scale.com/papers/reliable-enterprise-agent-deployment
- https://labs.scale.com/blog/ready
- https://labs.scale.com/ready-benchmarks

**Agent E rule:** compare baseline and full-stack under identical mission contract and identical economic assumptions. Required metrics now include:
- achieved reliability,
- reliability target,
- autonomous coverage,
- human review fraction,
- total cost per case,
- selective-escalation F1,
- completion rate,
- recovery success,
- verification rate,
- context loss,
- duplicate actions,
- tool failures,
- wall-clock time,
- branch-state merge attempts,
- verified branch-handoff rate.

The full stack cannot be called better if it misses the stated reliability target, regardless of improvements elsewhere.

## 5. The verifier must itself be falsified

Scale's 2026 verifier research found that reference-perfect outputs can hide useless graders, that critical corruptions can pass existing checks, and that hard gates plus dense scoring are needed.

Sources:
- https://labs.scale.com/blog/verifier-design-for-cua
- https://labs.scale.com/blog/agentic-rubrics
- https://scale.com/blog/swe-atlas-complete

**Agent E rule:** mission certification requires mutation-tested verifier evidence:
- corrupt at least one critical field or desired-state fingerprint,
- prove the verifier detects the corruption,
- preserve the corruption test as evidence,
- refuse certification when the verifier fails sensitivity.

Passing the happy path is not evidence that the verifier works.

## 6. Debug the corpus, not anecdotes

Scale's Insights Generator work shows that full-run-history analysis reveals systematic failure modes that individual traces hide.

Source: https://scale.com/blog/insights-generator

**System rule:** preserve every mission run and classify recurrent failures across the corpus:
- false completion,
- context loss,
- duplicate mutation,
- silent discarded execution,
- provider ambiguity,
- overconfident gap filling,
- verifier blind spots,
- state-continuity failure,
- tool-selection failure.

The learning loop promotes fixes only when failure frequency decreases on subsequent held-out runs.

## 7. Learning should prefer structural gains

VeRO found that improvements to tools/workflows transfer better across model swaps than prompt-only optimization.

Source: https://scale.com/blog/vero

**Compounding rule:** after Mission 1:
1. identify the structural mechanism that caused the gain,
2. version it,
3. test it on held-out cases,
4. rerun under at least one changed model/runtime condition when feasible,
5. register only verified reusable capability,
6. prove Mission 2 selects it automatically.

Prompt-only gains are lower-confidence unless they survive the same tests.

## 8. MCP is becoming stateless; mission state must be explicit

MCP 2026-07-28 moves the protocol core toward stateless requests and formalizes Tasks as durable state machines with task handles.

Sources:
- https://blog.modelcontextprotocol.io/posts/2026-07-28/
- https://tasks.extensions.modelcontextprotocol.io/specification/draft/tasks

**Integration rule:**
- never rely on hidden transport session state for mission continuity,
- pass explicit mission/task/continuation identifiers,
- use durable task handles for long-running calls,
- bind idempotency and authorization to explicit request identity,
- permit any compatible stateless worker to resume from durable state.

## 9. Evidence hierarchy

For each important claim, preserve:

```
CLAIM
→ SOURCE
→ REVISION
→ EXECUTION
→ PROVIDER OBSERVATION
→ INDEPENDENT VERIFICATION
→ MUTATION/FALSIFICATION TEST
→ RECEIPT
```

Source reading alone proves implementation shape, not runtime behavior.
A provider acceptance proves an attempt, not desired state.
A self-authored success flag proves neither.
Mission completion requires independent evidence across the chain.

## 10. Demo terminal condition

The demo is finished only when one command can drive the canonical mission through:

```
recover
→ discover
→ compose
→ decompose
→ execute
→ inject failure
→ recover
→ mutate provider
→ read back
→ evaluate
→ qualify
→ extract capability
→ preserve
→ run Mission 2
→ automatically reuse Mission-1 capability
→ demonstrate measured improvement
```

Required final evidence:
- exact mission contract,
- baseline run summary,
- full-stack run summary,
- deployment profile,
- B durability receipt,
- D current provider-routing/readback receipt,
- E verifier mutation proof,
- verification receipt,
- Mission-1 receipt,
- reusable capability registration,
- Mission-2 reuse receipt,
- comparative metrics,
- REPRODUCE.md.

## Current frontier

Already strong:
- A estate discovery / Gatling.
- B durable crash/lease behavior (independently re-executed by E).
- C Aspen/Genius resurrection and reuse mechanics.
- E independent verifier, now upgraded with deployment-readiness metrics and verifier mutation-test requirements.

Still blocking the full proof:
1. current Sigma → deployed Colossus routed provider proof,
2. B machine-readable completion artifact,
3. empirical same-mission single-agent baseline,
4. empirical same-mission full-stack run,
5. exact-head external CI for E,
6. real Mission-1 receipt,
7. real Mission-2 automatic reuse after Mission-1 registration.

That is the execution frontier. No architecture rewrite is warranted.
