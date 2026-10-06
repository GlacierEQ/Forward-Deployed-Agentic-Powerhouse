from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path

import pytest

from fde_powerhouse.scale_orchestrator import (
    MissionOrchestrationError,
    launcher_digest,
    load_launchers,
    load_mission,
    mission_digest,
    run_mission,
    subprocess_dispatch,
)


def canonical_mission() -> dict:
    return {
        "schema": "glaciereq.scale-fde-mission.v1",
        "id": "SCALE-FDE-DEMO-001",
        "revision": 2,
        "objective": "Prove the real desired state.",
        "terminal_condition": "all five workstreams independently evidenced",
        "principles": [
            "recover_before_recreate",
            "checkpoint_is_not_completion",
            "no_sixth_orchestration_framework",
        ],
        "workstreams": {
            "A": "estate_intelligence_gatling",
            "B": "runtime_swarm_durability",
            "C": "memory_composition_compounding",
            "D": "integration_mcp_sigma_glue",
            "E": "independent_verification_scale_product",
        },
    }


def launchers(command: list[str] | None = None) -> dict:
    command = command or [sys.executable, "-c", "raise SystemExit(0)"]
    return {
        "schema": "glaciereq.scale-fde-launchers.v1",
        "max_workers": 4,
        "workstreams": {
            "A": {"deps": [], "command": command},
            "B": {"deps": ["A"], "command": command},
            "C": {"deps": ["A"], "command": command},
            "D": {"deps": ["A"], "command": command},
            "E": {"deps": ["A"], "command": command},
        },
    }


def test_canonical_mission_and_launcher_digests_are_order_independent():
    mission = canonical_mission()
    mission_reordered = {
        "workstreams": mission["workstreams"],
        "objective": mission["objective"],
        "revision": mission["revision"],
        "schema": mission["schema"],
        "principles": mission["principles"],
        "terminal_condition": mission["terminal_condition"],
        "id": mission["id"],
    }
    binding = launchers()
    binding_reordered = {
        "workstreams": binding["workstreams"],
        "max_workers": binding["max_workers"],
        "schema": binding["schema"],
    }

    assert mission_digest(mission) == mission_digest(mission_reordered)
    assert launcher_digest(binding) == launcher_digest(binding_reordered)
    assert mission_digest(mission).startswith("sha256:")
    assert launcher_digest(binding).startswith("sha256:")


def test_run_mission_fires_a_then_b_to_e_in_bounded_parallel():
    active = 0
    max_active = 0
    lock = threading.Lock()
    calls: list[str] = []

    def dispatch(spec: dict) -> dict:
        nonlocal active, max_active
        with lock:
            active += 1
            max_active = max(max_active, active)
            calls.append(spec["id"])
        time.sleep(0.02)
        with lock:
            active -= 1
        return {"status": "success", "returncode": 0}

    result = run_mission(canonical_mission(), launchers(), dispatch=dispatch)

    assert result["status"] == "LAUNCH_COMPLETE"
    assert result["mission_complete"] is False
    assert result["mission_completion_authority"] == "ScaleControlPlane + Workstream E"
    assert result["completed"] == ["A", "B", "C", "D", "E"]
    assert calls[0] == "A"
    assert set(calls[1:]) == {"B", "C", "D", "E"}
    assert 1 < max_active <= 4
    assert result["waves"] == [["A"], ["B", "C", "D", "E"]]


def test_launcher_contract_must_match_canonical_five_workstreams():
    binding = launchers()
    del binding["workstreams"]["E"]
    with pytest.raises(MissionOrchestrationError, match="launcher workstreams"):
        run_mission(
            canonical_mission(),
            binding,
            dispatch=lambda spec: {"status": "success"},
        )

    binding = launchers()
    binding["workstreams"]["F"] = {
        "deps": [],
        "command": [sys.executable, "-c", "raise SystemExit(0)"],
    }
    with pytest.raises(MissionOrchestrationError, match="launcher workstreams"):
        run_mission(
            canonical_mission(),
            binding,
            dispatch=lambda spec: {"status": "success"},
        )


def test_canonical_mission_rejects_wrong_schema_or_wrong_workstream_identity():
    bad = canonical_mission()
    bad["schema"] = "glaciereq.scale-fde.mission.v1"
    with pytest.raises(MissionOrchestrationError, match="schema"):
        run_mission(bad, launchers(), dispatch=lambda spec: {"status": "success"})

    bad = canonical_mission()
    bad["workstreams"]["B"] = "invented_runtime"
    with pytest.raises(MissionOrchestrationError, match="canonical workstream"):
        run_mission(bad, launchers(), dispatch=lambda spec: {"status": "success"})


def test_resume_binds_both_mission_and_launcher_contracts():
    mission = canonical_mission()
    binding = launchers()
    prior = {
        "mission_digest": mission_digest(mission),
        "launcher_digest": launcher_digest(binding),
        "completed": ["A", "B"],
        "failed": [],
        "in_flight": [],
        "receipts": {},
    }
    calls: list[str] = []

    result = run_mission(
        mission,
        binding,
        dispatch=lambda spec: (
            calls.append(spec["id"]) or {"status": "success", "returncode": 0}
        ),
        prior_state=prior,
    )

    assert set(calls) == {"C", "D", "E"}
    assert result["status"] == "LAUNCH_COMPLETE"

    changed = launchers()
    changed["workstreams"]["C"]["command"] = [
        sys.executable,
        "-c",
        "print('changed')",
    ]
    with pytest.raises(MissionOrchestrationError, match="launcher digest"):
        run_mission(
            mission,
            changed,
            dispatch=lambda spec: {"status": "success"},
            prior_state=prior,
        )


def test_process_failure_blocks_only_declared_dependents():
    binding = launchers()
    binding["workstreams"]["C"]["deps"] = ["B"]

    calls: list[str] = []

    def dispatch(spec: dict) -> dict:
        calls.append(spec["id"])
        if spec["id"] == "B":
            return {"status": "failed", "returncode": 2}
        return {"status": "success", "returncode": 0}

    result = run_mission(canonical_mission(), binding, dispatch=dispatch)

    assert result["status"] == "LAUNCH_BLOCKED"
    assert result["failed"] == ["B"]
    assert result["blocked"] == ["C"]
    assert "C" not in calls
    assert set(calls) == {"A", "B", "D", "E"}


def test_completion_artifact_can_recover_already_finished_work_without_relaunch(
    tmp_path: Path,
):
    artifact = tmp_path / "WORKSTREAM_A.json"
    artifact.write_text(
        json.dumps({"terminal_condition": {"workstream_a_complete": True}}),
        encoding="utf-8",
    )
    binding = launchers()
    binding["workstreams"]["A"]["completion"] = {
        "artifact": str(artifact),
        "pointer": "terminal_condition.workstream_a_complete",
        "equals": True,
    }
    calls: list[str] = []

    result = run_mission(
        canonical_mission(),
        binding,
        dispatch=lambda spec: (
            calls.append(spec["id"]) or {"status": "success", "returncode": 0}
        ),
    )

    assert "A" not in calls
    assert set(calls) == {"B", "C", "D", "E"}
    assert result["receipts"]["A"]["source"] == "completion_artifact_recovery"


def test_subprocess_completion_readback_outweighs_zero_exit(tmp_path: Path):
    artifact = tmp_path / "WORKSTREAM_A.json"
    artifact.write_text(
        json.dumps({"terminal_condition": {"workstream_a_complete": False}}),
        encoding="utf-8",
    )
    spec = {
        "id": "A",
        "deps": [],
        "command": [sys.executable, "-c", "raise SystemExit(0)"],
        "completion": {
            "artifact": str(artifact),
            "pointer": "terminal_condition.workstream_a_complete",
            "equals": True,
        },
    }

    result = subprocess_dispatch(spec)

    assert result["returncode"] == 0
    assert result["transport_status"] == "success"
    assert result["status"] == "failed"
    assert result["completion_check"]["satisfied"] is False


def test_checkpoint_records_in_flight_before_launch():
    checkpoints: list[dict] = []
    result = run_mission(
        canonical_mission(),
        launchers(),
        dispatch=lambda spec: {"status": "success", "returncode": 0},
        checkpoint=lambda state: checkpoints.append(dict(state)),
    )

    assert result["status"] == "LAUNCH_COMPLETE"
    assert checkpoints[0]["in_flight"] == ["A"]
    assert any(
        set(item["in_flight"]) == {"B", "C", "D", "E"}
        for item in checkpoints
    )
    assert checkpoints[-1]["in_flight"] == []


def test_ambiguous_in_flight_fails_closed_unless_readback_or_explicit_retry(
    tmp_path: Path,
):
    mission = canonical_mission()
    binding = launchers()
    prior = {
        "mission_digest": mission_digest(mission),
        "launcher_digest": launcher_digest(binding),
        "completed": [],
        "failed": [],
        "in_flight": ["A"],
        "receipts": {},
    }

    with pytest.raises(MissionOrchestrationError, match="ambiguous in-flight"):
        run_mission(
            mission,
            binding,
            dispatch=lambda spec: {"status": "success"},
            prior_state=prior,
        )

    calls: list[str] = []
    result = run_mission(
        mission,
        binding,
        dispatch=lambda spec: (
            calls.append(spec["id"]) or {"status": "success", "returncode": 0}
        ),
        prior_state=prior,
        retry_ambiguous=True,
    )
    assert result["status"] == "LAUNCH_COMPLETE"
    assert calls[0] == "A"

    artifact = tmp_path / "WORKSTREAM_A.json"
    artifact.write_text(
        json.dumps({"terminal_condition": {"workstream_a_complete": True}}),
        encoding="utf-8",
    )
    binding2 = launchers()
    binding2["workstreams"]["A"]["completion"] = {
        "artifact": str(artifact),
        "pointer": "terminal_condition.workstream_a_complete",
        "equals": True,
    }
    prior2 = {
        "mission_digest": mission_digest(mission),
        "launcher_digest": launcher_digest(binding2),
        "completed": [],
        "failed": [],
        "in_flight": ["A"],
        "receipts": {},
    }
    calls.clear()
    result = run_mission(
        mission,
        binding2,
        dispatch=lambda spec: (
            calls.append(spec["id"]) or {"status": "success", "returncode": 0}
        ),
        prior_state=prior2,
    )
    assert "A" not in calls
    assert result["receipts"]["A"]["source"] == "ambiguous_readback_recovery"


def test_failed_launch_requires_explicit_retry():
    mission = canonical_mission()
    binding = launchers()
    prior = {
        "mission_digest": mission_digest(mission),
        "launcher_digest": launcher_digest(binding),
        "completed": [],
        "failed": ["A"],
        "in_flight": [],
        "receipts": {"A": {"status": "failed", "returncode": 9}},
    }
    calls: list[str] = []

    result = run_mission(
        mission,
        binding,
        dispatch=lambda spec: (
            calls.append(spec["id"]) or {"status": "success", "returncode": 0}
        ),
        prior_state=prior,
    )
    assert calls == []
    assert result["status"] == "LAUNCH_BLOCKED"

    result = run_mission(
        mission,
        binding,
        dispatch=lambda spec: (
            calls.append(spec["id"]) or {"status": "success", "returncode": 0}
        ),
        prior_state=prior,
        retry_failed=True,
    )
    assert result["status"] == "LAUNCH_COMPLETE"
    assert calls[0] == "A"


def test_subprocess_dispatch_never_uses_shell_and_hashes_receipt(tmp_path: Path):
    result = subprocess_dispatch(
        {
            "id": "A",
            "deps": [],
            "command": [sys.executable, "-c", "print('orchestrated')"],
            "cwd": str(tmp_path),
            "timeout_seconds": 10,
        }
    )

    assert result["status"] == "success"
    assert result["returncode"] == 0
    assert result["stdout_sha256"].startswith("sha256:")
    assert result["stderr_sha256"].startswith("sha256:")
    assert result["stdout_preview"].strip() == "orchestrated"
    assert result["shell"] is False


def test_loaders_read_canonical_mission_and_separate_launcher_contract(tmp_path: Path):
    mission_path = tmp_path / "SCALE_FDE_MISSION.yaml"
    mission_path.write_text(
        """
schema: glaciereq.scale-fde-mission.v1
id: SCALE-FDE-DEMO-001
revision: 2
objective: prove mission
terminal_condition: independently verified
workstreams:
  A: estate_intelligence_gatling
  B: runtime_swarm_durability
  C: memory_composition_compounding
  D: integration_mcp_sigma_glue
  E: independent_verification_scale_product
""".strip()
        + "\n",
        encoding="utf-8",
    )
    launch_path = tmp_path / "launchers.yaml"
    launch_path.write_text(
        f"""
schema: glaciereq.scale-fde-launchers.v1
max_workers: 4
workstreams:
  A: {{deps: [], command: [{json.dumps(sys.executable)}, -c, "raise SystemExit(0)"]}}
  B: {{deps: [A], command: [{json.dumps(sys.executable)}, -c, "raise SystemExit(0)"]}}
  C: {{deps: [A], command: [{json.dumps(sys.executable)}, -c, "raise SystemExit(0)"]}}
  D: {{deps: [A], command: [{json.dumps(sys.executable)}, -c, "raise SystemExit(0)"]}}
  E: {{deps: [A], command: [{json.dumps(sys.executable)}, -c, "raise SystemExit(0)"]}}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    mission = load_mission(mission_path)
    binding = load_launchers(launch_path)

    assert mission["id"] == "SCALE-FDE-DEMO-001"
    assert set(mission["workstreams"]) == set("ABCDE")
    assert binding["max_workers"] == 4
    assert set(binding["workstreams"]) == set("ABCDE")
