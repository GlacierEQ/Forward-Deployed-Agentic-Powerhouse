---
name: apex-specialist-registry
description: Dynamic capability federation across estate repositories, curated link registry, and bulk skill activation.
version: 1.0.0
status: active
---

# APEX Specialist Registry — Mega-Skill 7

**Dynamic Capability Federation** — Mesh capability, not repository homogenization.

## Composed Sub-Skills

| Sub-Skill | Role | Entry Point |
|-----------|------|-------------|
| auth | Authentication/authorization with least-privilege scoping | `auth` skill |
| env-vars | Environment management | `env-vars` skill |
| marketplace | Skill marketplace & capability discovery | `marketplace` skill |
| knowledge-update | Continuous knowledge refresh from sources | `knowledge-update` skill |
| library-of-links | Curated link registry with provenance | `library-of-links` skill |
| operator-is-the-universe | Operator-sovereign control plane | `operator-is-the-universe` skill |
| apex-pillars | Pillar architecture governance | `apex-pillars` skill |
| activate_all_skills | Bulk skill activation with dependency resolution | `activate_all_skills` skill |

## Unified Capabilities (apex.capabilities/v1)

```yaml
schema: apex.capabilities/v1
repository: GlacierEQ/Pro-DOCTOR-STRANGE
mega_skill: apex-specialist-registry
capabilities:
  - id: specialist.discover
    description: Dynamic capability discovery across estate repositories
    entrypoint: marketplace + repo-cartographer pattern
    interface: cli|library|http
    inputs:
      - domain: {type: string, enum: [legal, orchestration, connectors, device, memory, engineering, all]}
      - capability_query: {type: string}
    outputs:
      - specialists: {type: array}
      - capability_graph: {type: object}

  - id: specialist.auth
    description: Least-privilege credential scoping per capability
    entrypoint: auth + env-vars
    interface: library|http
    inputs:
      - capability: {type: string, required: true}
      - scope: {type: string, enum: [read, write, admin], default: read}
    outputs:
      - credentials: {type: object}
      - token: {type: string}
      - expires: {type: string}

  - id: specialist.update
    description: Continuous knowledge refresh from sources
    entrypoint: knowledge-update
    interface: cli|library|http
    inputs:
      - sources: {type: array, items: {type: string}}
      - force: {type: boolean, default: false}
    outputs:
      - updated: {type: array}
      - failed: {type: array}
      - timestamp: {type: string}

  - id: specialist.link
    description: Curated link registry with provenance
    entrypoint: library-of-links
    interface: cli|library|http
    inputs:
      - query: {type: string}
      - tags: {type: array, items: {type: string}}
    outputs:
      - links: {type: array}
      - provenance: {type: object}

  - id: specialist.activate
    description: Bulk skill activation with dependency resolution
    entrypoint: activate_all_skills
    interface: cli|library
    inputs:
      - skills: {type: array, items: {type: string}}
      - mode: {type: string, enum: [all, selective, minimal], default: selective}
    outputs:
      - activated: {type: array}
      - failed: {type: array}
      - dependency_graph: {type: object}

  - id: specialist.govern
    description: Operator-sovereign control plane
    entrypoint: operator-is-the-universe + apex-pillars
    interface: cli|library|http
    inputs:
      - action: {type: string, enum: [status, audit, reconfigure, emergency_stop]}
      - target: {type: string}
    outputs:
      - result: {type: object}
      - authority: {type: string}
```

## CLI Interface

```bash
apex-specialist <command> [options]

# Discovery
apex-specialist discover --domain legal --query "motion generation"
apex-specialist discover --domain all

# Authentication
apex-specialist auth --capability legal.automate --scope write

# Knowledge update
apex-specialist update --sources github,notion,legal --force

# Links
apex-specialist link --query "HFCR 60(b)(4)" --tags evidence,case-law

# Activation
apex-specialist activate --skills apex-legal-intelligence,apex-connector-mesh --mode selective

# Governance
apex-specialist govern --action status --target apex-legal-intelligence
apex-specialist govern --action emergency_stop --target all
```

## Verification Gates

| Gate | Test | Pass Criteria |
|------|------|---------------|
| G1 | `discover` | Returns ≥1 specialist per domain |
| G2 | `auth` | Returns scoped credentials with expiry |
| G3 | `update` | All sources refreshed, timestamp recorded |
| G4 | `link` | Returns links with provenance metadata |
| G5 | `activate` | All requested skills active, deps resolved |
| G6 | `govern` | Returns control plane status, operator authority verified |