# Invert Scan — Authority / Quality Inversion Hunter

**Layers:** pattern · semantic (negation/proximity) · cluster (co-occurrence)

## Run

```bash
python -m fde_powerhouse invert-scan --target .
python -m fde_powerhouse invert-scan --target /path/to/repo --fail-on-findings
```

Reports: `.fde/invert_scan/INVERT_SCAN.json` + `.md` (SHA-256).

## Semantic clusters

| Cluster | Signal |
|---------|--------|
| `authority_capture` | ≥2 authority/override terms in same file |
| `ambition_collapse` | ≥2 bounded-minimum / downward-scope terms |
| `governance_overreach` | ≥2 force-push / block-all terms |
| `framing_collapse` | ≥2 recruiter-collapse terms |

Negation / meta-discussion (`detect`, `forbid`, `anti-pattern`, …) **lowers confidence** so rules docs do not critical-fire on themselves.

## Rules

See `configs/inversion_rules.yaml`. Detection only — human remediates.
