# Scale FDE Mission — Reproduce Current Verification Frontier

Canonical mission: `shared/SCALE_FDE_MISSION.yaml` (`SCALE-FDE-DEMO-001`).

## Workstream E verifier

Source:
`GlacierEQ/computer-user@d0550aa93896343c01b4f9aaf80c845b7e4dcf90`
branch `scale/verification-product`.

Focused verification:

```bash
python -m pip install -e . pytest==9.1.1 ruff==0.16.1
PYTHON_BIN=python bash scripts/ci/scale_agent_e_verify.sh
```

The proof is implementation-scoped and deliberately sets
`mission_certification_claimed=false`.

## Workstream B independent behavior check

At:
`GlacierEQ/computer-user@dd9ea50bce265d5ffc235999909e4ee9b08a4732`

```bash
python -m pytest -q tests/test_scale_runtime_durability.py
```

Independent E execution on 2026-10-06: **12 passed**.

## Mission certification

Do not manufacture missing inputs. Once current D routed provider evidence plus
empirical baseline and full-stack summaries exist, run the verifier from the E
branch:

```bash
python scripts/scale_fde_verify.py \
  --mission-contract shared/SCALE_FDE_MISSION.yaml \
  --execution-receipt evidence/EXECUTION_INPUT.json \
  --evaluation-receipt evidence/EVALUATION_INPUT.json \
  --claim-chains evidence/CLAIM_CHAINS.json \
  --readback-assertions evidence/READBACK_ASSERTIONS.json \
  --falsification-tests evidence/FALSIFICATION_TESTS.json \
  --postconditions evidence/POSTCONDITIONS.json \
  --verifier-id agent-e \
  --output-dir scale_fde/evidence
```

A real `MISSION_RECEIPT.json` is permitted only if the verifier returns
`VERIFIED_SUCCESS`. C then consumes that receipt to perform real Mission-1
capability registration and Mission-2 automatic reuse.
