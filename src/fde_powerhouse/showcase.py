"""Impressive showcase — full power demonstration in one receipt."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .cycle import run_cycle
from .estate_leverage import catalog_summary, leverage_map
from .leading_edge import library_stats
from .modes import MODES
from .receipts import CycleReceipt


@dataclass
class ShowcasePack:
    version: str
    generated_at: str
    identity: str = "Forward Deployed Agentic AI"
    cycle: dict[str, Any] = field(default_factory=dict)
    estate: dict[str, Any] = field(default_factory=dict)
    leverage: dict[str, Any] = field(default_factory=dict)
    leading_edge: dict[str, Any] = field(default_factory=dict)
    composition_matrix: list[dict[str, Any]] = field(default_factory=list)
    operator_card: dict[str, str] = field(default_factory=dict)
    impressiveness_signals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _composition_matrix() -> list[dict[str, Any]]:
    cat = catalog_summary()
    ms = cat.get("mega_skills") or {}
    return [
        {
            "layer": "Skills pyramid",
            "system": "mega-skills",
            "scale": f"{ms.get('atomic')} atomic → {ms.get('compound')} compound → {ms.get('mega')} mega",
            "fde_use": "Capability hierarchy for agent missions",
        },
        {
            "layer": "Deep-work pipelines",
            "system": "mega-skills pipelines",
            "scale": f"{ms.get('pipelines')} pipelines; priority={ms.get('fde_priority')}",
            "fde_use": "Inception→deploy-gate with approval_packet_only",
        },
        {
            "layer": "Mastery forge",
            "system": "Genius-Mastery",
            "scale": f"kernel v{cat.get('genius_mastery', {}).get('version')}; loop={cat.get('genius_mastery', {}).get('loop_len')} steps",
            "fde_use": "Synthesize ForwardDeployedAgentic entities",
        },
        {
            "layer": "Production gate",
            "system": "mega-pipeline-production",
            "scale": f"{cat.get('production_gate_dimensions')}/7 dimensions",
            "fde_use": "No delivery without evidence",
        },
        {
            "layer": "Memory organism",
            "system": "aspen-grove-memory / Pro-Memory",
            "scale": "4-tier constellation",
            "fde_use": "Working → episodic → semantic → graph",
        },
        {
            "layer": "Public edge",
            "system": "leading_edge_sources",
            "scale": f"{library_stats().get('sources')} HTTPS homepages",
            "fde_use": "Continuous public tech edge awareness",
        },
        {
            "layer": "Proof spine",
            "system": "coordinator + safety + helix + powerhouse",
            "scale": "receipt-bound multi-agent + policy + portfolio",
            "fde_use": "Field delivery evidence",
        },
    ]


def _operator_card() -> dict[str, str]:
    return {
        "WHO": "Forward Deployed Agentic AI Engineer",
        "CYCLE": "Discover → Frame → Build → Integrate → Evaluate → Prove → Deploy",
        "ESTATE": "mega-skills · Genius-Mastery · memory · pipelines · Helix",
        "EDGE": f"{library_stats().get('sources')} public tech homepages",
        "LAW": "Full power + dual-plane honesty · approval_packet_only",
        "MODES": " · ".join(MODES),
    }


def _signals(cycle: CycleReceipt, cat: dict[str, Any]) -> list[str]:
    ms = cat.get("mega_skills") or {}
    return [
        f"Kernel v{__version__} — universal 9-mode cycle",
        f"Estate inventory: {ms.get('atomic')} skills / {ms.get('mega')} mega / {ms.get('pipelines')} pipelines",
        f"Cycle status={cycle.status} stages={len(cycle.stages)} sha256={cycle.digest()[:16]}…",
        f"Leading edge: {library_stats().get('sources')} public sources",
        "Deploy: human-gated — no silent merge/network",
        "Identity locked: Forward Deployed Agentic AI",
    ]


def run_showcase(
    target: str = "showcase",
    work_dir: str | Path = ".",
    mode: str = "compose",
) -> ShowcasePack:
    cycle = run_cycle(mode=mode, target=target, work_dir=work_dir)
    cat = catalog_summary()
    lev = leverage_map(mode)
    pack = ShowcasePack(
        version=__version__,
        generated_at=datetime.now(timezone.utc).isoformat(),
        cycle=cycle.to_dict(),
        estate=cat,
        leverage=lev,
        leading_edge=library_stats(),
        composition_matrix=_composition_matrix(),
        operator_card=_operator_card(),
        impressiveness_signals=_signals(cycle, cat),
    )
    out_dir = Path(work_dir) / ".fde" / f"showcase_{target}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "SHOWCASE.json").write_text(
        json.dumps(pack.to_dict(), indent=2, default=str), encoding="utf-8"
    )
    (out_dir / "OPERATOR_CARD.md").write_text(_card_md(pack), encoding="utf-8")
    (out_dir / "COMPOSITION.md").write_text(_matrix_md(pack), encoding="utf-8")
    return pack


def _card_md(pack: ShowcasePack) -> str:
    lines = ["# FDE Operator Card", "", f"Generated: {pack.generated_at}", ""]
    for k, v in pack.operator_card.items():
        lines.append(f"- **{k}:** {v}")
    lines.append("")
    lines.append("## Signals")
    for s in pack.impressiveness_signals:
        lines.append(f"- {s}")
    return "\n".join(lines) + "\n"


def _matrix_md(pack: ShowcasePack) -> str:
    lines = [
        "# Estate Composition Matrix",
        "",
        "| Layer | System | Scale | FDE use |",
        "|-------|--------|-------|---------|",
    ]
    for row in pack.composition_matrix:
        lines.append(
            f"| {row['layer']} | {row['system']} | {row['scale']} | {row['fde_use']} |"
        )
    return "\n".join(lines) + "\n"
