"""CLI — doctor, cycle, estate, compose, probe, edge."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .bridges import GeniusBridge, MegaSkillsBridge, MemoryBridge, PipelineBridge
from .cycle import run_cycle
from .estate import estate_status, load_estate
from .leading_edge import all_homepages, by_category, categories, library_stats
from .modes import MODES


def cmd_doctor(_: argparse.Namespace) -> int:
    print(f"fde-powerhouse {__version__}")
    print(f"modes: {', '.join(MODES)}")
    stats = library_stats()
    print(f"leading_edge: {stats.get('sources', 0)} sources across {stats.get('categories', 0)} categories")
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
    print("estate:")
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fde-powerhouse")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_doc = sub.add_parser("doctor", help="Kernel + estate + bridge + edge library health")
    p_doc.set_defaults(func=cmd_doctor)

    p_cyc = sub.add_parser("cycle", help="Run full cycle")
    p_cyc.add_argument("--mode", required=True, choices=MODES)
    p_cyc.add_argument("--name", default=None, help="ground_up system name")
    p_cyc.add_argument("--target", default=None, help="existing path/repo for upgrade modes")
    p_cyc.add_argument("--problem", default="", help="problem statement")
    p_cyc.add_argument("--work-dir", default=".")
    p_cyc.add_argument("--continue-on-fail", action="store_true")
    p_cyc.set_defaults(func=cmd_cycle)

    p_est = sub.add_parser("estate", help="Show estate resolution")
    p_est.set_defaults(func=cmd_estate)

    p_pr = sub.add_parser("probe", help="Probe estate bridges")
    p_pr.add_argument(
        "--bridge",
        choices=["mega_skills", "genius", "memory", "pipelines"],
        default=None,
    )
    p_pr.set_defaults(func=cmd_probe)

    p_co = sub.add_parser("compose", help="Run compose mode (skills+genius+memory+pipelines)")
    p_co.add_argument("--target", default="compose")
    p_co.add_argument("--problem", default="")
    p_co.add_argument("--work-dir", default=".")
    p_co.set_defaults(func=cmd_compose)

    p_edge = sub.add_parser("edge", help="Leading-edge public tech homepage library")
    p_edge.add_argument("--stats", action="store_true")
    p_edge.add_argument("--category", default=None, help="Filter by category id")
    p_edge.add_argument("--list-categories", action="store_true")
    p_edge.add_argument("--urls-only", action="store_true")
    p_edge.set_defaults(func=cmd_edge)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
