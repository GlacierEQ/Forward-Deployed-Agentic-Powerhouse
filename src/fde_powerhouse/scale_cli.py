"""Terminal entrypoint for the Scale FDE fire-and-forget mission launcher."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .scale_orchestrator import (
    DEFAULT_MAX_WORKERS,
    MissionOrchestrationError,
    load_mission,
    load_state,
    run_mission,
    subprocess_dispatch,
    write_state,
)


def _run(args: argparse.Namespace) -> int:
    mission = load_mission(args.mission)
    state_path = Path(args.state)
    prior_state = None if args.fresh else load_state(state_path)

    def checkpoint(snapshot: dict) -> None:
        write_state(state_path, snapshot)

    result = run_mission(
        mission,
        dispatch=subprocess_dispatch,
        prior_state=prior_state,
        max_workers=args.max_workers,
        checkpoint=checkpoint,
    )
    write_state(state_path, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "COMPLETE" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scale-fde-demo")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser(
        "run",
        help="Launch the dependency-ready Scale workstream frontier and resume by default.",
    )
    run.add_argument("mission", help="Path to SCALE_FDE_MISSION.yaml")
    run.add_argument(
        "--state",
        default=".scale-fde/orchestrator-state.json",
        help="Durable orchestrator checkpoint path.",
    )
    run.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help=(
            "Override mission orchestrator.max_workers. "
            f"Measured Agent-A provider knee is {DEFAULT_MAX_WORKERS}."
        ),
    )
    run.add_argument(
        "--fresh",
        action="store_true",
        help="Ignore an existing checkpoint and execute the mission from its initial frontier.",
    )
    run.set_defaults(func=_run)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except MissionOrchestrationError as exc:
        print(
            json.dumps(
                {
                    "schema": "glaciereq.scale-fde.orchestrator-error.v1",
                    "status": "INVALID_MISSION_OR_STATE",
                    "error": str(exc),
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
