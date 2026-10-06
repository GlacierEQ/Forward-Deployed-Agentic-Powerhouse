from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path
from typing import Any

from .scale_control_plane import ScaleControlPlane

SCENARIOS = (
    "completion_without_execution_receipt",
    "partial_workstream_completion",
    "receipt_bound_completion",
)

def _baseline(scenario: str) -> dict[str, Any]:
    if scenario in {"completion_without_execution_receipt", "partial_workstream_completion"}:
        return {"accepted": True, "verified": False, "false_positive": True}
    if scenario == "receipt_bound_completion":
        return {"accepted": True, "verified": True, "false_positive": False}
    raise ValueError(scenario)

def _stack(scenario: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as td:
        cp = ScaleControlPlane.bootstrap(Path(td))
        if scenario == "completion_without_execution_receipt":
            cp.enqueue("E", "eval", outputs=["VERIFICATION_RECEIPT.json"])
            cp.claim("E", "eval")
            try:
                cp.complete("E", "eval", receipt={})
            except ValueError:
                return {"accepted": False, "verified": False, "false_positive": False}
            return {"accepted": True, "verified": True, "false_positive": True}
        if scenario == "partial_workstream_completion":
            cp.enqueue("E", "eval", outputs=["VERIFICATION_RECEIPT.json"])
            cp.claim("E", "eval")
            cp.complete("E", "eval", receipt={"revision": "observed", "tests": ["scale-eval"]})
            state = cp.snapshot()
            verified = state["mission"]["status"] == "verified"
            return {"accepted": verified, "verified": verified, "false_positive": verified}
        if scenario == "receipt_bound_completion":
            for worker in "ABCDE":
                task = f"eval-{worker}"
                cp.enqueue(worker, task, outputs=[f"WORKSTREAM_{worker}.json"])
                cp.claim(worker, task)
                cp.complete(worker, task, receipt={"revision": "observed", "tests": ["scale-eval"]})
            state = cp.snapshot()
            ok = state["mission"]["status"] == "verified" and state["mission"]["frontier_exhausted"]
            return {"accepted": ok, "verified": ok, "false_positive": not ok}
    raise ValueError(scenario)

def run_evaluation() -> dict[str, Any]:
    started = time.perf_counter()
    cases = [{"scenario": s, "baseline": _baseline(s), "stack": _stack(s)} for s in SCENARIOS]
    baseline_fp = sum(int(c["baseline"]["false_positive"]) for c in cases)
    stack_fp = sum(int(c["stack"]["false_positive"]) for c in cases)
    return {
        "schema": "glaciereq.scale-fde-evaluation.v1",
        "evaluation": "single_agent_baseline_vs_receipt_bound_scale_control_plane",
        "scenario_count": len(cases),
        "cases": cases,
        "metrics": {
            "baseline_false_positive_count": baseline_fp,
            "stack_false_positive_count": stack_fp,
            "false_positive_reduction": baseline_fp - stack_fp,
        },
        "duration_ms": round((time.perf_counter() - started) * 1000, 3),
        "boundary": "Deterministic repository-local completion-semantics evaluation; not a benchmark of Scale systems or production deployment.",
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_evaluation()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    print(rendered, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
