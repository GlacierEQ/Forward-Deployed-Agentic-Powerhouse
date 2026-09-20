"""Zero-to-hero cycle tests."""

from pathlib import Path

from fde_powerhouse.cycle import run_cycle
from fde_powerhouse.modes import MODES
from fde_powerhouse.receipts import CycleReceipt


def test_ground_up_cycle(tmp_path: Path):
    receipt = run_cycle("ground_up", target="hero-demo", work_dir=tmp_path)
    assert isinstance(receipt, CycleReceipt)
    assert receipt.status == "ok"
    assert len(receipt.stages) == 7
    assert receipt.stages[0].stage == "discover"
    assert receipt.stages[-1].stage == "deploy"
    assert receipt.digest()


def test_all_modes_run(tmp_path: Path):
    for mode in MODES:
        r = run_cycle(mode, target=f"t-{mode}", work_dir=tmp_path)
        assert r.status == "ok", mode
        assert r.mode == mode


def test_receipt_hash_stable_fields(tmp_path: Path):
    r = run_cycle("compose", target="compose-demo", work_dir=tmp_path)
    d1 = r.digest()
    d2 = r.digest()
    assert d1 == d2
    assert len(d1) == 64


def test_compose_includes_graph(tmp_path: Path):
    r = run_cycle("compose", target="c1", work_dir=tmp_path)
    integ = next(s for s in r.stages if s.stage == "integrate")
    assert "compose_graph" in integ.evidence
