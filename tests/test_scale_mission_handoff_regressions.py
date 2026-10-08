"""Regression tests for Scale FDE evidence handoffs and anti-freeze controls.

Checks the actual checked-in canonical contracts; a successful local workstream
is not a certified mission, and Mission 2 must not depend on final certification.
"""
from __future__ import annotations

import json
from pathlib import Path

from fde_powerhouse.scale_control_plane import ScaleControlPlane

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "shared"


def _load(name: str) -> dict:
    return json.loads((SHARED / name).read_text(encoding="utf-8"))


def test_mission1_preterminal_handoff_breaks_circular_dependency():
    entries = {item["id"]: item for item in _load("INTEGRATION_QUEUE.json")["entries"]}
    e_first = entries["R3-E-001"]
    c = entries["R3-C-001"]
    e_final = entries["R3-E-002"]

    assert e_first["payload"]["waits_on"] == ["R3-B-001", "R3-D-001"]
    assert "MISSION1_CAPABILITY_RECEIPT.json" in e_first["payload"]["completion_artifacts"]
    assert "MISSION_RECEIPT.json" not in e_first["payload"]["completion_artifacts"]
    assert c["payload"]["waits_on"] == ["R3-E-001:MISSION1_CAPABILITY_RECEIPT.json"]
    assert e_final["payload"]["waits_on"] == ["R3-C-001"]
    assert "MISSION_RECEIPT.json" in e_final["payload"]["completion_artifacts"]

    # Check the complete active dependency graph, not just the expected edges.
    graph = {}
    for item in (e_first, c, e_final):
        graph[item["id"]] = [
            ref.split(":", 1)[0] for ref in item["payload"].get("waits_on", [])
        ]
    graph["R3-B-001"] = []
    graph["R3-D-001"] = []
    visiting, visited = set(), set()

    def walk(node: str) -> None:
        assert node not in visiting, f"dependency cycle through {node}"
        if node in visited:
            return
        assert node in graph, f"unresolved dependency {node}"
        visiting.add(node)
        for dependency in graph[node]:
            walk(dependency)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        walk(node)


def test_preterminal_contract_requires_independent_source_bound_capability():
    contract = _load("MISSION1_CAPABILITY_CONTRACT.json")
    assert contract["mission_id"] == "SCALE-FDE-DEMO-001"
    assert contract["producer"] == "E"
    assert contract["consumer"] == "C"
    assert contract["artifact"] == "shared/MISSION1_CAPABILITY_RECEIPT.json"
    required = set(contract["required_fields"])
    assert {"mission_id", "verification_status", "reusable_capability",
            "source_revision", "receipt_refs", "verifier_id",
            "mission_contract_sha256", "upstream_receipt_hashes"} <= required
    assert contract["allowed_verification_status"] == ["verified"]
    assert contract["terminal_mission_certification"] is False
    assert contract["upstream_sources_required"] == ["B", "D"]
    assert contract["provider_native_readback_required"] is True


def test_final_certification_remains_independent_and_post_reuse():
    architecture = _load("ARCHITECTURE_CONTRACT.json")
    assert architecture["workstreams"]["E"]["authority"] == "independent_verification"
    assert architecture["workstreams"]["D"]["authority"] == "external_mutation_only_from_B_intent"
    assert "Mission1CapabilityVerification" in architecture["typed_handoffs"]
    assert "Mission2ReuseReceipt" in architecture["typed_handoffs"]
    assert any("Colossus" in item for item in architecture["invariants"])
    assert any("pre-terminal" in item for item in architecture["invariants"])


def test_receipt_index_does_not_equate_contract_with_success():
    index = _load("RECEIPT_INDEX.json")
    assert "shared/MISSION1_CAPABILITY_RECEIPT.json" in index["unresolved"]
    assert "MISSION_RECEIPT.json" in index["unresolved"]
    assert not any(
        entry.get("id") == "MISSION1_CAPABILITY_RECEIPT" and
        entry.get("state") in {"VERIFIED", "GREEN", "CERTIFIED"}
        for entry in index["source_bound"]
    )


def test_runtime_local_workstream_counters_cannot_certify_full_mission(tmp_path):
    cp = ScaleControlPlane.bootstrap(tmp_path)
    for worker in "ABCDE":
        output = f"WORKSTREAM_{worker}.json"
        cp.enqueue(worker, f"task-{worker}", outputs=[output])
        cp.claim(worker, f"task-{worker}")
        cp.complete(worker, f"task-{worker}", receipt={
            "revision": f"test-{worker}",
            "tests": [{"state": "passed", "source": f"test://{worker}"}],
            "outputs": [{"path": output, "state": "verified",
                         "source": f"test://artifact/{worker}"}],
            "readback": {"state": "verified", "source": f"test://readback/{worker}"},
        })
    mission = cp.snapshot()["mission"]
    assert mission["verification_gates"]["all_workstreams_verified"] is True
    assert mission["status"] != "verified"
    assert mission["frontier_exhausted"] is False
    assert mission["workstream_frontier_exhausted"] is True


def test_unverified_evidence_never_freezes_parallel_engineering():
    """Only evidence promotion waits on predecessors; independent work proceeds."""
    queue = _load("INTEGRATION_QUEUE.json")
    entries = {entry["id"]: entry for entry in queue["entries"]}
    for worker in ("R3-B-001", "R3-D-001"):
        entry = entries[worker]
        assert entry["status"] == "dispatched"
        assert entry["payload"]["engineering_allowed"] is True
    for work_id, expected_dependency in (
        ("R3-E-001", ["R3-B-001", "R3-D-001"]),
        ("R3-C-001", ["R3-E-001:MISSION1_CAPABILITY_RECEIPT.json"]),
    ):
        entry = entries[work_id]
        assert entry["payload"]["engineering_allowed"] is True
        assert entry["payload"]["promotion_waits_on"] == expected_dependency
        assert entry["payload"]["next_executable_actions"]
        assert not any("no action" in action.lower() for action in entry["payload"]["next_executable_actions"])
    assert entries["R3-E-002"]["payload"]["promotion_waits_on"] == ["R3-C-001"]


def test_unverified_terminal_evidence_does_not_block_runtime_work(tmp_path):
    """An absent final E certificate must not disable normal task transitions."""
    cp = ScaleControlPlane.bootstrap(tmp_path)
    for worker in ("B", "D", "E", "C"):
        cp.enqueue(worker, "engineering", outputs=[f"WORKSTREAM_{worker}.json"])
        cp.claim(worker, "engineering")
    snapshot = cp.snapshot()
    assert all(
        snapshot["workstreams"][worker]["tasks"]["engineering"]["status"] == "running"
        for worker in ("B", "D", "E", "C")
    )
    assert snapshot["mission"]["status"] == "active"
    assert snapshot["mission"]["frontier_exhausted"] is False
