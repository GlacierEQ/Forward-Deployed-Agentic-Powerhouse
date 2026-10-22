---
name: apex-security-fortress
description: "Security hardening suite: secrets detection, dependency audit, zero-trust config, and compliance verification gates."
version: 1.0.0
status: active
---

# APEX Security Fortress — Mega-Skill 8

**Security Hardening Suite** — Zero-trust baseline for all mega-skills.

## Composed Sub-Skills

| Sub-Skill | Role | Entry Point |
|-----------|------|-------------|
| zero-fake-truth-enforcer | Evidence-backed claims only, anti-hallucination | `zero-fake-truth-enforcer` skill |
| auth | Least-privilege authentication/authorization | `auth` skill |
| env-vars | Secure environment/secret management | `env-vars` skill |
| verification | Independent verification ladder | `verification` skill |
| plugin-audit | Plugin/security audit (archived) | `plugin-audit` archived skill |
| security-auditor pattern | Vulnerability scanning, secrets detection, dependency audit | Subagent pattern |

## Unified Capabilities (apex.capabilities/v1)

```yaml
schema: apex.capabilities/v1
repository: GlacierEQ/Pro-DOCTOR-STRANGE
mega_skill: apex-security-fortress
capabilities:
  - id: security.scan_secrets
    description: Detect secrets, API keys, tokens in codebase
    entrypoint: security_audit.py scan_secrets
    interface: cli|library
    inputs:
      - path: {type: string, required: true}
      - patterns: {type: array, items: {type: string}}
    outputs:
      - findings: {type: array}
      - severity: {type: string}

  - id: security.audit_dependencies
    description: Audit npm/pip/cargo dependencies for vulnerabilities
    entrypoint: security_audit.py audit_deps
    interface: cli|library
    inputs:
      - manifest: {type: string, required: true}
      - registry: {type: string, enum: [npm, pypi, cargo], default: npm}
    outputs:
      - vulnerabilities: {type: array}
      - outdated: {type: array}
      - license_issues: {type: array}

  - id: security.review_permissions
    description: Review file/directory permissions, capability scopes
    entrypoint: security_audit.py review_perms
    interface: cli|library
    inputs:
      - path: {type: string, required: true}
      - policy: {type: string, enum: [least_privilege, standard, strict], default: least_privilege}
    outputs:
      - violations: {type: array}
      - recommendations: {type: array}

  - id: security.supply_chain
    description: Verify supply chain integrity (sigstore, SLSA, provenance)
    entrypoint: security_audit.py supply_chain
    interface: cli|library
    inputs:
      - artifacts: {type: array, items: {type: string}}
    outputs:
      - verified: {type: boolean}
      - attestations: {type: array}

  - id: security.compliance_gate
    description: Run compliance checks (SOC2, HIPAA, GDPR, custom policies)
    entrypoint: security_audit.py compliance
    interface: cli|library
    inputs:
      - policy: {type: string, required: true}
      - target: {type: string, required: true}
    outputs:
      - passed: {type: boolean}
      - violations: {type: array}
```

## CLI Interface

```bash
apex-security <command> [options]

# Secrets detection
apex-security scan --path ./src --patterns "API_KEY,SECRET,TOKEN,PASSWORD"

# Dependency audit
apex-security audit-deps --manifest package.json --registry npm
apex-security audit-deps --manifest requirements.txt --registry pypi

# Permission review
apex-security review-perms --path . --policy least_privilege

# Supply chain
apex-security supply-chain --artifacts dist/*

# Compliance gate
apex-security compliance --policy SOC2 --target ./src
```

## Verification Gates

| Gate | Test | Pass Criteria |
|------|------|---------------|
| G1 | `scan_secrets` on known test file | Detects 100% of planted secrets |
| G2 | `audit_deps` on vulnerable manifest | Reports known CVEs |
| G3 | `review_perms` on sensitive dirs | Flags world-writable, excessive perms |
| G4 | `supply_chain` on signed artifacts | Verifies sigstore attestations |
| G5 | `compliance_gate` on policy | Zero critical violations |