"""Bounded concurrent estate discovery with durable deterministic aggregation."""

from __future__ import annotations

import hashlib
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Iterable, Mapping, Sequence

MATURITY = {"prototype", "working", "hardened", "production"}
EVIDENCE_LEVELS = {
    "catalog_only",
    "source_inspected",
    "test_observed",
    "execution_observed",
    "provider_verified",
}
LIST_FIELDS = (
    "implementation_paths",
    "tests",
    "receipts",
    "dependencies",
    "scale_relevance",
    "known_defects",
)
REQUIRED_FIELDS = (
    "repository",
    "revision",
    "capability",
    *LIST_FIELDS,
    "maturity",
    "verified_state",
    "donor_value",
)
SWEEP_SCHEMA = "scale.capability-sweep/v2"
CHECKPOINT_SCHEMA = "scale.capability-sweep.checkpoint/v1"
BENCHMARK_SCHEMA = "scale.gatling-benchmark/v1"


class SweepIncompleteError(RuntimeError):
    """Strict sweep failure that retains the complete partial-result receipt."""

    def __init__(self, result: Mapping[str, Any]):
        self.result = dict(result)
        failed = len(self.result.get("failures") or [])
        super().__init__(f"capability sweep incomplete: {failed} repository failures")


def _json_digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _normalize_repositories(repositories: Sequence[str]) -> tuple[str, ...]:
    if isinstance(repositories, (str, bytes, bytearray)):
        raise ValueError("repositories must be an ordered collection of names")

    normalized: list[str] = []
    seen: set[str] = set()
    for raw in repositories:
        if not isinstance(raw, str):
            raise ValueError("repository names must be strings")
        repository = raw.strip()
        if not repository:
            raise ValueError("repository names cannot be empty")
        identity = repository.casefold()
        if identity in seen:
            continue
        seen.add(identity)
        normalized.append(repository)
    return tuple(normalized)


def repository_scope_digest(repositories: Sequence[str]) -> str:
    """Return an order-independent digest for the requested repository scope."""
    normalized = _normalize_repositories(repositories)
    canonical = sorted(normalized, key=lambda value: (value.casefold(), value))
    return _json_digest({"repositories": canonical})


def _normalize(node: Mapping[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in node]
    if missing:
        raise ValueError(
            "capability node missing required fields: " + ", ".join(missing)
        )

    maturity = node["maturity"]
    if maturity not in MATURITY:
        raise ValueError(f"invalid maturity: {maturity!r}")

    donor_value = node["donor_value"]
    if (
        isinstance(donor_value, bool)
        or not isinstance(donor_value, (int, float))
        or not 0 <= donor_value <= 10
    ):
        raise ValueError("donor_value must be a number in range 0..10")

    normalized = {
        "repository": str(node["repository"]),
        "revision": str(node["revision"]),
        "capability": str(node["capability"]),
    }
    for field in LIST_FIELDS:
        value = node[field]
        if not isinstance(value, Sequence) or isinstance(
            value, (str, bytes, bytearray)
        ):
            raise ValueError(f"{field} must be a list-like sequence")
        normalized[field] = sorted({str(item) for item in value})
    normalized["maturity"] = maturity
    normalized["verified_state"] = str(node["verified_state"])
    normalized["donor_value"] = donor_value

    if "evidence_level" in node:
        evidence_level = str(node["evidence_level"])
        if evidence_level not in EVIDENCE_LEVELS:
            raise ValueError(f"invalid evidence_level: {evidence_level!r}")
        normalized["evidence_level"] = evidence_level

    if "evidence" in node:
        evidence = node["evidence"]
        if not isinstance(evidence, Sequence) or isinstance(
            evidence, (str, bytes, bytearray)
        ):
            raise ValueError("evidence must be a list-like sequence")
        normalized_evidence: list[dict[str, str]] = []
        required_evidence = ("kind", "revision", "path", "claim", "digest")
        for record in evidence:
            if not isinstance(record, Mapping):
                raise ValueError("evidence records must be mappings")
            missing_evidence = [
                field for field in required_evidence if field not in record
            ]
            if missing_evidence:
                raise ValueError(
                    "evidence record missing required fields: "
                    + ", ".join(missing_evidence)
                )
            normalized_record = {
                field: str(record[field]) for field in required_evidence
            }
            if not re.fullmatch(
                r"sha256:[0-9a-f]{64}",
                normalized_record["digest"],
            ):
                raise ValueError(
                    "evidence digest must be lowercase sha256:<64 hex>"
                )
            normalized_evidence.append(normalized_record)
        normalized["evidence"] = sorted(
            normalized_evidence,
            key=lambda record: tuple(
                record[field] for field in required_evidence
            ),
        )
    return normalized


def _identity(node: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        node["repository"],
        node["revision"],
        node["capability"],
        tuple(node["implementation_paths"]),
    )


def aggregate_capability_nodes(
    nodes: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Validate, collapse exact duplicates, reject conflicts, and sort."""
    by_identity: dict[tuple[Any, ...], dict[str, Any]] = {}
    duplicates = 0

    for raw in nodes:
        node = _normalize(raw)
        key = _identity(node)
        existing = by_identity.get(key)
        if existing is None:
            by_identity[key] = node
            continue
        if existing != node:
            raise ValueError(
                "conflicting capability node for "
                f"{node['repository']}::{node['capability']}"
                f"@{node['revision']}"
            )
        duplicates += 1

    ordered = sorted(
        by_identity.values(),
        key=lambda item: (
            item["repository"].casefold(),
            item["capability"].casefold(),
            item["revision"],
            tuple(item["implementation_paths"]),
        ),
    )
    return {"nodes": ordered, "duplicate_findings": duplicates}


def semantic_digest(payload: Mapping[str, Any]) -> str:
    """Stable digest of semantic capability content, excluding telemetry."""
    raw_nodes = payload.get("nodes", [])
    if not isinstance(raw_nodes, Sequence) or isinstance(
        raw_nodes, (str, bytes, bytearray)
    ):
        raise ValueError("payload nodes must be a list-like sequence")
    normalized = aggregate_capability_nodes(raw_nodes)["nodes"]
    return _json_digest({"nodes": normalized})


def _build_checkpoint(
    scope: Sequence[str],
    *,
    completed_repositories: Sequence[str],
    failed_repositories: Sequence[str],
    nodes: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    scope_repositories = list(_normalize_repositories(scope))
    completed = set(completed_repositories)
    failed = set(failed_repositories)
    ordered_completed = [
        repository
        for repository in scope_repositories
        if repository in completed
    ]
    ordered_failed = [
        repository
        for repository in scope_repositories
        if repository in failed
    ]
    core = {
        "schema": CHECKPOINT_SCHEMA,
        "scope_digest": repository_scope_digest(scope_repositories),
        "scope_repositories": scope_repositories,
        "completed_repositories": ordered_completed,
        "failed_repositories": ordered_failed,
        "semantic_digest": semantic_digest({"nodes": nodes}),
    }
    return {**core, "checkpoint_sha256": _json_digest(core)}


def _validate_checkpoint(checkpoint: Mapping[str, Any]) -> None:
    if checkpoint.get("schema") != CHECKPOINT_SCHEMA:
        raise ValueError("checkpoint schema mismatch")
    recorded = checkpoint.get("checkpoint_sha256")
    core = {
        key: value
        for key, value in checkpoint.items()
        if key != "checkpoint_sha256"
    }
    if recorded != _json_digest(core):
        raise ValueError("checkpoint integrity mismatch")


def resume_repositories(
    repositories: Sequence[str],
    checkpoint: Mapping[str, Any],
) -> list[str]:
    """Return the unresolved subset after validating scope and checkpoint hash."""
    _validate_checkpoint(checkpoint)
    normalized = _normalize_repositories(repositories)
    if checkpoint.get("scope_digest") != repository_scope_digest(normalized):
        raise ValueError("checkpoint scope mismatch")

    scope = set(normalized)
    completed = set(checkpoint.get("completed_repositories") or [])
    failed = set(checkpoint.get("failed_repositories") or [])
    if (completed | failed) - scope:
        raise ValueError("checkpoint contains repositories outside scope")
    if completed & failed:
        raise ValueError("checkpoint repository cannot be complete and failed")

    return [
        repository
        for repository in normalized
        if repository not in completed
    ]


def _inspect_with_retries(
    repository: str,
    inspect: Callable[[str], Iterable[Mapping[str, Any]]],
    retries: int,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            rows = list(inspect(repository))
            return {
                "repository": repository,
                "attempts": attempt,
                "rows": rows,
                "failure": None,
            }
        except Exception as exc:  # noqa: BLE001 - preserve bounded worker failure
            last_error = exc

    assert last_error is not None
    return {
        "repository": repository,
        "attempts": retries + 1,
        "rows": [],
        "failure": {
            "repository": repository,
            "attempts": retries + 1,
            "error_type": type(last_error).__name__,
            "error": str(last_error),
        },
    }


def run_bounded_sweep(
    repositories: Sequence[str],
    inspect: Callable[[str], Iterable[Mapping[str, Any]]],
    *,
    workers: int = 6,
    retries: int = 0,
    strict: bool = True,
) -> dict[str, Any]:
    """Inspect a deduplicated scope concurrently and preserve partial progress."""
    if workers < 1:
        raise ValueError("workers must be >= 1")
    if retries < 0:
        raise ValueError("retries must be >= 0")

    scope = _normalize_repositories(repositories)
    started = time.perf_counter()
    ordered_outcomes: list[dict[str, Any] | None] = [None] * len(scope)

    if scope:
        with ThreadPoolExecutor(
            max_workers=min(workers, len(scope))
        ) as pool:
            futures = {
                pool.submit(
                    _inspect_with_retries,
                    repository,
                    inspect,
                    retries,
                ): index
                for index, repository in enumerate(scope)
            }
            for future in as_completed(futures):
                ordered_outcomes[futures[future]] = future.result()

    outcomes = [item for item in ordered_outcomes if item is not None]
    flat: list[Mapping[str, Any]] = []
    failures: list[dict[str, Any]] = []
    completed_repositories: list[str] = []
    retry_attempts = 0
    parent_payload: list[dict[str, Any]] = []

    for outcome in outcomes:
        retry_attempts += max(0, int(outcome["attempts"]) - 1)
        failure = outcome["failure"]
        if failure is not None:
            failures.append(dict(failure))
            parent_payload.append(
                {
                    "repository": outcome["repository"],
                    "failure": failure,
                }
            )
            continue

        completed_repositories.append(str(outcome["repository"]))
        rows = list(outcome["rows"])
        flat.extend(rows)
        parent_payload.append(
            {
                "repository": outcome["repository"],
                "rows": rows,
            }
        )

    aggregated = aggregate_capability_nodes(flat)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    checkpoint = _build_checkpoint(
        scope,
        completed_repositories=completed_repositories,
        failed_repositories=[
            str(failure["repository"]) for failure in failures
        ],
        nodes=aggregated["nodes"],
    )
    effective_workers = min(workers, len(scope)) if scope else 0
    result = {
        "schema": SWEEP_SCHEMA,
        "health_class": "HEALTHY" if not failures else "PARTIAL_FAILURE",
        "performance_valid": not failures,
        "nodes": aggregated["nodes"],
        "failures": failures,
        "semantic_digest": semantic_digest(
            {"nodes": aggregated["nodes"]}
        ),
        "checkpoint": checkpoint,
        "metrics": {
            "workers": effective_workers,
            "wall_clock_ms": elapsed_ms,
            "repos_inspected": len(scope),
            "repositories_succeeded": len(completed_repositories),
            "repositories_failed": len(failures),
            "retry_attempts": retry_attempts,
            "relevant_capabilities_recovered": len(
                aggregated["nodes"]
            ),
            "parent_context_consumption_bytes": len(
                json.dumps(
                    parent_payload,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                ).encode("utf-8")
            ),
            "duplicate_findings": aggregated["duplicate_findings"],
        },
    }
    if strict and failures:
        raise SweepIncompleteError(result)
    return result


def benchmark_serial_vs_parallel(
    repositories: Sequence[str],
    inspect: Callable[[str], Iterable[Mapping[str, Any]]],
    *,
    parallel_workers: int = 6,
    retries: int = 0,
) -> dict[str, Any]:
    """Run a matched serial/parallel experiment with health-gated metrics."""
    scope = _normalize_repositories(repositories)
    serial = run_bounded_sweep(
        scope,
        inspect,
        workers=1,
        retries=retries,
        strict=False,
    )
    parallel = run_bounded_sweep(
        scope,
        inspect,
        workers=parallel_workers,
        retries=retries,
        strict=False,
    )

    deterministic_match = (
        serial["semantic_digest"] == parallel["semantic_digest"]
    )
    both_healthy = (
        serial["health_class"] == "HEALTHY"
        and parallel["health_class"] == "HEALTHY"
    )
    if not both_healthy:
        health_class = "INFRA_FAILURE"
    elif not deterministic_match:
        health_class = "INVALID"
    else:
        health_class = "HEALTHY"

    performance_valid = health_class == "HEALTHY"
    serial_ms = float(serial["metrics"]["wall_clock_ms"])
    parallel_ms = float(parallel["metrics"]["wall_clock_ms"])
    speedup: float | None = None
    wall_clock_reduction_pct: float | None = None
    if performance_valid and parallel_ms > 0:
        speedup = serial_ms / parallel_ms
        if serial_ms > 0:
            wall_clock_reduction_pct = (
                (serial_ms - parallel_ms) / serial_ms * 100
            )

    def projection(result: Mapping[str, Any]) -> dict[str, Any]:
        return {
            **dict(result["metrics"]),
            "semantic_digest": result["semantic_digest"],
            "checkpoint_sha256": result["checkpoint"][
                "checkpoint_sha256"
            ],
            "failed_repositories": result["checkpoint"][
                "failed_repositories"
            ],
        }

    return {
        "schema": BENCHMARK_SCHEMA,
        "scope_digest": repository_scope_digest(scope),
        "scope_repositories": list(scope),
        "health_class": health_class,
        "performance_valid": performance_valid,
        "deterministic_result_match": deterministic_match,
        "serial": projection(serial),
        "parallel": projection(parallel),
        "speedup": speedup,
        "wall_clock_reduction_pct": wall_clock_reduction_pct,
    }
