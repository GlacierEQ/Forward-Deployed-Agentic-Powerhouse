# Scale FDE Mission — Reproducible Proof Surface

This repository contains a bounded forward-deployed engineering demonstration built around a concrete mission contract rather than a slideware architecture.

## Mission

The mission is defined in `shared/SCALE_FDE_MISSION.yaml`:

```text
recover → discover → compose → decompose → execute → fail → recover
→ verify → deploy → readback → compound → preserve
```

Five independently scoped workstreams share machine-readable contracts instead of coordinating through hidden conversational state:

- **A — Estate intelligence:** bounded parallel capability discovery and deterministic aggregation.
- **B — Runtime durability:** orchestration, resumability, failure recovery, and execution continuity.
- **C — Memory / compounding:** continuity substrate and Mission 1 → Mission 2 capability reuse.
- **D — Integration / MCP:** dependency-aware provider mutation, idempotency, reconciliation, and readback.
- **E — Verification / product:** independent evaluation, evidence graph, receipts, metrics, and the employer-facing proof surface.

## Why this is forward-deployed engineering

The point is not the framework. The point is the operating loop:

1. Recover the actual objective and current state.
2. Discover reusable capability before building new machinery.
3. Decompose work into independently testable surfaces.
4. Execute through real integration seams.
5. Inject and survive failures instead of assuming a happy path.
6. Verify target state rather than equating tool success with outcome success.
7. Preserve receipts and reusable capability so the next mission starts stronger.

The shared contract plane lives under `shared/` and includes the mission, architecture contract, workstream records, integration/defect queues, and receipt index.

## Evidence already present

A real integration defect exposed a convergence failure: the canonical control plane wrote Scale artifacts at the runtime root while workers published under `shared/`. The defect record preserves both the red and green evidence:

- RED CI run **37278166847** — failed because `shared/SCALE_FDE_MISSION.yaml` was missing.
- Repair revision **3ee3883b541def3179aeeb30cdacfaa8671fb8c5**.
- GREEN CI run **37278419952** — Python 3.11/3.12 full test + doctor + demo success observed; Python 3.13 test path success observed.

See `shared/DEFECT_QUEUE.json` for the preserved defect record.

This matters because the repository does not present “tests pass” as the whole story. It preserves the failure, the exact repair, and the verification evidence.

## Direct fit to the live Scale Public Sector FDE role

This demonstration is intentionally legible against the work Scale currently describes for its Honolulu Public Sector forward-deployed engineers, without claiming Scale affiliation or government deployment:

| Scale role surface | Reproducible evidence in this repository |
|---|---|
| Turn ambiguous customer missions into working software | `shared/SCALE_FDE_MISSION.yaml` + independently scoped workstreams |
| Own delivery from prototype through stable production behavior | runtime durability, failure recovery, verification, and readback loop |
| Build robust backend/data integrations | Integration / MCP workstream with dependency ordering, idempotency, reconciliation, and provider readback |
| Feed field patterns back into reusable platform capability | Memory / compounding workstream and Mission 1 → Mission 2 reuse contract |
| Operate agentic systems safely | explicit guardrails, evidence states, receipts, defect preservation, and independent verification |
| Orchestrate asynchronous agent work | five bounded workstreams coordinated through machine-readable shared contracts rather than hidden chat state |

Scale's adjacent Public Sector engineering roles also describe multi-layer agent guardrails, optimized retrieval, fleets of asynchronous agents, deviation alerts, and explainability. Those are evaluation targets for this proof surface—not claims of equivalence or production use inside Scale.

### Evidence boundary

This is an independent GlacierEQ engineering demonstration. It does **not** imply employment by Scale, access to Scale systems, government customer deployment, a security clearance, or completion of any unfinished workstream. The useful claim is narrower and reproducible: the repository exposes mechanisms for the same *class* of forward-deployed agentic problems and gives a reviewer concrete artifacts and commands to inspect them.

## Five-minute reproduction

```bash
python -m pip install -e ".[dev]"
ruff check src tests
pytest --cov=fde_powerhouse --cov-report=term-missing --cov-fail-under=70
python -m fde_powerhouse doctor
python -m fde_powerhouse demo
```

Then inspect:

```text
shared/SCALE_FDE_MISSION.yaml
shared/ARCHITECTURE_CONTRACT.json
shared/WORKSTREAM_A.json … shared/WORKSTREAM_E.json
shared/INTEGRATION_QUEUE.json
shared/DEFECT_QUEUE.json
shared/RECEIPT_INDEX.json
```

Missing or incomplete artifacts should be treated as incomplete mission evidence, not silently promoted to completion.

## What to evaluate

A reviewer should be able to answer four questions from repository evidence:

1. **Can the system turn an ambiguous objective into executable work?**
2. **Can it survive a failed route without losing the mission?**
3. **Can it prove what actually happened rather than merely report success?**
4. **Does successful work become reusable capability for the next mission?**

Those are the properties this demonstration is designed to make inspectable.
