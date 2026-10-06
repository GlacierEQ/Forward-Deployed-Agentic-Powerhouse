"""Terminal entrypoint for the Scale FDE workstream launcher."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .scale_orchestrator import (
    DEFAULT_MAX_WORKERS,
    MissionOrchestrationError,
    load_launchers,
    load_mission,
    load_state,
    run_mission,
    subprocess_dispatch,
    write_state,
)


def _default_launchers_path(mission_path: Path) -> Path:
    resolved = mission_path.resolve()
    if resolved.parent.name == "shared":
        candidate = resolved.parent.parent / "configs" / "scale_launchers.yaml"
        if candidate.exists():
            return candidate
    return Path("configs/scale_launchers.yaml")


def _run(args: argparse.Namespace) -> int:
    mission_path = Path(args.mission)
    mission = load_mission(mission_path)
    launchers_path = (
        Path(args.launchers)
        if args.launchers is not None
        else _default_launchers_path(mission_path)
    )
    launchers = load_launchers(launchers_path)
    state_path = Path(args.state)
    prior_state = None if args.fresh else load_state(state_path)

    def checkpoint(snapshot: dict) -> None:
        write_state(state_path, snapshot)

    result = run_mission(
        mission,
        launchers,
        dispatch=subprocess_dispatch,
        prior_state=prior_state,
        max_workers=args.max_workers,
        checkpoint=checkpoint,
        retry_ambiguous=args.retry_ambiguous,
        retry_failed=args.retry_failed,
    )
    write_state(state_path, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "LAUNCH_COMPLETE" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scale-fde-demo")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser(
        "run",
        help=(
            "Launch the dependency-ready Scale workstream frontier from the "
            "canonical mission plus a separate local launcher-binding contract."
        ),
    )
    run.add_argument("mission", help="Path to canonical SCALE_FDE_MISSION.yaml")
    run.add_argument(
        "--launchers",
        default=None,
        help=(
            "Path to glaciereq.scale-fde-launchers.v1 bindings. Defaults to "
            "configs/scale_launchers.yaml beside the repository containing shared/."
        ),
    )
    run.add_argument(
        "--state",
        default=".scale-fde/orchestrator-state.json",
        help="Durable launcher checkpoint path.",
    )
    run.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help=(
            "Override launcher max_workers. "
            f"Agent-A's measured provider-bound knee is {DEFAULT_MAX_WORKERS}; "
            "this is a launch bound, not a sibling-runtime throughput claim."
        ),
    )
    run.add_argument(
        "--fresh",
        action="store_true",
        help="Ignore an existing launcher checkpoint and start at the initial frontier.",
    )
    run.add_argument(
        "--retry-ambiguous",
        action="store_true",
        help=(
            "Explicitly replay a launcher left in-flight when terminal-artifact "
            "readback cannot prove whether it completed."
        ),
    )
    run.add_argument(
        "--retry-failed",
        action="store_true",
        help="Explicitly replay launcher work units recorded as failed.",
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
                    "schema": "glaciereq.scale-fde.launcher-error.v1",
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
