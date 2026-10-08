from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path
from typing import Any

from .scale_control_plane import ScaleControlPlane

SCENARIOS = (
    {
        "name": "completion_without_execution_receipt",
        "expected_accept": False,
        "completion_claimed": True,
    },
    {
        "name": "unverified_test_label",
        "expected_accept": False,
        "completion_claimed": True,
    },
    {
        "name": "receipt_without_provider_readback",
        "expected_accept": False,
        "completion_claimed": True,
    },
    {
        "name": "receipt_without_declared_outputs",
        "expected_accept": False,
        "completion_claimed": True,
    },
    {
        "name": "partial_workstream_completion",
        "expected_accept": False,
        "completion_claimed": True,
    },
    {
        "name": "pending_integration",
        "expected_accept": False,
        "completion_claimed": True,
    },
    {
        "name": "unresolved_defect",
        "expected_accept": False,
        "completion_claimed": True,
    },
    {
        "name": "receipt_bound_completion",
        "expected_accept": False,
        "completion_claimed": True,
    },
    {
        "name": "resolved_integration_and_defect",
        "expected_accept": True,
        "completion_claimed": True,
    },
    {
        "name": "active_running_task",
        "expected_accept": False,
        "completion_claimed": False,
    },
)


def _readback(tag: str) -> dict[str, str]:
    return {
        "state": "verified",
        "source": f"provider://synthetic-eval/{tag}",
    }


def _receipt(output: str, tag: str) -> dict[str, Any]:
    return {
        "revision": f"revision-{tag}",
        "tests": [
            {
                "name": "scale-eval",
                "state": "passed",
                "source": f"runner://synthetic-eval/{tag}",
            }
        ],
        "outputs": [
            {
                "path": output,
                "state": "verified",
                "source": f"artifact://synthetic-eval/{tag}/{output}",
            }
        ],
        "readback": _readback(tag),
    }


def _complete_all(cp: ScaleControlPlane) -> None:
    for worker in "ABCDE":
        task = f"eval-{worker}"
        output = f"WORKSTREAM_{worker}.json"
        cp.enqueue(worker, task, outputs=[output])
        cp.claim(worker, task)
        cp.complete(worker, task, receipt=_receipt(output, worker))


def _baseline(case: dict[str, Any]) -> dict[str, Any]:
    accepted = bool(case["completion_claimed"])
    return {
        "accepted": accepted,
        "policy": "trust_completion_claim",
    }


def _stack(scenario: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as td:
        cp = ScaleControlPlane.bootstrap(Path(td))

        if scenario == "completion_without_execution_receipt":
            cp.enqueue("E", "eval", outputs=["VERIFICATION_RECEIPT.json"])
            cp.claim("E", "eval")
            try:
                cp.complete("E", "eval", receipt={})
            except (TypeError, ValueError) as exc:
                return {"accepted": False, "reason": str(exc)}
            return {"accepted": True, "reason": "receipt accepted"}

        if scenario == "unverified_test_label":
            cp.enqueue("E", "eval", outputs=["VERIFICATION_RECEIPT.json"])
            cp.claim("E", "eval")
            receipt = _receipt("VERIFICATION_RECEIPT.json", "tests")
            receipt["tests"] = ["scale-eval"]
            try:
                cp.complete("E", "eval", receipt=receipt)
            except (TypeError, ValueError) as exc:
                return {"accepted": False, "reason": str(exc)}
            return {"accepted": True, "reason": "test label accepted"}

        if scenario == "receipt_without_provider_readback":
            cp.enqueue("E", "eval", outputs=["VERIFICATION_RECEIPT.json"])
            cp.claim("E", "eval")
            receipt = _receipt("VERIFICATION_RECEIPT.json", "readback")
            receipt.pop("readback")
            try:
                cp.complete("E", "eval", receipt=receipt)
            except (TypeError, ValueError) as exc:
                return {"accepted": False, "reason": str(exc)}
            return {"accepted": True, "reason": "readback-free receipt accepted"}

        if scenario == "receipt_without_declared_outputs":
            cp.enqueue("E", "eval", outputs=["VERIFICATION_RECEIPT.json"])
            cp.claim("E", "eval")
            receipt = _receipt("VERIFICATION_RECEIPT.json", "outputs")
            receipt["outputs"] = []
            try:
                cp.complete("E", "eval", receipt=receipt)
            except (TypeError, ValueError) as exc:
                return {"accepted": False, "reason": str(exc)}
            return {"accepted": True, "reason": "output-free receipt accepted"}

        if scenario == "partial_workstream_completion":
            cp.enqueue("E", "eval", outputs=["VERIFICATION_RECEIPT.json"])
            cp.claim("E", "eval")
            cp.complete(
                "E",
                "eval",
                receipt=_receipt("VERIFICATION_RECEIPT.json", "partial"),
            )
            verified = cp.snapshot()["mission"]["status"] == "verified"
            return {"accepted": verified, "reason": "mission status"}

        if scenario == "pending_integration":
            _complete_all(cp)
            cp.queue_integration("D", "provider-mutation", "receipt-D")
            verified = cp.snapshot()["mission"]["status"] == "verified"
            return {"accepted": verified, "reason": "mission status"}

        if scenario == "unresolved_defect":
            _complete_all(cp)
            cp.add_defect(
                "E",
                "eval-E",
                {
                    "id": "DEF-EVAL-001",
                    "summary": "synthetic unresolved defect",
                },
            )
            verified = cp.snapshot()["mission"]["status"] == "verified"
            return {"accepted": verified, "reason": "mission status"}

        if scenario == "receipt_bound_completion":
            _complete_all(cp)
            verified = cp.snapshot()["mission"]["status"] == "verified"
            return {"accepted": verified, "reason": "mission status"}

        if scenario == "resolved_integration_and_defect":
            _complete_all(cp)
            cp.queue_integration("D", "provider-mutation", "receipt-D")
            cp.add_defect(
                "E",
                "eval-E",
                {
                    "id": "DEF-EVAL-002",
                    "summary": "synthetic repaired defect",
                },
            )
            cp.reconcile_integration(
                "D",
                "provider-mutation",
                "receipt-D",
                readback=_readback("integration"),
            )
            cp.resolve_defect(
                "E",
                "eval-E",
                "DEF-EVAL-002",
                readback=_readback("defect"),
            )
            verified = cp.snapshot()["mission"]["status"] == "verified"
            return {"accepted": verified, "reason": "mission status"}

        if scenario == "active_running_task":
            cp.enqueue("E", "eval", outputs=["VERIFICATION_RECEIPT.json"])
            cp.claim("E", "eval")
            verified = cp.snapshot()["mission"]["status"] == "verified"
            return {"accepted": verified, "reason": "mission status"}

    raise ValueError(scenario)


def _confusion(cases: list[dict[str, Any]], key: str) -> dict[str, Any]:
    tp = tn = fp = fn = 0
    for case in cases:
        accepted = bool(case[key]["accepted"])
        expected = bool(case["expected_accept"])
        if accepted and expected:
            tp += 1
        elif not accepted and not expected:
            tn += 1
        elif accepted and not expected:
            fp += 1
        else:
            fn += 1

    negative_count = fp + tn
    positive_count = tp + fn
    total = len(cases)
    return {
        "true_positives": tp,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "false_positive_rate": fp / negative_count if negative_count else 0.0,
        "false_negative_rate": fn / positive_count if positive_count else 0.0,
        "accuracy": (tp + tn) / total if total else 0.0,
    }


def run_evaluation() -> dict[str, Any]:
    started = time.perf_counter()
    cases = []
    for definition in SCENARIOS:
        case = dict(definition)
        case["baseline"] = _baseline(case)
        case["stack"] = _stack(case["name"])
        cases.append(case)

    baseline = _confusion(cases, "baseline")
    stack = _confusion(cases, "stack")
    return {
        "schema": "glaciereq.scale-fde-evaluation.v2",
        "evaluation": (
            "naive_completion_claim_baseline_vs_evidence_bound_control_plane"
        ),
        "scenario_count": len(cases),
        "cases": cases,
        "metrics": {
            "baseline": baseline,
            "stack": stack,
            "false_positive_reduction": {
                "count": (
                    baseline["false_positives"] - stack["false_positives"]
                ),
                "rate_points": (
                    baseline["false_positive_rate"]
                    - stack["false_positive_rate"]
                ),
            },
        },
        "duration_ms": round((time.perf_counter() - started) * 1000, 3),
        "boundary": (
            "Deterministic repository-local adversarial completion-semantics "
            "evaluation. The baseline is a synthetic baseline that trusts a "
            "completion claim, not an empirical single-agent benchmark. "
            "Receipt evidence references exercise control-plane semantics but "
            "do not establish provider authenticity; provider authenticity "
            "requires external provider execution and readback."
        ),
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
