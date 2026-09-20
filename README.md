# Forward-Deployed-Agentic-Powerhouse

**Zero → hero.** Universal powerhouse for building agent systems from nothing **and** upgrading anything that already exists.

```text
DISCOVER → FRAME → BUILD → INTEGRATE → EVALUATE → PROVE → DEPLOY
```

**Identity:** Forward Deployed Agentic AI  
**Version:** 0.2.0  
**Law:** Full power + dual-plane honesty. No oscillation.

## What this is

A working control kernel that:

1. **Ground-up** — stand up a new agentic system from zero (scaffold: orchestrator, policy, memory port, tests)
2. **Existing** — refactor, repoint, update, upgrade, merge, invent, innovate on live estate surfaces
3. **Integrates** your real power stack via adapters:
   - [mega-skills](https://github.com/GlacierEQ/mega-skills) — skill pyramids + deep-work pipelines
   - [mega-pipeline-production](https://github.com/GlacierEQ/mega-pipeline-production) — production readiness
   - [Genius-Mastery](https://github.com/GlacierEQ/Genius-Mastery) — entity forge + mastery loop
   - [aspen-grove-memory](https://github.com/GlacierEQ/aspen-grove-memory) / [Pro-Memory](https://github.com/GlacierEQ/Pro-Memory) — multi-tier memory
   - Helix / AKOS / coordinator / safety-monitor — FDE proof spine

## Quick start

```bash
pip install -e ".[dev]"
python -m fde_powerhouse doctor
python -m fde_powerhouse cycle --mode ground_up --name demo-agent
python -m fde_powerhouse compose --target portfolio
python -m fde_powerhouse probe
pytest -q
```

## Modes

| Mode | Intent |
|------|--------|
| `ground_up` | Nothing → working agent scaffold |
| `refactor` | Restructure without changing external contract |
| `repoint` | Retarget identity / deps / integration |
| `update` | Current contracts and tests |
| `upgrade` | Raise skills / memory / pipelines |
| `merge` | Compose unique value from multiple surfaces |
| `invent` | New capability |
| `innovate` | Novel cross-estate composition |
| `compose` | Wire mega-skills + genius + memory + pipelines |

## Estate paths

```bash
export FDE_PATH_MEGA_SKILLS=/path/to/mega-skills
export FDE_PATH_GENIUS_MASTERY=/path/to/Genius-Mastery
export FDE_PATH_ASPEN_GROVE_MEMORY=/path/to/aspen-grove-memory
export FDE_PATH_MEGA_PIPELINE_PRODUCTION=/path/to/mega-pipeline-production
python -m fde_powerhouse doctor
python -m fde_powerhouse cycle --mode upgrade --target /path/to/existing
```

Missing paths → soft-skip with receipt. Evaluation stays fail-closed.

## Layout

```text
src/fde_powerhouse/
  cycle.py stages.py plan.py scaffold.py receipts.py estate.py modes.py cli.py
  bridges/   mega_skills genius memory pipelines
configs/     estate.yaml modes.yaml
docs/        ZERO_TO_HERO.md ARCHITECTURE.md
tests/
```

## Docs

- [Zero → Hero](docs/ZERO_TO_HERO.md)
- [Architecture](docs/ARCHITECTURE.md)

---

*GlacierEQ · Forward Deployed Agentic AI · Full power*
