"""CLI — doctor, cycle, showcase, proof, invoke, genius, edge-probe, demo."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .bridges import GeniusBridge, MegaSkillsBridge, MemoryBridge, PipelineBridge
from .cycle import run_cycle
from .edge_probe import probe_edge
from .estate import estate_status, load_estate
from .estate_leverage import catalog_summary, leverage_map
from .genius_invoke import invoke_genius_doctor, invoke_genius_role_brief
from .invoke import ALLOWED_PIPELINES, invoke_pipeline, invoke_validate_hierarchy
from .leading_edge import all_homepages, by_category, categories, library_stats
from .modes import MODES
from .proof_pack import proof_pack
from .showcase import run_showcase


def cmd_doctor(_: argparse.Namespace) -> int:
    print(f"fde-powerhouse {__version__}")
    print(f"modes: {', '.join(MODES)}")
    stats = library_stats()
    print(f"leading_edge: {stats.get('sources', 0)} sources across {stats.get('categories', 0)} categories")
    cat = catalog_summary()
    ms = cat.get("mega_skills") or {}
    print(
        f"estate_catalog: atomic={ms.get('atomic')} compound={ms.get('compound')} "
        f"mega={ms.get('mega')} pipelines={ms.get('pipelines')}"
    )
    print("bridges:")
    for name, probe in (
        ("mega_skills", MegaSkillsBridge().probe()),
        ("genius", GeniusBridge().probe()),
        ("memory", MemoryBridge().probe()),
        ("pipelines", PipelineBridge().probe()),
    ):
        avail = probe.get("available")
        if avail is None and isinstance(probe, dict):
            avail = any(
                (v or {}).get("available")
                for k, v in probe.items()
                if isinstance(v, dict) and "available" in v
            )
        print(f"  [{'OK' if avail else '--'}] {name}")
    status = estate_status()
    print("estate local paths:")
    for key, entry in status.items():
        flag = "OK" if entry.get("available") else "--"
        path = entry.get("effective_path") or entry.get("default_path") or "(unset)"
        print(f"  [{flag}] {key}: {entry.get('repo')} → {path}")
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
    pack = run_showcase(
        target=args.target or "showcase",
        work_dir=args.work_dir,
        mode=args.mode,
    )
    print(json.dumps(pack.to_dict(), indent=2, default=str))
    return 0 if pack.cycle.get("status") == "ok" else 1


def cmd_proof(_: argparse.Namespace) -> int:
    print(json.dumps(proof_pack(), indent=2))
    return 0


def cmd_invoke(args: argparse.Namespace) -> int:
    if args.hierarchy:
        result = invoke_validate_hierarchy()
    else:
        result = invoke_pipeline(
            args.pipeline,
            validate_only=not args.execute,
            timeout_sec=args.timeout,
        )
    print(json.dumps(result.to_dict(), indent=2, default=str))
    if result.status == "skip":
        return 0
    return 0 if result.status == "ok" else 1


def cmd_genius(args: argparse.Namespace) -> int:
    if args.brief:
        r = invoke_genius_role_brief()
    else:
        r = invoke_genius_doctor()
    print(json.dumps(r.to_dict(), indent=2, default=str))
    if r.status == "skip":
        return 0
    return 0 if r.status == "ok" else 1


def cmd_edge_probe(args: argparse.Namespace) -> int:
    receipt = probe_edge(
        category=args.category,
        limit=args.limit,
        timeout=args.timeout,
        workers=args.workers,
    )
    print(json.dumps(receipt.to_dict(), indent=2))
    # Soft: do not fail CI if some hosts down
    return 0 if receipt.ok_count > 0 or receipt.sample_size == 0 else 1


def cmd_demo(args: argparse.Namespace) -> int:
    steps = []
    steps.append({"step": "doctor", "version": __version__})
    steps.append({"step": "proof", "pack_keys": list(proof_pack().keys())})
    pack = run_showcase(target="recorded-demo", work_dir=args.work_dir, mode="compose")
    steps.append({"step": "showcase", "status": pack.cycle.get("status")})
    cyc = run_cycle("ground_up", target="demo-field-agent", work_dir=args.work_dir)
    steps.append({"step": "ground_up", "status": cyc.status})
    steps.append({"step": "leverage", "priority": (leverage_map("compose").get("catalog") or {}).get("mega_skills")})
    inv = invoke_pipeline("control-plane", validate_only=True)
    steps.append({"step": "invoke_validate", "status": inv.status})
    g = invoke_genius_doctor()
    steps.append({"step": "genius", "status": g.status})
    # small edge probe
    edge = probe_edge(limit=4, timeout=4.0)
    steps.append(
        {
            "step": "edge_probe",
            "ok": edge.ok_count,
            "fail": edge.fail_count,
            "sha256": edge.to_dict().get("sha256", "")[:16],
        }
    )
    out = {
        "demo": "recorded-path-v0.5",
        "doc": "docs/DEMO.md",
        "steps": steps,
        "closing": "Forward Deployed Agentic AI — stronger: live genius + edge probe receipts.",
    }
    print(json.dumps(out, indent=2, default=str))
    ok = cyc.status == "ok" and pack.cycle.get("status") == "ok"
    return 0 if ok else 1


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
        mode="compose",
        target=args.target or "compose",
        work_dir=args.work_dir,
        problem=args.problem or "Compose mega-skills + genius + memory + pipelines",
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

    sub.add_parser("doctor", help="Health").set_defaults(func=cmd_doctor)

    p_cyc = sub.add_parser("cycle", help="Full cycle")
    p_cyc.add_argument("--mode", required=True, choices=MODES)
    p_cyc.add_argument("--name", default=None)
    p_cyc.add_argument("--target", default=None)
    p_cyc.add_argument("--problem", default="")
    p_cyc.add_argument("--work-dir", default=".")
    p_cyc.add_argument("--continue-on-fail", action="store_true")
    p_cyc.set_defaults(func=cmd_cycle)

    p_sh = sub.add_parser("showcase", help="Impressive pack")
    p_sh.add_argument("--target", default="showcase")
    p_sh.add_argument("--mode", default="compose", choices=MODES)
    p_sh.add_argument("--work-dir", default=".")
    p_sh.set_defaults(func=cmd_showcase)

    sub.add_parser("proof", help="Diligence pack").set_defaults(func=cmd_proof)

    p_inv = sub.add_parser("invoke", help="Live mega-skills")
    p_inv.add_argument("--pipeline", default="control-plane", choices=sorted(ALLOWED_PIPELINES))
    p_inv.add_argument("--execute", action="store_true")
    p_inv.add_argument("--hierarchy", action="store_true")
    p_inv.add_argument("--timeout", type=int, default=120)
    p_inv.set_defaults(func=cmd_invoke)

    p_g = sub.add_parser("genius", help="Live Genius-Mastery hook")
    p_g.add_argument("--brief", action="store_true", help="Emit FDE role brief only")
    p_g.set_defaults(func=cmd_genius)

    p_ep = sub.add_parser("edge-probe", help="Probe public tech homepages (receipts)")
    p_ep.add_argument("--category", default=None)
    p_ep.add_argument("--limit", type=int, default=12)
    p_ep.add_argument("--timeout", type=float, default=5.0)
    p_ep.add_argument("--workers", type=int, default=6)
    p_ep.set_defaults(func=cmd_edge_probe)

    p_demo = sub.add_parser("demo", help="Recorded demo path")
    p_demo.add_argument("--work-dir", default=".")
    p_demo.set_defaults(func=cmd_demo)

    sub.add_parser("estate", help="Paths").set_defaults(func=cmd_estate)

    p_pr = sub.add_parser("probe", help="Bridges")
    p_pr.add_argument("--bridge", choices=["mega_skills", "genius", "memory", "pipelines"], default=None)
    p_pr.set_defaults(func=cmd_probe)

    p_co = sub.add_parser("compose", help="Compose cycle")
    p_co.add_argument("--target", default="compose")
    p_co.add_argument("--problem", default="")
    p_co.add_argument("--work-dir", default=".")
    p_co.set_defaults(func=cmd_compose)

    p_edge = sub.add_parser("edge", help="Homepage library")
    p_edge.add_argument("--stats", action="store_true")
    p_edge.add_argument("--category", default=None)
    p_edge.add_argument("--list-categories", action="store_true")
    p_edge.add_argument("--urls-only", action="store_true")
    p_edge.set_defaults(func=cmd_edge)

    p_lev = sub.add_parser("leverage", help="Recommendations")
    p_lev.add_argument("--mode", default="compose", choices=MODES)
    p_lev.add_argument("--summary", action="store_true")
    p_lev.set_defaults(func=cmd_leverage)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
