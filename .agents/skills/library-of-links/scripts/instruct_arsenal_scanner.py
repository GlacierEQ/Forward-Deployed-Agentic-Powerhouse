#!/usr/bin/env python3
"""
APEX .MD Instruct Arsenal Discovery & Liveness Synchronizer v1.0
Automatically scans the entire estate for high-leverage markdown instruction files,
playbooks, rules, and machine contracts, keeping the library-of-links arsenal 100% current.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apex_env import get_home_dir, get_termux_home, get_library_of_links_root, get_monolith_root

ROOT = get_library_of_links_root()
DATA_FILE = ROOT / "data" / "instructions_arsenal.json"

# Search roots across all portable environments
SEARCH_ROOTS = [
    get_home_dir() / ".agents",
    get_home_dir(),
    get_termux_home() / ".agents",
    get_termux_home(),
    get_monolith_root() / "governance",
    get_monolith_root() / "rules",
]

KNOWN_ARSENAL_FILENAMES = {
    "AGENTS.md": ("operating_contracts", "Sovereign & Holographic Mesh Operating Contract"),
    "CONSTANTS.md": ("estate_invariants", "Estate Invariant Constants & Physical Laws"),
    "EPISTEMOLOGY.md": ("epistemic_doctrine", "L0–L5 Epistemic Hierarchy & Anti-Symptom-Chasing Law"),
    "EXCELLENCE.md": ("machine_gate_contracts", "12-Stage Boolean Machine Gate Specification"),
    "pro_code_humanized_engineering.md": ("code_craftsmanship", "Principal Systems Engineer Craftsmanship Contract"),
    "MASTER_FOUNDRY.md": ("foundry_architecture", "4-Wave Autonomous Master Build Foundry"),
    "REPO_EXCELLENCE_CRYSTALLIZED.md": ("machine_gate_contracts", "Executable Repository State Machine & Gate Predicates"),
    "PHASE_PLAYBOOKS.md": ("swarm_orchestration_dag", "Longest Horizon Swarm Execution Playbooks"),
    "EPISTEMIC_STANDARDS.md": ("epistemic_doctrine", "Epistemic Truth Standards & Verification Protocol"),
}


def compute_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def scan_and_synchronize_arsenal(verbose: bool = True) -> dict[str, Any]:
    now_iso = datetime.now(timezone.utc).isoformat()
    current_entries: list[dict[str, Any]] = []
    
    if DATA_FILE.exists():
        try:
            current_entries = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            current_entries = []

    entries_by_url = {item["url"]: item for item in current_entries}
    discovered_count = 0
    updated_count = 0

    seen_paths: set[Path] = set()

    for base in SEARCH_ROOTS:
        if not base.exists():
            continue
        for p in base.rglob("*.md"):
            # Skip hidden git caches, temp build directories, and third-party node_modules
            p_str = str(p)
            if any(skip in p_str for skip in (".git/", "node_modules/", ".pytest_cache/", "tmp/", ".bun/", "dist/", "vendor/")):
                continue
            if p.name in KNOWN_ARSENAL_FILENAMES:
                resolved_p = p.resolve()
                if resolved_p in seen_paths:
                    continue
                seen_paths.add(resolved_p)
                
                url = f"file://{resolved_p}"
                subdomain, default_desc = KNOWN_ARSENAL_FILENAMES[p.name]
                file_sha = compute_file_sha256(resolved_p)
                file_size = resolved_p.stat().st_size
                
                if url in entries_by_url:
                    # Update existing record with latest hash and timestamp
                    entry = entries_by_url[url]
                    entry["verification"] = {
                        "status": "VERIFIED_FILE",
                        "last_checked": now_iso,
                        "sha256": file_sha,
                        "bytes": file_size,
                        "http_status": 200,
                    }
                    updated_count += 1
                else:
                    # Create new entry
                    entry_id = f"inst-{len(entries_by_url) + 1:04d}"
                    entry = {
                        "id": entry_id,
                        "title": f"{p.name} — {default_desc}",
                        "url": url,
                        "domain": "instructions_arsenal",
                        "subdomain": subdomain,
                        "description": default_desc,
                        "tags": sorted(["instructions_arsenal", subdomain, p.stem.lower()]),
                        "provenance": {
                            "source": f"Local Estate File ({p.name})",
                            "curator": "APEX Arsenal Synchronizer",
                            "added_at": now_iso,
                        },
                        "verification": {
                            "status": "VERIFIED_FILE",
                            "last_checked": now_iso,
                            "sha256": file_sha,
                            "bytes": file_size,
                            "http_status": 200,
                        },
                    }
                    entries_by_url[url] = entry
                    discovered_count += 1
                    if verbose:
                        print(f"📄 [Arsenal Discovered] [{entry_id}] {p.name} ({resolved_p})")

    all_entries = sorted(entries_by_url.values(), key=lambda x: (x.get("subdomain", ""), x.get("id", "")))
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(all_entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Re-export to Monolith
    from registry_engine import export_markdown
    monolith_path = get_monolith_root() / "status" / "KNOWLEDGE_FEDERATION.md"
    out = export_markdown()
    monolith_path.parent.mkdir(parents=True, exist_ok=True)
    monolith_path.write_text(out, encoding="utf-8")

    return {
        "total_arsenal": len(all_entries),
        "newly_discovered": discovered_count,
        "verified_and_updated": updated_count,
        "monolith_synced": str(monolith_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="APEX .MD Instruct Arsenal Synchronizer")
    parser.add_argument("--sync", action="store_true", default=True, help="Scan and sync all .md instruct files")
    args = parser.parse_args()

    print("\n⚡ --- SCANNING & SYNCHRONIZING APEX .MD INSTRUCT ARSENAL ---")
    res = scan_and_synchronize_arsenal(verbose=True)
    print(f"🟢 Arsenal Total: {res['total_arsenal']} active instructions | New: +{res['newly_discovered']} | Updated: {res['verified_and_updated']}")
    print(f"🟢 Monolith Board: {res['monolith_synced']}\n")


if __name__ == "__main__":
    main()

# WHY: Explaining resilience and recovery rationale ensures non-blocking operational continuity.
