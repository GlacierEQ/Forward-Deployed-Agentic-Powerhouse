# Full Process — Forward-Deployed-Agentic-Powerhouse

**On main.** Identity: Forward Deployed Agentic AI.  
**Law:** Full power + dual-plane honesty. No oscillation.

---

## 1. Install

```bash
git clone https://github.com/GlacierEQ/Forward-Deployed-Agentic-Powerhouse
cd Forward-Deployed-Agentic-Powerhouse
pip install -e ".[dev]"
python -m fde_powerhouse doctor
pytest -q
```

## 2. Point estate (optional, for live integration)

```bash
export FDE_PATH_MEGA_SKILLS=/path/to/mega-skills
export FDE_PATH_GENIUS_MASTERY=/path/to/Genius-Mastery
export FDE_PATH_ASPEN_GROVE_MEMORY=/path/to/aspen-grove-memory
export FDE_PATH_MEGA_PIPELINE_PRODUCTION=/path/to/mega-pipeline-production
python -m fde_powerhouse probe
```

Missing paths soft-skip with receipt. Evaluation stays fail-closed.

## 3. Ground-up (zero → hero)

```bash
python -m fde_powerhouse cycle --mode ground_up --name my-agent \
  --problem "Ship a tool-using agent with policy gates"
```

Produces:
- 7-stage hash-bound receipt (stdout JSON)
- `.fde/my-agent/` scaffold: orchestrator, policy, memory port, PLAN.yaml, smoke tests

## 4. Existing surface (upgrade / merge / invent / compose)

```bash
python -m fde_powerhouse cycle --mode upgrade --target /path/to/system
python -m fde_powerhouse cycle --mode merge --target surface-a+surface-b
python -m fde_powerhouse cycle --mode invent --name new-capability
python -m fde_powerhouse compose --target portfolio
```

## 5. Leading edge (public tech)

```bash
python -m fde_powerhouse edge --stats
python -m fde_powerhouse edge --category ai_frontier
python -m fde_powerhouse edge --urls-only
```

Library: `configs/leading_edge_sources.yaml` (tech news, AI labs, dev, arXiv, declassified/public technical, security, hardware).

## 6. Cycle spine (every mode)

```text
DISCOVER  → estate + bridges + leading-edge catalog awareness
FRAME     → CyclePlan (skills, genius, memory, pipelines, constraints)
BUILD     → scaffold (ground_up/invent) or upgrade workspace
INTEGRATE → mega-skills / genius / memory / pipelines compose graph
EVALUATE  → fail-closed gates
PROVE     → receipt chain + FDE proof spine pointers
DEPLOY    → human-gated approval packet only
```

## 7. Modes

| Mode | When |
|------|------|
| ground_up | Greenfield agent system |
| refactor | Structure change, same contract |
| repoint | New identity or integration targets |
| update | Contracts/tests drift |
| upgrade | Raise skills / memory / pipeline level |
| merge | Combine unique lineage |
| invent | Capability that did not exist |
| innovate | Novel cross-estate composition |
| compose | Explicit skills + genius + memory + pipelines |

## 8. Anti-oscillation

| Forbidden | Required |
|-----------|----------|
| Lead with what it cannot be | Lead with what it ships |
| Grand claims without receipt | Architecture ambition + verified core |
| Auto-merge / silent network | `approval_packet_only` |
| Vendor estate code | Adapters + FDE_PATH_* |

## 9. Done when

- `doctor` exits 0  
- `pytest -q` green  
- One ground_up cycle emits 7 ok stages  
- Edge library loads ≥40 HTTPS homepages  
