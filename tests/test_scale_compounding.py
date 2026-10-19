"""Workstream C integration contract tests: RED before implementation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import ClassVar

import pytest

from fde_powerhouse.scale_compounding import (
    prepare_canonical_frontier,
    run_compounding_proof,
)


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


def _write_canonical_shared_snapshot(root: Path, *, e_mission_id: str = "SCALE-FDE-DEMO-001"):
    root.mkdir(parents=True, exist_ok=True)
    (root / "SCALE_FDE_MISSION.yaml").write_text(
        "schema: glaciereq.scale-fde-mission.v1\n"
        "id: SCALE-FDE-DEMO-001\n"
        "revision: 2\n"
        "objective: Prove the real desired state and compound verified capability reuse.\n",
        encoding="utf-8",
    )
    (root / "SCALE_CAPABILITY_GRAPH.json").write_text(
        json.dumps(
            {
                "schema": "glaciereq.scale-fde.capability-graph.v1",
                "mission": "Scale FDE demonstration",
                "workstream": "A",
                "nodes": [
                    {"repository": "GlacierEQ/aspen-grove-memory", "donor_value": 10},
                    {"repository": "GlacierEQ/Genius-Mastery", "donor_value": 10},
                ],
            }
        ),
        encoding="utf-8",
    )
    (root / "WORKSTREAM_E.json").write_text(
        json.dumps(
            {
                "schema": "glaciereq.scale-fde-workstream.v1",
                "mission_id": e_mission_id,
                "workstream": "E",
                "status": "PARTIAL",
                "unresolved_dependencies": ["MISSION_RECEIPT.json is not source-bound"],
            }
        ),
        encoding="utf-8",
    )
    (root / "RECEIPT_INDEX.json").write_text(
        json.dumps(
            {
                "schema": "glaciereq.scale-fde-receipt-index.v1",
                "mission_id": "SCALE-FDE-DEMO-001",
                "unresolved": ["MISSION_RECEIPT.json", "MISSION1_CAPABILITY_RECEIPT.json", "Mission 2 automatic reuse proof"],
            }
        ),
        encoding="utf-8",
    )


def test_canonical_frontier_prepares_with_missing_preterminal_capability_receipt(tmp_path):
    FakeContinuityStore.records.clear()
    shared = tmp_path / "shared"
    db = tmp_path / "continuity.sqlite3"
    registry = tmp_path / "learned-capabilities.json"
    _write_canonical_shared_snapshot(shared)

    result = prepare_canonical_frontier(
        shared_root=shared,
        db_path=db,
        registry_path=registry,
        continuity_cls=FakeContinuityStore,
    )

    assert result["status"] == "preparing_awaiting_verified_capability"
    assert result["mission_id"] == "SCALE-FDE-DEMO-001"
    assert result["capability_receipt"]["present"] is False
    assert result["capability_registry_mutated"] is False
    assert not registry.exists()
    assert result["continuation"]["current_frontier"] == [
        "await:shared/MISSION1_CAPABILITY_RECEIPT.json"
    ]
    assert "MISSION1_CAPABILITY_RECEIPT.json" in result["continuation"]["unresolved_dependencies"][0]
    assert result["continuation"]["engineering_ready"] is True
    assert set(result["source_snapshot"]) == {
        "SCALE_FDE_MISSION.yaml",
        "SCALE_CAPABILITY_GRAPH.json",
        "WORKSTREAM_E.json",
        "RECEIPT_INDEX.json",
    }
    assert all(item["sha256"] for item in result["source_snapshot"].values())

    records = FakeContinuityStore.records[str(db)]
    continuation = [payload for kind, payload in records if kind == "continuation"]
    assert continuation
    assert continuation[-1]["frontier"] == ["await:shared/MISSION1_CAPABILITY_RECEIPT.json"]


def test_canonical_frontier_rejects_cross_mission_shared_artifacts(tmp_path):
    FakeContinuityStore.records.clear()
    shared = tmp_path / "shared"
    _write_canonical_shared_snapshot(shared, e_mission_id="OTHER-MISSION")

    with pytest.raises(ValueError, match="mission_id"):
        prepare_canonical_frontier(
            shared_root=shared,
            db_path=tmp_path / "continuity.sqlite3",
            registry_path=tmp_path / "learned-capabilities.json",
            continuity_cls=FakeContinuityStore,
        )


def _preterminal_capability_receipt(shared: Path) -> dict:
    mission_digest = hashlib.sha256((shared / "SCALE_FDE_MISSION.yaml").read_bytes()).hexdigest()
    return {
        "mission_id": "SCALE-FDE-DEMO-001",
        "verification_status": "verified",
        "mission_contract_sha256": mission_digest,
        "verifier_id": "independent-E",
        "executor_id": "runtime-B",
        "source_revision": "a" * 40,
        "receipt_refs": ["github://GlacierEQ/computer-user@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"],
        "upstream_receipt_hashes": {"B": "b" * 64, "D": "d" * 64},
        "provider_readback": {
            "state": "verified",
            "verification_method": "provider_native_readback",
            "source_ref": "github://GlacierEQ/sigma-glue@dddddddddddddddddddddddddddddddddddddddd",
        },
        "reusable_capability": {
            "id": "cap.provider-readback-reconcile",
            "description": "Provider readback and reconciliation",
            "tags": ["provider", "readback"],
            "input_contract": {"requires": ["provider identity"]},
            "output_contract": {"emits": ["reconciliation decision"]},
        },
    }


def test_canonical_frontier_prepares_valid_preterminal_receipt_without_claiming_completion(tmp_path):
    FakeContinuityStore.records.clear()
    shared = tmp_path / "shared"
    _write_canonical_shared_snapshot(shared)
    receipt = _preterminal_capability_receipt(shared)
    (shared / "MISSION1_CAPABILITY_RECEIPT.json").write_text(json.dumps(receipt))
    registry = tmp_path / "registry.json"
    result = prepare_canonical_frontier(
        shared_root=shared,
        db_path=tmp_path / "continuity.sqlite3",
        registry_path=registry,
        continuity_cls=FakeContinuityStore,
    )
    assert result["status"] == "ready_for_external_provenance_confirmation"
    assert result["capability_receipt"]["present"] is True
    assert result["capability_receipt"]["reusable_capability_id"] == "cap.provider-readback-reconcile"
    assert result["capability_registry_mutated"] is False
    assert not registry.exists()


@pytest.mark.parametrize("field,value", [
    ("mission_id", "WRONG-MISSION"),
    ("verification_status", "executed"),
    ("mission_contract_sha256", "0" * 64),
    ("source_revision", "not-a-git-revision"),
    ("verifier_id", "runtime-B"),
    ("receipt_refs", []),
    ("upstream_receipt_hashes", {}),
    ("reusable_capability", {}),
    ("provider_readback", {}),
])
def test_canonical_frontier_rejects_invalid_preterminal_capability(tmp_path, field, value):
    FakeContinuityStore.records.clear()
    shared = tmp_path / "shared"
    _write_canonical_shared_snapshot(shared)
    receipt = _preterminal_capability_receipt(shared)
    receipt[field] = value
    (shared / "MISSION1_CAPABILITY_RECEIPT.json").write_text(json.dumps(receipt))
    registry = tmp_path / "registry.json"
    with pytest.raises((ValueError, TypeError), match="capability|receipt|mission|verifier|readback|revision|contract"):
        prepare_canonical_frontier(
            shared_root=shared,
            db_path=tmp_path / "continuity.sqlite3",
            registry_path=registry,
            continuity_cls=FakeContinuityStore,
        )
    assert not registry.exists()
