"""Universal modes: ground_up, refactor, repoint, update, upgrade, merge, invent, innovate, compose."""

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
    cfg = load_modes()
    entry = (cfg.get("modes") or {}).get(mode) or {}
    emphasis = entry.get("emphasis") or list(STAGES)
    # Always run full spine; emphasis is priority signal only
    ordered = []
    for s in STAGES:
        if s in emphasis or s.replace("_", "-") in emphasis:
            ordered.append(s)
    for s in STAGES:
        if s not in ordered:
            ordered.append(s)
    return ordered
