"""Universal modes: ground_up through compose.

Emphasis in modes.yaml is a priority signal only.
Stage execution order is always the fixed FDE spine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DEFAULT_MODES = Path(__file__).resolve().parents[2] / "configs" / "modes.yaml"

MODES = (
    "ground_up",
    "refactor",
    "repoint",
    "update",
    "upgrade",
    "merge",
    "invent",
    "innovate",
    "compose",
)

STAGES = (
    "discover",
    "frame",
    "build",
    "integrate",
    "evaluate",
    "prove",
    "deploy",
)


def load_modes(config_path: Path | None = None) -> dict[str, Any]:
    path = config_path or DEFAULT_MODES
    if not path.is_file():
        return {"modes": {m: {"description": m, "emphasis": list(STAGES)} for m in MODES}}
    with path.open() as f:
        return yaml.safe_load(f) or {}


def mode_emphasis(mode: str) -> list[str]:
    """Return fixed spine order. Emphasis metadata is available via load_modes."""
    _ = mode  # mode selects plan/skill targets elsewhere; spine is universal
    return list(STAGES)


def mode_priority_stages(mode: str) -> list[str]:
    """Optional priority list from config (does not change execution order)."""
    cfg = load_modes()
    entry = (cfg.get("modes") or {}).get(mode) or {}
    emphasis = entry.get("emphasis") or list(STAGES)
    return [s for s in emphasis if s in STAGES]
