from pathlib import Path

from fde_powerhouse.plan import build_plan
from fde_powerhouse.scaffold import write_scaffold


def test_scaffold_writes_agent_package(tmp_path: Path):
    plan = build_plan("ground_up", "hero-agent")
    result = write_scaffold(tmp_path / "hero-agent", plan)
    assert result["count"] >= 7
    root = Path(result["root"])
    assert (root / "IDENTITY.md").is_file()
    assert (root / "PLAN.yaml").is_file()
    assert (root / "src/agent/orchestrator.py").is_file()
    assert (root / "src/agent/policy.py").is_file()
    assert (root / "src/agent/memory_port.py").is_file()
    assert (root / "src/agent/tools.py").is_file()
    assert (root / "tests/test_agent_loop.py").is_file()


def test_ground_up_cycle_creates_scaffold(tmp_path: Path):
    from fde_powerhouse.cycle import run_cycle

    r = run_cycle("ground_up", target="full-hero", work_dir=tmp_path)
    assert r.status == "ok"
    build = next(s for s in r.stages if s.stage == "build")
    assert build.evidence.get("count", 0) >= 7
