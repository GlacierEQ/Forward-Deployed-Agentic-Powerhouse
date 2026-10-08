"""Scale FDE: evidence promotion prerequisites may not freeze executable work."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "shared"


def _load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_all_active_round3_workstreams_can_engineer_before_receipt_promotion():
    queue = _load("INTEGRATION_QUEUE.json")
    entries = {item["id"]: item for item in queue["entries"]}
    for entry_id in ("R3-B-001", "R3-D-001", "R3-E-001", "R3-C-001", "R3-E-002"):
        item = entries[entry_id]
        assert item["payload"]["engineering_allowed"] is True
        assert item["payload"]["next_executable_actions"]
        assert "promotion" in item["payload"]["blocked_scope"].lower() or (
            item["payload"]["blocked_scope"].startswith("None;")
        )
    assert "not implementation" in queue["dependency_semantics"] or (
        "not implementation" in queue["dependency_semantics"].lower()
    )


def test_preterminal_capability_handoff_precedes_final_mission_receipt():
    queue = _load("INTEGRATION_QUEUE.json")
    entries = {item["id"]: item for item in queue["entries"]}
    assert entries["R3-E-001"]["payload"]["promotion_waits_on"] == [
        "R3-B-001", "R3-D-001"
    ]
    assert entries["R3-C-001"]["payload"]["promotion_waits_on"] == [
        "R3-E-001:MISSION1_CAPABILITY_RECEIPT.json"
    ]
    assert entries["R3-E-002"]["payload"]["promotion_waits_on"] == [
        "R3-C-001"
    ]
    assert "MISSION1_CAPABILITY_RECEIPT.json" in (
        entries["R3-E-001"]["payload"]["completion_artifacts"]
    )
    assert "MISSION_RECEIPT.json" not in (
        entries["R3-E-001"]["payload"]["completion_artifacts"]
    )
    assert "MISSION_RECEIPT.json" in (
        entries["R3-E-002"]["payload"]["completion_artifacts"]
    )


def test_preterminal_contract_requires_real_evidence_and_preserves_colossus():
    contract = _load("MISSION1_CAPABILITY_CONTRACT.json")
    architecture = _load("ARCHITECTURE_CONTRACT.json")
    assert contract["producer"] == "E"
    assert contract["consumer"] == "C"
    assert contract["terminal_mission_certification"] is False
    assert contract["provider_native_readback_required"] is True
    assert contract["upstream_sources_required"] == ["B", "D"]
    assert any("Colossus" in item for item in architecture["invariants"])


def test_unresolved_receipts_are_not_promoted_by_control_contract_change():
    index = _load("RECEIPT_INDEX.json")
    unresolved = set(index["unresolved"])
    assert "shared/MISSION1_CAPABILITY_RECEIPT.json" in unresolved
    assert "MISSION_RECEIPT.json" in unresolved
    assert all(
        entry.get("state") != "CERTIFIED"
        for entry in index.get("source_bound", [])
    )
