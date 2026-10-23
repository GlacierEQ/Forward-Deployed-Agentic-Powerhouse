"""Bridge to GlacierEQ/mega-skills — hierarchy + deep-work pipelines."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..estate import load_estate, resolve_repo


class MegaSkillsBridge:
    def __init__(self, estate: dict[str, Any] | None = None) -> None:
        self.estate = estate or load_estate()
        self.entry = resolve_repo(self.estate, "mega_skills")

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
                "hint": "Set FDE_PATH_MEGA_SKILLS to local checkout",
            }
        root = self.root
        registries = {}
        for name in ("skills.json", "combo-skills.json", "mega-skills.json", "pipelines.json"):
            path = root / "registry" / name
            if path.is_file():
                try:
                    data = json.loads(path.read_text())
                    registries[name] = {
                        "path": str(path),
                        "entries": len(data) if isinstance(data, (list, dict)) else None,
                    }
                except (OSError, json.JSONDecodeError) as exc:
                    registries[name] = {"path": str(path), "error": str(exc)}
            else:
                registries[name] = {"missing": True}

        # Check for local skills directory layout (e.g. .agents/skills)
        skill_files = list(root.glob("*/SKILL.md")) if root.is_dir() else []
        if skill_files and all(r.get("missing") for r in registries.values()):
            registries["skills_directory"] = {
                "path": str(root),
                "entries": len(skill_files),
                "skills": sorted([p.parent.name for p in skill_files]),
            }

        return {
            "available": True,
            "repo": self.entry.get("repo"),
            "root": str(root),
            "registries": registries,
        }

    def suggested_pipelines(self) -> list[str]:
        return [
            "inception-to-deployment",
            "control-plane",
            "memory-fleet",
            "change-swe",
            "cultivate-main",
            "anthropic-applied-ai-readiness",
        ]
