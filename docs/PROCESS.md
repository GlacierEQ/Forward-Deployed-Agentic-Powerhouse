# Full Process — v0.7.1

```bash
git clone https://github.com/GlacierEQ/Forward-Deployed-Agentic-Powerhouse
cd Forward-Deployed-Agentic-Powerhouse
pip install -e ".[dev]"
python -m fde_powerhouse doctor
python -m fde_powerhouse maximize
python -m fde_powerhouse invert-scan --target .
pytest --cov=fde_powerhouse --cov-fail-under=70
```

Optional estate:

```bash
export FDE_PATH_MEGA_SKILLS=/path/to/mega-skills
export FDE_PATH_GENIUS_MASTERY=/path/to/Genius-Mastery
python -m fde_powerhouse invoke --pipeline control-plane
```

CI private pin: repository secret `ESTATE_CHECKOUT_TOKEN`.
