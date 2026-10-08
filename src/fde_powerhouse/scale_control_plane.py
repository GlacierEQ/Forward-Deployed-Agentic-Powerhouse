from __future__ import annotations

import hashlib
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
                "schema": "glaciereq.scale-fde-control-plane.v2",
                "mission": {
                    "id": "SCALE-FDE-DEMO-001",
                    "status": "active",
                    "frontier_exhausted": False,
                    "verification_gates": {},
                },
                "workstreams": {
                    k: {"role": v, "tasks": {}} for k, v in WORKSTREAMS.items()
                },
                "integration_queue": [],
                "defect_queue": [],
                "receipts": [],
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
        self._worker(state, worker)["tasks"][task_id] = {
            "status": "queued",
            "outputs": outputs,
            "receipt": None,
        }
        self._persist(state)

    def claim(self, worker: str, task_id: str) -> None:
        state = self.snapshot()
        task = self._task(state, worker, task_id)
        if task["status"] != "queued":
            raise ValueError("only queued tasks may be claimed")
        task["status"] = "running"
        self._persist(state)

    def complete(
        self,
        worker: str,
        task_id: str,
        *,
        receipt: dict[str, Any],
    ) -> None:
        state = self.snapshot()
        task = self._task(state, worker, task_id)
        if task["status"] != "running":
            raise ValueError("only running tasks may complete")
        self._validate_receipt(task, receipt)
        task["status"] = "verified"
        task["receipt"] = receipt
        state["receipts"].append(
            {"worker": worker, "task_id": task_id, **receipt}
        )
        self._persist(state)

    def add_defect(
        self,
        worker: str,
        task_id: str,
        defect: dict[str, Any],
    ) -> None:
        state = self.snapshot()
        item = {"worker": worker, "task_id": task_id, **defect}
        item.setdefault("status", "open")
        state["defect_queue"].append(item)
        self._persist(state)

    def resolve_defect(
        self,
        worker: str,
        task_id: str,
        defect_id: str,
        *,
        readback: dict[str, Any],
    ) -> None:
        self._validate_readback(readback)
        state = self.snapshot()
        for defect in state["defect_queue"]:
            if (
                defect.get("worker") == worker
                and defect.get("task_id") == task_id
                and defect.get("id") == defect_id
            ):
                defect["status"] = "resolved"
                defect["resolution_readback"] = readback
                self._persist(state)
                return
        raise ValueError(f"unknown defect: {defect_id}")

    def queue_integration(
        self,
        worker: str,
        artifact: str,
        receipt_ref: str,
    ) -> None:
        state = self.snapshot()
        state["integration_queue"].append(
            {
                "worker": worker,
                "artifact": artifact,
                "receipt_ref": receipt_ref,
                "status": "pending",
            }
        )
        self._persist(state)

    def reconcile_integration(
        self,
        worker: str,
        artifact: str,
        receipt_ref: str,
        *,
        readback: dict[str, Any],
    ) -> None:
        self._validate_readback(readback)
        state = self.snapshot()
        for item in state["integration_queue"]:
            if (
                item.get("worker") == worker
                and item.get("artifact") == artifact
                and item.get("receipt_ref") == receipt_ref
            ):
                item["status"] = "verified"
                item["readback"] = readback
                self._persist(state)
                return
        raise ValueError(
            f"unknown integration: {worker}:{artifact}:{receipt_ref}"
        )

    def _terminal_evidence_valid(self, evidence: Any) -> bool:
        """Require E's sealed final receipts and C's actual reuse evidence."""
        if not isinstance(evidence, dict):
            return False
        receipts = {}
        for name in ("execution", "evaluation", "verification", "mission"):
            receipt = evidence.get(name)
            if not isinstance(receipt, dict):
                return False
            digest = receipt.get("receipt_sha256")
            body = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
            observed = hashlib.sha256(json.dumps(
                body, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")).hexdigest()
            if digest != observed:
                return False
            receipts[name] = receipt
        mission_path = self.root / "shared" / "SCALE_FDE_MISSION.yaml"
        if not mission_path.exists():
            return False
        contract_hash = hashlib.sha256(mission_path.read_bytes()).hexdigest()
        if any(r.get("mission_contract_sha256") != contract_hash
               or r.get("mission_id") != "SCALE-FDE-DEMO-001"
               for r in receipts.values()):
            return False
        execution, evaluation = receipts["execution"], receipts["evaluation"]
        verification, mission = receipts["verification"], receipts["mission"]
        if (execution.get("status") != "completed"
                or evaluation.get("verdict") != "FULL_STACK_BETTER"
                or evaluation.get("baseline_status") != "completed"
                or evaluation.get("full_stack_status") != "completed"
                or verification.get("decision") != "CERTIFIED"
                or mission.get("status") != "VERIFIED_SUCCESS"):
            return False
        if not verification.get("verifier_id") or (
            verification.get("verifier_id") == execution.get("executor_id")
        ):
            return False
        if any(mission.get(f"{name}_receipt_sha256") != receipts[name]["receipt_sha256"]
               for name in ("execution", "evaluation", "verification")):
            return False
        if (verification.get("execution_receipt_sha256") != execution["receipt_sha256"]
                or verification.get("evaluation_receipt_sha256") != evaluation["receipt_sha256"]):
            return False
        return self._verified_mission2_reuse(evidence, verification)

    @staticmethod
    def _verified_mission2_reuse(evidence: dict[str, Any],
                                 verification: dict[str, Any]) -> bool:
        proof = evidence.get("mission2_reuse")
        if not isinstance(proof, dict):
            return False
        first, second = proof.get("mission1"), proof.get("mission2")
        if not isinstance(first, dict) or not isinstance(second, dict):
            return False
        return bool(
            second.get("automatic_reuse") is True
            and first.get("extracted_capability_id")
            and first["extracted_capability_id"] == second.get("auto_reused_capability_id")
            and any(p.get("name") == "mission2_automatic_reuse" and p.get("verified") is True
                    for p in verification.get("postconditions", []) if isinstance(p, dict))
        )

    def record_terminal_evidence(self, evidence: dict[str, Any]) -> None:
        verified = self._terminal_evidence_valid(evidence)
        if not verified:
            raise ValueError("terminal evidence validation failed")
        state = self.snapshot()
        state["mission"]["terminal_evidence"] = evidence
        state["mission"]["independent_terminal_certification"] = verified
        self._persist(state)

    def _persist(self, state: dict[str, Any]) -> None:
        tasks = [
            task
            for workstream in state["workstreams"].values()
            for task in workstream["tasks"].values()
        ]
        tasks_verified = (
            bool(tasks)
            and all(task["status"] == "verified" for task in tasks)
            and all(
                state["workstreams"][worker]["tasks"]
                for worker in WORKSTREAMS
            )
        )
        integration_reconciled = all(
            item.get("status") == "verified"
            for item in state["integration_queue"]
        )
        defects_resolved = all(
            item.get("status") == "resolved"
            for item in state["defect_queue"]
        )
        receipts_indexed = (
            sum(task["status"] == "verified" for task in tasks)
            == len(state["receipts"])
        )

        gates = {
            "all_workstreams_verified": tasks_verified,
            "integration_reconciled": integration_reconciled,
            "defects_resolved": defects_resolved,
            "receipts_indexed": receipts_indexed,
        }
        workstream_exhausted = bool(gates) and all(gates.values())
        terminal_certified = bool(
            state["mission"].get("independent_terminal_certification") is True
            and self._terminal_evidence_valid(state["mission"].get("terminal_evidence"))
        )
        gates["independent_terminal_certification"] = terminal_certified
        exhausted = workstream_exhausted and terminal_certified
        state["mission"]["verification_gates"] = gates
        state["mission"]["workstream_frontier_exhausted"] = workstream_exhausted
        state["mission"]["frontier_exhausted"] = exhausted
        state["mission"]["status"] = (
            "verified" if exhausted
            else "awaiting_independent_certification" if workstream_exhausted
            else "active"
        )
        self._write_json(self._state_path, state)
        self._materialize_contracts(state)

    @classmethod
    def _validate_receipt(
        cls,
        task: dict[str, Any],
        receipt: dict[str, Any],
    ) -> None:
        revision = receipt.get("revision") if receipt else None
        if not isinstance(revision, str) or not revision.strip():
            raise ValueError("completion requires a receipt revision")

        tests = receipt.get("tests")
        if not isinstance(tests, list):
            raise TypeError("tests must contain evidence objects")
        if not tests:
            raise ValueError("completion requires verified test evidence")
        for test in tests:
            if not isinstance(test, dict):
                raise TypeError("tests must contain evidence objects")
            if test.get("state") != "passed" or not test.get("source"):
                raise ValueError("tests require passed state and source")

        output_proofs = receipt.get("outputs")
        if not isinstance(output_proofs, list):
            raise TypeError("completion requires outputs evidence")
        verified_outputs = set()
        for proof in output_proofs:
            if not isinstance(proof, dict):
                raise TypeError("outputs must contain evidence objects")
            if proof.get("state") != "verified" or not proof.get("source"):
                raise ValueError("outputs require verified state and source")
            if proof.get("path"):
                verified_outputs.add(proof["path"])
        missing = set(task["outputs"]) - verified_outputs
        if missing:
            raise ValueError(
                "receipt outputs missing declared proofs: "
                + ", ".join(sorted(missing))
            )

        cls._validate_readback(receipt.get("readback"))

    @staticmethod
    def _validate_readback(readback: Any) -> None:
        if not isinstance(readback, dict):
            raise TypeError("provider readback is required")
        if readback.get("state") != "verified" or not readback.get("source"):
            raise ValueError(
                "provider readback requires verified state and source"
            )

    def _materialize_contracts(self, state: dict[str, Any]) -> None:
        mission = (
            "schema: glaciereq.scale-fde-mission.v2\n"
            "id: SCALE-FDE-DEMO-001\n"
            "objective: prove ambiguous mission to verified deployed outcome "
            "with recovery and compounding\n"
            "terminal_condition: all five workstreams verified, integration "
            "reconciled, defects resolved, receipts indexed\n"
            "principles:\n"
            "  - recover_before_recreate\n"
            "  - checkpoint_is_not_completion\n"
            "  - provider_readback_required\n"
            "  - preserve_stronger_existing_capability\n"
        )
        architecture = {
            "schema": "glaciereq.scale-fde-architecture.v2",
            "workstreams": WORKSTREAMS,
            "shared_artifacts": [
                "SCALE_CAPABILITY_GRAPH.json",
                "INTEGRATION_QUEUE.json",
                "DEFECT_QUEUE.json",
                "RECEIPT_INDEX.json",
            ],
        }

        shared = self.root / "shared"
        shared.mkdir(parents=True, exist_ok=True)

        (self.root / "SCALE_FDE_MISSION.yaml").write_text(mission)
        self._write_json(
            self.root / "ARCHITECTURE_CONTRACT.json",
            architecture,
        )
        shared_mission = shared / "SCALE_FDE_MISSION.yaml"
        if not shared_mission.exists():
            shared_mission.write_text(mission)
        shared_architecture = shared / "ARCHITECTURE_CONTRACT.json"
        if not shared_architecture.exists():
            self._write_json(shared_architecture, architecture)

        for worker in WORKSTREAMS:
            runtime_projection = state["workstreams"][worker]
            self._write_json(
                self.root / f"WORKSTREAM_{worker}.json",
                runtime_projection,
            )
            shared_path = shared / f"WORKSTREAM_{worker}.json"
            if not shared_path.exists():
                self._write_json(shared_path, runtime_projection)

        generated = {
            "INTEGRATION_QUEUE.json": state["integration_queue"],
            "DEFECT_QUEUE.json": state["defect_queue"],
            "RECEIPT_INDEX.json": state["receipts"],
        }
        for name, value in generated.items():
            self._write_json(self.root / name, value)
            shared_path = shared / name
            if not shared_path.exists():
                self._write_json(shared_path, value)

        empty_graph = {
            "schema": "glaciereq.scale-capability-graph.v1",
            "nodes": [],
            "edges": [],
        }
        for cap in (
            self.root / "SCALE_CAPABILITY_GRAPH.json",
            shared / "SCALE_CAPABILITY_GRAPH.json",
        ):
            if not cap.exists():
                self._write_json(cap, empty_graph)

    @staticmethod
    def _write_json(path: Path, value: Any) -> None:
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")

    @staticmethod
    def _worker(state: dict[str, Any], worker: str) -> dict[str, Any]:
        if worker not in WORKSTREAMS:
            raise ValueError(f"unknown workstream: {worker}")
        return state["workstreams"][worker]

    def _task(
        self,
        state: dict[str, Any],
        worker: str,
        task_id: str,
    ) -> dict[str, Any]:
        tasks = self._worker(state, worker)["tasks"]
        if task_id not in tasks:
            raise ValueError(f"unknown task: {task_id}")
        return tasks[task_id]
