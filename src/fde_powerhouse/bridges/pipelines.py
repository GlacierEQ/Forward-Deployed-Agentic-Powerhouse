"""Bridge to mega-pipeline-production + mega-skills deep-work pipelines."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..estate import load_estate, resolve_repo


class PipelineBridge:
    def __init__(self, estate: dict[str, Any] | None = None) -> None:
        self.estate = estate or load_estate()
        self.prod = resolve_repo(self.estate, "mega_pipeline_production")
        self.skills = resolve_repo(self.estate, "mega_skills")

    def probe(self) -> dict[str, Any]:
        return {
            "mega_pipeline_production": self._probe_entry(self.prod),
            "mega_skills_pipelines": self._probe_entry(self.skills),
            "default_deploy_mode": "approval_packet_only",
        }

    def _probe_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        if not entry.get("available"):
            return {"available": False, "repo": entry.get("repo")}
        root = Path(entry["effective_path"])
        return {
            "available": True,
            "repo": entry.get("repo"),
            "root": str(root),
            "has_readme": (root / "README.md").is_file(),
        }
