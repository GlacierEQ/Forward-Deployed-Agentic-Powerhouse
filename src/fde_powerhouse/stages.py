"""Cycle stages — DISCOVER through DEPLOY with estate-aware adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .bridges import GeniusBridge, MegaSkillsBridge, MemoryBridge, PipelineBridge
from .estate import estate_status, load_estate
from .leading_edge import library_stats
from .plan import build_plan
from .receipts import StageReceipt
from .scaffold import write_scaffold


def stage_discover(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    estate = load_estate()
    status = estate_status(estate)
    available = {k: v for k, v in status.items() if v.get("available")}
    mega = MegaSkillsBridge(estate).probe()
    genius = GeniusBridge(estate).probe()
    memory = MemoryBridge(estate).probe()
    pipes = PipelineBridge(estate).probe()
    edge = library_stats()
    summary = (
        f"Discovered target={target!r} mode={mode}; "
        f"estate available={len(available)}/{len(status)}; "
        f"mega_skills={mega.get('available')}; genius={genius.get('available')}; "
        f"memory={MemoryBridge(estate).available}; "
        f"leading_edge_sources={edge.get('sources', 0)}"
    )
    return StageReceipt(
        stage="discover",
        mode=mode,
        status="ok",
        summary=summary,
        evidence={
            "target": target,
            "estate_available": sorted(available.keys()),
            "estate_missing": sorted(k for k, v in status.items() if not v.get("available")),
            "mega_skills": mega,
            "genius": genius,
            "memory": memory,
            "pipelines": pipes,
            "leading_edge": edge,
        },
    )


def stage_frame(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    problem = ctx.get("problem", "")
    plan = build_plan(mode, target, problem=problem)
    ctx["plan"] = plan
    genius_brief = GeniusBridge().role_brief(plan.genius_role, plan.genius_outcomes)
    return StageReceipt(
        stage="frame",
        mode=mode,
        status="ok",
        summary=f"Framed FDE plan for {target} mode={mode} skills={len(plan.skill_targets)}",
        evidence={"plan": plan.to_dict(), "genius_brief": genius_brief},
    )


def stage_build(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    plan = ctx.get("plan") or build_plan(mode, target)
    artifact_dir = Path(ctx.get("work_dir", ".")) / ".fde" / target.replace("/", "_")
    if mode in ("ground_up", "invent", "innovate"):
        result = write_scaffold(artifact_dir, plan)
        ctx["artifact_dir"] = result["root"]
        ctx["scaffold"] = result
        return StageReceipt(
            stage="build",
            mode=mode,
            status="ok",
            summary=f"Scaffold written: {result['count']} files at {result['root']}",
            evidence=result,
        )
    artifact_dir.mkdir(parents=True, exist_ok=True)
    marker = artifact_dir / "UPGRADE.md"
    marker.write_text(
        f"# Upgrade surface — {target}\n\nmode: {mode}\nidentity: Forward Deployed Agentic AI\n",
        encoding="utf-8",
    )
    ctx["artifact_dir"] = str(artifact_dir)
    return StageReceipt(
        stage="build",
        mode=mode,
        status="ok",
        summary=f"Upgrade workspace at {artifact_dir}",
        evidence={"artifact_dir": str(artifact_dir), "marker": str(marker)},
    )


def stage_integrate(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    estate = load_estate()
    mega = MegaSkillsBridge(estate).probe()
    genius = GeniusBridge(estate).probe()
    memory = MemoryBridge(estate).probe()
    pipes = PipelineBridge(estate).probe()
    wired = []
    if mega.get("available"):
        wired.append("mega_skills")
    if genius.get("available"):
        wired.append("genius_mastery")
    if MemoryBridge(estate).available:
        wired.append("memory")
    if (pipes.get("mega_pipeline_production") or {}).get("available") or (
        pipes.get("mega_skills_pipelines") or {}
    ).get("available"):
        wired.append("pipelines")
    compose_graph = {
        "skills": mega.get("registries") or MegaSkillsBridge().suggested_pipelines(),
        "genius_loop": genius.get("loop")
        or ["MAP", "BUILD", "VERIFY", "TEACH"],
        "memory_tiers": (memory.get("tiers_model") or ["working", "episodic", "semantic", "graph"]),
        "deploy_mode": pipes.get("default_deploy_mode", "approval_packet_only"),
        "leading_edge_sources": library_stats().get("sources", 0),
    }
    ctx["compose_graph"] = compose_graph
    note = "wired" if wired else "soft-skip (set FDE_PATH_* for live estate)"
    return StageReceipt(
        stage="integrate",
        mode=mode,
        status="ok",
        summary=f"Integrate: {note}; wired={wired}",
        evidence={
            "wired": wired,
            "compose_graph": compose_graph,
            "probes": {"mega": mega, "genius": genius, "memory": memory, "pipelines": pipes},
            "policy": "adapters_only_no_vendor",
        },
    )


def stage_evaluate(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    checks = {
        "plan_present": "plan" in ctx,
        "artifact_dir": bool(ctx.get("artifact_dir")),
        "identity_fde": True,
        "compose_graph_present": "compose_graph" in ctx,
    }
    if mode in ("ground_up", "invent") and ctx.get("scaffold"):
        checks["scaffold_files"] = ctx["scaffold"].get("count", 0) >= 5
    ok = all(bool(v) for v in checks.values())
    return StageReceipt(
        stage="evaluate",
        mode=mode,
        status="ok" if ok else "fail",
        summary="Evaluation gates " + ("passed" if ok else "failed"),
        evidence=checks,
    )


def stage_prove(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    spine = {
        "coordinator": "GlacierEQ/anthropic-agent-coordinator",
        "safety_monitor": "GlacierEQ/anthropic-safety-monitor",
        "helix": "GlacierEQ/job-app-helix",
        "akos": "GlacierEQ/AKOS",
        "powerhouse": "GlacierEQ/Forward-Deployed-Agentic-Powerhouse",
    }
    return StageReceipt(
        stage="prove",
        mode=mode,
        status="ok",
        summary="Proof packet prepared — stage receipts + FDE spine",
        evidence={"proof_spine": spine, "mode": mode, "target": target},
    )


def stage_deploy(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    packet = {
        "deploy_mode": "approval_packet_only",
        "target": target,
        "mode": mode,
        "artifact_dir": ctx.get("artifact_dir"),
        "next": "Human approval required before merge/network/send",
    }
    return StageReceipt(
        stage="deploy",
        mode=mode,
        status="ok",
        summary="Human-gated handoff packet (no auto-merge / no network send)",
        evidence=packet,
    )


STAGE_FNS: dict[str, Callable[..., StageReceipt]] = {
    "discover": stage_discover,
    "frame": stage_frame,
    "build": stage_build,
    "integrate": stage_integrate,
    "evaluate": stage_evaluate,
    "prove": stage_prove,
    "deploy": stage_deploy,
}
