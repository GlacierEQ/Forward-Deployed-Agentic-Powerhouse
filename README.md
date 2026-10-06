# Forward-Deployed-Agentic-Powerhouse

A public proof surface for **forward-deployed agent engineering**: take an ambiguous operational problem, frame it into a bounded plan, integrate agent capabilities, evaluate the result, emit evidence, and stop at a human approval boundary.

```text
DISCOVER → FRAME → BUILD → INTEGRATE → EVALUATE → PROVE → DEPLOY
```

The repository is designed to demonstrate the engineering loop behind field-deployed AI systems rather than an application-specific workflow. The core invariant is **power with verifiable boundaries**: execution produces receipts and deployment remains `approval_packet_only` unless a human explicitly authorizes the next step.

## Design note

This repository is deliberately built to merge with established enterprise delivery epistemology — specifically the "Simplifying AI" operating model: experimentation-to-production discipline, Say:Do accountability, and measurable business outcomes. The lifecycle stages, evidence receipts, and approval-gated deployment mirror the consulting delivery motion (discovery → build → eval → handoff) so the system plugs into existing enterprise motions instead of inventing new ones. Every gate and receipt in this repo exists because enterprise engagements fail without them. Nothing here is theoretical.

## What this proves

- **Problem framing:** converts a target and operating mode into a structured execution plan.
- **Agent integration:** composes local capability bridges and validates supported pipeline integrations.
- **Evaluation:** runs explicit stage gates and returns failure instead of silently promoting a bad result.
- **Evidence:** emits hash-bound stage and cycle receipts plus proof/showcase packets.
- **Human control:** defaults to validate-only integration and approval-gated deployment.
- **Regression discipline:** CI runs Ruff, coverage-gated tests, doctor, and demo across Python 3.11–3.13.

## Five-minute proof

```bash
python -m pip install -e ".[dev]"
python -m fde_powerhouse doctor
python -m fde_powerhouse showcase --target diligence
python -m fde_powerhouse proof
pytest --cov=fde_powerhouse --cov-report=term-missing --cov-fail-under=70
```

For the guided walkthrough and what to inspect in each output, see [DEMO.md](DEMO.md).

## Command surface

| Command | Purpose |
|---|---|
| `doctor` | Inspect the runtime and optional capability bridges |
| `cycle --mode …` | Run the DISCOVER→DEPLOY lifecycle and emit a cycle receipt |
| `showcase` | Produce a diligence-oriented proof pack |
| `proof` | Emit the current proof surface |
| `invoke` | Validate a supported integration; validate-only by default |
| `invert-scan` | Detect authority/quality inversion patterns |
| `scan --target` | Inventory an existing target for upgrade work |
| `maximize` / `demo` | Exercise the broad local proof surface |

## Safety and authority model

The runtime separates **capability** from **authority**. Pipeline integration is validate-only by default. The deploy stage emits an approval packet rather than merging, sending, or deploying on its own. Optional private integrations are additive: the public proof path remains inspectable without granting external authority.

## Architecture

The lifecycle is implemented as explicit stages with structured receipts:

1. **Discover** available capability and target context.
2. **Frame** the problem into a mode-specific plan.
3. **Build** a bounded workspace or scaffold.
4. **Integrate** supported capability bridges and validate integration paths.
5. **Evaluate** explicit gates.
6. **Prove** the result with evidence and receipts.
7. **Deploy** an approval-gated handoff packet.

The repository can optionally compose with a larger capability estate, but those integrations are not required to understand the lifecycle, authority model, or evidence mechanism demonstrated here.

## Development and verification

```bash
ruff check src tests
pytest --cov=fde_powerhouse --cov-report=term-missing --cov-fail-under=70
python -m fde_powerhouse doctor
python -m fde_powerhouse demo
```

CI runs these checks on Python 3.11, 3.12, and 3.13. A pinned optional integration validation is maintained separately; see [docs/CI_AND_PINS.md](docs/CI_AND_PINS.md). See [docs/INVERT_SCAN.md](docs/INVERT_SCAN.md) for the inversion scanner.

## Optional estate integrations

When the corresponding repositories are available locally, environment paths can enable additional validation surfaces:

```bash
export FDE_PATH_MEGA_SKILLS=/path/to/mega-skills
export FDE_PATH_GENIUS_MASTERY=/path/to/Genius-Mastery
python -m fde_powerhouse maximize
```

These are optional capability extensions, not prerequisites for the public proof.

---

**Forward Deployed Agentic AI · v0.7.1**
