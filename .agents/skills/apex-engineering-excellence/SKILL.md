---
name: apex-engineering-excellence
description: "Pro-code engineering suite: verification ladder, performance benchmarking, optimized builds, and zero-fake execution."
version: 1.0.0
status: active
---

# APEX Engineering Excellence — Mega-Skill 6

**Pro-Code Engineering Suite** — Production-grade code that survives adversarial review.

## Composed Sub-Skills

| Sub-Skill | Role | Entry Point |
|-----------|------|-------------|
| verification | Independent verification (syntax → unit → integration → e2e → runtime → deploy) | `verification` skill |
| benchmark-suite | Throughput, latency, memory, token cost with before/after measurements | `benchmark-suite` skill |
| turbopack | Optimized builds with Turbopack | `turbopack` skill |
| nextjs-ecosystem | Next.js ecosystem engineering | `nextjs-ecosystem` skill |
| frontend-ui-toolkit | Frontend engineering toolkit | `frontend-ui-toolkit` skill |
| release | Automated release with verification gates | `release` skill |
| runtime-cache | Multi-layer caching for sub-second tool execution | `runtime-cache` skill |
| zero-fake-truth-enforcer | Zero fake execution, evidence-backed claims only | `zero-fake-truth-enforcer` skill |

## Unified Capabilities (apex.capabilities/v1)

```yaml
schema: apex.capabilities/v1
repository: GlacierEQ/Pro-DOCTOR-STRANGE
mega_skill: apex-engineering-excellence
capabilities:
  - id: code.verify
    description: Independent verification ladder (syntax → unit → integration → e2e → runtime → deploy)
    entrypoint: verification
    interface: cli|library|http
    inputs:
      - target: {type: string, required: true}
      - level: {type: string, enum: [syntax, unit, integration, e2e, runtime, deploy], default: syntax}
    outputs:
      - passed: {type: boolean}
      - level: {type: string}
      - details: {type: object}

  - id: code.benchmark
    description: Performance benchmarking with before/after measurements
    entrypoint: benchmark-suite
    interface: cli|library|http
    inputs:
      - target: {type: string, required: true}
      - metrics: {type: array, items: {type: string, enum: [throughput, latency, memory, token_cost]}}
      - baseline: {type: object}
    outputs:
      - results: {type: object}
      - comparison: {type: object}

  - id: code.build
    description: Optimized builds with Turbopack, Next.js ecosystem
    entrypoint: turbopack + nextjs-ecosystem
    interface: cli|library
    inputs:
      - project_path: {type: string, required: true}
      - mode: {type: string, enum: [dev, prod, analyze], default: prod}
    outputs:
      - build_artifacts: {type: object}
      - metrics: {type: object}

  - id: code.release
    description: Automated release with verification gates
    entrypoint: release
    interface: cli|library
    inputs:
      - version: {type: string}
      - changelog: {type: string}
      - gates: {type: array, items: {type: string}}
    outputs:
      - release_artifact: {type: object}
      - gate_results: {type: object}

  - id: code.cache
    description: Multi-layer caching for sub-second tool execution
    entrypoint: runtime-cache
    interface: library|http
    inputs:
      - key: {type: string}
      - compute_fn: {type: string}
    outputs:
      - cached: {type: boolean}
      - value: {type: object}
      - latency_ms: {type: integer}

  - id: code.enforce
    description: Zero fake execution, evidence-backed claims only
    entrypoint: zero-fake-truth-enforcer
    interface: cli|library
    inputs:
      - claim: {type: string}
      - evidence: {type: object}
    outputs:
      - verified: {type: boolean}
      - violations: {type: array}
```

## CLI Interface

```bash
apex-code <command> [options]

# Verification
apex-code verify --target ./src --level unit
apex-code verify --target ./src --level integration
apex-code verify --target ./src --level e2e

# Benchmark
apex-code benchmark --target ./dist --metrics throughput,latency,memory --baseline baseline.json

# Build
apex-code build --project ./my-app --mode prod

# Release
apex-code release --version 1.0.0 --changelog CHANGELOG.md --gates verify,benchmark,security

# Cache
apex-code cache --key "build:prod" --compute "npm run build"

# Enforce
apex-code enforce --claim "All tests pass" --evidence evidence.json
```

## Verification Gates

| Gate | Test | Pass Criteria |
|------|------|---------------|
| G1 | `verify --level syntax` | 0 syntax/type errors |
| G2 | `verify --level unit` | 100% unit tests pass |
| G3 | `verify --level integration` | All integration tests pass |
| G4 | `verify --level e2e` | E2E paths verified |
| G5 | `benchmark` | Metrics measured, baseline comparison |
| G6 | `build --mode prod` | Production build succeeds, bundle size < threshold |
| G7 | `release` | All gates pass, artifact signed |
| G8 | `enforce` | Zero fake execution violations |