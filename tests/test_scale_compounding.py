"""Workstream C integration contract tests: RED before implementation."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import ClassVar

import pytest
from fde_powerhouse.scale_compounding import run_compounding_proof


class FakeContinuityStore:
    records: ClassVar[dict[str, list[tuple[str, dict]]]] = {}

    def __init__(self, db_path: str | Path):
        self.key = str(db_path)
        self.records.setdefault(self.key, [])

    def close(self) -> None:
        return None

    def record_mission(self, mission_id: str, **payload):
        self.records[self.key].append(("mission", {"mission_id": mission_id, **payload}))

    def record_decision(self, mission_id: str, **payload):
        self.records[self.key].append(("decision", {"mission_id": mission_id, **payload}))

    def record_execution(self, mission_id: str, **payload):
        self.records[self.key].append(("execution", {"mission_id": mission_id, **payload}))

    def record_receipt(self, mission_id: str, **payload):
        self.records[self.key].append(("receipt", {"mission_id": mission_id, **payload}))

    def record_capability(self, mission_id: str, **payload):
        self.records[self.key].append(("capability", {"mission_id": mission_id, **payload}))

    def record_continuation(self, mission_id: str, **payload):
        self.records[self.key].append(("continuation", {"mission_id": mission_id, **payload}))


def _compounding_api():
    def extract(receipt):
        if receipt["verification_status"] != "verified":
            raise ValueError("verified mission required")
        reusable = receipt["reusable_capability"]
        return {
            **reusable,
            "stage": "verified",
            "source_mission_id": receipt["mission_id"],
            "source_revision": receipt["source_revision"],
            "evidence_refs": list(receipt["receipt_refs"]),
        }

    def register(path, capability):
        data = {"schema_version": 1, "capabilities": [capability]}
        Path(path).write_text(json.dumps(data), encoding="utf-8")
        return {"path": str(path), "capability_count": 1, "sha256": "fixture-registry"}

    def select(mission, capabilities, minimum_score=0.35):
        capability = next(iter(capabilities))
        return {
            "mission_id": mission["mission_id"],
            "minimum_score": minimum_score,
            "selected": {
                "capability": capability,
                "score": 0.91,
                "matched_terms": ["provider", "readback"],
            },
            "ranked": [],
        }

    return SimpleNamespace(
        extract_reusable_capability=extract,
        register_capability=register,
        select_reusable_capability=select,
    )


def _mission1():
    return {
        "mission_id": "mission-1",
        "objective": "Recover from ambiguous provider mutation",
        "verification_status": "verified",
        "source_revision": "m1-verified-sha",
        "receipt_refs": ["receipt://mission-1/verified"],
        "reusable_capability": {
            "id": "cap.provider-readback-reconcile",
            "description": "Provider readback reconciliation",
            "tags": ["provider", "readback", "reconciliation"],
            "input_contract": {"requires": ["provider identity"]},
            "output_contract": {"emits": ["confirmed applied", "confirmed absent", "unknown"]},
        },
    }


def _mission2():
    return {
        "mission_id": "mission-2",
        "objective": "Safely reconcile an ambiguous provider mutation with readback",
        "requirements": ["provider", "readback"],
    }


def test_verified_mission_is_compounded_and_mission2_auto_reuses_it(tmp_path):
    recovery = {
        "mission_id": "mission-1",
        "objective": "Recover from ambiguous provider mutation",
        "decisions": [{"decision_id": "extract-reusable-capability"}],
        "completed_tasks": [{"execution_id": "mission-1-verified"}],
        "receipts": [{"receipt_id": "mission-1-verification"}],
        "capabilities": [{"capability_id": "cap.provider-readback-reconcile"}],
        "unresolved_dependencies": [],
        "current_frontier": ["mission-2"],
    }

    proof = run_compounding_proof(
        mission1_receipt=_mission1(),
        mission2=_mission2(),
        db_path=tmp_path / "continuity.sqlite3",
        registry_path=tmp_path / "learned-capabilities.json",
        continuity_cls=FakeContinuityStore,
        compounding_api=_compounding_api(),
        fresh_hydrator=lambda *_args, **_kwargs: recovery,
    )

    assert proof["mission1"]["extracted_capability_id"] == "cap.provider-readback-reconcile"
    assert proof["resurrection"]["objective"] == recovery["objective"]
    assert proof["mission2"]["auto_reused_capability_id"] == "cap.provider-readback-reconcile"
    assert proof["mission2"]["selection_score"] == pytest.approx(0.91)
    assert proof["mission2"]["automatic_reuse"] is True
    assert "raw transcript" in proof["truth_boundary"].lower()


def test_unverified_mission_cannot_be_compounded(tmp_path):
    receipt = _mission1()
    receipt["verification_status"] = "executed"
    with pytest.raises(ValueError, match="verified mission"):
        run_compounding_proof(
            mission1_receipt=receipt,
            mission2=_mission2(),
            db_path=tmp_path / "continuity.sqlite3",
            registry_path=tmp_path / "learned-capabilities.json",
            continuity_cls=FakeContinuityStore,
            compounding_api=_compounding_api(),
            fresh_hydrator=lambda *_args, **_kwargs: {},
        )
