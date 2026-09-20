# Forward-Deployed-Agentic-Powerhouse

**Zero → hero.** Universal powerhouse for building agent systems from nothing **and** upgrading anything that already exists.

```text
DISCOVER → FRAME → BUILD → INTEGRATE → EVALUATE → PROVE → DEPLOY
```

**Identity:** Forward Deployed Agentic AI  
**Law:** Full power + dual-plane honesty. No oscillation.

## What this is

A working control kernel that:

1. **Ground-up** — stand up a new agentic system from zero
2. **Existing** — refactor, repoint, update, upgrade, merge, invent, innovate on live estate surfaces
3. **Integrates** your real power stack:
   - [mega-skills](https://github.com/GlacierEQ/mega-skills) — atomic → compound → mega skill pyramids + deep-work pipelines
   - [mega-pipeline-production](https://github.com/GlacierEQ/mega-pipeline-production) — production readiness phases
   - [Genius-Mastery](https://github.com/GlacierEQ/Genius-Mastery) — entity forge, mastery loop, epistemic engine
   - [aspen-grove-memory](https://github.com/GlacierEQ/aspen-grove-memory) / [Pro-Memory](https://github.com/GlacierEQ/Pro-Memory) — multi-tier memory
   - Helix / AKOS / coordinator / safety-monitor — FDE proof spine

## Quick start

```bash
pip install -e ".[dev]"
python -m fde_powerhouse doctor
python -m fde_powerhouse cycle --mode ground_up --name demo-agent
python -m fde_powerhouse cycle --mode upgrade --target path/or/repo
pytest -q
```

## Modes (universal)

| Mode | Intent |
|------|--------|
| `ground_up` | Nothing → working agent system |
| `refactor` | Restructure without changing external contract |
| `repoint` | Retarget identity / deps / integration points |
| `update` | Bring to current contracts and tests |
| `upgrade` | Raise capability level (skills, memory, pipelines) |
| `merge` | Compose unique value from multiple surfaces |
| `invent` | New capability not previously present |
| `innovate` | Novel composition across estate systems |
| `compose` | Wire mega-skills + pipelines + genius + memory |

## Cycle stages

Every mode runs the same seven stages. Stage adapters differ by mode; the spine does not.

1. **DISCOVER** — problem boundary, existing surfaces, memory recall
2. **FRAME** — typed plan, skill pyramid targets, genius role brief
3. **BUILD** — agents, tools, state, failure semantics
4. **INTEGRATE** — MCP, memory tiers, mega-skill compounds, pipelines
5. **EVALUATE** — tests, policy, epistemic classification
6. **PROVE** — receipts, pinned evidence, mastery signals
7. **DEPLOY** — handoff packet (human-gated by default)

## Estate integration map

| System | Role in powerhouse |
|--------|--------------------|
| mega-skills | Skill hierarchy + deep-work pipeline runner |
| mega-pipeline-production | 10-phase production readiness |
| Genius-Mastery | Synthesize / analyze / teach Genius entities |
| aspen-grove-memory / Pro-Memory | Persistent multi-tier memory organism |
| anthropic-agent-coordinator | Multi-agent scheduling proof |
| anthropic-safety-monitor | Tool policy gates |
| job-app-helix | Portfolio control + FDE hire package |
| monolith / tower-of-babel | Catalog + polyglot placement |

Paths are resolved via `estate.yaml` (override with env or CLI).

## Layout

```text
src/fde_powerhouse/     kernel
  cycle.py              full-cycle runner
  modes.py              universal mode adapters
  estate.py             integration pointers
  stages/               DISCOVER…DEPLOY
  receipts.py           hash-bound stage receipts
configs/
  estate.yaml           default estate map
  modes.yaml            mode → stage adapters
tests/
docs/
```

## Status

Kernel is runnable. Estate connectors are **adapters + contracts** — they call into your real repos when paths are present; they do not vendor those codebases.

---

*GlacierEQ · Forward Deployed Agentic AI · Full power*
