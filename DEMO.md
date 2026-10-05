# Five-minute diligence walkthrough

This walkthrough demonstrates the repository's forward-deployed engineering loop without requiring authority to merge, send, or deploy anything.

## 1. Inspect the runtime

```bash
python -m pip install -e ".[dev]"
python -m fde_powerhouse doctor
```

**Inspect:** version, supported modes, leading-edge catalog visibility, and the availability state of optional capability bridges. Missing optional bridges should be reported rather than invented.

## 2. Run a bounded lifecycle

```bash
python -m fde_powerhouse cycle \
  --mode compose \
  --target customer-proof \
  --problem "Turn an ambiguous operational request into an evaluated, approval-gated agent workflow."
```

**Inspect:** the ordered stage receipts from DISCOVER through DEPLOY. Each receipt carries structured evidence and a SHA-256 digest. The final deploy stage should produce an approval packet rather than performing an external deployment.

## 3. Generate the diligence surfaces

```bash
python -m fde_powerhouse showcase --target diligence
python -m fde_powerhouse proof
```

**Inspect:** explicit cycle status, proof metadata, integration evidence, and the boundary between available capability and authorized action.

## 4. Validate an integration without executing it

```bash
python -m fde_powerhouse invoke --pipeline control-plane --validate-only
```

If the optional integration is unavailable locally, the result should say so. Availability is evidence; absence of a local integration is not converted into a fabricated success.

## 5. Run the regression gates

```bash
ruff check src tests
pytest --cov=fde_powerhouse --cov-report=term-missing --cov-fail-under=70
```

CI repeats the quality gates across Python 3.11, 3.12, and 3.13 and then runs the runtime doctor and demo.

## What this demonstrates

The important artifact is not a polished transcript. It is the system behavior: ambiguous input is framed, execution is decomposed into explicit stages, integrations are validated, evaluation can fail closed, evidence is emitted, and external authority remains human-gated.
