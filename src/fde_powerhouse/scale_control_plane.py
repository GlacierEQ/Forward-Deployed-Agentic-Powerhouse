from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

WORKSTREAMS = {
    "A": "estate_intelligence_gatling",
    "B": "runtime_swarm",
    "C": "memory_composition",
    "D": "integration_mcp_glue",
    "E": "verification_scale_product",
}


@dataclass
class ScaleControlPlane:
    root: Path

    @classmethod
    def bootstrap(cls, root: Path) -> ScaleControlPlane:
        root.mkdir(parents=True, exist_ok=True)
        cp = cls(root)
        if not cp._state_path.exists():
            state = {
                "schema": "glaciereq.scale-fde-control-plane.v1",
                "mission": {"id": "SCALE-FDE-DEMO-001", "status": "active", "frontier_exhausted": False},
                "workstreams": {k: {"role": v, "tasks": {}} for k, v in WORKSTREAMS.items()},
                "integration_queue": [], "defect_queue": [], "receipts": [],
            }
            cp._write_json(cp._state_path, state)
            cp._materialize_contracts(state)
        return cp

    @property
    def _state_path(self) -> Path:
        return self.root / "CONTROL_PLANE_STATE.json"

    def snapshot(self) -> dict[str, Any]:
        return json.loads(self._state_path.read_text())

    def enqueue(self, worker: str, task_id: str, *, outputs: list[str]) -> None:
        state = self.snapshot()
        self._worker(state, worker)["tasks"][task_id] = {"status": "queued", "outputs": outputs, "receipt": None}
        self._persist(state)

    def claim(self, worker: str, task_id: str) -> None:
        state = self.snapshot()
        task = self._task(state, worker, task_id)
        if task["status"] != "queued":
            raise ValueError("only queued tasks may be claimed")
        task["status"] = "running"
        self._persist(state)

    def complete(self, worker: str, task_id: str, *, receipt: dict[str, Any]) -> None:
        if not receipt or not receipt.get("revision") or not receipt.get("tests"):
            raise ValueError("completion requires an execution receipt with revision and tests")
        state = self.snapshot()
        task = self._task(state, worker, task_id)
        if task["status"] != "running":
            raise ValueError("only running tasks may complete")
        task["status"] = "verified"
        task["receipt"] = receipt
        state["receipts"].append({"worker": worker, "task_id": task_id, **receipt})
        self._persist(state)

    def add_defect(self, worker: str, task_id: str, defect: dict[str, Any]) -> None:
        state = self.snapshot()
        state["defect_queue"].append({"worker": worker, "task_id": task_id, **defect})
        self._persist(state)

    def queue_integration(self, worker: str, artifact: str, receipt_ref: str) -> None:
        state = self.snapshot()
        state["integration_queue"].append({"worker": worker, "artifact": artifact, "receipt_ref": receipt_ref, "status": "pending"})
        self._persist(state)

    def _persist(self, state: dict[str, Any]) -> None:
        tasks = [t for w in state["workstreams"].values() for t in w["tasks"].values()]
        exhausted = bool(tasks) and all(t["status"] == "verified" for t in tasks) and all(state["workstreams"][w]["tasks"] for w in WORKSTREAMS)
        state["mission"]["frontier_exhausted"] = exhausted
        state["mission"]["status"] = "verified" if exhausted else "active"
        self._write_json(self._state_path, state)
        self._materialize_contracts(state)

    def _materialize_contracts(self, state: dict[str, Any]) -> None:
        mission = """schema: glaciereq.scale-fde-mission.v1\nid: SCALE-FDE-DEMO-001\nobjective: prove ambiguous mission to verified deployed outcome with recovery and compounding\nterminal_condition: all five workstreams verified, integration reconciled, receipts indexed\nprinciples:\n  - recover_before_recreate\n  - checkpoint_is_not_completion\n  - provider_readback_required\n  - preserve_stronger_existing_capability\n"""
        (self.root / "SCALE_FDE_MISSION.yaml").write_text(mission)
        architecture = {"schema": "glaciereq.scale-fde-architecture.v1", "workstreams": WORKSTREAMS, "shared_artifacts": ["SCALE_CAPABILITY_GRAPH.json", "INTEGRATION_QUEUE.json", "DEFECT_QUEUE.json", "RECEIPT_INDEX.json"]}
        self._write_json(self.root / "ARCHITECTURE_CONTRACT.json", architecture)
        for worker in WORKSTREAMS:
            self._write_json(self.root / f"WORKSTREAM_{worker}.json", state["workstreams"][worker])
        self._write_json(self.root / "INTEGRATION_QUEUE.json", state["integration_queue"])
        self._write_json(self.root / "DEFECT_QUEUE.json", state["defect_queue"])
        self._write_json(self.root / "RECEIPT_INDEX.json", state["receipts"])
        cap = self.root / "SCALE_CAPABILITY_GRAPH.json"
        if not cap.exists():
            self._write_json(cap, {"schema": "glaciereq.scale-capability-graph.v1", "nodes": [], "edges": []})

    @staticmethod
    def _write_json(path: Path, value: Any) -> None:
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")

    @staticmethod
    def _worker(state: dict[str, Any], worker: str) -> dict[str, Any]:
        if worker not in WORKSTREAMS:
            raise ValueError(f"unknown workstream: {worker}")
        return state["workstreams"][worker]

    def _task(self, state: dict[str, Any], worker: str, task_id: str) -> dict[str, Any]:
        tasks = self._worker(state, worker)["tasks"]
        if task_id not in tasks:
            raise ValueError(f"unknown task: {task_id}")
        return tasks[task_id]
