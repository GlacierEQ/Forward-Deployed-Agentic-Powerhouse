"""Cycle stages — DISCOVER through DEPLOY with estate leverage."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .bridges import GeniusBridge, MegaSkillsBridge, MemoryBridge, PipelineBridge
from .estate import estate_status, load_estate
from .estate_leverage import catalog_summary, leverage_map
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
    catalog = catalog_summary()
    lev = leverage_map(mode)
    ctx["leverage"] = lev
    summary = (
        f"Discovered target={target!r} mode={mode}; "
        f"estate local={len(available)}/{len(status)}; "
        f"catalog mega={((catalog.get('mega_skills') or {}).get('mega'))} "
        f"pipelines={((catalog.get('mega_skills') or {}).get('pipelines'))}; "
        f"leading_edge={edge.get('sources', 0)}"
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
            "estate_catalog": catalog,
            "leverage": lev,
        },
    )


def stage_frame(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    problem = ctx.get("problem", "")
    plan = build_plan(mode, target, problem=problem)
    # Prefer catalog FDE priority pipelines when framing compose/upgrade
    lev = ctx.get("leverage") or leverage_map(mode)
    cat = lev.get("catalog") or {}
    priority = (cat.get("mega_skills") or {}).get("fde_priority") or []
    if priority:
        plan.pipeline_hints = list(priority)[:6]
    ctx["plan"] = plan
    genius_brief = GeniusBridge().role_brief(plan.genius_role, plan.genius_outcomes)
    return StageReceipt(
        stage="frame",
        mode=mode,
        status="ok",
        summary=f"Framed FDE plan for {target} mode={mode} skills={len(plan.skill_targets)} pipelines={len(plan.pipeline_hints)}",
        evidence={"plan": plan.to_dict(), "genius_brief": genius_brief, "leverage_hints": priority},
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
    lev = ctx.get("leverage") or leverage_map(mode)
    marker.write_text(
        f"# Upgrade surface — {target}\n\nmode: {mode}\nidentity: Forward Deployed Agentic AI\n\n"
        f"## Estate leverage\n\n```json\n{__import__('json').dumps(lev.get('recommendations', []), indent=2)}\n```\n",
        encoding="utf-8",
    )
    ctx["artifact_dir"] = str(artifact_dir)
    return StageReceipt(
        stage="build",
        mode=mode,
        status="ok",
        summary=f"Upgrade workspace at {artifact_dir}",
        evidence={"artifact_dir": str(artifact_dir), "marker": str(marker), "leverage": lev},
    )


def stage_integrate(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    estate = load_estate()
    mega = MegaSkillsBridge(estate).probe()
    genius = GeniusBridge(estate).probe()
    memory = MemoryBridge(estate).probe()
    pipes = PipelineBridge(estate).probe()
    lev = ctx.get("leverage") or leverage_map(mode)
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
    cat = lev.get("catalog") or catalog_summary()
    compose_graph = {
        "catalog_mega": (cat.get("mega_skills") or {}).get("mega"),
        "catalog_pipelines": (cat.get("mega_skills") or {}).get("pipelines"),
        "fde_priority_pipelines": (cat.get("mega_skills") or {}).get("fde_priority"),
        "genius_loop_len": (cat.get("genius_mastery") or {}).get("loop_len"),
        "production_gate_dimensions": cat.get("production_gate_dimensions"),
        "skills_probe": mega.get("registries") or MegaSkillsBridge().suggested_pipelines(),
        "memory_tiers": (memory.get("tiers_model") or ["working", "episodic", "semantic", "graph"]),
        "deploy_mode": pipes.get("default_deploy_mode", "approval_packet_only"),
        "leading_edge_sources": library_stats().get("sources", 0),
        "recommendations": lev.get("recommendations"),
    }
    ctx["compose_graph"] = compose_graph
    note = "wired" if wired else "catalog-driven (set FDE_PATH_* for local execution)"
    return StageReceipt(
        stage="integrate",
        mode=mode,
        status="ok",
        summary=f"Integrate: {note}; wired={wired}; catalog mega={(cat.get('mega_skills') or {}).get('mega')}",
        evidence={
            "wired": wired,
            "compose_graph": compose_graph,
            "probes": {"mega": mega, "genius": genius, "memory": memory, "pipelines": pipes},
            "policy": "catalog_inventory_plus_optional_local_execution",
        },
    )


def stage_evaluate(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    checks = {
        "plan_present": "plan" in ctx,
        "artifact_dir": bool(ctx.get("artifact_dir")),
        "identity_fde": True,
        "compose_graph_present": "compose_graph" in ctx,
        "leverage_present": "leverage" in ctx or mode == "refactor",
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
        "mega_skills": "GlacierEQ/mega-skills",
        "genius_mastery": "GlacierEQ/Genius-Mastery",
    }
    return StageReceipt(
        stage="prove",
        mode=mode,
        status="ok",
        summary="Proof packet — stage receipts + estate spine",
        evidence={"proof_spine": spine, "mode": mode, "target": target},
    )


def stage_deploy(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    packet = {
        "deploy_mode": "approval_packet_only",
        "target": target,
        "mode": mode,
        "artifact_dir": ctx.get("artifact_dir"),
        "next": "Human approval required before merge/network/send",
        "estate_note": "Local FDE_PATH_* enables mega-skills/Genius runners without vendoring",
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
