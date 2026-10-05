"""Scale FDE Workstream C composition sidecar.

This module composes existing Aspen Grove continuity and Genius-Mastery
compounding primitives. It owns no independent memory store and no independent
capability-scoring framework.
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

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
    proc = subprocess.run(  # noqa: S603
        ["git", "rev-parse", "HEAD"],  # noqa: S607
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
    proc = subprocess.run(  # noqa: S603
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
        raise RuntimeError("fresh-process resurrection did not return an object")
    return recovered


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
        raise RuntimeError("Mission 2 did not select a reusable capability")

    selected_capability = selected.get("capability")
    if not isinstance(selected_capability, dict):
        raise RuntimeError("Mission 2 selection is missing capability details")
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
