from pathlib import Path

from fde_powerhouse.edge_store import history_summary, load_latest, persist_probe


def test_persist_and_history(tmp_path: Path):
    # limit 1 to keep network light
    result = persist_probe(work_dir=tmp_path, limit=1)
    assert Path(result["path"]).is_file()
    assert Path(result["latest"]).is_file()
    latest = load_latest(tmp_path)
    assert latest is not None
    assert "sha256" in latest
    hist = history_summary(tmp_path)
    assert hist["count"] >= 1
