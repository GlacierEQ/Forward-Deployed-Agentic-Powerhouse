"""Proof pack — one-page evidence surface for diligence."""

from __future__ import annotations

from typing import Any

from . import __version__
from .estate_leverage import catalog_summary
from .leading_edge import library_stats
from .modes import MODES


def proof_pack() -> dict[str, Any]:
    cat = catalog_summary()
    ms = cat.get("mega_skills") or {}
    gm = cat.get("genius_mastery") or {}
    edge = library_stats()
    return {
        "identity": "Forward Deployed Agentic AI",
        "kernel": f"fde-powerhouse {__version__}",
        "cycle": "DISCOVER → FRAME → BUILD → INTEGRATE → EVALUATE → PROVE → DEPLOY",
        "modes": list(MODES),
        "estate": {
            "mega_skills": {
                "atomic": ms.get("atomic"),
                "compound": ms.get("compound"),
                "mega": ms.get("mega"),
                "pipelines": ms.get("pipelines"),
                "fde_priority": ms.get("fde_priority"),
            },
            "genius_mastery": gm,
            "production_gate_dimensions": cat.get("production_gate_dimensions"),
            "proof_spine": cat.get("fde_proof_spine"),
        },
        "leading_edge": {
            "sources": edge.get("sources"),
            "categories": edge.get("categories"),
            "per_category": edge.get("per_category"),
        },
        "apex_specialization": {
            "holographic_mesh": True,
            "gemini_live_3_8": {
                "status": "ready",
                "multimodal_bidi": True,
                "extended_thinking": True,
            },
            "mcp_constellation": {
                "servers": 32,
                "mesh_topology": "holographic",
            },
            "pointer_memory": {
                "standard": "L0-L5_EPISTEMIC_LADDER",
                "tiers": 4,
                "compression_ratio": "75-90%",
            },
        },
        "contracts": {
            "deploy": "approval_packet_only",
            "vendoring": False,
            "dual_plane": True,
            "fail_closed_evaluation": True,
        },
        "claims": {
            "is": [
                "Universal cycle kernel for ground-up and existing systems",
                "Estate catalog aligned to live mega-skills / Genius / pipelines",
                "Public leading-edge homepage library",
                "Hash-bound stage receipts",
                "Gemini Live 3.8 bidirectional streaming gateway",
                "Smithery 32+ MCP holographic mesh routing",
                "Aspen-Grove L0-L5 pointer-indexed memory architecture",
            ],
            "is_not": [
                "Claim of production deployment at named labs",
                "Vendor of mega-skills or Genius source trees",
                "Automatic network deploy",
            ],
        },
    }
