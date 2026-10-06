from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path

import pytest

from fde_powerhouse.scale_orchestrator import (
    MissionOrchestrationError,
    load_mission,
    mission_digest,
    run_mission,
    subprocess_dispatch,
)


def mission(command: list[str] | None = None) -> dict:
    command = command or [sys.executable, "-c", "raise SystemExit(0)"]
    return {
        "schema": "glaciereq.scale-fde.mission.v1",
        "mission_id": "scale-fde-demo",
        "orchestrator": {"max_workers": 4},
        "workstreams": [
            {"id": "A", "deps": [], "command": command},
            {"id": "B", "deps": ["A"], "command": command},
            {"id": "C", "deps": ["A"], "command": command},
            {"id": "D", "deps": ["A"], "command": command},
            {"id": "E", "deps": ["A"], "command": command},
        ],
    }


def test_mission_digest_is_stable_for_mapping_order():
    left = mission()
    right = {
        "mission_id": left["mission_id"],
        "workstreams": left["workstreams"],
        "orchestrator": left["orchestrator"],
        "schema": left["schema"],
    }

    assert mission_digest(left) == mission_digest(right)
    assert mission_digest(left).startswith("sha256:")


def test_run_mission_fires_dependency_ready_workstreams_in_bounded_parallel():
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

    result = run_mission(mission(), dispatch=dispatch)

    assert result["status"] == "COMPLETE"
    assert result["completed"] == ["A", "B", "C", "D", "E"]
    assert result["failed"] == []
    assert result["blocked"] == []
    assert calls[0] == "A"
    assert set(calls[1:]) == {"B", "C", "D", "E"}
    assert 1 < max_active <= 4
    assert result["waves"] == [["A"], ["B", "C", "D", "E"]]


def test_run_mission_preserves_failure_and_never_launches_blocked_dependents():
    calls: list[str] = []

    def dispatch(spec: dict) -> dict:
        calls.append(spec["id"])
        if spec["id"] == "A":
            return {"status": "failed", "returncode": 2}
        return {"status": "success", "returncode": 0}

    result = run_mission(mission(), dispatch=dispatch)

    assert result["status"] == "BLOCKED"
    assert calls == ["A"]
    assert result["completed"] == []
    assert result["failed"] == ["A"]
    assert result["blocked"] == ["B", "C", "D", "E"]


def test_run_mission_resume_skips_completed_work_and_launches_remaining_frontier():
    calls: list[str] = []
    prior = {
        "mission_digest": mission_digest(mission()),
        "completed": ["A", "B"],
        "failed": [],
    }

    def dispatch(spec: dict) -> dict:
        calls.append(spec["id"])
        return {"status": "success", "returncode": 0}

    result = run_mission(mission(), dispatch=dispatch, prior_state=prior)

    assert result["status"] == "COMPLETE"
    assert set(calls) == {"C", "D", "E"}
    assert len(calls) == 3
    assert result["completed"] == ["A", "B", "C", "D", "E"]


def test_resume_rejects_state_from_different_mission():
    prior = {
        "mission_digest": "sha256:" + "0" * 64,
        "completed": ["A"],
        "failed": [],
    }

    with pytest.raises(MissionOrchestrationError, match="mission digest"):
        run_mission(mission(), dispatch=lambda spec: {"status": "success"}, prior_state=prior)


def test_mission_validation_rejects_cycles_unknown_dependencies_and_shell_strings():
    cyc = mission()
    cyc["workstreams"][0]["deps"] = ["E"]
    with pytest.raises(MissionOrchestrationError, match="cycle"):
        run_mission(cyc, dispatch=lambda spec: {"status": "success"})

    unknown = mission()
    unknown["workstreams"][1]["deps"] = ["NOPE"]
    with pytest.raises(MissionOrchestrationError, match="unknown dependency"):
        run_mission(unknown, dispatch=lambda spec: {"status": "success"})

    unsafe = mission()
    unsafe["workstreams"][0]["command"] = "echo nope"
    with pytest.raises(MissionOrchestrationError, match="command"):
        run_mission(unsafe, dispatch=lambda spec: {"status": "success"})


def test_subprocess_dispatch_executes_without_shell_and_returns_digest_receipt(tmp_path: Path):
    spec = {
        "id": "A",
        "deps": [],
        "command": [
            sys.executable,
            "-c",
            "print('orchestrated')",
        ],
        "cwd": str(tmp_path),
        "timeout_seconds": 10,
    }

    result = subprocess_dispatch(spec)

    assert result["status"] == "success"
    assert result["returncode"] == 0
    assert result["stdout_sha256"].startswith("sha256:")
    assert result["stderr_sha256"].startswith("sha256:")
    assert result["stdout_preview"].strip() == "orchestrated"
    assert result["shell"] is False


def test_load_mission_reads_yaml_mapping(tmp_path: Path):
    path = tmp_path / "mission.yaml"
    path.write_text(
        """
schema: glaciereq.scale-fde.mission.v1
mission_id: scale-fde-demo
orchestrator:
  max_workers: 4
workstreams:
  - id: A
    deps: []
    command: [python, -c, "raise SystemExit(0)"]
""".strip()
        + "\n",
        encoding="utf-8",
    )

    loaded = load_mission(path)

    assert loaded["mission_id"] == "scale-fde-demo"
    assert loaded["orchestrator"]["max_workers"] == 4


def test_result_is_json_serializable_and_contains_launch_receipts():
    result = run_mission(
        mission(),
        dispatch=lambda spec: {
            "status": "success",
            "returncode": 0,
            "worker": spec["id"],
        },
    )

    rendered = json.dumps(result, sort_keys=True)
    assert '"status": "COMPLETE"' in rendered
    assert set(result["receipts"]) == {"A", "B", "C", "D", "E"}



def test_completion_artifact_recovery_skips_already_complete_workstream(tmp_path: Path):
    artifact = tmp_path / "WORKSTREAM_A.json"
    artifact.write_text(
        json.dumps({"terminal_condition": {"workstream_a_complete": True}}),
        encoding="utf-8",
    )
    m = mission()
    m["workstreams"][0]["completion"] = {
        "artifact": str(artifact),
        "pointer": "terminal_condition.workstream_a_complete",
        "equals": True,
    }
    calls: list[str] = []

    result = run_mission(
        m,
        dispatch=lambda spec: (
            calls.append(spec["id"])
            or {"status": "success", "returncode": 0}
        ),
    )

    assert "A" not in calls
    assert set(calls) == {"B", "C", "D", "E"}
    assert result["completed"] == ["A", "B", "C", "D", "E"]
    assert result["receipts"]["A"]["source"] == "completion_artifact_recovery"


def test_subprocess_success_is_not_completion_when_terminal_artifact_is_false(
    tmp_path: Path,
):
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
    assert result["status"] == "failed"
    assert result["completion_check"]["satisfied"] is False
    assert result["completion_check"]["observed"] is False


def test_checkpoint_marks_wave_in_flight_before_dispatch():
    checkpoints: list[dict] = []

    result = run_mission(
        mission(),
        dispatch=lambda spec: {"status": "success", "returncode": 0},
        checkpoint=lambda state: checkpoints.append(dict(state)),
    )

    assert result["status"] == "COMPLETE"
    assert checkpoints[0]["in_flight"] == ["A"]
    assert any(
        set(state["in_flight"]) == {"B", "C", "D", "E"}
        for state in checkpoints
    )
    assert checkpoints[-1]["in_flight"] == []


def test_resume_with_ambiguous_in_flight_fails_closed_without_readback():
    m = mission()
    prior = {
        "mission_digest": mission_digest(m),
        "completed": [],
        "failed": [],
        "in_flight": ["A"],
        "receipts": {},
    }

    with pytest.raises(MissionOrchestrationError, match="ambiguous in-flight"):
        run_mission(
            m,
            dispatch=lambda spec: {"status": "success", "returncode": 0},
            prior_state=prior,
        )


def test_retry_ambiguous_requires_explicit_opt_in():
    m = mission()
    prior = {
        "mission_digest": mission_digest(m),
        "completed": [],
        "failed": [],
        "in_flight": ["A"],
        "receipts": {},
    }
    calls: list[str] = []

    result = run_mission(
        m,
        dispatch=lambda spec: (
            calls.append(spec["id"])
            or {"status": "success", "returncode": 0}
        ),
        prior_state=prior,
        retry_ambiguous=True,
    )

    assert result["status"] == "COMPLETE"
    assert calls[0] == "A"


def test_ambiguous_in_flight_resolves_from_terminal_artifact_before_replay(
    tmp_path: Path,
):
    artifact = tmp_path / "WORKSTREAM_A.json"
    artifact.write_text(
        json.dumps({"terminal_condition": {"workstream_a_complete": True}}),
        encoding="utf-8",
    )
    m = mission()
    m["workstreams"][0]["completion"] = {
        "artifact": str(artifact),
        "pointer": "terminal_condition.workstream_a_complete",
        "equals": True,
    }
    prior = {
        "mission_digest": mission_digest(m),
        "completed": [],
        "failed": [],
        "in_flight": ["A"],
        "receipts": {},
    }
    calls: list[str] = []

    result = run_mission(
        m,
        dispatch=lambda spec: (
            calls.append(spec["id"])
            or {"status": "success", "returncode": 0}
        ),
        prior_state=prior,
    )

    assert "A" not in calls
    assert result["receipts"]["A"]["source"] == "ambiguous_readback_recovery"
    assert result["status"] == "COMPLETE"



def test_failed_workstream_is_not_replayed_without_explicit_retry():
    m = mission()
    prior = {
        "mission_digest": mission_digest(m),
        "completed": [],
        "failed": ["A"],
        "in_flight": [],
        "receipts": {"A": {"status": "failed", "returncode": 9}},
    }
    calls: list[str] = []

    result = run_mission(
        m,
        dispatch=lambda spec: (
            calls.append(spec["id"])
            or {"status": "success", "returncode": 0}
        ),
        prior_state=prior,
    )

    assert calls == []
    assert result["status"] == "BLOCKED"
    assert result["failed"] == ["A"]


def test_retry_failed_requires_explicit_opt_in():
    m = mission()
    prior = {
        "mission_digest": mission_digest(m),
        "completed": [],
        "failed": ["A"],
        "in_flight": [],
        "receipts": {"A": {"status": "failed", "returncode": 9}},
    }
    calls: list[str] = []

    result = run_mission(
        m,
        dispatch=lambda spec: (
            calls.append(spec["id"])
            or {"status": "success", "returncode": 0}
        ),
        prior_state=prior,
        retry_failed=True,
    )

    assert result["status"] == "COMPLETE"
    assert calls[0] == "A"
    assert result["failed"] == []
