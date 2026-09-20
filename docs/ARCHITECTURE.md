# Architecture — v0.7.1

## Spine (fixed order)

```text
discover → frame → build → integrate → evaluate → prove → deploy
```

Mode `emphasis` in `configs/modes.yaml` is **priority metadata only** — never reorders execution.

## Invert-scan

```text
rules YAML → pattern match → window context → negation softens confidence
           → semantic proximity boost → file-level clusters (≥2 terms)
           → hash-bound report
```

## Scaffold agent

```text
Orchestrator → PolicyEngine (fail-closed) → ToolRegistry → MemoryPort
Receipt always deploy_mode: approval_packet_only
```
