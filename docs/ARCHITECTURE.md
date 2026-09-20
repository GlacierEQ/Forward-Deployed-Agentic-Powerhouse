# Architecture — Forward-Deployed-Agentic-Powerhouse

## Spine

```text
CLI / API
   → cycle.run_cycle(mode, target)
       → stages: discover → frame → build → integrate → evaluate → prove → deploy
           → bridges: mega_skills | genius | memory | pipelines
           → plan + scaffold (ground_up / invent)
           → receipts (sha256)
```

## Dual use

| Path | Behavior |
|------|----------|
| **Ground-up** | `build_plan` → `write_scaffold` → orchestrator/policy/memory stubs + smoke tests |
| **Existing** | Upgrade workspace + estate probes; no vendor of mega-skills/genius/memory code |

## Bridges

Adapters only. Resolve via `configs/estate.yaml` + `FDE_PATH_*`.

| Bridge | Estate repo | Responsibility |
|--------|-------------|----------------|
| MegaSkillsBridge | mega-skills | Registry probe, pipeline hints |
| GeniusBridge | Genius-Mastery | Markers, mastery loop, role brief |
| MemoryBridge | aspen-grove-memory, Pro-Memory | Tier model, availability |
| PipelineBridge | mega-pipeline-production, mega-skills | Deploy mode, path probe |

## Anti-oscillation

- Claim plane: receipts only  
- Capability plane: full FDE direction + estate composition  
- Deploy: `approval_packet_only` — no silent merge/network  

## Version

0.2.0 — expanded bridges, scaffolds, compose graph, CI.
