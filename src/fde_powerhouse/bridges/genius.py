"""Bridge to GlacierEQ/Genius-Mastery — entity forge + mastery loop."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..estate import load_estate, resolve_repo


class GeniusBridge:
    def __init__(self, estate: dict[str, Any] | None = None) -> None:
        self.estate = estate or load_estate()
        self.entry = resolve_repo(self.estate, "genius_mastery")

    @property
    def available(self) -> bool:
        return bool(self.entry.get("available"))

    @property
    def root(self) -> Path | None:
        p = self.entry.get("effective_path")
        return Path(p) if p else None

    def probe(self) -> dict[str, Any]:
        if not self.available or not self.root:
            return {
                "available": False,
                "repo": self.entry.get("repo"),
                "hint": "Set FDE_PATH_GENIUS_MASTERY to local checkout",
            }
        root = self.root
        markers = {}
        for rel in (
            "docs/EPISTEMOLOGY.md",
            "schemas/capability.schema.json",
            "schemas/role-brief.schema.json",
            "pyproject.toml",
        ):
            markers[rel] = (root / rel).is_file()
        return {
            "available": True,
            "repo": self.entry.get("repo"),
            "root": str(root),
            "markers": markers,
            "loop": [
                "MAP",
                "RESEARCH",
                "MODEL",
                "BUILD",
                "BREAK",
                "MEASURE",
                "VERIFY",
                "OPERATE",
                "EXPLAIN",
                "SYNTHESIZE",
                "PROVE",
                "EXPAND",
                "TEACH",
            ],
        }

    def role_brief(self, role: str, outcomes: list[str]) -> dict[str, Any]:
        return {
            "role": role,
            "outcomes": outcomes,
            "family": "Genius-{purpose}",
            "note": "Mapped structure only until evidence promotes mastery",
        }
