# Forward-Deployed-Agentic-Powerhouse

A public proof surface for **forward-deployed agent engineering**: take an ambiguous operational problem, frame it into a bounded plan, integrate agent capabilities, evaluate the result, emit evidence, and stop at a human approval boundary.

```text
DISCOVER → FRAME → BUILD → INTEGRATE → EVALUATE → PROVE → DEPLOY
```

The repository demonstrates the engineering loop behind field-deployed AI systems. The core invariant is **power with verifiable boundaries**: execution produces receipts and deployment remains `approval_packet_only` unless a human explicitly authorizes the next step.

---

## What this proves

- **Problem framing:** converts a target and operating mode into a structured execution plan.
- **Agent integration & bridges:** composes 7 capability bridges including Gemini Live 3.8, Smithery MCP Mesh, and Aspen-Grove Pointer Memory.
- **Evaluation:** runs explicit stage gates and returns failure instead of silently promoting a bad result.
- **Evidence:** emits hash-bound stage and cycle receipts plus proof/showcase packets.
- **Human control:** defaults to validate-only integration and approval-gated deployment.
- **Regression discipline:** CI runs Ruff, coverage-gated tests, doctor, and demo across Python 3.11–3.14.

---

## Specialized Capability Bridges

The powerhouse provides 7 composable bridges:

| Bridge | Role & Specification | Status |
|---|---|---|
| `mega_skills` | APEX Diamond Skills hierarchy (709 atomic → 33 compound → 29 mega) | Live / Auto-resolved |
| `genius` | Entity forge + 13-stage epistemic mastery loop | Live / Auto-resolved |
| `memory` | Multi-tier memory organism (working → episodic → semantic → graph) | Live / Auto-resolved |
| `pipelines` | Production readiness gates & deep-work execution pipelines | Live / Auto-resolved |
| `gemini_live` | Gemini 3.8 Live real-time bidirectional multimodal streaming + AI gateway fallback | Specialized |
| `mcp_mesh` | Smithery 32+ MCP holographic mesh discovery and tool routing | Specialized |
| `pointer_memory` | Aspen-Grove L0–L5 pointer-indexed memory (75–90% token compression) | Specialized |

---

## Five-minute proof

```bash
python -m pip install -e ".[dev]"
python -m fde_powerhouse doctor
python -m fde_powerhouse showcase --target diligence
python -m fde_powerhouse proof
pytest
```

For the guided walkthrough and what to inspect in each output, see [DEMO.md](DEMO.md).

---

## Command surface

| Command | Purpose |
|---|---|
| `doctor` | Inspect runtime and verify all 7 capability bridges (`[OK]`) |
| `cycle --mode …` | Run the DISCOVER→DEPLOY lifecycle and emit a hash-bound cycle receipt |
| `showcase` | Produce a diligence-oriented proof pack |
| `proof` | Emit the current proof surface with APEX specialization schema |
| `probe --bridge …` | Probe specific bridges (`gemini_live`, `mcp_mesh`, `pointer_memory`, etc.) |
| `invoke` | Validate a supported integration; validate-only by default |
| `invert-scan` | Detect authority/quality inversion patterns |
| `scan --target` | Inventory an existing target for upgrade work |
| `maximize` / `demo` | Exercise the broad local proof surface |

---

## Safety and authority model

The runtime separates **capability** from **authority**. Pipeline integration is validate-only by default. The deploy stage emits an approval packet rather than merging, sending, or deploying on its own. Optional private integrations are additive: the public proof path remains inspectable without granting external authority.

---

## Architecture

The lifecycle is implemented as explicit stages with structured receipts:

1. **Discover** available capability and target context.
2. **Frame** the problem into a mode-specific plan.
3. **Build** a bounded workspace or scaffold.
4. **Integrate** supported capability bridges and validate integration paths.
5. **Evaluate** explicit gates.
6. **Prove** the result with evidence and receipts.
7. **Deploy** an approval-gated handoff packet.

---

## Development and verification

```bash
ruff check src tests
pytest
python -m fde_powerhouse doctor
python -m fde_powerhouse demo
```

CI runs these checks on Python 3.11, 3.12, 3.13, and 3.14. See [docs/INVERT_SCAN.md](docs/INVERT_SCAN.md) for the inversion scanner.

---

**Forward Deployed Agentic AI · v0.8.0**
