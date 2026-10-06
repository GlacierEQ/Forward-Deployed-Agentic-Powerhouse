import threading
import time

import pytest

from fde_powerhouse.gatling_estate import (
    aggregate_capability_nodes,
    run_bounded_sweep,
    semantic_digest,
)


def node(repo: str, capability: str = "cap") -> dict:
    return {
        "repository": repo,
        "revision": "a" * 40,
        "capability": capability,
        "implementation_paths": ["src/core.py"],
        "tests": ["tests/test_core.py"],
        "receipts": [],
        "dependencies": [],
        "maturity": "working",
        "verified_state": "code and tests recovered",
        "scale_relevance": ["discovery"],
        "known_defects": [],
        "donor_value": 7,
    }


def test_bounded_sweep_is_parallel_bounded_and_deterministic():
    lock = threading.Lock()
    active = 0
    max_active = 0

    def inspect(repo: str):
        nonlocal active, max_active
        with lock:
            active += 1
            max_active = max(max_active, active)
        time.sleep(0.02)
        with lock:
            active -= 1
        rows = [node(repo)]
        if repo == "repo-2":
            rows.append(node(repo))
        return rows

    result = run_bounded_sweep([f"repo-{i}" for i in range(8)], inspect, workers=3)

    assert 1 < max_active <= 3
    assert result["metrics"]["workers"] == 3
    assert result["metrics"]["repos_inspected"] == 8
    assert result["metrics"]["duplicate_findings"] == 1
    assert result["metrics"]["relevant_capabilities_recovered"] == 8
    assert [n["repository"] for n in result["nodes"]] == [f"repo-{i}" for i in range(8)]


def test_aggregator_rejects_conflicting_duplicate_identity():
    left = node("repo-a")
    right = node("repo-a")
    right["verified_state"] = "different claim"

    with pytest.raises(ValueError, match="conflicting capability node"):
        aggregate_capability_nodes([left, right])


def test_aggregator_rejects_invalid_donor_value():
    bad = node("repo-a")
    bad["donor_value"] = 11

    with pytest.raises(ValueError, match="donor_value"):
        aggregate_capability_nodes([bad])


def test_aggregator_preserves_and_validates_evidence_provenance():
    item = node("repo-evidence")
    item["evidence_level"] = "source_inspected"
    item["evidence"] = [
        {
            "kind": "implementation",
            "revision": "a" * 40,
            "path": "src/core.py",
            "claim": "bounded discovery implementation recovered",
            "digest": "sha256:" + "b" * 64,
        }
    ]

    result = aggregate_capability_nodes([item])
    recovered = result["nodes"][0]

    assert recovered["evidence_level"] == "source_inspected"
    assert recovered["evidence"] == item["evidence"]

    invalid = dict(item)
    invalid["evidence_level"] = "confidence_guess"
    with pytest.raises(ValueError, match="evidence_level"):
        aggregate_capability_nodes([invalid])


def test_semantic_digest_is_order_independent_and_ignores_metrics():
    left = run_bounded_sweep(["repo-b", "repo-a"], lambda repo: [node(repo)], workers=1)
    right = run_bounded_sweep(["repo-a", "repo-b"], lambda repo: [node(repo)], workers=2)

    assert semantic_digest(left) == semantic_digest(right)
    assert semantic_digest(left).startswith("sha256:")


def test_semantic_digest_changes_when_capability_evidence_changes():
    first = node("repo-a")
    second = node("repo-a")
    second["verified_state"] = "stronger source evidence recovered"

    assert semantic_digest({"nodes": [first]}) != semantic_digest({"nodes": [second]})
