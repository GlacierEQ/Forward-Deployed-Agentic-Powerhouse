# Recorded Demo Path — Forward-Deployed-Agentic-Powerhouse

**Duration:** ~3–5 minutes  
**Goal:** Show zero-to-hero + estate leverage + (optional) live mega-skills validate

---

## Prerequisites

```bash
git clone https://github.com/GlacierEQ/Forward-Deployed-Agentic-Powerhouse
cd Forward-Deployed-Agentic-Powerhouse
pip install -e ".[dev]"
```

Optional (live invoke):

```bash
export FDE_PATH_MEGA_SKILLS=/absolute/path/to/mega-skills
```

---

## Script (record this)

### 1. Doctor (15s)

```bash
python -m fde_powerhouse doctor
```

**Say:** Kernel health, estate catalog counts (709/33/29), edge library size, bridge status.

### 2. Proof pack (20s)

```bash
python -m fde_powerhouse proof | head -80
```

**Say:** Diligence surface — is / is not, dual-plane honesty.

### 3. Showcase (45s)

```bash
python -m fde_powerhouse showcase --target demo
ls -la .fde/showcase_demo/
```

**Say:** Full cycle receipt + composition matrix + operator card written to disk.

### 4. Ground-up scaffold (30s)

```bash
python -m fde_powerhouse cycle --mode ground_up --name field-agent \
  --problem "Tool-using agent with policy gates"
ls .fde/field-agent/src/agent/
```

**Say:** Zero → hero: orchestrator, policy, memory port, tests.

### 5. Leverage map (20s)

```bash
python -m fde_powerhouse leverage --mode compose
```

**Say:** Recommendations aligned to control-plane, memory-fleet, Genius, production gate.

### 6. Live mega-skills validate (optional, 30–60s)

```bash
python -m fde_powerhouse invoke --pipeline control-plane
# or explicit:
python -m fde_powerhouse invoke --pipeline control-plane --validate-only
```

**Say:** When FDE_PATH_MEGA_SKILLS is set, we call the real runner in validate-only mode — no deploy, no merge, no network.

Without path:

```text
status: skip — Set FDE_PATH_MEGA_SKILLS …
```

### 7. Tests (20s)

```bash
pytest -q
```

**Say:** CI-backed; cycle, scaffold, bridges, edge, leverage, invoke soft-skip, showcase.

---

## Closing line

> Forward Deployed Agentic AI — universal cycle, estate-aligned, human-gated deploy. Full power with honest limits.

---

## Do not demo

- Auto git push / merge
- Claims of lab production deployment
- Full pipeline execute without saying validate-only is the default safe path
