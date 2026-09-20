"""Typed cycle plan — FDE identity + skill/genius/memory targets."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class CyclePlan:
    identity: str = "Forward Deployed Agentic AI"
    mode: str = "ground_up"
    target: str = "default"
    problem: str = ""
    skill_targets: list[str] = field(
        default_factory=lambda: [
            "orchestration",
            "tool_policy",
            "mcp_integration",
            "memory",
            "evaluation",
            "evidence_receipts",
        ]
    )
    mega_skill_hints: list[str] = field(default_factory=list)
    genius_role: str = "ForwardDeployedAgentic"
    genius_outcomes: list[str] = field(
        default_factory=lambda: [
            "working multi-agent system",
            "tool policy gates",
            "hash-bound receipts",
        ]
    )
    memory_tiers: list[str] = field(
        default_factory=lambda: ["working", "episodic", "semantic", "graph"]
    )
    pipeline_hints: list[str] = field(
        default_factory=lambda: ["inception-to-deployment", "control-plane"]
    )
    constraints: list[str] = field(
        default_factory=lambda: [
            "fail_closed_evaluation",
            "human_gated_deploy",
            "no_vendor_estate_code",
            "dual_plane_honesty",
        ]
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_plan(mode: str, target: str, problem: str = "") -> CyclePlan:
    plan = CyclePlan(mode=mode, target=target, problem=problem or f"FDE cycle for {target}")
    if mode == "compose":
        plan.mega_skill_hints = [
            "inception-to-deployment",
            "memory-fleet",
            "control-plane",
        ]
        plan.pipeline_hints = [
            "inception-to-deployment",
            "control-plane",
            "change-swe",
        ]
    elif mode == "invent":
        plan.skill_targets.append("novel_capability")
        plan.genius_outcomes.append("new capability with evidence path")
    elif mode == "upgrade":
        plan.skill_targets.extend(["skill_pyramid_lift", "memory_tier_lift"])
    elif mode == "merge":
        plan.constraints.append("preserve_unique_lineage")
    return plan
