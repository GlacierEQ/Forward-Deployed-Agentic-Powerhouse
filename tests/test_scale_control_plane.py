from pathlib import Path

from fde_powerhouse.scale_control_plane import ScaleControlPlane


def test_shared_contract_has_five_exclusive_workstreams(tmp_path: Path) -> None:
    cp = ScaleControlPlane.bootstrap(tmp_path)
    state = cp.snapshot()
    assert set(state["workstreams"]) == set("ABCDE")
    assert state["mission"]["status"] == "active"
    assert state["mission"]["frontier_exhausted"] is False
    assert (tmp_path / "SCALE_FDE_MISSION.yaml").exists()
    assert (tmp_path / "ARCHITECTURE_CONTRACT.json").exists()


def test_receipt_closes_task_and_advances_frontier(tmp_path: Path) -> None:
    cp = ScaleControlPlane.bootstrap(tmp_path)
    cp.enqueue("A", "estate-discovery", outputs=["SCALE_CAPABILITY_GRAPH.json"])
    cp.claim("A", "estate-discovery")
    cp.complete("A", "estate-discovery", receipt={"revision": "abc123", "tests": ["pytest"]})
    state = cp.snapshot()
    assert state["workstreams"]["A"]["tasks"]["estate-discovery"]["status"] == "verified"
    assert state["receipts"][0]["revision"] == "abc123"


def test_cannot_complete_without_receipt(tmp_path: Path) -> None:
    cp = ScaleControlPlane.bootstrap(tmp_path)
    cp.enqueue("B", "runtime", outputs=["WORKSTREAM_B.json"])
    cp.claim("B", "runtime")
    try:
        cp.complete("B", "runtime", receipt={})
    except ValueError as exc:
        assert "receipt" in str(exc).lower()
    else:
        raise AssertionError("completion without evidence must fail")


def test_mission_only_exhausts_when_every_workstream_is_verified(tmp_path: Path) -> None:
    cp = ScaleControlPlane.bootstrap(tmp_path)
    for worker in "ABCDE":
        task = f"task-{worker}"
        cp.enqueue(worker, task, outputs=[f"WORKSTREAM_{worker}.json"])
        cp.claim(worker, task)
        cp.complete(worker, task, receipt={"revision": worker, "tests": ["contract"]})
    state = cp.snapshot()
    assert state["mission"]["frontier_exhausted"] is True
    assert state["mission"]["status"] == "verified"
