"""CLI smoke — lifts coverage on cmd entrypoints."""

import json

from fde_powerhouse.cli import main


def test_doctor(capsys):
    assert main(["doctor"]) == 0
    out = capsys.readouterr().out
    assert "fde-powerhouse" in out


def test_proof(capsys):
    assert main(["proof"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert "is" in data or "identity" in data or isinstance(data, dict)


def test_leverage_summary(capsys):
    assert main(["leverage", "--summary"]) == 0


def test_edge_stats(capsys):
    assert main(["edge", "--stats"]) == 0


def test_estate(capsys):
    assert main(["estate"]) == 0


def test_probe(capsys):
    assert main(["probe"]) == 0


def test_invert_scan_clean(tmp_path, capsys):
    (tmp_path / "ok.py").write_text("x = 1\n")
    rc = main(["invert-scan", "--target", str(tmp_path), "--work-dir", str(tmp_path)])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["status"] in ("clean", "findings")


def test_cycle_ground_up(tmp_path, capsys):
    rc = main([
        "cycle", "--mode", "ground_up", "--name", "cli-hero",
        "--work-dir", str(tmp_path),
    ])
    assert rc == 0


def test_scan(tmp_path, capsys):
    (tmp_path / "a.py").write_text("print(1)\n")
    assert main(["scan", "--target", str(tmp_path)]) == 0


def test_genius_brief(capsys):
    assert main(["genius", "--brief"]) == 0
