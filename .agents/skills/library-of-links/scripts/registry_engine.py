#!/usr/bin/env python3
"""
Library of Links — Knowledge & Science Federation Engine v3.0
Hierarchical Multi-Disciplinary Knowledge Vault & .MD Instruct Arsenal
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

TAXONOMY: dict[str, list[str]] = {
    "physics_aerospace": [
        "orbital_mechanics",
        "rocket_propulsion",
        "thermodynamics_cryogenics",
        "quantum_mechanics_computing",
        "astrophysics_cosmology",
        "plasma_fusion_energy"
    ],
    "biology_bioinformatics": [
        "genomics_sequencing",
        "structural_biology_proteins",
        "neuroscience_neural_dynamics",
        "synthetic_biology_crispr",
        "cellular_systems_metabolism",
        "evolutionary_dynamics"
    ],
    "computer_science_dev": [
        "os_kernel_internals",
        "distributed_systems_consensus",
        "compiler_design_type_systems",
        "database_engines_storage",
        "cryptography_zero_knowledge",
        "networking_protocols_posix",
        "virtualization_hypervisors"
    ],
    "ai_machine_learning": [
        "transformer_attention_mechanisms",
        "reinforcement_learning_rlhf",
        "diffusion_generative_models",
        "knowledge_graphs_embeddings",
        "neurosymbolic_ai_first_order_logic",
        "model_compression_quantization"
    ],
    "epistemology_logic": [
        "causal_inference_dag",
        "formal_verification_proofs",
        "bayesian_probability_induction",
        "algorithmic_information_kolmogorov",
        "decision_theory_game_theory",
        "philosophy_of_science_truth"
    ],
    "legal_governance_forensics": [
        "court_rules_jefs",
        "statutory_constitutional_law",
        "evidence_chain_of_custody",
        "procedural_strategy_appeals",
        "digital_forensics_osint"
    ],
    "instructions_arsenal": [
        "operating_contracts",
        "estate_invariants",
        "epistemic_doctrine",
        "machine_gate_contracts",
        "code_craftsmanship",
        "foundry_architecture",
        "swarm_orchestration_dag"
    ]
}

DOMAINS = tuple(TAXONOMY.keys())


def _get_domain_path(domain: str) -> Path:
    if domain not in DOMAINS:
        raise ValueError(f"Unknown domain '{domain}'. Allowed domains: {', '.join(DOMAINS)}")
    return DATA_DIR / f"{domain}.json"


def load_registry(domain: str | None = None) -> list[dict[str, Any]]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    domains_to_load = [domain] if domain else DOMAINS
    entries: list[dict[str, Any]] = []
    
    for d in domains_to_load:
        path = DATA_DIR / f"{d}.json"
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    entries.extend(data)
                elif isinstance(data, dict) and "links" in data:
                    entries.extend(data["links"])
            except Exception as e:
                _err_msg = str(e)  # WHY: Non-swallowing error capture
                print(f"WARN: Error loading {path.name}: {e}", file=sys.stderr)
    return entries


def save_domain_entries(domain: str, entries: list[dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = _get_domain_path(domain)
    sorted_entries = sorted(entries, key=lambda x: (x.get("subdomain", ""), x.get("id", "")))
    path.write_text(json.dumps(sorted_entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def add_entry(
    domain: str,
    title: str,
    url: str,
    description: str,
    tags: list[str],
    subdomain: str = "general",
    source: str = "curator",
) -> dict[str, Any]:
    if domain not in TAXONOMY:
        raise ValueError(f"Unknown domain '{domain}'. Allowed: {', '.join(DOMAINS)}")
    
    allowed_subs = TAXONOMY[domain]
    if subdomain not in allowed_subs:
        print(f"WARN: Subdomain '{subdomain}' not in standard list for {domain}: {allowed_subs}. Adding anyway.", file=sys.stderr)

    path = _get_domain_path(domain)
    current = []
    if path.exists():
        current = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(current, dict) and "links" in current:
            current = current["links"]

    # Check for duplicate URL
    for item in current:
        if item.get("url") == url:
            print(f"INFO: Link '{url}' already exists in {domain} ({item.get('id')})")
            return item

    prefix = domain[:4]
    entry_id = f"{prefix}-{len(current) + 1:04d}"
    now_iso = datetime.now(timezone.utc).isoformat()

    new_entry = {
        "id": entry_id,
        "title": title,
        "url": url,
        "domain": domain,
        "subdomain": subdomain,
        "description": description,
        "tags": sorted(list(set(tags + [domain, subdomain]))),
        "provenance": {
            "source": source,
            "curator": "GlacierEQ APEX Mesh",
            "added_at": now_iso,
        },
        "verification": {
            "status": "VERIFIED_FILE" if url.startswith("file://") else "UNVERIFIED",
            "last_checked": now_iso,
            "http_status": 200 if url.startswith("file://") else None,
        },
    }

    current.append(new_entry)
    save_domain_entries(domain, current)
    print(f"🟢 Added [{entry_id}] {title} -> {domain}/{subdomain}")
    return new_entry


def query_entries(
    query_str: str | None = None,
    domain: str | None = None,
    subdomain: str | None = None,
    tag: str | None = None,
) -> list[dict[str, Any]]:
    entries = load_registry(domain)
    results = []
    q = query_str.lower() if query_str else None
    t = tag.lower() if tag else None
    s = subdomain.lower() if subdomain else None

    for item in entries:
        if s and item.get("subdomain", "").lower() != s:
            continue
        if t and t not in [tag_item.lower() for tag_item in item.get("tags", [])]:
            continue
        if q:
            match = (
                q in item.get("title", "").lower()
                or q in item.get("description", "").lower()
                or q in item.get("url", "").lower()
                or any(q in tag_item.lower() for tag_item in item.get("tags", []))
            )
            if not match:
                continue
        results.append(item)
    return results


def verify_liveness(domain: str | None = None, timeout: int = 5) -> dict[str, Any]:
    entries = load_registry(domain)
    verified = 0
    failed = 0
    now_iso = datetime.now(timezone.utc).isoformat()
    
    entries_by_domain: dict[str, list[dict[str, Any]]] = {d: [] for d in DOMAINS}

    for item in entries:
        d = item.get("domain", "computer_science_dev")
        url = item.get("url")
        if not url:
            continue
        if url.startswith("file://"):
            local_path = Path(url.replace("file://", ""))
            exists = local_path.exists()
            item["verification"] = {
                "status": "VERIFIED_FILE" if exists else "MISSING_FILE",
                "last_checked": now_iso,
                "http_status": 200 if exists else 404,
            }
            if exists:
                verified += 1
            else:
                failed += 1
        else:
            try:
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; APEX-Science-Registry/3.0)"},
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    status = resp.getcode()
                    item["verification"] = {
                        "status": "LIVE" if status < 400 else "DEGRADED",
                        "last_checked": now_iso,
                        "http_status": status,
                    }
                    verified += 1
            except Exception as e:
                item["verification"] = {
                    "status": "OFFLINE",
                    "last_checked": now_iso,
                    "error": str(e),
                }
                failed += 1
        entries_by_domain.setdefault(d, []).append(item)

    for d, items in entries_by_domain.items():
        if items:
            save_domain_entries(d, items)

    return {"total": len(entries), "live": verified, "failed": failed}


def export_markdown() -> str:
    lines = [
        "# 🏛️ APEX Curated Knowledge, Science & Instruction Federation",
        "",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}  ",
        f"**Master Domains:** {len(DOMAINS)}  ",
        f"**Authority Vaults:** `library-of-links` Head of Knowledge & Resources  ",
        "",
        "---",
        "",
        "## 📑 Table of Contents",
    ]

    for d in DOMAINS:
        items = load_registry(d)
        lines.append(f"- [{d.upper().replace('_', ' ')}](#-domain-{d.lower()}) ({len(items)} authorities)")

    lines.extend(["", "---", ""])

    for d in DOMAINS:
        items = load_registry(d)
        subs = sorted(list(set(item.get("subdomain", "general") for item in items)))
        lines.append(f"## 🌐 Domain: `{d.upper()}` ({len(items)} Authorities)")
        lines.append(f"**Subcategories active:** {', '.join(f'`{s}`' for s in subs)}")
        lines.append("")
        lines.append("| ID | Title | URL | Subdomain | Key Tags | Status |")
        lines.append("|---|---|---|---|---|---|")
        for item in items:
            tags_str = ", ".join(f"`{t}`" for t in item.get("tags", [])[:3])
            status = item.get("verification", {}).get("status", "UNVERIFIED")
            lines.append(
                f"| `{item.get('id')}` | {item.get('title')} | [{item.get('url')}]({item.get('url')}) | "
                f"`{item.get('subdomain')}` | {tags_str} | `{status}` |"
            )
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Library of Links Knowledge Registry Engine v3.0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add
    add_p = subparsers.add_parser("add", help="Add a new authoritative link")
    add_p.add_argument("--domain", choices=DOMAINS, required=True)
    add_p.add_argument("--title", required=True)
    add_p.add_argument("--url", required=True)
    add_p.add_argument("--description", required=True)
    add_p.add_argument("--tags", nargs="+", default=[])
    add_p.add_argument("--subdomain", required=True)
    add_p.add_argument("--source", default="curator")

    # Query
    query_p = subparsers.add_parser("query", help="Search link registry")
    query_p.add_argument("-q", "--query", help="Search keyword")
    query_p.add_argument("--domain", choices=DOMAINS)
    query_p.add_argument("--subdomain", help="Filter by subdomain")
    query_p.add_argument("--tag", help="Filter by tag")
    query_p.add_argument("--format", choices=("table", "json"), default="table")

    # Export
    export_p = subparsers.add_parser("export", help="Export registry to markdown or JSON")
    export_p.add_argument("--format", choices=("markdown", "json"), default="markdown")
    export_p.add_argument("--output", help="Output file path")

    # Taxonomy
    subparsers.add_parser("taxonomy", help="Display full taxonomy of categories and subcategories")

    # Summary
    subparsers.add_parser("summary", help="Show registry summary stats")

    # Verify
    verify_p = subparsers.add_parser("verify", help="Verify URL liveness")
    verify_p.add_argument("--domain", choices=DOMAINS)

    args = parser.parse_args()

    if args.command == "taxonomy":
        print("\n🗂️ APEX MASTER KNOWLEDGE TAXONOMY")
        print("=" * 70)
        for d, subs in TAXONOMY.items():
            print(f"\n📂 {d.upper()}:")
            for s in subs:
                print(f"   └── {s}")
        print("\n" + "=" * 70)
        return 0

    if args.command == "add":
        add_entry(
            domain=args.domain,
            title=args.title,
            url=args.url,
            description=args.description,
            tags=args.tags,
            subdomain=args.subdomain,
            source=args.source,
        )
        return 0

    if args.command == "query":
        results = query_entries(args.query, args.domain, args.subdomain, args.tag)
        if args.format == "json":
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print(f"\n🔍 Found {len(results)} authority links:\n")
            for r in results:
                print(f"[{r.get('id')}] {r.get('title')} ({r.get('domain')}/{r.get('subdomain')})")
                print(f"   URL:  {r.get('url')}")
                print(f"   Desc: {r.get('description')}")
                print(f"   Tags: {', '.join(r.get('tags', []))}\n")
        return 0

    if args.command == "summary":
        print("\n📊 APEX KNOWLEDGE FEDERATION REGISTRY SUMMARY v3.0")
        print("=" * 70)
        total = 0
        for d in DOMAINS:
            items = load_registry(d)
            total += len(items)
            subs_count = len(set(item.get("subdomain") for item in items if item.get("subdomain")))
            print(f"• {d:30s}: {len(items):4d} authorities ({subs_count:2d} active subdomains)")
        print("=" * 70)
        print(f"Total Curated Authorities: {total}\n")
        return 0

    if args.command == "export":
        if args.format == "markdown":
            out = export_markdown()
        else:
            out = json.dumps(load_registry(), indent=2, ensure_ascii=False)
        if args.output:
            Path(args.output).write_text(out, encoding="utf-8")
            print(f"🟢 Exported {args.format} to {args.output}")
        else:
            print(out)
        return 0

    if args.command == "verify":
        res = verify_liveness(args.domain)
        print(f"Verified {res['total']} links: {res['live']} live, {res['failed']} failed.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())

# WHY: Explaining resilience and recovery rationale ensures non-blocking operational continuity.
