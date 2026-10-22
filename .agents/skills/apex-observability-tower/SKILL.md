---
name: apex-observability-tower
description: Observability & Monitoring Suite — Structured logs, metrics, tracing, health endpoints, SLO/SLI, alerting, dashboards. Composes runtime-cache, verification, benchmark-suite, routing-middleware, workflow, apex-sovereign-supreme runtime optimizer.
version: 1.0.0
status: active
---

# APEX Observability Tower — Mega-Skill 9

**Observability & Monitoring Suite** — Full visibility into all mega-skills.

## Composed Sub-Skills

| Sub-Skill | Role | Entry Point |
|-----------|------|-------------|
| runtime-cache | Multi-layer caching, latency tracking | `runtime-cache` skill |
| verification | Independent verification ladder | `verification` skill |
| benchmark-suite | Performance benchmarking | `benchmark-suite` skill |
| routing-middleware | Request routing, middleware chain | `routing-middleware` skill |
| workflow | Workflow orchestration | `workflow` skill |
| apex-sovereign-supreme/runtime_optimizer | Auto-healing, resource monitoring | `scripts/runtime_optimizer_supreme.py` |

## Unified Capabilities (apex.capabilities/v1)

```yaml
schema: apex.capabilities/v1
repository: GlacierEQ/Pro-DOCTOR-STRANGE
mega_skill: apex-observability-tower
capabilities:
  - id: obs.logs
    description: Structured logging with correlation IDs, levels, structured fields
    entrypoint: observability.py logs
    interface: cli|library|http
    inputs:
      - level: {type: string, enum: [debug, info, warn, error], default: info}
      - service: {type: string}
      - correlation_id: {type: string}
    outputs:
      - log_entry: {type: object}

  - id: obs.metrics
    description: Metrics collection (counters, gauges, histograms, summaries)
    entrypoint: observability.py metrics
    interface: cli|library|http
    inputs:
      - name: {type: string, required: true}
      - type: {type: string, enum: [counter, gauge, histogram, summary], required: true}
      - value: {type: number}
      - labels: {type: object}
    outputs:
      - recorded: {type: boolean}

  - id: obs.traces
    description: Distributed tracing with span context propagation
    entrypoint: observability.py traces
    interface: cli|library|http
    inputs:
      - operation: {type: string, required: true}
      - parent_context: {type: object}
      - tags: {type: object}
    outputs:
      - span: {type: object}
      - trace_id: {type: string}

  - id: obs.health
    description: Health endpoints with dependency checks (liveness, readiness, startup)
    entrypoint: observability.py health
    interface: cli|http
    inputs:
      - check_type: {type: string, enum: [liveness, readiness, startup], default: liveness}
    outputs:
      - healthy: {type: boolean}
      - checks: {type: array}
      - latency_ms: {type: integer}

  - id: obs.slo
    description: SLO/SLI definitions, error budgets, burn rate alerts
    entrypoint: observability.py slo
    interface: cli|library
    inputs:
      - service: {type: string, required: true}
      - sli: {type: string, required: true}
      - target: {type: number, required: true}
      - window: {type: string, required: true}
    outputs:
      - error_budget_remaining: {type: number}
      - burn_rate: {type: number}
      - alerting: {type: boolean}

  - id: obs.alerts
    description: Alerting rules, notification routing, on-call integration
    entrypoint: observability.py alerts
    interface: cli|library|http
    inputs:
      - rule: {type: string, required: true}
      - condition: {type: string, required: true}
      - severity: {type: string, enum: [critical, warning, info], required: true}
      - notifications: {type: array, items: {type: string}}
    outputs:
      - alert_id: {type: string}
      - status: {type: string}

  - id: obs.dashboard
    description: Dashboard definitions, panel configs, drill-down links
    entrypoint: observability.py dashboard
    interface: cli|library
    inputs:
      - name: {type: string, required: true}
      - panels: {type: array, items: {type: object}}
    outputs:
      - dashboard_json: {type: object}
```

## CLI Interface

```bash
apex-obs <command> [options]

# Logs
apex-obs logs --level info --service apex-legal-intelligence --correlation-id abc123

# Metrics
apex-obs metrics --name http_requests_total --type counter --value 1 --labels '{"service":"apex-command-core","endpoint":"/verify"}'

# Traces
apex-obs traces --operation "legal.reason" --parent-context '{}' --tags '{"case":"1FDV-23-0001009"}'

# Health
apex-obs health --check-type liveness
apex-obs health --check-type readiness

# SLO/SLI
apex-obs slo --service apex-connector-mesh --sli availability --target 0.999 --window 30d

# Alerts
apex-obs alerts --rule "high_error_rate" --condition "error_rate > 0.05" --severity critical --notifications "slack,pagerduty"

# Dashboard
apex-obs dashboard --name "Mega-Skills Overview" --panels panels.json
```

## Verification Gates

| Gate | Test | Pass Criteria |
|------|------|---------------|
| G1 | `logs` structured output | JSON with level, timestamp, service, correlation_id |
| G2 | `metrics` counter increments | Value persists, labels indexed |
| G3 | `traces` span creation | Trace ID generated, context propagated |
| G4 | `health` liveness/readiness | Returns healthy=false when deps down |
| G5 | `slo` error budget calc | Correct burn rate, alerting triggers |
| G6 | `alerts` rule evaluation | Fires when condition met, routes notifications |
| G7 | `dashboard` JSON output | Valid Grafana/Grafonnet compatible JSON |