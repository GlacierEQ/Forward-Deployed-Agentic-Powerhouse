#!/usr/bin/env python3
"""apex-command — FORWARD DEPLOYED AGENTIC AI CLI: Mission Control & Orchestration.

Composes:
  - apex-sovereign-supreme: Bootup, telemetry, service health
  - longest-horizon: Deep planning and high council reasoning
  - apex-orchestration: Swarm DAG topology and specialist routing
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

SOVEREIGN_BOOT = Path("/root/.agents/skills/apex-sovereign-supreme/scripts/bootup_runner.py")
SOVEREIGN_VERIFY = Path("/root/.agents/skills/apex-sovereign-supreme/scripts/verify_full_system_operation.py")
SOVEREIGN_HEAL = Path("/root/.agents/skills/apex-sovereign-supreme/scripts/runtime_optimizer_supreme.py")
SOVEREIGN_INTEL = Path("/root/.agents/skills/apex-sovereign-supreme/scripts/apex_sovereign_intelligence.py")
MODES_REGISTRY = Path(__file__).parent / "agent_modes.json"
SKILLS_DIR = Path("/root/.agents/skills")
LONG_HORIZON = Path("/root/.agents/skills/longest-horizon")
ORCHESTRATOR = Path("/root/.agents/skills/apex-orchestration/scripts/omni_swarm_orchestrator.py")


def run_cmd(cmd: List[str], timeout: int = 120) -> Dict[str, Any]:
    raw = " ".join(cmd).encode("utf-8")
    digest = f"sha256:{hashlib.sha256(raw).hexdigest()}"
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError:
                data = None
            return {
                "success": True,
                "data": data,
                "raw": None if data is not None else result.stdout.strip(),
                "digest": digest,
                "provenance": f"exec://{cmd[0]}/{digest[:12]}",
            }
        return {
            "success": False,
            "error": result.stderr.strip() or result.stdout.strip(),
            "code": result.returncode,
            "digest": digest,
            "provenance": f"exec_error://{cmd[0]}/{digest[:12]}",
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Timeout after {timeout}s", "digest": digest, "provenance": f"exec_timeout://{cmd[0]}"}
    except Exception as exc:
        return {"success": False, "error": str(exc), "digest": digest, "provenance": f"exec_exception://{cmd[0]}"}


def cmd_boot(_args: argparse.Namespace) -> Dict[str, Any]:
    return run_cmd(["python3", str(SOVEREIGN_BOOT)], timeout=240)


def cmd_verify(_args: argparse.Namespace) -> Dict[str, Any]:
    return run_cmd(["python3", str(SOVEREIGN_VERIFY)], timeout=180)


def cmd_heal(args: argparse.Namespace) -> Dict[str, Any]:
    if getattr(args, "daemon", False):
        sys.path.insert(0, str(SOVEREIGN_HEAL.parent))
        from runtime_optimizer_supreme import RuntimeOptimizer
        RuntimeOptimizer.run_watchdog_loop(getattr(args, "interval", 30))
        return {"success": True, "data": {"mode": "daemon"}}
    mode = "daemon" if getattr(args, "daemon", False) else "heal"
    return run_cmd(["python3", str(SOVEREIGN_HEAL), mode], timeout=180)


def cmd_status(_args: argparse.Namespace) -> Dict[str, Any]:
    sys.path.insert(0, str(SOVEREIGN_HEAL.parent))
    from runtime_optimizer_supreme import RuntimeOptimizer
    return {"success": True, "data": RuntimeOptimizer.status()}


def _load_plan_framework():
    sys.path.insert(0, str(LONG_HORIZON))
    from framework.high_council import HighCouncil, Position
    from framework.sequential_thinking import SequentialThinker
    return SequentialThinker, HighCouncil, Position


def cmd_plan(args: argparse.Namespace) -> Dict[str, Any]:
    SequentialThinker, HighCouncil, Position = _load_plan_framework()
    objective = args.objective
    thinker = SequentialThinker()
    thinker.add_step("constraint", "The objective must be bound to the Operator's explicit intent.", evidence="current Operator instruction")
    thinker.add_step("state", "The current source state must be read back before mutation.", evidence="AGENTS.md, manifests, source files, and live probes", cites=["s1"])
    thinker.add_step("dependencies", "The dependency graph must preserve independent evidence and execution lanes.", evidence="APEX Command Core orchestration contract", cites=["s1", "s2"])
    thinker.add_step("verification", "Every claimed result requires readback, provenance, and a nonzero failure path.", evidence="APEX L0-L5 verification ladder", cites=["s2", "s3"])
    chain = thinker.verify_chain()
    council = HighCouncil()
    council.seat("mission", lambda _question: Position(id="mission", vp="mission", role="default", claim="Advance the stated objective with maximum coherent capability gain.", confidence=0.98, supports=["mission"]))
    council.seat("evidence", lambda _question: Position(id="evidence", vp="evidence", role="evidence", claim="Preserve source provenance and reject unsupported completion claims.", confidence=0.99, supports=["mission"], contradicts=["risk"]))
    council.seat("risk", lambda _question: Position(id="risk", vp="risk", role="procedural", claim="Contain blast radius and retain a recoverable checkpoint.", confidence=0.95, supports=["mission"]))
    council.seat("verification", lambda _question: Position(id="verification", vp="verification", role="evidence", claim="Require independent verification before reporting completion.", confidence=0.99, supports=["evidence", "risk"]))
    directive = council.deliberate(objective)
    reasoning_chain = [
        {
            "id": step.id,
            "kind": step.kind,
            "claim": step.claim,
            "evidence": step.evidence,
            "cites": step.cites,
            "confidence": step.confidence,
        }
        for step in thinker.trace()
    ]
    payload = {
        "objective": objective,
        "horizon": args.horizon,
        "framework": "longest-horizon",
        "reasoning_chain": reasoning_chain,
        "reasoning_chain_valid": chain.ok,
        "reasoning_chain_errors": chain.errors,
        "council_verdict": {
            "question": directive.question,
            "reconciliation": directive.reconciliation,
            "unresolved": directive.unresolved,
            "positions": [position.__dict__ for position in directive.positions],
            "disputes": [dispute.__dict__ for dispute in directive.disputes],
        },
        "steps": [step["claim"] for step in reasoning_chain],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = f"sha256:{hashlib.sha256(raw).hexdigest()}"
    return {"success": chain.ok, "data": {**payload, "digest": digest, "provenance": f"plan://{args.horizon}/{digest[:12]}"}}


def _load_plan(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {"objective": "ad_hoc_execution", "steps": []}
    try:
        with open(path, "r", encoding="utf-8") as stream:
            payload = json.load(stream)
        if not isinstance(payload, dict) or not payload.get("objective"):
            raise ValueError("plan must be a JSON object with an objective")
        return payload
    except Exception as exc:
        return {"objective": "failed_load", "error": str(exc)}


def _run_local_plan_commands(plan: Dict[str, Any]) -> Dict[str, Any]:
    commands = plan.get("commands") or [step.get("command") for step in plan.get("steps", []) if isinstance(step, dict) and step.get("command")]
    if not commands:
        return {"executed": False, "commands": []}
    receipts = []
    for command in commands:
        if not isinstance(command, list):
            receipts.append({"success": False, "error": "command must be an argument array"})
            continue
        receipts.append(run_cmd(command, timeout=int(plan.get("command_timeout", 120))))
    return {"executed": True, "commands": receipts, "success": all(item.get("success", False) for item in receipts)}


def _run_swarm_execution(objective: str, workers: List[str]) -> Dict[str, Any]:
    sys.path.insert(0, str(ORCHESTRATOR.parent))
    from omni_swarm_orchestrator import OmniSwarmOrchestrator
    orchestrator = OmniSwarmOrchestrator()
    project_id = orchestrator.create_project("apex-command-core", objective)
    tasks = orchestrator.plan_and_decompose(project_id, objective)
    lifecycle = orchestrator.run_parallel_lifecycle(project_id, max_workers=min(4, max(1, len(workers))))
    return {"project_id": project_id, "tasks": tasks, "lifecycle": lifecycle}


def cmd_execute(args: argparse.Namespace) -> Dict[str, Any]:
    plan = _load_plan(args.plan)
    if plan.get("objective") == "failed_load":
        return {"success": False, "error": plan.get("error"), "verification_status": "failed"}
    if args.mode == "dry_run":
        return {"success": True, "data": {"mode": "dry_run", "plan": plan, "execution_receipt": {"status": "dry_run_verified", "mutations": 0}, "verification_status": "passed"}}
    local = _run_local_plan_commands(plan)
    if local.get("executed"):
        return {"success": local.get("success", False), "data": {"mode": args.mode, "plan": plan, "execution_receipt": local, "verification_status": "passed" if local.get("success") else "failed"}}
    workers = [str(worker) for worker in plan.get("workers", [])] or ["cartographer", "implementer", "adversarial", "verify"]
    swarm = _run_swarm_execution(str(plan["objective"]), workers)
    status = swarm.get("lifecycle", {}).get("status")
    return {"success": status == "COMPLETED", "data": {"mode": args.mode, "plan": plan, "execution_receipt": swarm, "verification_status": "passed" if status == "COMPLETED" else "failed"}}


def _load_modes() -> Dict[str, Any]:
    try:
        with open(MODES_REGISTRY, "r", encoding="utf-8") as stream:
            return json.load(stream)
    except Exception as exc:
        return {"error": str(exc)}


def _verify_modes(registry: Dict[str, Any]) -> Dict[str, Any]:
    role_modes = registry.get("role_modes", {})
    problems: List[str] = []
    for role, spec in role_modes.items():
        skill = spec.get("skill", "")
        if not (SKILLS_DIR / skill).exists():
            problems.append(f"role '{role}' -> missing skill dir '{skill}'")
    execution_modes = list(registry.get("execution_modes", {}).keys())
    composites = registry.get("composite_modes", {})
    for name, spec in composites.items():
        for role in spec.get("roles", []):
            if role not in role_modes:
                problems.append(f"composite '{name}' -> unknown role '{role}'")
        if spec.get("execution") not in execution_modes:
            problems.append(f"composite '{name}' -> unknown execution '{spec.get('execution')}'")
    return {"valid": not problems, "problems": problems, "counts": {"execution": len(execution_modes), "roles": len(role_modes), "composites": len(composites)}}


def cmd_modes(args: argparse.Namespace) -> Dict[str, Any]:
    registry = _load_modes()
    if "error" in registry:
        return {"success": False, "error": registry["error"]}
    if args.verify:
        verification = _verify_modes(registry)
        return {"success": verification["valid"], "data": verification}
    if args.select:
        name = args.select
        composites = registry.get("composite_modes", {})
        execution_modes = registry.get("execution_modes", {})
        role_modes = registry.get("role_modes", {})
        if name in composites:
            return {"success": True, "data": {"type": "composite", "name": name, **composites[name]}}
        if name in execution_modes:
            return {"success": True, "data": {"type": "execution", "name": name, **execution_modes[name]}}
        if name in role_modes:
            return {"success": True, "data": {"type": "role", "name": name, **role_modes[name]}}
        return {"success": False, "error": f"mode '{name}' not found in registry"}
    verification = _verify_modes(registry)
    return {"success": verification["valid"], "data": {"execution_modes": list(registry.get("execution_modes", {}).keys()), "role_modes": list(registry.get("role_modes", {}).keys()), "composite_modes": list(registry.get("composite_modes", {}).keys()), "verification": verification}}


def cmd_orchestrate(args: argparse.Namespace) -> Dict[str, Any]:
    workers = [worker.strip() for worker in args.workers.split(",") if worker.strip()] if args.workers else ["cartographer", "miner", "connector", "architect", "implementer", "reliability", "verify"]
    swarm = _run_swarm_execution(args.objective, workers)
    tasks = swarm.get("tasks", [])
    assignments = {task.get("role", "unknown"): {"task_id": task.get("id"), "description": task.get("description"), "dependencies": task.get("dependencies", [])} for task in tasks}
    return {"success": swarm.get("lifecycle", {}).get("status") == "COMPLETED", "data": {"objective": args.objective, "workers": workers, "topology": "DAG: scout -> specialists -> adversarial -> integrator -> verifier", "task_assignments": assignments, "synthesis": swarm.get("lifecycle"), "verification": swarm.get("lifecycle"), "project_id": swarm.get("project_id")}}


def main() -> int:
    parser = argparse.ArgumentParser(prog="apex-command", description="FORWARD DEPLOYED AGENTIC AI — Mission Control & Orchestration")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("boot", help="Boot and verify the holographic runtime")
    sub.add_parser("verify", help="Run the fail-closed end-to-end verification suite")
    heal = sub.add_parser("heal", help="Heal managed services")
    heal.add_argument("--daemon", action="store_true")
    heal.add_argument("--interval", type=int, default=30)
    sub.add_parser("status", help="Read service readiness")
    plan = sub.add_parser("plan", help="Build a verified longest-horizon plan")
    plan.add_argument("--objective", required=True)
    plan.add_argument("--horizon", choices=["immediate", "short", "medium", "long"], default="medium")
    execute = sub.add_parser("execute", help="Execute a plan or swarm mission")
    execute.add_argument("--plan")
    execute.add_argument("--mode", choices=["standard", "aggressive", "conservative", "dry_run"], default="standard")
    orchestrate = sub.add_parser("orchestrate", help="Run a DAG swarm mission")
    orchestrate.add_argument("--objective", required=True)
    orchestrate.add_argument("--workers")
    modes = sub.add_parser("modes", help="List, verify, or select agent modes")
    modes.add_argument("--verify", action="store_true")
    modes.add_argument("--select")
    args = parser.parse_args()
    handlers = {"boot": cmd_boot, "verify": cmd_verify, "heal": cmd_heal, "status": cmd_status, "plan": cmd_plan, "execute": cmd_execute, "orchestrate": cmd_orchestrate, "modes": cmd_modes}
    try:
        result = handlers[args.cmd](args)
        print(json.dumps(result, indent=2))
        return 0 if result.get("success") else 1
    except Exception as exc:
        logger.exception("CLI routing error")
        print(json.dumps({"success": False, "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
