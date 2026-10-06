import threading
import time

import pytest

from fde_powerhouse.gatling_estate import (
    SweepIncompleteError,
    aggregate_capability_nodes,
    benchmark_serial_vs_parallel,
    graph_semantic_digest,
    resume_repositories,
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


def test_partial_failure_preserves_successes_and_builds_resumable_checkpoint():
    def inspect(repo: str):
        if repo == "repo-b":
            raise TimeoutError("provider timed out")
        return [node(repo)]

    result = run_bounded_sweep(
        ["repo-a", "repo-b", "repo-c"],
        inspect,
        workers=2,
        strict=False,
    )

    assert result["health_class"] == "PARTIAL_FAILURE"
    assert result["performance_valid"] is False
    assert [item["repository"] for item in result["nodes"]] == ["repo-a", "repo-c"]
    assert result["failures"] == [
        {
            "repository": "repo-b",
            "attempts": 1,
            "error_type": "TimeoutError",
            "error": "provider timed out",
        }
    ]
    assert result["checkpoint"]["completed_repositories"] == ["repo-a", "repo-c"]
    assert resume_repositories(
        ["repo-a", "repo-b", "repo-c"],
        result["checkpoint"],
    ) == ["repo-b"]


def test_strict_failure_raises_with_partial_result_instead_of_erasing_progress():
    def inspect(repo: str):
        if repo == "repo-b":
            raise RuntimeError("boom")
        return [node(repo)]

    with pytest.raises(SweepIncompleteError) as caught:
        run_bounded_sweep(["repo-a", "repo-b", "repo-c"], inspect, workers=3)

    result = caught.value.result
    assert [item["repository"] for item in result["nodes"]] == ["repo-a", "repo-c"]
    assert result["checkpoint"]["failed_repositories"] == ["repo-b"]


def test_transient_worker_failure_retries_and_recovers_without_duplicate_findings():
    attempts = {"repo-a": 0, "repo-b": 0}

    def inspect(repo: str):
        attempts[repo] += 1
        if repo == "repo-b" and attempts[repo] == 1:
            raise ConnectionError("transient")
        return [node(repo)]

    result = run_bounded_sweep(
        ["repo-a", "repo-b"],
        inspect,
        workers=2,
        retries=1,
    )

    assert result["health_class"] == "HEALTHY"
    assert result["performance_valid"] is True
    assert result["failures"] == []
    assert result["metrics"]["retry_attempts"] == 1
    assert attempts == {"repo-a": 1, "repo-b": 2}
    assert result["metrics"]["duplicate_findings"] == 0


def test_resume_rejects_scope_drift_and_checkpoint_tampering():
    result = run_bounded_sweep(["repo-a"], lambda repo: [node(repo)], workers=1)
    checkpoint = result["checkpoint"]

    with pytest.raises(ValueError, match="scope"):
        resume_repositories(["repo-a", "repo-b"], checkpoint)

    tampered = dict(checkpoint)
    tampered["completed_repositories"] = []
    with pytest.raises(ValueError, match="checkpoint"):
        resume_repositories(["repo-a"], tampered)


def test_duplicate_repository_inputs_are_inspected_once():
    calls = []

    def inspect(repo: str):
        calls.append(repo)
        return [node(repo)]

    result = run_bounded_sweep(
        ["repo-a", "repo-a", " repo-b ", "repo-b"],
        inspect,
        workers=4,
    )

    assert calls.count("repo-a") == 1
    assert calls.count("repo-b") == 1
    assert result["metrics"]["repos_inspected"] == 2
    assert result["checkpoint"]["scope_repositories"] == ["repo-a", "repo-b"]


def test_matched_serial_parallel_benchmark_requires_healthy_identical_semantics():
    def inspect(repo: str):
        time.sleep(0.01)
        return [node(repo)]

    result = benchmark_serial_vs_parallel(
        ["repo-a", "repo-b", "repo-c"],
        inspect,
        parallel_workers=3,
    )

    assert result["health_class"] == "HEALTHY"
    assert result["performance_valid"] is True
    assert result["deterministic_result_match"] is True
    assert result["serial"]["workers"] == 1
    assert result["parallel"]["workers"] == 3
    assert result["speedup"] is not None


def test_matched_benchmark_rejects_semantic_drift_between_serial_and_parallel_runs():
    calls = 0
    lock = threading.Lock()

    def inspect(repo: str):
        nonlocal calls
        with lock:
            calls += 1
            phase = "serial" if calls <= 2 else "parallel"
        item = node(repo)
        item["verified_state"] = phase
        return [item]

    result = benchmark_serial_vs_parallel(
        ["repo-a", "repo-b"],
        inspect,
        parallel_workers=2,
    )

    assert result["health_class"] == "INVALID"
    assert result["performance_valid"] is False
    assert result["deterministic_result_match"] is False
    assert result["speedup"] is None


def test_evidence_digest_must_be_sha256():
    item = node("repo-evidence")
    item["evidence_level"] = "source_inspected"
    item["evidence"] = [
        {
            "kind": "implementation",
            "revision": "a" * 40,
            "path": "src/core.py",
            "claim": "implementation recovered",
            "digest": "not-a-sha256",
        }
    ]

    with pytest.raises(ValueError, match="evidence digest"):
        aggregate_capability_nodes([item])


def test_type_contracts_fail_with_type_error_not_value_error():
    with pytest.raises(TypeError, match="repositories"):
        run_bounded_sweep("repo-a", lambda repo: [node(repo)])

    invalid = node("repo-a")
    invalid["tests"] = "tests/test_core.py"
    with pytest.raises(TypeError, match="tests"):
        aggregate_capability_nodes([invalid])


def test_graph_semantic_digest_is_order_independent_for_nodes_edges_and_scope():
    edge_a = {
        "source": "repo-a",
        "target": "repo-b",
        "relation": "DEPENDS_ON",
        "evidence": [
            {
                "repository": "repo-a",
                "revision": "a" * 40,
                "path": "README.md",
                "blob_sha": "1" * 40,
                "line_start": 10,
                "line_end": 12,
                "claim": "repo-a depends on repo-b",
            }
        ],
    }
    edge_b = {
        "source": "repo-b",
        "target": "repo-a",
        "relation": "DONOR_TO",
        "evidence": [
            {
                "repository": "repo-b",
                "revision": "b" * 40,
                "path": "README.md",
                "blob_sha": "2" * 40,
                "line_start": None,
                "line_end": None,
                "claim": "repo-b contributes a donor pattern",
            }
        ],
    }
    left = {
        "nodes": [node("repo-b"), node("repo-a")],
        "edges": [edge_b, edge_a],
        "mission_critical_subgraph": {"repositories": ["repo-b", "repo-a"]},
        "verification": {"wall_clock_ms": 999},
    }
    right = {
        "nodes": [node("repo-a"), node("repo-b")],
        "edges": [edge_a, edge_b],
        "mission_critical_subgraph": {"repositories": ["repo-a", "repo-b"]},
        "verification": {"wall_clock_ms": 1},
    }

    assert graph_semantic_digest(left) == graph_semantic_digest(right)
    assert graph_semantic_digest(left).startswith("sha256:")


def test_graph_semantic_digest_changes_when_typed_edge_changes():
    base = {
        "nodes": [node("repo-a"), node("repo-b")],
        "edges": [
            {
                "source": "repo-a",
                "target": "repo-b",
                "relation": "DEPENDS_ON",
                "evidence": [
                    {
                        "repository": "repo-a",
                        "revision": "a" * 40,
                        "path": "README.md",
                        "blob_sha": "1" * 40,
                        "line_start": 10,
                        "line_end": 12,
                        "claim": "repo-a depends on repo-b",
                    }
                ],
            }
        ],
        "mission_critical_subgraph": {"repositories": ["repo-a", "repo-b"]},
    }
    changed = {
        **base,
        "edges": [{**base["edges"][0], "relation": "COMPOSES_WITH"}],
    }

    assert graph_semantic_digest(base) != graph_semantic_digest(changed)
