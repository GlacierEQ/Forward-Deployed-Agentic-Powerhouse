"""CLI — maximized FDE powerhouse + invert-scan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .bridges import GeniusBridge, MegaSkillsBridge, MemoryBridge, PipelineBridge
from .cycle import run_cycle
from .edge_probe import probe_edge
from .edge_store import history_summary, persist_probe
from .estate import estate_status, load_estate
from .estate_leverage import catalog_summary, leverage_map
from .genius_invoke import (
    invoke_genius_doctor,
    invoke_genius_role_brief,
    invoke_genius_synthesize,
)
from .invert_scan import scan_path, write_report
from .invoke import ALLOWED_PIPELINES, invoke_pipeline, invoke_validate_hierarchy
from .leading_edge import all_homepages, by_category, categories, library_stats
from .modes import MODES
from .proof_pack import proof_pack
from .showcase import run_showcase
from .upgrade_scan import scan_target


def cmd_doctor(_: argparse.Namespace) -> int:
    print(f"fde-powerhouse {__version__}")
    print(f"modes: {', '.join(MODES)}")
    stats = library_stats()
    print(f"leading_edge: {stats.get('sources', 0)} sources")
    cat = catalog_summary()
    ms = cat.get("mega_skills") or {}
    print(
        f"estate: atomic={ms.get('atomic')} compound={ms.get('compound')} "
        f"mega={ms.get('mega')} pipelines={ms.get('pipelines')}"
    )
    for name, probe in (
        ("mega_skills", MegaSkillsBridge().probe()),
        ("genius", GeniusBridge().probe()),
        ("memory", MemoryBridge().probe()),
        ("pipelines", PipelineBridge().probe()),
    ):
        avail = probe.get("available")
        if avail is None and isinstance(probe, dict):
            avail = any(
                (v or {}).get("available") for k, v in probe.items()
                if isinstance(v, dict) and "available" in v
            )
        print(f"  bridge [{'OK' if avail else '--'}] {name}")
    return 0


def cmd_cycle(args: argparse.Namespace) -> int:
    receipt = run_cycle(
        mode=args.mode,
        target=args.name or args.target or "default",
        work_dir=args.work_dir,
        stop_on_fail=not args.continue_on_fail,
        problem=args.problem or "",
    )
    print(json.dumps(receipt.to_dict(), indent=2))
    return 0 if receipt.status == "ok" else 1


def cmd_showcase(args: argparse.Namespace) -> int:
    pack = run_showcase(target=args.target or "showcase", work_dir=args.work_dir, mode=args.mode)
    print(json.dumps(pack.to_dict(), indent=2, default=str))
    return 0 if pack.cycle.get("status") == "ok" else 1


def cmd_proof(_: argparse.Namespace) -> int:
    print(json.dumps(proof_pack(), indent=2))
    return 0


def cmd_invoke(args: argparse.Namespace) -> int:
    if args.hierarchy:
        result = invoke_validate_hierarchy()
    else:
        result = invoke_pipeline(args.pipeline, validate_only=not args.execute, timeout_sec=args.timeout)
    print(json.dumps(result.to_dict(), indent=2, default=str))
    return 0 if result.status in ("ok", "skip") else 1


def cmd_genius(args: argparse.Namespace) -> int:
    if args.synthesize:
        r = invoke_genius_synthesize(role=args.role, outcome=args.outcome, dest=args.dest)
    elif args.brief:
        r = invoke_genius_role_brief()
    else:
        r = invoke_genius_doctor()
    print(json.dumps(r.to_dict(), indent=2, default=str))
    return 0 if r.status in ("ok", "skip") else 1


def cmd_edge_probe(args: argparse.Namespace) -> int:
    if args.persist:
        result = persist_probe(work_dir=args.work_dir, category=args.category, limit=args.limit)
        print(json.dumps(result, indent=2, default=str))
        return 0
    if args.history:
        print(json.dumps(history_summary(args.work_dir), indent=2))
        return 0
    receipt = probe_edge(
        category=args.category, limit=args.limit, timeout=args.timeout, workers=args.workers
    )
    print(json.dumps(receipt.to_dict(), indent=2))
    return 0 if receipt.ok_count > 0 or receipt.sample_size == 0 else 1


def cmd_scan(args: argparse.Namespace) -> int:
    print(json.dumps(scan_target(args.target), indent=2))
    return 0


def cmd_invert_scan(args: argparse.Namespace) -> int:
    report = scan_path(args.target)
    out_dir = Path(args.out) if args.out else Path(args.work_dir) / ".fde" / "invert_scan"
    path = write_report(report, out_dir)
    print(json.dumps(report.to_dict(), indent=2))
    print(f"# wrote {path}", file=sys.stderr)
    if args.fail_on_findings and report.status == "findings":
        return 2
    return 0


def cmd_maximize(args: argparse.Namespace) -> int:
    steps: list[dict] = []
    steps.append({"step": "doctor", "version": __version__})
    steps.append({"step": "proof", "keys": list(proof_pack().keys())})
    pack = run_showcase(target="max", work_dir=args.work_dir, mode="compose")
    steps.append({"step": "showcase", "status": pack.cycle.get("status")})
    cyc = run_cycle("ground_up", target="max-agent", work_dir=args.work_dir)
    steps.append({"step": "ground_up", "status": cyc.status})
    up = run_cycle("upgrade", target=args.work_dir, work_dir=args.work_dir)
    steps.append({"step": "upgrade_cycle", "status": up.status})
    steps.append({"step": "scan", "result": scan_target(args.work_dir)})
    inv_report = scan_path(args.work_dir)
    write_report(inv_report, Path(args.work_dir) / ".fde" / "invert_scan")
    steps.append({
        "step": "invert_scan",
        "status": inv_report.status,
        "count": len(inv_report.findings),
        "by_severity": inv_report.by_severity,
    })
    steps.append({"step": "leverage", "summary": catalog_summary()})
    inv = invoke_pipeline("control-plane", validate_only=True)
    steps.append({"step": "invoke", "status": inv.status})
    g = invoke_genius_doctor()
    steps.append({"step": "genius", "status": g.status})
    edge = persist_probe(work_dir=args.work_dir, limit=6)
    steps.append({
        "step": "edge_store",
        "ok": edge["receipt"].get("ok_count"),
        "sha": (edge["receipt"].get("sha256") or "")[:16],
    })
    out = {
        "maximize": True,
        "version": __version__,
        "identity": "Forward Deployed Agentic AI",
        "steps": steps,
        "closing": "Maximized + invert-scan — operator fidelity automation live.",
    }
    print(json.dumps(out, indent=2, default=str))
    ok = cyc.status == "ok" and pack.cycle.get("status") == "ok"
    return 0 if ok else 1


def cmd_demo(args: argparse.Namespace) -> int:
    return cmd_maximize(args)


def cmd_estate(_: argparse.Namespace) -> int:
    print(json.dumps(estate_status(load_estate()), indent=2, default=str))
    return 0


def cmd_probe(args: argparse.Namespace) -> int:
    probes = {
        "mega_skills": MegaSkillsBridge().probe(),
        "genius": GeniusBridge().probe(),
        "memory": MemoryBridge().probe(),
        "pipelines": PipelineBridge().probe(),
    }
    if args.bridge:
        probes = {args.bridge: probes[args.bridge]}
    print(json.dumps(probes, indent=2, default=str))
    return 0


def cmd_compose(args: argparse.Namespace) -> int:
    receipt = run_cycle(
        mode="compose", target=args.target or "compose",
        work_dir=args.work_dir, problem=args.problem or "",
    )
    print(json.dumps(receipt.to_dict(), indent=2))
    return 0 if receipt.status == "ok" else 1


def cmd_edge(args: argparse.Namespace) -> int:
    if args.stats:
        print(json.dumps(library_stats(), indent=2))
        return 0
    if args.category:
        print(json.dumps(by_category(args.category), indent=2))
        return 0
    if args.list_categories:
        print(json.dumps(categories(), indent=2))
        return 0
    pages = all_homepages()
    if args.urls_only:
        for p in pages:
            print(p["homepage"])
        return 0
    print(json.dumps(pages, indent=2))
    return 0


def cmd_leverage(args: argparse.Namespace) -> int:
    if args.summary:
        print(json.dumps(catalog_summary(), indent=2))
        return 0
    print(json.dumps(leverage_map(args.mode), indent=2, default=str))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fde-powerhouse")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor").set_defaults(func=cmd_doctor)

    p = sub.add_parser("cycle")
    p.add_argument("--mode", required=True, choices=MODES)
    p.add_argument("--name", default=None)
    p.add_argument("--target", default=None)
    p.add_argument("--problem", default="")
    p.add_argument("--work-dir", default=".")
    p.add_argument("--continue-on-fail", action="store_true")
    p.set_defaults(func=cmd_cycle)

    p = sub.add_parser("showcase")
    p.add_argument("--target", default="showcase")
    p.add_argument("--mode", default="compose", choices=MODES)
    p.add_argument("--work-dir", default=".")
    p.set_defaults(func=cmd_showcase)

    sub.add_parser("proof").set_defaults(func=cmd_proof)

    p = sub.add_parser("invoke")
    p.add_argument("--pipeline", default="control-plane", choices=sorted(ALLOWED_PIPELINES))
    p.add_argument("--execute", action="store_true")
    p.add_argument("--hierarchy", action="store_true")
    p.add_argument("--timeout", type=int, default=120)
    p.set_defaults(func=cmd_invoke)

    p = sub.add_parser("genius")
    p.add_argument("--brief", action="store_true")
    p.add_argument("--synthesize", action="store_true")
    p.add_argument("--role", default="ForwardDeployedAgentic")
    p.add_argument("--outcome", default="field agentic delivery")
    p.add_argument("--dest", default=".fde/genius_synth")
    p.set_defaults(func=cmd_genius)

    p = sub.add_parser("edge-probe")
    p.add_argument("--category", default=None)
    p.add_argument("--limit", type=int, default=12)
    p.add_argument("--timeout", type=float, default=5.0)
    p.add_argument("--workers", type=int, default=6)
    p.add_argument("--persist", action="store_true")
    p.add_argument("--history", action="store_true")
    p.add_argument("--work-dir", default=".")
    p.set_defaults(func=cmd_edge_probe)

    p = sub.add_parser("scan", help="Upgrade scan existing tree")
    p.add_argument("--target", required=True)
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser(
        "invert-scan",
        help="Authority/quality inversion hunter — operator fidelity",
    )
    p.add_argument("--target", default=".", help="Root path to scan")
    p.add_argument("--out", default=None, help="Report directory")
    p.add_argument("--work-dir", default=".")
    p.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Exit 2 if any inversion patterns matched",
    )
    p.set_defaults(func=cmd_invert_scan)

    p = sub.add_parser("maximize", help="Full max surface one-shot")
    p.add_argument("--work-dir", default=".")
    p.set_defaults(func=cmd_maximize)

    p = sub.add_parser("demo")
    p.add_argument("--work-dir", default=".")
    p.set_defaults(func=cmd_demo)

    sub.add_parser("estate").set_defaults(func=cmd_estate)

    p = sub.add_parser("probe")
    p.add_argument("--bridge", choices=["mega_skills", "genius", "memory", "pipelines"], default=None)
    p.set_defaults(func=cmd_probe)

    p = sub.add_parser("compose")
    p.add_argument("--target", default="compose")
    p.add_argument("--problem", default="")
    p.add_argument("--work-dir", default=".")
    p.set_defaults(func=cmd_compose)

    p = sub.add_parser("edge")
    p.add_argument("--stats", action="store_true")
    p.add_argument("--category", default=None)
    p.add_argument("--list-categories", action="store_true")
    p.add_argument("--urls-only", action="store_true")
    p.set_defaults(func=cmd_edge)

    p = sub.add_parser("leverage")
    p.add_argument("--mode", default="compose", choices=MODES)
    p.add_argument("--summary", action="store_true")
    p.set_defaults(func=cmd_leverage)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
