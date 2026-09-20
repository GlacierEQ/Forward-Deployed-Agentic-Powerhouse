"""Estate integration map — pointers to mega-skills, pipelines, genius, memory."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "configs" / "estate.yaml"


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
        entry["effective_path"] = None
    entry["available"] = bool(entry["effective_path"] and Path(entry["effective_path"]).exists())
    return entry


def estate_status(estate: dict[str, Any] | None = None) -> dict[str, Any]:
    estate = estate or load_estate()
    status = {}
    for key in estate.get("repos") or {}:
        status[key] = resolve_repo(estate, key)
    return status
