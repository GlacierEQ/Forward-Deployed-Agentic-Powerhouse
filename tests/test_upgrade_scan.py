from pathlib import Path

from fde_powerhouse.upgrade_scan import scan_target


def test_scan_missing():
    r = scan_target("/nonexistent/path/xyz")
    assert r["exists"] is False


def test_scan_self(tmp_path: Path):
    (tmp_path / "README.md").write_text("x")
    (tmp_path / "main.py").write_text("print(1)\n")
    r = scan_target(tmp_path)
    assert r["exists"] is True
    assert r["py_file_count"] >= 1
    assert "align_fde_cycle" in r["recommendations"]
