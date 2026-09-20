---
name: apex-command-core
description: Mission Control & Orchestration — Full system bootup, verification, auto-healing, deep-horizon planning, multi-mode execution, DAG-based swarm orchestration. Composes apex-sovereign-supreme, apex-bootup-supreme, longest-horizon, apex-orchestration, apex-fail-safe-governor, apex-execution-modes, workflow, routing-middleware, apexruntime.
version: 1.0.0
status: active
---

# APEX Command Core — Mega-Skill 1

**Mission Control & Orchestration** — The central nervous system for all APEX operations.

## Composed Sub-Skills

| Sub-Skill | Role | Entry Point |
|-----------|------|-------------|
| apex-sovereign-supreme | Supreme bootup, device, connectors, runtime, intelligence | `scripts/bootup_runner.py` |
| apex-bootup-supreme | Vault activation, service resurrection, storage mounts | `scripts/bootup_runner.py` |
| longest-horizon | Deep time memory, sequential reasoning, High Council | `longest-horizon` skill |
| apex-orchestration | Multi-agent coordination, task decomposition | `apex-orchestration` skill |
| apex-fail-safe-governor | Safety guardrails, destructive action protocol | `apex-fail-safe-governor` skill |
| apex-execution-modes | Execution mode switching | `apex-execution-modes` skill |
| workflow | Workflow orchestration | `workflow` skill |
| routing-middleware | Request routing, middleware chain | `routing-middleware` skill |
| apexruntime | Runtime management | `apexruntime` skill |

## Unified Capabilities (apex.capabilities/v1)

```yaml
schema: apex.capabilities/v1
repository: GlacierEQ/Pro-DOCTOR-STRANGE
mega_skill: apex-command-core
capabilities:
  - id: mission.boot
    description: Full system bootup — vaults, services, storage, device, connectors
    entrypoint: scripts/bootup_runner.py
    interface: cli
    outputs:
      - vaults_activated: integer
      - services_online: integer
      - storage_mounted: integer
      - device_telemetry: object
  - id: mission.verify
    description: End-to-end system verification (14 tests)
    entrypoint: scripts/verify_full_system_operation.py
    interface: cli
    outputs:
      - tests_passed: integer
      - tests_total: integer
      - health_percentage: number
  - id: mission.heal
    description: Auto-healing service resurrection + resource optimization
    entrypoint: scripts/runtime_optimizer_supreme.py
    interface: cli
    inputs:
      - mode: {type: string, enum: [heal, daemon], default: heal}
    outputs:
      - restored_services: integer
      - health_percentage: number
      - logs_rotated: integer
      - memory_freed_mb: number
  - id: mission.plan
    description: Deep-horizon planning with sequential reasoning + High Council adjudication
    entrypoint: longest-horizon
    interface: cli|library
    inputs:
      - objective: {type: string, required: true}
      - horizon: {type: string, enum: [immediate, short, medium, long], default: medium}
    outputs:
      - plan: object
      - reasoning_chain: array
      - council_verdict: object
  - id: mission.execute
    description: Multi-mode execution with fail-safe governance
    entrypoint: apex-execution-modes
    interface: cli|library
    inputs:
      - mode: {type: string, enum: [standard, aggressive, conservative, dry_run], default: standard}
      - plan: {type: object}
    outputs:
      - execution_receipt: object
      - verification_status: string
  - id: mission.orchestrate
    description: DAG-based swarm orchestration with specialist assignment
    entrypoint: apex-orchestration
    interface: library|http
    inputs:
      - objective: {type: string, required: true}
      - workers: {type: array, items: {type: string}}
      - dependencies: {type: object}
    outputs:
      - task_assignments: object
      - synthesis: object
      - verification: object
```

## CLI Interface

```bash
apex-command <command> [options]

# Commands
apex-command boot                    # Full system bootup
apex-command verify                  # 14-test verification suite
apex-command heal [--daemon]         # Auto-heal services (or run daemon)
apex-command plan --objective "..."  # Deep-horizon planning
apex-command execute --plan plan.json --mode standard
apex-command orchestrate --objective "..." --workers "repo-cartographer,legal-analyst,..."
```

## Verification Gates

| Gate | Test | Pass Criteria |
|------|------|---------------|
| G1 | `apex-command boot` | 12/12 services ONLINE, 4 vaults active |
| G2 | `apex-command verify` | 14/14 tests PASS (100%) |
| G3 | `apex-command heal` | 100% health, 0 restored (already healthy) |
| G4 | `apex-command plan` | Valid plan with reasoning chain + council verdict |
| G5 | `apex-command orchestrate` | All workers complete, synthesis verified |