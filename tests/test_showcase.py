from pathlib import Path

from fde_powerhouse.proof_pack import proof_pack
from fde_powerhouse.showcase import run_showcase


def test_showcase_writes_artifacts(tmp_path: Path):
    pack = run_showcase(target="demo", work_dir=tmp_path, mode="compose")
    assert pack.cycle.get("status") == "ok"
    assert len(pack.composition_matrix) >= 6
    assert len(pack.impressiveness_signals) >= 4
    out = tmp_path / ".fde" / "showcase_demo"
    assert (out / "SHOWCASE.json").is_file()
    assert (out / "OPERATOR_CARD.md").is_file()
    assert (out / "COMPOSITION.md").is_file()


def test_proof_pack_structure():
    p = proof_pack()
    assert p["identity"] == "Forward Deployed Agentic AI"
    assert p["estate"]["mega_skills"]["atomic"] == 709
    assert p["leading_edge"]["sources"] >= 40
    assert "is" in p["claims"] and "is_not" in p["claims"]
