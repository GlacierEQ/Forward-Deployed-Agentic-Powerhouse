# Zero → Hero

## Ground up (nothing → working system)

```bash
pip install -e ".[dev]"
python -m fde_powerhouse doctor
python -m fde_powerhouse cycle --mode ground_up --name my-agent
pytest -q
```

Produces a full 7-stage receipt chain and a local `.fde/my-agent/` scaffold.

## Existing system (refactor / upgrade / merge / invent)

```bash
# Point estate paths at your checkouts
export FDE_PATH_MEGA_SKILLS=/path/to/mega-skills
export FDE_PATH_GENIUS_MASTERY=/path/to/Genius-Mastery
export FDE_PATH_ASPEN_GROVE_MEMORY=/path/to/aspen-grove-memory
export FDE_PATH_MEGA_PIPELINE_PRODUCTION=/path/to/mega-pipeline-production

python -m fde_powerhouse cycle --mode upgrade --target /path/to/existing-system
python -m fde_powerhouse cycle --mode compose --target portfolio
python -m fde_powerhouse cycle --mode invent --target new-capability
python -m fde_powerhouse cycle --mode merge --target surface-a+surface-b
```

## Mode cheat sheet

| Mode | Use when |
|------|----------|
| ground_up | Greenfield agent system |
| refactor | Structure change, same contract |
| repoint | New identity or integration targets |
| update | Contracts/tests drift |
| upgrade | Raise skills / memory / pipeline level |
| merge | Combine unique value from multiple repos |
| invent | Capability that did not exist |
| innovate | Novel cross-estate composition |
| compose | Explicit mega-skills + genius + memory + pipelines wire-up |

## Integration truth

This repo does **not** vendor mega-skills, Genius-Mastery, or Aspen memory.  
It **resolves** them via `configs/estate.yaml` and `FDE_PATH_*` env vars, runs the universal cycle, and emits hash-bound receipts.

When paths are missing, integrate stage soft-skips with an explicit receipt — fail-open on absence, fail-closed on evaluation gates inside the cycle.
