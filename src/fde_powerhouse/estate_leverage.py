"""Leverage the GlacierEQ estate — catalog facts + compose recommendations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .estate import estate_status, load_estate

DEFAULT_CATALOG = (
    Path(__file__).resolve().parents[2] / "configs" / "estate_catalog.yaml"
)


def load_catalog(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_CATALOG
    if not p.is_file():
        return {"schema": "fde.estate_catalog/v1", "error": "catalog_missing"}
    with p.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def catalog_summary(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    c = catalog or load_catalog()
    ms = c.get("mega_skills") or {}
    regs = ms.get("registries") or {}
    pipes = ms.get("pipelines") or []
    gm = c.get("genius_mastery") or {}
    return {
        "snapshot_date": c.get("snapshot_date"),
        "mega_skills": {
            "atomic": regs.get("atomic_skills"),
            "compound": regs.get("compound_skills"),
            "mega": regs.get("mega_skills"),
            "pipelines": len(pipes),
            "fde_priority": ms.get("fde_priority_pipelines") or [],
        },
        "genius_mastery": {
            "version": gm.get("package_version"),
            "doctrine": gm.get("doctrine"),
            "loop_len": len(gm.get("mastery_loop") or []),
            "kernel": gm.get("kernel"),
        },
        "production_gate_dimensions": len(
            (c.get("mega_pipeline_production") or {}).get("dimensions") or []
        ),
        "fde_proof_spine": [
            x.get("repo") for x in (c.get("fde_proof_spine") or [])
        ],
    }


def leverage_map(mode: str = "compose") -> dict[str, Any]:
    """How this cycle should use the estate for a given mode."""
    c = load_catalog()
    local = estate_status(load_estate())
    available_local = [k for k, v in local.items() if v.get("available")]

    ms = c.get("mega_skills") or {}
    priority = list(ms.get("fde_priority_pipelines") or [])
    gm = c.get("genius_mastery") or {}
    brief = gm.get("fde_role_brief") or {}

    recommendations: list[dict[str, Any]] = []

    if mode in ("compose", "innovate", "upgrade", "ground_up"):
        recommendations.append(
            {
                "system": "mega-skills",
                "action": "align_cycle_to_pipelines",
                "pipelines": priority,
                "local": "mega_skills" in available_local,
            }
        )
        recommendations.append(
            {
                "system": "Genius-Mastery",
                "action": "role_brief_forward_deployed",
                "brief": brief,
                "local": "genius_mastery" in available_local,
            }
        )
        recommendations.append(
            {
                "system": "memory",
                "action": "tier_model",
                "tiers": ((c.get("memory") or {}).get("aspen_grove_memory") or {}).get(
                    "tiers"
                ),
                "local": any(
                    k in available_local for k in ("aspen_grove_memory", "pro_memory")
                ),
            }
        )
        recommendations.append(
            {
                "system": "mega-pipeline-production",
                "action": "production_readiness_gate_7",
                "dimensions": (c.get("mega_pipeline_production") or {}).get("dimensions"),
                "local": "mega_pipeline_production" in available_local,
            }
        )

    if mode in ("merge", "repoint", "upgrade"):
        recommendations.append(
            {
                "system": "job-app-helix",
                "action": "sync_fde_hire_package",
                "path": (c.get("hire_package_bridge") or {}).get("path"),
                "local": "job_app_helix" in available_local,
            }
        )

    return {
        "mode": mode,
        "catalog": catalog_summary(c),
        "local_available": available_local,
        "recommendations": recommendations,
        "policy": "catalog_is_inventory_not_runtime; local paths enable execution",
    }
