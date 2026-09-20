"""Upgrade/merge scan — inventory an existing tree for FDE upgrade."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def scan_target(target: str | Path) -> dict[str, Any]:
    root = Path(target)
    if not root.exists():
        return {"exists": False, "target": str(target), "error": "path not found"}

    py_files = list(root.rglob("*.py")) if root.is_dir() else []
    # cap walk cost
    py_files = py_files[:500]
    md_files = list(root.rglob("*.md"))[:100] if root.is_dir() else []
    has_tests = any("test" in str(p).lower() for p in py_files)
    has_pyproject = (root / "pyproject.toml").is_file() if root.is_dir() else False
    has_readme = (root / "README.md").is_file() if root.is_dir() else False
    has_ci = (root / ".github" / "workflows").is_dir() if root.is_dir() else False

    recommendations = []
    if not has_tests:
        recommendations.append("add_tests")
    if not has_pyproject:
        recommendations.append("add_pyproject")
    if not has_ci:
        recommendations.append("add_ci")
    if not has_readme:
        recommendations.append("add_readme")
    recommendations.extend([
        "align_fde_cycle",
        "wire_estate_bridges",
        "hash_bound_receipts",
        "approval_packet_only_deploy",
    ])

    return {
        "exists": True,
        "target": str(root.resolve()),
        "is_dir": root.is_dir(),
        "py_file_count": len(py_files),
        "md_file_count": len(md_files),
        "has_tests": has_tests,
        "has_pyproject": has_pyproject,
        "has_readme": has_readme,
        "has_ci": has_ci,
        "recommendations": recommendations,
        "fde_identity": "Forward Deployed Agentic AI",
    }
