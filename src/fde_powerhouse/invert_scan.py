"""Authority / quality inversion hunter — operator fidelity scan."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import yaml

DEFAULT_RULES = (
    Path(__file__).resolve().parents[2] / "configs" / "inversion_rules.yaml"
)

TEXT_SUFFIXES = {
    ".py", ".md", ".txt", ".yaml", ".yml", ".json", ".toml",
    ".ts", ".tsx", ".js", ".jsx", ".rs", ".go", ".sh", ".env.example",
}


@dataclass
class Finding:
    rule_id: str
    severity: str
    category: str
    description: str
    path: str
    line: int
    snippet: str
    pattern: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class InvertReport:
    scanned_at: str
    root: str
    files_scanned: int
    findings: list[Finding] = field(default_factory=list)
    by_severity: dict[str, int] = field(default_factory=dict)
    by_rule: dict[str, int] = field(default_factory=dict)
    status: str = "clean"  # clean | findings | error
    sha256: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = {
            "scanned_at": self.scanned_at,
            "root": self.root,
            "files_scanned": self.files_scanned,
            "findings": [f.to_dict() for f in self.findings],
            "by_severity": self.by_severity,
            "by_rule": self.by_rule,
            "status": self.status,
            "count": len(self.findings),
        }
        payload = json.dumps(d, sort_keys=True, default=str)
        d["sha256"] = hashlib.sha256(payload.encode()).hexdigest()
        return d


def load_rules(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_RULES
    with p.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _excluded(path: Path, root: Path, globs: list[str]) -> bool:
    rel = path.relative_to(root).as_posix()
    parts = set(path.parts)
    if any(x in parts for x in (".git", "node_modules", ".venv", "venv", "__pycache__", ".fde")):
        return True
    for g in globs:
        # simple segment match
        g2 = g.replace("**/", "").replace("/**", "").strip("*")
        if g2 and g2 in rel:
            return True
    return False


def _iter_files(root: Path, exclude_globs: list[str]) -> Iterator[Path]:
    if root.is_file():
        yield root
        return
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in TEXT_SUFFIXES and p.name not in (
            "Dockerfile", "Makefile", "SKILL.md", "COMBO.md", "MEGA.md"
        ):
            continue
        if _excluded(p, root, exclude_globs):
            continue
        yield p


def scan_path(
    root: str | Path,
    *,
    rules_path: Path | None = None,
    max_findings: int = 500,
) -> InvertReport:
    root_p = Path(root).resolve()
    cfg = load_rules(rules_path)
    rules = cfg.get("rules") or []
    exclude = list(cfg.get("exclude_globs") or [])
    suppress = list(cfg.get("suppress_if_path_contains") or [])

    compiled: list[tuple[dict[str, Any], re.Pattern[str], str]] = []
    for rule in rules:
        for pat in rule.get("patterns") or []:
            compiled.append(
                (rule, re.compile(re.escape(pat), re.IGNORECASE), pat)
            )

    findings: list[Finding] = []
    files_scanned = 0

    for fpath in _iter_files(root_p, exclude):
        rel = str(fpath.relative_to(root_p)) if fpath.is_relative_to(root_p) else str(fpath)
        if any(s in rel for s in suppress):
            continue
        try:
            text = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        files_scanned += 1
        lines = text.splitlines()
        for i, line in enumerate(lines, start=1):
            for rule, cre, pat in compiled:
                if cre.search(line):
                    findings.append(
                        Finding(
                            rule_id=rule.get("id", "unknown"),
                            severity=rule.get("severity", "medium"),
                            category=rule.get("category", "unknown"),
                            description=rule.get("description", ""),
                            path=rel,
                            line=i,
                            snippet=line.strip()[:200],
                            pattern=pat,
                        )
                    )
                    if len(findings) >= max_findings:
                        break
            if len(findings) >= max_findings:
                break
        if len(findings) >= max_findings:
            break

    by_sev: dict[str, int] = {}
    by_rule: dict[str, int] = {}
    for f in findings:
        by_sev[f.severity] = by_sev.get(f.severity, 0) + 1
        by_rule[f.rule_id] = by_rule.get(f.rule_id, 0) + 1

    status = "clean" if not findings else "findings"
    report = InvertReport(
        scanned_at=datetime.now(timezone.utc).isoformat(),
        root=str(root_p),
        files_scanned=files_scanned,
        findings=findings,
        by_severity=by_sev,
        by_rule=by_rule,
        status=status,
    )
    report.sha256 = report.to_dict()["sha256"]
    return report


def write_report(report: InvertReport, out_dir: str | Path) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    data = report.to_dict()
    path = out / "INVERT_SCAN.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    md = out / "INVERT_SCAN.md"
    lines = [
        "# Invert Scan Report",
        "",
        f"- **Root:** `{report.root}`",
        f"- **Scanned at:** {report.scanned_at}",
        f"- **Files:** {report.files_scanned}",
        f"- **Findings:** {len(report.findings)}",
        f"- **Status:** {report.status}",
        f"- **SHA256:** `{data.get('sha256', '')}`",
        "",
        "## By severity",
        "",
    ]
    for k, v in sorted(report.by_severity.items()):
        lines.append(f"- {k}: {v}")
    lines.extend(["", "## Findings", ""])
    if not report.findings:
        lines.append("_Clean — no inversion patterns matched._")
    for f in report.findings[:100]:
        lines.append(
            f"- **{f.severity}** `{f.rule_id}` {f.path}:{f.line} — {f.snippet}"
        )
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
