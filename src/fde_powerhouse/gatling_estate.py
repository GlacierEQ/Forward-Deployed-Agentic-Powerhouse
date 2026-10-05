"""Bounded concurrent estate discovery with deterministic capability aggregation."""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Iterable, Mapping, Sequence

MATURITY = {"prototype", "working", "hardened", "production"}
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


def _normalize(node: Mapping[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in node]
    if missing:
        raise ValueError(f"capability node missing required fields: {', '.join(missing)}")

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
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
            raise ValueError(f"{field} must be a list-like sequence")
        normalized[field] = sorted({str(item) for item in value})
    normalized["maturity"] = maturity
    normalized["verified_state"] = str(node["verified_state"])
    normalized["donor_value"] = donor_value
    return normalized


def _identity(node: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        node["repository"],
        node["revision"],
        node["capability"],
        tuple(node["implementation_paths"]),
    )


def aggregate_capability_nodes(nodes: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Validate, deduplicate exact repeats, reject conflicts, and sort deterministically."""
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
                f"{node['repository']}::{node['capability']}@{node['revision']}"
            )
        duplicates += 1

    ordered = sorted(
        by_identity.values(),
        key=lambda n: (
            n["repository"].casefold(),
            n["capability"].casefold(),
            n["revision"],
            tuple(n["implementation_paths"]),
        ),
    )
    return {"nodes": ordered, "duplicate_findings": duplicates}


def run_bounded_sweep(
    repositories: Sequence[str],
    inspect: Callable[[str], Iterable[Mapping[str, Any]]],
    *,
    workers: int = 6,
) -> dict[str, Any]:
    """Inspect repositories concurrently while keeping concurrency bounded."""
    if workers < 1:
        raise ValueError("workers must be >= 1")
    if not repositories:
        return {
            "schema": "scale.capability-sweep/v1",
            "nodes": [],
            "metrics": {
                "workers": workers,
                "wall_clock_ms": 0,
                "repos_inspected": 0,
                "relevant_capabilities_recovered": 0,
                "parent_context_consumption_bytes": 0,
                "duplicate_findings": 0,
            },
        }

    started = time.perf_counter()
    ordered_results: list[list[Mapping[str, Any]] | None] = [None] * len(repositories)

    with ThreadPoolExecutor(max_workers=min(workers, len(repositories))) as pool:
        futures = {
            pool.submit(inspect, repository): index
            for index, repository in enumerate(repositories)
        }
        for future in as_completed(futures):
            ordered_results[futures[future]] = list(future.result())

    flat: list[Mapping[str, Any]] = []
    parent_context_bytes = 0
    for result in ordered_results:
        rows = result or []
        flat.extend(rows)
        parent_context_bytes += len(
            json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        )

    aggregated = aggregate_capability_nodes(flat)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    return {
        "schema": "scale.capability-sweep/v1",
        "nodes": aggregated["nodes"],
        "metrics": {
            "workers": min(workers, len(repositories)),
            "wall_clock_ms": elapsed_ms,
            "repos_inspected": len(repositories),
            "relevant_capabilities_recovered": len(aggregated["nodes"]),
            "parent_context_consumption_bytes": parent_context_bytes,
            "duplicate_findings": aggregated["duplicate_findings"],
        },
    }
