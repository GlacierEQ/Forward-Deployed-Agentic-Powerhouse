from __future__ import annotations

from pathlib import Path

from fde_powerhouse.scale_orchestrator import load_launchers


def test_checked_in_scale_launcher_bindings_are_complete_and_real():
    config = load_launchers(Path("configs/scale_launchers.yaml"))

    assert config["schema"] == "glaciereq.scale-fde-launchers.v1"
    assert config["max_workers"] == 4
    assert set(config["workstreams"]) == set("ABCDE")

    a = config["workstreams"]["A"]
    assert a["command"] is None
    assert a["completion"] == {
        "artifact": "shared/WORKSTREAM_A.json",
        "pointer": "terminal_condition.workstream_a_complete",
        "equals": True,
    }

    b = config["workstreams"]["B"]
    assert b["source_repository"] == "GlacierEQ/computer-user"
    assert b["source_branch"] == "scale/runtime-swarm"
    assert b["source_revision"] == "dd9ea50bce265d5ffc235999909e4ee9b08a4732"
    assert b["cwd"] == "${SCALE_FDE_RUNTIME_SWARM_ROOT}"
    assert b["command"] == [
        "python3",
        "-m",
        "pytest",
        "-q",
        "tests/test_scale_runtime_durability.py",
    ]

    c = config["workstreams"]["C"]
    assert c["source_repository"] == "GlacierEQ/Forward-Deployed-Agentic-Powerhouse"
    assert c["source_branch"] == "scale/memory-composition"
    assert c["source_revision"] == "7bbafb8d6d6eb156cc2527bdb8df53f3c08f197e"
    assert c["cwd"] == "${SCALE_FDE_MEMORY_COMPOSITION_ROOT}"
    assert c["command"][:3] == ["python3", "-m", "fde_powerhouse.scale_compounding"]
    assert "prove" in c["command"]

    d = config["workstreams"]["D"]
    assert d["source_repository"] == "GlacierEQ/sigma-glue"
    assert d["source_branch"] == "scale/integration-mcp"
    assert d["source_revision"] == "a910c04402d99ea811c19a7700ea879ed9e267e7"
    assert d["cwd"] == "${SCALE_FDE_INTEGRATION_MCP_ROOT}"
    assert d["command"] == [
        "node",
        "--test",
        "tests/scale-multi-provider-integration.test.mjs",
        "tests/provider-boundary-proof.test.mjs",
    ]

    e = config["workstreams"]["E"]
    assert e["source_repository"] == "GlacierEQ/computer-user"
    assert e["source_branch"] == "scale/verification-product"
    assert e["source_revision"] == "d0550aa93896343c01b4f9aaf80c845b7e4dcf90"
    assert e["cwd"] == "${SCALE_FDE_VERIFICATION_PRODUCT_ROOT}"
    assert e["command"] == ["bash", "scripts/ci/scale_agent_e_verify.sh"]

    assert all(
        item["deps"] == ["A"]
        for key, item in config["workstreams"].items()
        if key != "A"
    )
