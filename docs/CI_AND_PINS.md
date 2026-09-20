# CI, pins, coverage, scheduled edge

## Pinned mega-skills

| Field | Value |
|-------|--------|
| Repo | `GlacierEQ/mega-skills` |
| Pin SHA | `c100fbb3b603d5cc3141c3dd8755c2d0f62ac39a` |
| Config | `configs/pins.yaml` |
| Job | `mega-skills-pinned` in `.github/workflows/ci.yml` |
| Mode | **validate-only** (safe; no deploy/merge/network) |

### Secret for private checkout

If the default `GITHUB_TOKEN` cannot read `mega-skills`:

1. Create a fine-grained or classic PAT with `contents:read` on `GlacierEQ/mega-skills`
2. Add repository secret **`ESTATE_CHECKOUT_TOKEN`**
3. Re-run CI — job checks out pin and runs:

```bash
FDE_PATH_MEGA_SKILLS=$GITHUB_WORKSPACE/mega-skills \
  python -m fde_powerhouse invoke --pipeline control-plane --validate-only
```

Full `--execute` remains **opt-in locally** only (approval_packet_only inside mega-skills).

## Coverage gate

```bash
pytest --cov=fde_powerhouse --cov-report=term-missing --cov-fail-under=70
```

Enforced on every CI matrix job (3.11–3.13). Raise toward 80+ as suite grows.

## Scheduled edge artifacts

Workflow: `.github/workflows/edge-scheduled.yml`

| Trigger | When |
|---------|------|
| `schedule` | Mondays 16:00 UTC |
| `workflow_dispatch` | Manual |

Produces `.fde/edge_history/` and uploads artifact `edge-history-<run_id>` (90-day retention).
