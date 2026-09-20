"""Leading-edge public tech library — homepages for continuous edge-catching."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DEFAULT_SOURCES = (
    Path(__file__).resolve().parents[2] / "configs" / "leading_edge_sources.yaml"
)


def load_sources(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_SOURCES
    if not p.is_file():
        return {"schema": "fde.leading_edge_sources/v1", "categories": {}}
    with p.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def all_homepages(data: dict[str, Any] | None = None) -> list[dict[str, str]]:
    data = data or load_sources()
    out: list[dict[str, str]] = []
    for cat_id, cat in (data.get("categories") or {}).items():
        for src in cat.get("sources") or []:
            out.append(
                {
                    "category": cat_id,
                    "id": src.get("id", ""),
                    "name": src.get("name", ""),
                    "homepage": src.get("homepage", ""),
                }
            )
    return out


def by_category(category: str, data: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    data = data or load_sources()
    cat = (data.get("categories") or {}).get(category) or {}
    return list(cat.get("sources") or [])


def categories(data: dict[str, Any] | None = None) -> list[str]:
    data = data or load_sources()
    return sorted((data.get("categories") or {}).keys())


def library_stats(data: dict[str, Any] | None = None) -> dict[str, Any]:
    data = data or load_sources()
    cats = data.get("categories") or {}
    per = {k: len(v.get("sources") or []) for k, v in cats.items()}
    return {
        "schema": data.get("schema"),
        "categories": len(cats),
        "sources": sum(per.values()),
        "per_category": per,
        "homepages": len([h for h in all_homepages(data) if h.get("homepage")]),
    }
