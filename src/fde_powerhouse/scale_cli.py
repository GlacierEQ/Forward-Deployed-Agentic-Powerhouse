"""Terminal entrypoint for the Scale FDE workstream launcher."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .scale_fusion import (
    FusionContractError,
    load_fusion,
    preflight_fusion,
    write_faraway_projection,
)
from .scale_orchestrator import (
    DEFAULT_MAX_WORKERS,
    MissionOrchestrationError,
    launcher_digest,
    load_launchers,
    load_mission,
    load_state,
    mission_digest,
    run_mission,
    subprocess_dispatch,
    write_state,
)


def _resolve_mission_path(mission_path: Path) -> Path:
    if mission_path.exists():
        return mission_path
    if mission_path.name == "SCALE_FDE_MISSION.yaml" and mission_path.parent == Path("."):
        shared = Path("shared") / mission_path.name
        if shared.exists():
            return shared
    return mission_path


def _default_config_path(mission_path: Path, filename: str) -> Path:
    resolved = mission_path.resolve()
    if resolved.parent.name == "shared":
        candidate = resolved.parent.parent / "configs" / filename
        if candidate.exists():
            return candidate
    return Path("configs") / filename


def _default_launchers_path(mission_path: Path) -> Path:
    return _default_config_path(mission_path, "scale_launchers.yaml")


def _default_fusion_path(mission_path: Path) -> Path:
    return _default_config_path(mission_path, "scale_fusion.yaml")


def _run(args: argparse.Namespace) -> int:
    mission_path = _resolve_mission_path(Path(args.mission))
    mission = load_mission(mission_path)
    launchers_path = (
        Path(args.launchers)
        if args.launchers is not None
        else _default_launchers_path(mission_path)
    )
    launchers = load_launchers(launchers_path)

    fusion_path = (
        Path(args.fusion)
        if args.fusion is not None
        else _default_fusion_path(mission_path)
    )
    fusion_receipt = None
    if args.fusion is not None or fusion_path.exists():
        fusion = load_fusion(fusion_path)
        fusion_receipt = preflight_fusion(fusion, live=args.live)

    state_path = Path(args.state)
    prior_state = None if args.fresh else load_state(state_path)
    mission_hash = mission_digest(mission)
    launcher_hash = launcher_digest(launchers)

    fusion_receipt_path = state_path.parent / "fusion-receipt.json"
    faraway_root = state_path.parent / "faraway-party"
    if fusion_receipt is not None:
        write_state(fusion_receipt_path, fusion_receipt)

    def checkpoint(snapshot: dict) -> None:
        durable_snapshot = dict(snapshot)
        if fusion_receipt is not None:
            durable_snapshot["fusion"] = {
                "status": fusion_receipt["status"],
                "fusion_digest": fusion_receipt["fusion_digest"],
                "receipt": str(fusion_receipt_path),
            }
        write_state(state_path, durable_snapshot)
        if fusion_receipt is not None:
            write_faraway_projection(
                faraway_root,
                mission=mission,
                mission_digest=mission_hash,
                launcher_digest=launcher_hash,
                fusion_receipt=fusion_receipt,
                launcher_state=durable_snapshot,
            )

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
    if fusion_receipt is not None:
        result = {
            **result,
            "fusion": {
                "status": fusion_receipt["status"],
                "fusion_digest": fusion_receipt["fusion_digest"],
                "receipt": str(fusion_receipt_path),
                "faraway_root": str(faraway_root),
                "live": bool(args.live),
            },
        }
    write_state(state_path, result)
    if fusion_receipt is not None:
        write_faraway_projection(
            faraway_root,
            mission=mission,
            mission_digest=mission_hash,
            launcher_digest=launcher_hash,
            fusion_receipt=fusion_receipt,
            launcher_state=result,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "LAUNCH_COMPLETE" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scale-fde-demo")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser(
        "run",
        help=(
            "Launch the dependency-ready Scale workstream frontier from the "
            "canonical mission plus separate launcher and capability-fusion contracts."
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
        "--fusion",
        default=None,
        help=(
            "Path to glaciereq.scale-fde-fusion.v1. When omitted, "
            "configs/scale_fusion.yaml is used if present."
        ),
    )
    run.add_argument(
        "--live",
        action="store_true",
        help=(
            "Require live-core fusion preflights. Computer User and Mega Pipeline "
            "must be configured and healthy before workstream launch."
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
    except (MissionOrchestrationError, FusionContractError) as exc:
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
