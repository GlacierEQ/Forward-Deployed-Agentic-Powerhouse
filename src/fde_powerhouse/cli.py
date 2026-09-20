"""CLI — doctor, cycle, estate status."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .cycle import run_cycle
from .estate import estate_status, load_estate
from .modes import MODES


def cmd_doctor(_: argparse.Namespace) -> int:
    print(f"fde-powerhouse {__version__}")
    print(f"modes: {', '.join(MODES)}")
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
    )
    print(json.dumps(receipt.to_dict(), indent=2))
    return 0 if receipt.status == "ok" else 1


def cmd_estate(_: argparse.Namespace) -> int:
    print(json.dumps(estate_status(load_estate()), indent=2, default=str))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fde-powerhouse")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_doc = sub.add_parser("doctor", help="Kernel + estate health")
    p_doc.set_defaults(func=cmd_doctor)

    p_cyc = sub.add_parser("cycle", help="Run full cycle")
    p_cyc.add_argument("--mode", required=True, choices=MODES)
    p_cyc.add_argument("--name", default=None, help="ground_up system name")
    p_cyc.add_argument("--target", default=None, help="existing path/repo for upgrade modes")
    p_cyc.add_argument("--work-dir", default=".")
    p_cyc.add_argument("--continue-on-fail", action="store_true")
    p_cyc.set_defaults(func=cmd_cycle)

    p_est = sub.add_parser("estate", help="Show estate resolution")
    p_est.set_defaults(func=cmd_estate)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
