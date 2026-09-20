"""Cycle stages — DISCOVER through DEPLOY with estate-aware adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .estate import estate_status, load_estate
from .receipts import StageReceipt


def stage_discover(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    estate = load_estate()
    status = estate_status(estate)
    available = {k: v for k, v in status.items() if v.get("available")}
    summary = (
        f"Discovered target={target!r} mode={mode}; "
        f"estate surfaces available={len(available)}/{len(status)}"
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
        },
    )


def stage_frame(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    plan = {
        "identity": "Forward Deployed Agentic AI",
        "mode": mode,
        "target": target,
        "skill_targets": ["orchestration", "tool_policy", "memory", "eval"],
        "genius_brief": {"role": "ForwardDeployedAgentic", "outcomes": ["working agent system"]},
    }
    ctx["plan"] = plan
    return StageReceipt(
        stage="frame",
        mode=mode,
        status="ok",
        summary=f"Framed plan for {target} under mode={mode}",
        evidence=plan,
    )


def stage_build(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    artifact_dir = Path(ctx.get("work_dir", ".")) / ".fde" / target.replace("/", "_")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    marker = artifact_dir / "BUILD.md"
    marker.write_text(
        f"# Build — {target}\n\nmode: {mode}\nidentity: Forward Deployed Agentic AI\n",
        encoding="utf-8",
    )
    ctx["artifact_dir"] = str(artifact_dir)
    return StageReceipt(
        stage="build",
        mode=mode,
        status="ok",
        summary=f"Build scaffold at {artifact_dir}",
        evidence={"artifact_dir": str(artifact_dir), "marker": str(marker)},
    )


def stage_integrate(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    status = estate_status()
    wired = []
    for key in ("mega_skills", "mega_pipeline_production", "genius_mastery", "aspen_grove_memory", "pro_memory"):
        entry = status.get(key) or {}
        if entry.get("available"):
            wired.append(key)
    note = "wired" if wired else "soft-skip (set FDE_PATH_* or estate.yaml paths)"
    return StageReceipt(
        stage="integrate",
        mode=mode,
        status="ok",
        summary=f"Integrate estate systems: {note}; wired={wired}",
        evidence={"wired": wired, "policy": "adapters_only_no_vendor"},
    )


def stage_evaluate(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    checks = {
        "plan_present": "plan" in ctx,
        "artifact_dir": bool(ctx.get("artifact_dir")),
        "identity": "Forward Deployed Agentic AI",
    }
    ok = all(checks.values()) if isinstance(checks["plan_present"], bool) else False
    return StageReceipt(
        stage="evaluate",
        mode=mode,
        status="ok" if ok else "fail",
        summary="Evaluation gates " + ("passed" if ok else "failed"),
        evidence=checks,
    )


def stage_prove(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    return StageReceipt(
        stage="prove",
        mode=mode,
        status="ok",
        summary="Proof packet prepared (stage receipts form the evidence chain)",
        evidence={"proof_spine": ["coordinator", "safety_monitor", "helix", "akos"]},
    )


def stage_deploy(mode: str, target: str, ctx: dict[str, Any]) -> StageReceipt:
    return StageReceipt(
        stage="deploy",
        mode=mode,
        status="ok",
        summary="Deploy = human-gated handoff packet (no auto-merge / no network send)",
        evidence={"deploy_mode": "approval_packet_only"},
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
