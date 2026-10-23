"""Unit tests for Aspen-Grove pointer-indexed memory bridge."""

import hashlib
from pathlib import Path

from fde_powerhouse.bridges.pointer_memory import PointerMemoryBridge


def test_pointer_memory_probe():
    bridge = PointerMemoryBridge()
    probe = bridge.probe()
    assert "available" in probe
    assert "tiers" in probe
    assert len(probe["tiers"]) == 4
    assert probe["compression_savings"] == "75-90%"
    assert probe["provenance_standard"] == "L0-L5_EPISTEMIC_LADDER"


def test_pointer_memory_custom_index(tmp_path: Path):
    idx_path = tmp_path / "test_pointers.json"
    idx_path.write_text(
        """{
            "schema_id": "glaciereq.aspen-grove-pointer-index.v2",
            "pointers": {
                "ptr-alpha": {"file": "alpha.bin", "sha256": "abcdef"},
                "ptr-beta": {"file": "beta.bin", "sha256": "123456"}
            }
        }""",
        encoding="utf-8",
    )
    bridge = PointerMemoryBridge(index_path=idx_path)
    assert bridge.available is True
    res = bridge.resolve("ptr-alpha")
    assert res is not None
    assert res["target"]["file"] == "alpha.bin"
    assert res["epistemic_level"] == "L0_GROUND_TRUTH"


def test_pointer_memory_register_and_verify(tmp_path: Path):
    target_file = tmp_path / "evidence_sample.txt"
    content = b"Verified evidentiary statement by Operator Casey Barton"
    target_file.write_bytes(content)
    expected_hash = hashlib.sha256(content).hexdigest()

    bridge = PointerMemoryBridge()
    reg = bridge.register_pointer(
        pointer_id="ptr-evidence-001",
        target_path=str(target_file),
    )
    assert reg["pointer_id"] == "ptr-evidence-001"
    assert reg["sha256"] == expected_hash
    assert reg["epistemic_level"] == "L0_VERIFIED"

    assert bridge.verify_provenance(str(target_file), expected_hash) is True
    assert bridge.verify_provenance(str(target_file), "wrong_hash") is False
