"""Scale FDE Workstream C composition sidecar.

This module composes existing Aspen Grove continuity and Genius-Mastery
compounding primitives. It owns no independent memory store and no independent
capability-scoring framework.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from .estate import load_estate, resolve_repo

Hydrator = Callable[[Path, str], dict[str, Any]]


def _resolve_donor_root(key: str) -> Path:
    entry = resolve_repo(load_estate(), key)
    root = entry.get("effective_path")
    if not entry.get("available") or not root:
        env_key = f"FDE_PATH_{key.upper()}"
        raise RuntimeError(f"{key} unavailable; set {env_key} to a verified checkout")
    return Path(root).resolve()


def _load_continuity(aspen_root: Path | None = None):
    root = (aspen_root or _resolve_donor_root("aspen_grove_memory")).resolve()
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    module = importlib.import_module("src.scale_continuity")
    return module.ScaleContinuityStore


def _load_compounding(genius_root: Path | None = None):
    root = (genius_root or _resolve_donor_root("genius_mastery")).resolve()
    source_root = str(root / "src")
    if source_root not in sys.path:
        sys.path.insert(0, source_root)
    return importlib.import_module("genius.compounding")


def _git_revision(root: Path) -> str | None:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def hydrate(db_path: Path, mission_id: str) -> dict[str, Any]:
    """Hydrate one mission from Aspen Grove structured continuity only."""
    continuity_cls = _load_continuity()
    store = continuity_cls(db_path)
    try:
        return store.resurrect(mission_id)
    finally:
        store.close()


def _fresh_process_hydrate(db_path: Path, mission_id: str) -> dict[str, Any]:
    command = [
        sys.executable,
        "-m",
        "fde_powerhouse.scale_compounding",
        "hydrate",
        "--db",
        str(db_path.resolve()),
        "--mission",
        mission_id,
    ]
    proc = subprocess.run(
        command,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "fresh-process Aspen resurrection failed: "
            + (proc.stderr.strip() or proc.stdout.strip())
        )
    recovered = json.loads(proc.stdout)
    if not isinstance(recovered, dict):
        raise TypeError("fresh-process resurrection did not return an object")
    return recovered


_CANONICAL_SHARED_INPUTS = (
    "SCALE_FDE_MISSION.yaml",
    "SCALE_CAPABILITY_GRAPH.json",
    "WORKSTREAM_E.json",
    "RECEIPT_INDEX.json",
)

_VERIFIED_RECEIPT_STATES = {"verified", "operationally_verified"}


def _load_mapping(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix in {".yaml", ".yml"}:
        value = yaml.safe_load(text)
    else:
        value = json.loads(text)
    if not isinstance(value, dict):
        raise TypeError(f"{path.name} must contain an object")
    return value


def _artifact_descriptor(path: Path) -> dict[str, Any]:
    content = path.read_bytes()
    return {
        "path": f"shared/{path.name}",
        "sha256": hashlib.sha256(content).hexdigest(),
        "size_bytes": len(content),
    }


def _contains_unresolved(items: Any, filename: str) -> bool:
    return any(filename in str(item) for item in (items or []))


def prepare_canonical_frontier(
    *,
    shared_root: Path,
    db_path: Path,
    registry_path: Path,
    continuity_cls=None,
) -> dict[str, Any]:
    """Hydrate the real shared mission and stop exactly at E's verification gate.

    This function deliberately does not synthesize a mission receipt or infer a
    reusable capability from partial workstream evidence.
    """
    shared_root = Path(shared_root)
    paths = {name: shared_root / name for name in _CANONICAL_SHARED_INPUTS}
    documents = {name: _load_mapping(path) for name, path in paths.items()}
    source_snapshot = {
        name: _artifact_descriptor(path) for name, path in paths.items()
    }

    mission = documents["SCALE_FDE_MISSION.yaml"]
    graph = documents["SCALE_CAPABILITY_GRAPH.json"]
    workstream_e = documents["WORKSTREAM_E.json"]
    receipt_index = documents["RECEIPT_INDEX.json"]

    mission_id = str(mission.get("id") or "").strip()
    if not mission_id:
        raise ValueError("SCALE_FDE_MISSION.yaml requires id")
    for label, document in (
        ("WORKSTREAM_E.json", workstream_e),
        ("RECEIPT_INDEX.json", receipt_index),
    ):
        observed = str(document.get("mission_id") or "").strip()
        if observed != mission_id:
            raise ValueError(
                f"{label} mission_id {observed!r} does not match {mission_id!r}"
            )

    if str(graph.get("workstream") or "") != "A":
        raise ValueError("SCALE_CAPABILITY_GRAPH.json must be owned by Workstream A")
    repositories = {
        str(node.get("repository") or "")
        for node in (graph.get("nodes") or [])
        if isinstance(node, dict)
    }
    required_donors = {
        "GlacierEQ/aspen-grove-memory",
        "GlacierEQ/Genius-Mastery",
    }
    missing_donors = sorted(required_donors - repositories)
    if missing_donors:
        raise ValueError(
            "canonical capability graph is missing Agent C donors: "
            + ", ".join(missing_donors)
        )

    continuity = continuity_cls or _load_continuity()
    source_refs = [
        f"artifact://{item['path']}#sha256={item['sha256']}"
        for item in source_snapshot.values()
    ]
    objective = str(mission.get("objective") or "").strip()
    principles = [str(value) for value in (mission.get("principles") or [])]

    store = continuity(db_path)
    try:
        store.record_mission(
            mission_id,
            objective=objective,
            constraints=principles,
            source_refs=source_refs,
        )
        receipt_path = shared_root / "MISSION_RECEIPT.json"
        if not receipt_path.is_file():
            if not _contains_unresolved(
                receipt_index.get("unresolved"), "MISSION_RECEIPT.json"
            ):
                raise ValueError(
                    "MISSION_RECEIPT.json is absent but RECEIPT_INDEX.json "
                    "does not preserve it as unresolved"
                )
            if not _contains_unresolved(
                workstream_e.get("unresolved_dependencies"),
                "MISSION_RECEIPT.json",
            ):
                raise ValueError(
                    "MISSION_RECEIPT.json is absent but WORKSTREAM_E.json "
                    "does not preserve it as unresolved"
                )

            dependency = (
                "Workstream E verified shared/MISSION_RECEIPT.json is required "
                "before reusable capability extraction"
            )
            frontier = ["await:shared/MISSION_RECEIPT.json"]
            store.record_decision(
                mission_id,
                decision_id="fail-closed-await-independent-verification",
                summary="Do not compound partial workstream evidence.",
                rationale=(
                    "Workstream E owns independent mission verification; "
                    "an absent receipt cannot be inferred from implementation."
                ),
                source_refs=source_refs,
            )
            store.record_continuation(
                mission_id,
                frontier=frontier,
                unresolved_dependencies=[dependency],
                source_refs=source_refs,
            )
            return {
                "schema": "glaciereq.scale-fde.workstream-c-frontier/v1",
                "status": "blocked_external_dependency",
                "mission_id": mission_id,
                "source_snapshot": source_snapshot,
                "mission_receipt": {
                    "path": "shared/MISSION_RECEIPT.json",
                    "present": False,
                    "required_verification_states": sorted(
                        _VERIFIED_RECEIPT_STATES
                    ),
                },
                "continuation": {
                    "current_frontier": frontier,
                    "unresolved_dependencies": [dependency],
                },
                "capability_registry": str(Path(registry_path)),
                "capability_registry_mutated": False,
                "truth_boundary": (
                    "Canonical mission state is hydrated and preserved. "
                    "No reusable capability is extracted until Workstream E "
                    "emits an independently verified mission receipt."
                ),
            }
    finally:
        store.close()

    receipt = _load_mapping(shared_root / "MISSION_RECEIPT.json")
    observed_mission_id = str(receipt.get("mission_id") or "").strip()
    if observed_mission_id != mission_id:
        raise ValueError(
            "MISSION_RECEIPT.json mission_id "
            f"{observed_mission_id!r} does not match {mission_id!r}"
        )
    verification = str(receipt.get("verification_status") or "").casefold()
    if verification not in _VERIFIED_RECEIPT_STATES:
        raise ValueError(
            "MISSION_RECEIPT.json is present but not independently verified"
        )
    return {
        "schema": "glaciereq.scale-fde.workstream-c-frontier/v1",
        "status": "ready_for_verified_compounding",
        "mission_id": mission_id,
        "source_snapshot": source_snapshot,
        "mission_receipt": {
            "path": "shared/MISSION_RECEIPT.json",
            "present": True,
            "verification_status": verification,
        },
        "capability_registry": str(Path(registry_path)),
        "capability_registry_mutated": False,
        "truth_boundary": (
            "Independent mission verification is present. Capability extraction "
            "is now eligible, but remains a separate C-owned execution step."
        ),
    }


def run_compounding_proof(
    *,
    mission1_receipt: dict[str, Any],
    mission2: dict[str, Any],
    db_path: Path,
    registry_path: Path,
    continuity_cls=None,
    compounding_api=None,
    fresh_hydrator: Hydrator | None = None,
) -> dict[str, Any]:
    """Execute the verified Mission-1 -> capability -> Mission-2 reuse loop."""
    continuity = continuity_cls or _load_continuity()
    compounding = compounding_api or _load_compounding()
    hydrator = fresh_hydrator or _fresh_process_hydrate

    capability = compounding.extract_reusable_capability(mission1_receipt)
    registry_receipt = compounding.register_capability(registry_path, capability)

    mission1_id = str(mission1_receipt["mission_id"])
    objective = str(mission1_receipt.get("objective") or "")
    receipt_refs = list(mission1_receipt.get("receipt_refs") or [])
    receipt_source = receipt_refs[0] if receipt_refs else "receipt://mission-1/verified"

    store = continuity(db_path)
    try:
        store.record_mission(
            mission1_id,
            objective=objective,
            constraints=["structured-state-only", "reuse-before-rebuild"],
            source_refs=[str(mission1_receipt.get("source_revision") or "unknown")],
        )
        store.record_decision(
            mission1_id,
            decision_id="extract-reusable-capability",
            summary="Separate mission-specific state from the verified reusable capability.",
            rationale="Mission success can compound only through explicit reusable contracts.",
        )
        store.record_execution(
            mission1_id,
            execution_id="mission-1-verified",
            task="Verify Mission 1 and expose reusable capability contract.",
            status="completed",
            receipt_refs=receipt_refs,
        )
        store.record_receipt(
            mission1_id,
            receipt_id="mission-1-verification",
            kind="mission-verification",
            status="verified",
            source=receipt_source,
        )
        store.record_capability(
            mission1_id,
            capability_id=str(capability["id"]),
            description=str(capability["description"]),
            stage=str(capability["stage"]),
            evidence_refs=list(capability.get("evidence_refs") or []),
        )
        store.record_continuation(
            mission1_id,
            frontier=[str(mission2.get("mission_id") or "mission-2")],
            unresolved_dependencies=[],
        )
    finally:
        store.close()

    resurrection = hydrator(Path(db_path), mission1_id)
    registry = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    capabilities = list(registry.get("capabilities") or [])
    selection = compounding.select_reusable_capability(
        mission2,
        capabilities,
        minimum_score=0.35,
    )
    selected = selection.get("selected")
    if not isinstance(selected, dict):
        raise TypeError("Mission 2 did not select a reusable capability")

    selected_capability = selected.get("capability")
    if not isinstance(selected_capability, dict):
        raise TypeError("Mission 2 selection is missing capability details")
    selected_id = str(selected_capability.get("id") or "")
    if selected_id != str(capability["id"]):
        raise RuntimeError(
            f"Mission 2 selected {selected_id!r}, expected {capability['id']!r}"
        )

    mission2_id = str(mission2.get("mission_id") or "mission-2")
    mission2_store = continuity(db_path)
    try:
        mission2_store.record_mission(
            mission2_id,
            objective=str(mission2.get("objective") or ""),
            constraints=list(mission2.get("constraints") or []),
            source_refs=[f"capability-registry:{registry_receipt['sha256']}"],
        )
        mission2_store.record_decision(
            mission2_id,
            decision_id="auto-reuse-mission-1-capability",
            summary=f"Automatically reuse {selected_id}.",
            rationale=(
                "Genius deterministic mission-fit scoring selected the verified "
                "capability above the reuse threshold."
            ),
        )
        mission2_store.record_execution(
            mission2_id,
            execution_id="mission-2-capability-selection",
            task=f"Select reusable capability {selected_id}",
            status="completed",
            receipt_refs=[],
        )
        mission2_store.record_continuation(
            mission2_id,
            frontier=[f"execute:{selected_id}"],
            unresolved_dependencies=[],
        )
    finally:
        mission2_store.close()

    return {
        "schema": "glaciereq.scale-fde.workstream-c-proof/v1",
        "mission1": {
            "mission_id": mission1_id,
            "extracted_capability_id": capability["id"],
            "source_revision": capability.get("source_revision"),
            "registry_sha256": registry_receipt["sha256"],
        },
        "resurrection": resurrection,
        "mission2": {
            "mission_id": mission2_id,
            "auto_reused_capability_id": selected_id,
            "selection_score": selected["score"],
            "matched_terms": list(selected.get("matched_terms") or []),
            "automatic_reuse": True,
        },
        "truth_boundary": (
            "This proof verifies the Workstream-C mechanism with structured Aspen "
            "Grove state and no raw transcript continuity. It does not assert that "
            "the full multi-workstream Scale mission has already completed."
        ),
    }


def _fixture_mission1() -> dict[str, Any]:
    return {
        "mission_id": "mission-1",
        "objective": "Recover from an ambiguous provider mutation.",
        "verification_status": "verified",
        "source_revision": "fixture-mission-1-verified",
        "receipt_refs": ["receipt://fixture/mission-1/verified"],
        "reusable_capability": {
            "id": "cap.provider-readback-reconcile",
            "description": (
                "Provider readback and reconciliation after ambiguous external mutation"
            ),
            "tags": ["provider", "readback", "reconciliation", "idempotency"],
            "input_contract": {
                "requires": ["attempted mutation", "provider identity"],
            },
            "output_contract": {
                "emits": ["confirmed applied", "confirmed absent", "unknown"],
            },
        },
    }


def _fixture_mission2() -> dict[str, Any]:
    return {
        "mission_id": "mission-2",
        "objective": (
            "Safely reconcile an ambiguous provider mutation using provider readback."
        ),
        "requirements": ["idempotency", "provider confirmation", "readback"],
    }


def run_fixture_proof(workdir: Path) -> dict[str, Any]:
    """Execute the deterministic cross-process Workstream-C proof fixture."""
    workdir.mkdir(parents=True, exist_ok=True)
    proof = run_compounding_proof(
        mission1_receipt=_fixture_mission1(),
        mission2=_fixture_mission2(),
        db_path=workdir / "scale-continuity.sqlite3",
        registry_path=workdir / "learned-capabilities.json",
    )
    proof["donors"] = {
        "aspen_grove_memory": {
            "root": str(_resolve_donor_root("aspen_grove_memory")),
            "revision": _git_revision(_resolve_donor_root("aspen_grove_memory")),
        },
        "genius_mastery": {
            "root": str(_resolve_donor_root("genius_mastery")),
            "revision": _git_revision(_resolve_donor_root("genius_mastery")),
        },
    }
    return proof


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    hydrate_parser = commands.add_parser("hydrate")
    hydrate_parser.add_argument("--db", type=Path, required=True)
    hydrate_parser.add_argument("--mission", required=True)

    prove_parser = commands.add_parser("prove")
    prove_parser.add_argument("--workdir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "hydrate":
        result = hydrate(args.db, args.mission)
    else:
        result = run_fixture_proof(args.workdir)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
