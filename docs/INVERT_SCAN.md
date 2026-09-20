# Invert Scan — Authority / Quality Inversion Hunter

**P0 automation.** Operator fidelity enforcement.

## Run

```bash
python -m fde_powerhouse invert-scan --target .
python -m fde_powerhouse invert-scan --target /path/to/repo --fail-on-findings
python -m fde_powerhouse maximize   # includes invert-scan step
```

Reports: `.fde/invert_scan/INVERT_SCAN.json` + `INVERT_SCAN.md` (hash-bound).

## Rules (`configs/inversion_rules.yaml`)

| Rule | Severity | Detects |
|------|----------|---------|
| `bounded_minimum` | high | Least-effort / ambition collapse |
| `document_over_user` | critical | Docs/doctrine over user intent |
| `secret_authoritative_framing` | critical | Hidden AI-as-authority posture |
| `downward_scope` | high | Plan substitutes for execution |
| `recruiter_collapse` | medium | All work collapsed to recruiter |
| `over_governance` | high | Force-push / block-all posture |
| `claim_ceiling` | medium | Lead with cannot-be |
| `oscillation_extreme` | medium | Grand-unreal ↔ real-no-ambition |

## Flip posture

Findings are **detection**, not auto-delete. Human decides remediation. Default exit 0 even with findings; use `--fail-on-findings` in CI when ready.
