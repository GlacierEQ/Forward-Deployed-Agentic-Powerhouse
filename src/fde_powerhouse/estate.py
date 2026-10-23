"""Estate integration map — pointers to mega-skills, pipelines, genius, memory."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "configs" / "estate.yaml"

CANDIDATE_ESTATE_PATHS: dict[str, list[str]] = {
    "mega_skills": [
        "/root/.agents/skills",
        "/data/data/com.termux/files/home/.agents/skills",
    ],
    "aspen_grove_memory": [
        "/root/aspen-grove-memory",
        "/root/aspen-grove-core",
        "/data/data/com.termux/files/home/MISSIONS/APEX_INFRASTRUCTURE/aspen-grove-operator-v7",
    ],
    "pro_memory": [
        "/root/.apex_memory",
        "/root/.apex",
        "/data/data/com.termux/files/home/.apex_vault",
    ],
    "genius_mastery": [
        "/root/genius-technician",
        "/data/data/com.termux/files/home/MISSIONS/PRO_AGENTS/pro-code",
    ],
    "job_app_helix": [
        "/root/job-app-helix",
        "/data/data/com.termux/files/home/MISSIONS/AEON_777/CORE_MISSION/JOB_ACQUISITION",
    ],
    "monolith": [
        "/root/monolith",
        "/data/data/com.termux/files/home/monolith",
    ],
    "tower_of_babel": [
        "/root/the-tower-of-babel",
        "/data/data/com.termux/files/home/the-tower-of-babel",
    ],
    "mega_pipeline_production": [
        "/root/.agents/skills/apex-deep-work-kernel",
        "/root/engine_forge",
    ],
    "agent_coordinator": [
        "/root/apex-mesh-engine",
    ],
    "safety_monitor": [
        "/root/.agents/skills/apex-fail-safe-governor",
        "/root/.agents/skills/zero-fake-truth-enforcer",
    ],
}


def load_estate(config_path: Path | None = None) -> dict[str, Any]:
    path = config_path or Path(os.environ.get("FDE_ESTATE_CONFIG", DEFAULT_CONFIG))
    if not path.is_file():
        return {"schema": "fde.estate.map/v1", "repos": {}, "integration_policy": {}}
    with path.open() as f:
        return yaml.safe_load(f) or {}


def resolve_repo(estate: dict[str, Any], key: str) -> dict[str, Any]:
    """Return repo entry with effective local path if present."""
    repos = estate.get("repos") or {}
    entry = dict(repos.get(key) or {})
    env_key = f"FDE_PATH_{key.upper()}"
    env_path = os.environ.get(env_key)
    if env_path:
        entry["effective_path"] = env_path
    elif entry.get("default_path"):
        entry["effective_path"] = entry["default_path"]
    else:
        # Check automatic candidates for local APEX estate environment
        auto_found = None
        for candidate in CANDIDATE_ESTATE_PATHS.get(key, []):
            if Path(candidate).exists():
                auto_found = candidate
                break
        entry["effective_path"] = auto_found

    entry["available"] = bool(entry["effective_path"] and Path(entry["effective_path"]).exists())
    return entry


def estate_status(estate: dict[str, Any] | None = None) -> dict[str, Any]:
    estate = estate or load_estate()
    status = {}
    for key in estate.get("repos") or {}:
        status[key] = resolve_repo(estate, key)
    return status
