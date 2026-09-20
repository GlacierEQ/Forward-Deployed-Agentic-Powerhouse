# Full Process — v0.4.0

**Branch:** `main`  
**Identity:** Forward Deployed Agentic AI  
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

## 2. Recorded demo (canonical)

```bash
python -m fde_powerhouse demo
# or follow docs/DEMO.md for a screen recording
```

## 3. Optional live estate

```bash
export FDE_PATH_MEGA_SKILLS=/path/to/mega-skills
export FDE_PATH_GENIUS_MASTERY=/path/to/Genius-Mastery
python -m fde_powerhouse invoke --pipeline control-plane
python -m fde_powerhouse cycle --mode compose --target live
```

## 4. Ground-up

```bash
python -m fde_powerhouse cycle --mode ground_up --name field-agent \
  --problem "Tool-using agent with policy gates"
```

## 5. Cycle spine

```text
DISCOVER  → estate + catalog + edge
FRAME     → CyclePlan + FDE priority pipelines
BUILD     → scaffold or upgrade workspace
INTEGRATE → compose graph + live validate-only invoke
EVALUATE  → fail-closed gates
PROVE     → receipts + spine
DEPLOY    → approval_packet_only
```

## 6. Done when

- `doctor` exits 0  
- `demo` exits 0  
- `pytest -q` green  
- Optional: `invoke --pipeline control-plane` returns VALID when path set  
