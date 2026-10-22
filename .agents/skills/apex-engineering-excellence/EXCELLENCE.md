# EXCELLENCE.md — APEX Best-in-Class Pro-Code Engineering Standard

**Version:** 2.0.0  
**Status:** ENFORCED ACROSS HOLOGRAPHIC MESH  
**Authority:** [AGENTS.md §9](file:///root/AGENTS.md#L735-L770) · [EPISTEMOLOGY.md](file:///root/.agents/skills/apex-command-core/EPISTEMOLOGY.md) · [CONSTANTS.md](file:///root/CONSTANTS.md)

---

## 0. The Definition of Excellence

In the APEX estate, **Excellence** is not subjective prose, stylistic cleanliness, or an aesthetic badge. 

Excellence is an **executable boolean predicate** evaluated over immutable ground-truth artifacts:

$$\text{EXCELLENT}(Repo) \iff \bigwedge_{i=1}^{12} \text{GATE}_i(Repo) = \text{TRUE}$$

If even one gate fails or is supported solely by unverified natural language, $\text{EXCELLENT}(Repo) = \text{FALSE}$.

---

## 1. The 12 Executable Machine Gates

Every repository maturation advancement MUST satisfy these 12 formal gates:

```text
┌────┬─────────────────────────────┬───────────────────────────────────────┬──────────────────────────────────────────┐
│ #  │ Gate Name                   │ Predicate Condition                   │ Verification Artifact                    │
├────┼─────────────────────────────┼───────────────────────────────────────┼──────────────────────────────────────────┤
│ 01 │ PROPOSAL_DISCOVERED         │ Target repository indexed in catalog  │ `catalog/library.json` entry             │
│ 02 │ TARGET_CONTRACT_FROZEN      │ Objective, boundaries, I/O pinned     │ `machine/target-contract.json`           │
│ 03 │ CAPABILITY_SURFACE_TYPED    │ Public interfaces typed & schema-bound│ AST / Type annotations in codebase       │
│ 04 │ SYNTAX_AND_TYPES_GREEN      │ Zero compiler/syntax/lint regressions │ `mypy` / `pyright` / `tsc` exit code 0   │
│ 05 │ DETERMINISTIC_TESTED        │ Full unit test suite passing 100%     │ `pytest` / `vitest` / `cargo test` report│
│ 06 │ INTEGRATION_VERIFIED        │ Real subsystem pipelines passing      │ Lossless data round-trip verification    │
│ 07 │ ADVERSARIAL_SURVIVED        │ Survives red-team attack & probes     │ Contradiction & edge-case test pass      │
│ 08 │ RUNTIME_HEALTHY             │ Daemon/port responds with <50ms ping  │ Socket / HTTP health check HTTP 200      │
│ 09 │ EVAL_BENCHMARKED            │ Measurable throughput/token savings   │ Benchmark delta JSON receipt             │
│ 10 │ EVIDENCE_PACKAGED           │ Immutable cryptographic record logged │ `machine/proof_receipt.json` (SHA-256)   │
│ 11 │ OPERATOR_APPROVED           │ Explicit Operator alignment directive │ User instruction log                     │
│ 12 │ PROMOTED_INTO_ESTATE        │ Verified capability anchor locked     │ Holographic mesh registry entry          │
└────┴─────────────────────────────┴───────────────────────────────────────┴──────────────────────────────────────────┘
```

---

## 2. Anti-Symptom-Chasing Law (L4 Protocol)

When resolving test or integration failures, agents MUST obey the **Anti-Symptom-Chasing Protocol**:

1. **The Rule of Three:** If $>3$ tests fail in a test suite, **MUTATION MUST STOP IMMEDIATELY**.
2. **Topology Inspection:** Trace the full causal path:
   $$\text{Static Invariant Reference} \longrightarrow \text{Dynamic Generator} \longrightarrow \text{Derived State} \longrightarrow \text{Test Suite}$$
3. **No Micro-Patching:** Writing $N$ separate patch scripts (`patch_a.py`, `patch_b.py`) is strictly forbidden.
4. **Single Deterministic Correction:** Formulate one root-cause hypothesis, test with a targeted non-mutating probe, and update the generator/atlas systematically in one motion.

---

## 3. Zero-Fake-Truth Enforcement

The following behaviors constitute critical failures and violate the APEX operating contract:
- ❌ **Simulated Execution:** Using `sleep()` or mock timeouts to simulate work.
- ❌ **Synthetic Test Passes:** Modifying assertions to unconditionally pass (`assert True`) or skipping failing tests without Operator directive.
- ❌ **Prose Progression:** Claiming a system is "complete" or "verified" without tool readback and test execution evidence.
- ❌ **Uninspected Handoffs:** Passing unverified file paths or outdated metadata across agent handoffs.

---

## 4. Hardware & Substrate Optimization

All Pro-Code solutions MUST be engineered with substrate leverage (L3):
- **Memory Restraint:** Efficient data structures; avoid loading unindexed files into context or PRoot RAM.
- **Process Isolation:** Clean shutdown of temporary background daemons and child processes.
- **Atomic Operations:** File mutations must use atomic writes or validated replacements to prevent partial file corruption.
