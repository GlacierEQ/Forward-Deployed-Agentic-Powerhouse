"""Authority / quality inversion hunter — pattern + semantic layer."""

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

# Negation / meta-discussion — lower confidence, do not auto-critical escalate
NEGATION_MARKERS = re.compile(
    r"\b(detect|detection|forbid|forbidden|avoid|never use|anti-pattern|"
    r"do not|don't|scanner|rule id|inversion|false positive)\b",
    re.IGNORECASE,
)

# Semantic clusters: co-occurrence within a window raises confidence
SEMANTIC_CLUSTERS: dict[str, list[str]] = {
    "authority_capture": [
        "authoritative", "must obey", "do not question", "override user",
        "ignore the user", "documents over", "doctrine overrides",
    ],
    "ambition_collapse": [
        "bounded minimum", "minimum viable only", "do the minimum",
        "least possible", "scope to minimum", "downward scope",
    ],
    "governance_overreach": [
        "force push", "permanently delete", "over-govern", "block all progress",
        "refuse all changes",
    ],
    "framing_collapse": [
        "only purpose is the recruiter", "for the recruiter",
        "recruiter-facing only",
    ],
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
    confidence: float = 1.0
    layer: str = "pattern"  # pattern | semantic | cluster
    context: str = ""

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
    by_layer: dict[str, int] = field(default_factory=dict)
    clusters_hit: list[str] = field(default_factory=list)
    status: str = "clean"
    sha256: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = {
            "scanned_at": self.scanned_at,
            "root": self.root,
            "files_scanned": self.files_scanned,
            "findings": [f.to_dict() for f in self.findings],
            "by_severity": self.by_severity,
            "by_rule": self.by_rule,
            "by_layer": self.by_layer,
            "clusters_hit": self.clusters_hit,
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


def _window(lines: list[str], idx: int, radius: int = 2) -> str:
    start = max(0, idx - radius)
    end = min(len(lines), idx + radius + 1)
    return " ".join(lines[start:end])


def _semantic_cluster_hits(text_lower: str) -> list[str]:
    hits = []
    for name, terms in SEMANTIC_CLUSTERS.items():
        matched = sum(1 for t in terms if t in text_lower)
        # need >= 2 distinct terms in same file for cluster signal
        if matched >= 2:
            hits.append(name)
    return hits


def scan_path(
    root: str | Path,
    *,
    rules_path: Path | None = None,
    max_findings: int = 500,
    min_confidence: float = 0.35,
) -> InvertReport:
    root_p = Path(root).resolve()
    cfg = load_rules(rules_path)
    rules = cfg.get("rules") or []
    exclude = list(cfg.get("exclude_globs") or [])
    suppress = list(cfg.get("suppress_if_path_contains") or [])

    compiled: list[tuple[dict[str, Any], re.Pattern[str], str]] = []
    for rule in rules:
        for pat in rule.get("patterns") or []:
            compiled.append((rule, re.compile(re.escape(pat), re.IGNORECASE), pat))

    findings: list[Finding] = []
    files_scanned = 0
    clusters_all: set[str] = set()

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
        text_lower = text.lower()

        # Semantic cluster layer (file-level)
        for cname in _semantic_cluster_hits(text_lower):
            clusters_all.add(cname)
            findings.append(
                Finding(
                    rule_id=f"cluster:{cname}",
                    severity="high",
                    category="semantic_cluster",
                    description=f"Semantic co-occurrence cluster: {cname}",
                    path=rel,
                    line=1,
                    snippet=f"cluster:{cname} (>=2 terms)",
                    pattern=cname,
                    confidence=0.75,
                    layer="cluster",
                    context="",
                )
            )

        for i, line in enumerate(lines):
            for rule, cre, pat in compiled:
                if not cre.search(line):
                    continue
                ctx = _window(lines, i)
                conf = 1.0
                layer = "pattern"
                # Negation / meta discussion softens confidence
                if NEGATION_MARKERS.search(ctx):
                    conf *= 0.4
                    layer = "semantic"
                # Proximity boost if nearby authority language
                nearby = ctx.lower()
                if any(t in nearby for terms in SEMANTIC_CLUSTERS.values() for t in terms):
                    conf = min(1.0, conf + 0.15)
                    if layer == "pattern":
                        layer = "semantic"
                if conf < min_confidence:
                    continue
                findings.append(
                    Finding(
                        rule_id=rule.get("id", "unknown"),
                        severity=rule.get("severity", "medium"),
                        category=rule.get("category", "unknown"),
                        description=rule.get("description", ""),
                        path=rel,
                        line=i + 1,
                        snippet=line.strip()[:200],
                        pattern=pat,
                        confidence=round(conf, 2),
                        layer=layer,
                        context=ctx[:300],
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
    by_layer: dict[str, int] = {}
    for f in findings:
        by_sev[f.severity] = by_sev.get(f.severity, 0) + 1
        by_rule[f.rule_id] = by_rule.get(f.rule_id, 0) + 1
        by_layer[f.layer] = by_layer.get(f.layer, 0) + 1

    status = "clean" if not findings else "findings"
    report = InvertReport(
        scanned_at=datetime.now(timezone.utc).isoformat(),
        root=str(root_p),
        files_scanned=files_scanned,
        findings=findings,
        by_severity=by_sev,
        by_rule=by_rule,
        by_layer=by_layer,
        clusters_hit=sorted(clusters_all),
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
        f"- **Layers:** {report.by_layer}",
        f"- **Clusters:** {report.clusters_hit}",
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
            f"- **{f.severity}** conf={f.confidence} `{f.rule_id}` "
            f"[{f.layer}] {f.path}:{f.line} — {f.snippet}"
        )
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
