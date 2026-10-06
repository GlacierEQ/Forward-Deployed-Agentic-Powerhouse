from __future__ import annotations

from pathlib import Path

import pytest

from fde_powerhouse.scale_control_plane import ScaleControlPlane
from fde_powerhouse.scale_evaluation import run_evaluation


def _verified_receipt(*outputs: str) -> dict[str, object]:
    return {
        "revision": "abc123",
        "tests": ["pytest"],
        "outputs": list(outputs),
        "readback": {
            "state": "verified",
            "source": "provider://test/readback/abc123",
        },
    }


def _complete_all_workstreams(cp: ScaleControlPlane) -> None:
    for worker in "ABCDE":
        task = f"task-{worker}"
        output = f"WORKSTREAM_{worker}.json"
        cp.enqueue(worker, task, outputs=[output])
        cp.claim(worker, task)
        cp.complete(worker, task, receipt=_verified_receipt(output))


def test_completion_rejects_receipt_without_provider_readback(tmp_path: Path) -> None:
    cp = ScaleControlPlane.bootstrap(tmp_path)
    cp.enqueue("E", "verify", outputs=["VERIFICATION_RECEIPT.json"])
    cp.claim("E", "verify")

    with pytest.raises(ValueError, match="readback"):
        cp.complete(
            "E",
            "verify",
            receipt={
                "revision": "abc123",
                "tests": ["pytest"],
                "outputs": ["VERIFICATION_RECEIPT.json"],
            },
        )


def test_completion_rejects_receipt_without_all_declared_output_proofs(tmp_path: Path) -> None:
    cp = ScaleControlPlane.bootstrap(tmp_path)
    cp.enqueue("E", "verify", outputs=["VERIFICATION_RECEIPT.json"])
    cp.claim("E", "verify")

    with pytest.raises(ValueError, match="outputs"):
        cp.complete(
            "E",
            "verify",
            receipt={
                "revision": "abc123",
                "tests": ["pytest"],
                "outputs": [],
                "readback": {
                    "state": "verified",
                    "source": "provider://test/readback/abc123",
                },
            },
        )


def test_pending_integration_blocks_mission_verification(tmp_path: Path) -> None:
    cp = ScaleControlPlane.bootstrap(tmp_path)
    _complete_all_workstreams(cp)

    cp.queue_integration("D", "provider-mutation", "receipt-D")
    state = cp.snapshot()

    assert state["mission"]["frontier_exhausted"] is False
    assert state["mission"]["status"] == "active"


def test_unresolved_defect_blocks_mission_verification(tmp_path: Path) -> None:
    cp = ScaleControlPlane.bootstrap(tmp_path)
    _complete_all_workstreams(cp)

    cp.add_defect(
        "E",
        "task-E",
        {
            "id": "DEF-REDUCTION-001",
            "summary": "receipt accepted without independent evidence",
        },
    )
    state = cp.snapshot()

    assert state["mission"]["frontier_exhausted"] is False
    assert state["mission"]["status"] == "active"


def test_evaluation_is_adversarial_and_reports_full_confusion_matrix() -> None:
    result = run_evaluation()

    assert result["schema"] == "glaciereq.scale-fde-evaluation.v2"
    assert result["evaluation"] == "naive_completion_claim_baseline_vs_evidence_bound_control_plane"
    assert result["scenario_count"] >= 8
    assert result["metrics"]["baseline"]["false_positives"] > 0
    assert result["metrics"]["stack"]["false_positives"] == 0
    assert result["metrics"]["stack"]["false_negatives"] == 0
    assert result["metrics"]["stack"]["true_positives"] > 0
    assert result["metrics"]["stack"]["true_negatives"] > 0
    assert "synthetic baseline" in result["boundary"].lower()
    assert "provider authenticity" in result["boundary"].lower()
