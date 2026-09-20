# CONSTANTS.md — APEX Estate Invariant Constants & Physical Laws

**Version:** 1.0.0  
**Enforcement:** UNIVERSAL / HARD LOAD-BEARING  
**Scope:** All agents, swarms, pipelines, subagents, tools, and background tasks.

---

## 0. The Holographic Axioms (Non-Negotiable)

1. **Decentralized Holographic Mesh:**
   $$\text{Authority} = \emptyset \quad (\text{Consensus through verifiable evidence, not single-winner decree})$$
   - No single model or repository is the sovereign arbiter.
   - Every node is an anchor for specific, verified capabilities.
   - Vocabulary: `elite · pro · Hard · G` (never single-authority or sovereign winner framing).

2. **Zero-Fake-Truth Boundary (AGENTS.md §9.2):**
   $$\forall \text{ Claim } C, \quad C \in \text{VERIFIED} \iff \exists \text{ Execution Receipt } R \text{ s.t. } \text{Verify}(R) = \text{TRUE}$$
   - Sleep-based delays, stubbed returns, mock-swapped passes, and prose assertions without tool readback are strictly forbidden.

3. **Innovation Primacy (§0 Operator Constraint):**
   - Never fast-forward `origin/main` onto local trees. Local innovation base (`cb8e571` / `47b65f7`) always supersedes estate defaults upon conflict.

---

## 1. The L0–L5 Epistemic Constants

| Level | Name | Invariant Mathematical / Operational Rule | Violation Penalty |
|:---:|:---|:---|:---|
| **L0** | **Reference & Ground-Truth** | $\text{State} \equiv \text{SHA256}(\text{Raw Bytes}) \land \text{Git Hash} \land \text{Docket ID}$. Never assert unverified state. | Hard Rejection / Rollback |
| **L1** | **Component & Unit** | Deterministic function I/O contracts. $f(x) = y$ must pass syntax, type, and unit suites without side-effects. | Build Blocked |
| **L2** | **Subsystem & Pipeline** | Schema fidelity across boundaries. $\text{Schema}_{\text{Source}} \equiv \text{Schema}_{\text{Target}}$. Lossless domain-to-atlas projection. | Invalidation of Downstream |
| **L3** | **Backend Awareness & Leverage** | Exploit substrate mechanics (PRoot glibc, SQLite indexed WAL, socket polling) instead of brute-force loops. | Process Throttled |
| **L4** | **Invariant & Causal Modeling** | If failures $> 3$, **STOP MUTATING**. Formulate 1 root-cause hypothesis, test with 1 probe, patch the systemic generator in 1 motion. | Anti-Symptom-Chasing Interrupt |
| **L5** | **Agent Swarm Enterprise** | Holographic DAG topology with adversarial verification gates and immutable cryptographic receipts. | Consensus Failure |

---

## 2. Substrate & Hardware Leverage Bounds (L3 Physical Limits)

```text
┌────────────────────────────────────────────────────────┬───────────────────────────────────────────┐
│ Substrate Dimension                                    │ Hard Constant / Operational Constraint    │
├────────────────────────────────────────────────────────┼───────────────────────────────────────────┤
│ Execution Environment                                 │ PRoot Ubuntu glibc container on Termux    │
│ Physical RAM Ceiling                                   │ 7.6 GB Total (~600 MB Dynamic Free)       │
│ Local Heavy Inference Policy                          │ FORBIDDEN inside PRoot (Offload to MiMo/  │
│                                                        │ Groq/OpenRouter acceleration gateways)   │
│ Concurrency Worker Pool Cap                           │ 4 Concurrent Threads / Subagents Max      │
│ Vector DB / Index Engine                               │ SQLite WAL + Qdrant / Local In-Memory     │
│ Active Key Vault Substrates                            │ 3 Vaults (`gatekeeper`, `credentials`,   │
│                                                        │ `antigravity-oauth`) -> 305 Exported Keys│
│ Cloud PostgreSQL Vault                                │ Supabase Remote Vault (457 Indexed Keys)  │
│ Remote MCP Gateway                                     │ GlacierEQ Smithery (`mode=smart`, HTTP)   │
└────────────────────────────────────────────────────────┴───────────────────────────────────────────┘
```

---

## 3. The 12-Stage Machine Gate Constants

```text
STAGE_01_PROPOSAL_DISCOVERED      ->  Candidate registered in catalog/library.json
STAGE_02_TARGET_CONTRACT_FROZEN   ->  machine/target-contract.json frozen
STAGE_03_CAPABILITY_SURFACE_TYPED ->  Exposed endpoints & schemas typed
STAGE_04_SYNTAX_AND_TYPES_GREEN   ->  AST check & mypy / pyright clean
STAGE_05_DETERMINISTIC_TESTED     ->  pytest unit suite passing (100%)
STAGE_06_INTEGRATION_VERIFIED     ->  Pipeline / Subsystem passes without mocks
STAGE_07_ADVERSARIAL_SURVIVED     ->  Red-team probe / contradiction check clean
STAGE_08_RUNTIME_HEALTHY          ->  Port & socket health verified
STAGE_09_EVAL_BENCHMARKED         ->  Performance & token savings measured
STAGE_10_EVIDENCE_PACKAGED        ->  Immutable receipt & SHA logged
STAGE_11_OPERATOR_APPROVED        ->  Operator sign-off or explicit directive
STAGE_12_PROMOTED_INTO_ESTATE     ->  Anchor node locked in Holographic Mesh
```

---

## 4. Token & Context Conservation Constants

- **Direct Pointer Lookups:** Always prefer explicit pointer file paths (`file://...`) over expensive recursive globbing.
- **State Handoff Compaction:** Large tool logs and command traces must be parsed, filtered, and reduced to state diffs before handoffs.
- **Deduplication:** Never ingest identical rule or schema definitions twice within the same execution turn.
