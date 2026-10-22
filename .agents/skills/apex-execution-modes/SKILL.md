---
name: apex-execution-modes
description: Agent operational mode switching — execution posture (standard/aggressive/conservative/dry_run/autonomous/swarm/deep/recovery), specialist persona selection, and composite mission presets. Consumed by apex-command-core via agent_modes.json.
version: 1.0.0
status: active
---

# APEX Execution Modes

Execution posture + specialist persona selection for APEX agents. This is the mode engine
referenced by `apex-command-core` in its compose table.

## Authority

The canonical mode catalogue lives at:

```
/root/.agents/skills/apex-command-core/agent_modes.json
```

It is machine-readable (`apex.agent-modes/v1`) and self-verifying:

```bash
python3 /root/.agents/skills/apex-command-core/apex_command.py modes --verify
```

## Mode taxonomy

### Execution modes (how work is performed)
`standard` · `aggressive` · `conservative` · `dry_run` · `autonomous` · `swarm` · `deep` · `recovery`

Each carries: `intent`, `parallelism`, `verification`, `blast_radius`, `fail_safe`, `use_when`.

### Role modes (which specialist persona)
The 17 worker roles from `AGENTS.md §6.2`, each bound to its owning skill:
cartographer, miner, connector, architect, implementer, reliability, perf,
legal-research, forensics, evidence, adversarial, procedural, brief, citation,
contradiction, redteam, verify.

### Composite modes (prebuilt mission presets)
`job-app-finalize` · `legal-strike` · `code-sprint` · `discovery` · `mesh-repair`

A composite pairs an execution mode with an ordered role set and a `use_when`.

## Selection contract

```bash
# List everything + verification status
apex-command modes

# Validate registry + skill bindings
apex-command modes --verify

# Resolve a single mode (execution / role / composite)
apex-command modes --select swarm
apex-command modes --select forensics
apex-command modes --select job-app-finalize
```

## Integration

- `apex-command-core` `execute --mode <execution_mode>` consumes execution modes.
- `apex-command-core` `orchestrate --workers <role,role,...>` consumes role modes.
- Composite modes are sugar: they expand into `(execution, roles[])` for the two commands above.

## Verification gate

`agent_modes.json` must resolve: every `role_mode.skill` is an installed skill dir;
every composite references only known roles + a known execution mode. The `--verify`
command is the gate (maps to command-core gate G6 extension).
