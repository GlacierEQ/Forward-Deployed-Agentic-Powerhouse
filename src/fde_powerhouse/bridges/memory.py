"""Bridge to aspen-grove-memory / Pro-Memory."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..estate import load_estate, resolve_repo


class MemoryBridge:
    def __init__(self, estate: dict[str, Any] | None = None) -> None:
        self.estate = estate or load_estate()
        self.aspen = resolve_repo(self.estate, "aspen_grove_memory")
        self.pro = resolve_repo(self.estate, "pro_memory")

    @property
    def available(self) -> bool:
        return bool(self.aspen.get("available") or self.pro.get("available"))

    def probe(self) -> dict[str, Any]:
        def one(entry: dict[str, Any]) -> dict[str, Any]:
            if not entry.get("available"):
                return {
                    "available": False,
                    "repo": entry.get("repo"),
                    "hint": "Set FDE_PATH_ASPEN_GROVE_MEMORY or FDE_PATH_PRO_MEMORY",
                }
            root = Path(entry["effective_path"])
            return {
                "available": True,
                "repo": entry.get("repo"),
                "root": str(root),
                "has_readme": (root / "README.md").is_file(),
            }

        return {
            "aspen_grove_memory": one(self.aspen),
            "pro_memory": one(self.pro),
            "tiers_model": ["working", "episodic", "semantic", "graph"],
        }
