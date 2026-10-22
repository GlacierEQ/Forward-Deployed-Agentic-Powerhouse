"""Legal WORM mega-run — organize and hash-lock the operator's legal repos.

This is the activation of the longest-horizon skill against the legal estate:
  * INVENTORY   — discover legal artifacts across the known legal repos;
  * ORGANIZE    — extract each module's purpose (docstring + top-level symbols)
                  and emit a human-readable ORGANIZATION map;
  * WORM-LOCK   — SHA-256 every artifact and store it in an Aspen-Grove pointer
                  index, so the set of legal artifacts is immutable + verifiable;
  * VERIFY      — re-scan and assert every digest still matches (tamper-evident).

WORM here means Write-Once-Read-Many: the manifest is the trusted anchor; any
later change to a legal artifact is detected, not silently accepted. This stops
hallucinated "evidence unchanged" claims — it does not block legitimate work.
"""
from __future__ import annotations

import ast
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from framework.aspen_grove import AspenGrove
from framework.hardening import atomic_write

DEFAULT_LEGAL_REPOS = [
    "apex_case_framework",
    "computer-user/case_brain",
    "computer-user/skills/legal-motion-template",
]

_SCANNABLE = {".py", ".md", ".json", ".yaml", ".yml", ".txt", ".sql", ".env.example"}


def _digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _summarize_py(path: Path) -> Dict[str, object]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError):
        return {"doc": "", "symbols": []}
    doc = ast.get_docstring(tree) or ""
    symbols = [
        n.name
        for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]
    return {"doc": doc.splitlines()[0] if doc else "", "symbols": symbols}


def _summarize_md(path: Path) -> Dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    return {"doc": first, "symbols": []}


@dataclass
class WormReport:
    repos_scanned: int
    artifacts: int
    manifest_path: str
    pointer_index_path: str
    organization_path: str


def run_legal_worm(
    repos: List[str] | None = None,
    output_root: str | Path = "/root/legal_mesh_worm",
    base: str | Path = "/root",
) -> WormReport:
    repos = repos or list(DEFAULT_LEGAL_REPOS)
    out = Path(output_root)
    grove = AspenGrove(out / "worm_grove")
    manifest: Dict[str, object] = {
        "generated_at": time.time(),
        "base": str(base),
        "repos": {},
        "artifacts": [],
    }

    for repo in repos:
        rpath = Path(base) / repo
        if not rpath.exists():
            continue
        repo_artifacts: List[Dict[str, object]] = []
        for f in sorted(rpath.rglob("*")):
            if not f.is_file():
                continue
            if ".git" in f.parts:
                continue
            if f.suffix not in _SCANNABLE:
                continue
            digest = _digest_file(f)
            rel = str(f.relative_to(rpath))
            meta: Dict[str, object] = {
                "repo": repo,
                "path": rel,
                "ext": f.suffix,
                "bytes": f.stat().st_size,
                "digest": digest,
            }
            if f.suffix == ".py":
                meta.update(_summarize_py(f))
            elif f.suffix == ".md":
                meta.update(_summarize_md(f))
            grove.remember("legal_artifact", meta, source=repo)
            repo_artifacts.append(meta)
        manifest["repos"][repo] = {  # type: ignore[index]
            "artifact_count": len(repo_artifacts),
            "artifacts": repo_artifacts,
        }
        manifest["artifacts"].extend(repo_artifacts)  # type: ignore[arg-type]

    manifest_path = out / "legal_worm_manifest.json"
    atomic_write(manifest_path, json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8"))

    organization_path = out / "ORGANIZATION.md"
    atomic_write(organization_path, _render_organization(manifest).encode("utf-8"))

    return WormReport(
        repos_scanned=len(manifest["repos"]),  # type: ignore[arg-type]
        artifacts=len(manifest["artifacts"]),  # type: ignore[arg-type]
        manifest_path=str(manifest_path),
        pointer_index_path=str(grove.root / "pointer_index.json"),
        organization_path=str(organization_path),
    )


def _render_organization(manifest: Dict[str, object]) -> str:
    lines = ["# Legal Estate — Organization Map", ""]
    lines.append(f"_Generated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(manifest['generated_at']))}_")
    lines.append(f"_Artifacts WORM-locked: {len(manifest['artifacts'])}_\n")  # type: ignore[arg-type]
    repos = manifest["repos"]  # type: ignore[assignment]
    for repo, info in repos.items():  # type: ignore[union-attr]
        assert isinstance(info, dict)
        lines.append(f"## {repo}")
        lines.append(f"Artifacts: {info['artifact_count']}\n")
        for art in info["artifacts"]:  # type: ignore[union-attr]
            assert isinstance(art, dict)
            doc = art.get("doc") or "(no summary)"
            sym = ", ".join(art.get("symbols") or [])  # type: ignore[union-attr]
            lines.append(f"- `{art['path']}` — {doc}")
            if sym:
                lines.append(f"    symbols: {sym}")
        lines.append("")
    return "\n".join(lines)


def verify_legal_worm(
    output_root: str | Path = "/root/legal_mesh_worm",
    base: str | Path = "/root",
) -> Dict[str, object]:
    """Re-scan the repos and assert every current digest matches the manifest.

    Returns a report; any mismatch means a legal artifact changed since locking.
    """
    manifest_path = Path(output_root) / "legal_worm_manifest.json"
    if not manifest_path.is_file():
        return {"ok": False, "reason": "manifest missing"}
    manifest = json.loads(manifest_path.read_text())
    mismatches: List[str] = []
    missing: List[str] = []
    for art in manifest["artifacts"]:  # type: ignore[union-attr]
        assert isinstance(art, dict)
        f = Path(base) / art["repo"] / art["path"]  # type: ignore[index]
        if not f.is_file():
            missing.append(f"{art['repo']}/{art['path']}")
            continue
        if _digest_file(f) != art["digest"]:
            mismatches.append(f"{art['repo']}/{art['path']}")
    return {
        "ok": not mismatches and not missing,
        "mismatches": mismatches,
        "missing": missing,
        "verified": len(manifest["artifacts"]) - len(mismatches) - len(missing),  # type: ignore[arg-type]
        "total": len(manifest["artifacts"]),  # type: ignore[arg-type]
    }

# WHY: Explaining resilience and recovery rationale ensures non-blocking operational continuity.
