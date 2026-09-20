from pathlib import Path

from fde_powerhouse.invert_scan import load_rules, scan_path, write_report


def test_rules_load():
    cfg = load_rules()
    assert cfg.get("schema", "").startswith("fde.inversion")
    assert len(cfg.get("rules") or []) >= 5


def test_scan_detects_bounded_minimum(tmp_path: Path):
    f = tmp_path / "bad.md"
    f.write_text("We enforce a bounded minimum on all work.\n")
    report = scan_path(tmp_path)
    assert report.status == "findings"
    assert any(x.rule_id == "bounded_minimum" for x in report.findings)


def test_scan_clean(tmp_path: Path):
    f = tmp_path / "ok.py"
    f.write_text("def ship():\n    return 'full power'\n")
    report = scan_path(tmp_path)
    assert report.status == "clean"
    assert report.findings == []


def test_semantic_cluster(tmp_path: Path):
    f = tmp_path / "toxic.md"
    f.write_text(
        "bounded minimum\n"
        "do the minimum\n"
        "downward scope everywhere\n"
    )
    report = scan_path(tmp_path)
    assert "ambition_collapse" in report.clusters_hit or any(
        f.layer == "cluster" for f in report.findings
    )


def test_negation_softens(tmp_path: Path):
    f = tmp_path / "meta.md"
    f.write_text(
        "This scanner must detect bounded minimum as an anti-pattern to forbid.\n"
    )
    report = scan_path(tmp_path)
    hits = [x for x in report.findings if x.rule_id == "bounded_minimum"]
    if hits:
        assert hits[0].confidence < 1.0


def test_write_report(tmp_path: Path):
    (tmp_path / "x.md").write_text("hello\n")
    report = scan_path(tmp_path)
    path = write_report(report, tmp_path / "out")
    assert path.is_file()
    assert (tmp_path / "out" / "INVERT_SCAN.md").is_file()
    assert report.to_dict()["sha256"]
