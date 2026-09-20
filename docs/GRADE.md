# Grade — v0.6.1 (9+ closeout items landed)

**Bar:** 9+

| Dimension | Grade |
|-----------|-------|
| Identity | **A** |
| Zero-to-hero | **A** |
| Modes | **A** |
| Estate catalog | **A** |
| Live mega-skills | **A** (pinned CI validate-only) |
| Genius hook | **A-** |
| Edge + history + schedule | **A** |
| Coverage gate | **A-** (fail-under 70; climb to 80) |
| Maximize | **A** |
| CI | **A** |
| Production agent runtime | **B+** |
| Anti-oscillation | **A** |

## Overall: **A / 9-range**

Closed on main:

1. **Pinned mega-skills CI** — SHA in `configs/pins.yaml` + validate-only job  
2. **Coverage gate** — `--cov-fail-under=70` on matrix  
3. **Scheduled edge artifacts** — weekly + manual, 90-day artifact retention  

Optional: set `ESTATE_CHECKOUT_TOKEN` so the pinned job always runs against private mega-skills.
