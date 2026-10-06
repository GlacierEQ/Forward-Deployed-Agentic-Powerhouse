from pathlib import Path

from fde_powerhouse.scale_control_plane import ScaleControlPlane


def _verified_receipt(output: str, tag: str) -> dict[str, object]:
    return {
        "revision": tag,
        "tests": [
            {
                "name": "pytest",
                "state": "passed",
                "source": f"runner://test/{tag}",
            }
        ],
        "outputs": [
            {
                "path": output,
                "state": "verified",
                "source": f"artifact://test/{tag}/{output}",
            }
        ],
        "readback": {
            "state": "verified",
            "source": f"provider://test/{tag}",
        },
    }


def test_shared_contract_has_five_exclusive_workstreams(
    tmp_path: Path,
) -> None:
    cp = ScaleControlPlane.bootstrap(tmp_path)
    state = cp.snapshot()
    assert set(state["workstreams"]) == set("ABCDE")
    assert state["mission"]["status"] == "active"
    assert state["mission"]["frontier_exhausted"] is False
    assert (tmp_path / "SCALE_FDE_MISSION.yaml").exists()
    assert (tmp_path / "ARCHITECTURE_CONTRACT.json").exists()


def test_receipt_closes_task_and_advances_frontier(tmp_path: Path) -> None:
    cp = ScaleControlPlane.bootstrap(tmp_path)
    output = "SCALE_CAPABILITY_GRAPH.json"
    cp.enqueue("A", "estate-discovery", outputs=[output])
    cp.claim("A", "estate-discovery")
    cp.complete(
        "A",
        "estate-discovery",
        receipt=_verified_receipt(output, "abc123"),
    )
    state = cp.snapshot()
    assert state["workstreams"]["A"]["tasks"]["estate-discovery"]["status"] == (
        "verified"
    )
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


def test_mission_only_exhausts_when_every_workstream_is_verified(
    tmp_path: Path,
) -> None:
    cp = ScaleControlPlane.bootstrap(tmp_path)
    for worker in "ABCDE":
        task = f"task-{worker}"
        output = f"WORKSTREAM_{worker}.json"
        cp.enqueue(worker, task, outputs=[output])
        cp.claim(worker, task)
        cp.complete(
            worker,
            task,
            receipt=_verified_receipt(output, worker),
        )
    state = cp.snapshot()
    assert state["mission"]["frontier_exhausted"] is True
    assert state["mission"]["status"] == "verified"


def test_canonical_contracts_materialize_under_shared_directory(
    tmp_path: Path,
) -> None:
    ScaleControlPlane.bootstrap(tmp_path)

    shared = tmp_path / "shared"
    assert (shared / "SCALE_FDE_MISSION.yaml").exists()
    assert (shared / "ARCHITECTURE_CONTRACT.json").exists()
    assert (shared / "SCALE_CAPABILITY_GRAPH.json").exists()
    assert (shared / "INTEGRATION_QUEUE.json").exists()
    assert (shared / "DEFECT_QUEUE.json").exists()
    assert (shared / "RECEIPT_INDEX.json").exists()
    for worker in "ABCDE":
        assert (shared / f"WORKSTREAM_{worker}.json").exists()


def test_materialization_does_not_overwrite_richer_worker_artifact(
    tmp_path: Path,
) -> None:
    shared = tmp_path / "shared"
    shared.mkdir()
    worker_artifact = shared / "WORKSTREAM_A.json"
    worker_artifact.write_text(
        '{"schema":"glaciereq.scale-fde.workstream.v1",'
        '"workstream":"A","state":"COMPLETE_WITH_EVIDENCE"}\n'
    )

    ScaleControlPlane.bootstrap(tmp_path)

    assert '"state":"COMPLETE_WITH_EVIDENCE"' in worker_artifact.read_text()


def test_materialization_preserves_richer_shared_contracts(
    tmp_path: Path,
) -> None:
    shared = tmp_path / "shared"
    shared.mkdir()
    mission = shared / "SCALE_FDE_MISSION.yaml"
    architecture = shared / "ARCHITECTURE_CONTRACT.json"
    mission_source = (
        "schema: glaciereq.scale-fde-mission.v1\n"
        "revision: 99\n"
        "principles:\n"
        "  - preserve_stronger_existing_capability\n"
        "  - operator_semantic_sovereignty\n"
    )
    architecture_source = (
        '{"schema":"glaciereq.scale-fde-architecture.v99",'
        '"invariants":["preserve richer source"]}\n'
    )
    mission.write_text(mission_source)
    architecture.write_text(architecture_source)

    ScaleControlPlane.bootstrap(tmp_path)

    assert mission.read_text() == mission_source
    assert architecture.read_text() == architecture_source
