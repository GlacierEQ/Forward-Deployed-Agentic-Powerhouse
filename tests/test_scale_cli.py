from __future__ import annotations

import json
import sys
from pathlib import Path

from fde_powerhouse.scale_cli import main
from fde_powerhouse.scale_orchestrator import (
    launcher_digest,
    load_launchers,
    load_mission,
    mission_digest,
)


def _mission_text() -> str:
    return """
schema: glaciereq.scale-fde-mission.v1
id: SCALE-FDE-DEMO-001
revision: 2
objective: prove mission
terminal_condition: independently verified
workstreams:
  A: estate_intelligence_gatling
  B: runtime_swarm_durability
  C: memory_composition_compounding
  D: integration_mcp_sigma_glue
  E: independent_verification_scale_product
""".strip() + "\n"


def _launchers_text(command: list[str]) -> str:
    rendered = json.dumps(command)
    return f"""
schema: glaciereq.scale-fde-launchers.v1
max_workers: 4
workstreams:
  A: {{deps: [], command: {rendered}}}
  B: {{deps: [A], command: {rendered}}}
  C: {{deps: [A], command: {rendered}}}
  D: {{deps: [A], command: {rendered}}}
  E: {{deps: [A], command: {rendered}}}
""".strip() + "\n"


def _write_inputs(tmp_path: Path, command: list[str]):
    shared = tmp_path / "shared"
    configs = tmp_path / "configs"
    shared.mkdir()
    configs.mkdir()
    mission = shared / "SCALE_FDE_MISSION.yaml"
    launchers = configs / "scale_launchers.yaml"
    mission.write_text(_mission_text(), encoding="utf-8")
    launchers.write_text(_launchers_text(command), encoding="utf-8")
    return mission, launchers


def test_scale_cli_run_uses_canonical_mission_and_default_launcher_path(
    tmp_path: Path,
    monkeypatch,
    capsys,
):
    mission, _ = _write_inputs(
        tmp_path,
        [sys.executable, "-c", "raise SystemExit(0)"],
    )
    state = tmp_path / ".scale-fde" / "orchestrator-state.json"
    monkeypatch.chdir(tmp_path)

    code = main(["run", str(mission), "--state", str(state)])

    assert code == 0
    saved = json.loads(state.read_text(encoding="utf-8"))
    assert saved["status"] == "LAUNCH_COMPLETE"
    assert saved["mission_complete"] is False
    assert saved["completed"] == ["A", "B", "C", "D", "E"]
    printed = json.loads(capsys.readouterr().out)
    assert printed["status"] == "LAUNCH_COMPLETE"


def test_scale_cli_explicit_launchers_path_and_resume_skip_completed_work(
    tmp_path: Path,
    capsys,
):
    marker = tmp_path / "marker.txt"
    command = [
        sys.executable,
        "-c",
        (
            "from pathlib import Path; "
            f"p=Path({str(marker)!r}); "
            "p.write_text(p.read_text() + 'x' if p.exists() else 'x')"
        ),
    ]
    mission, launchers = _write_inputs(tmp_path, command)
    state = tmp_path / "state.json"

    assert (
        main(
            [
                "run",
                str(mission),
                "--launchers",
                str(launchers),
                "--state",
                str(state),
            ]
        )
        == 0
    )
    capsys.readouterr()
    first = marker.read_text(encoding="utf-8")
    assert len(first) == 5

    assert (
        main(
            [
                "run",
                str(mission),
                "--launchers",
                str(launchers),
                "--state",
                str(state),
            ]
        )
        == 0
    )
    capsys.readouterr()
    assert marker.read_text(encoding="utf-8") == first


def test_scale_cli_fresh_reruns_launch_frontier(tmp_path: Path, capsys):
    marker = tmp_path / "marker.txt"
    command = [
        sys.executable,
        "-c",
        (
            "from pathlib import Path; "
            f"p=Path({str(marker)!r}); "
            "p.write_text(p.read_text() + 'x' if p.exists() else 'x')"
        ),
    ]
    mission, launchers = _write_inputs(tmp_path, command)
    state = tmp_path / "state.json"
    args = [
        "run",
        str(mission),
        "--launchers",
        str(launchers),
        "--state",
        str(state),
    ]

    assert main(args) == 0
    capsys.readouterr()
    first = marker.read_text(encoding="utf-8")
    assert main([*args, "--fresh"]) == 0
    capsys.readouterr()
    assert len(marker.read_text(encoding="utf-8")) == len(first) + 5


def test_scale_cli_requires_launcher_contract_when_default_missing(
    tmp_path: Path,
    monkeypatch,
    capsys,
):
    shared = tmp_path / "shared"
    shared.mkdir()
    mission = shared / "SCALE_FDE_MISSION.yaml"
    mission.write_text(_mission_text(), encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    code = main(["run", str(mission)])

    assert code == 2
    error = json.loads(capsys.readouterr().err)
    assert error["status"] == "INVALID_MISSION_OR_STATE"
    assert "launcher" in error["error"].lower()


def test_scale_cli_retry_controls_are_explicit(tmp_path: Path, capsys):
    marker = tmp_path / "marker.txt"
    command = [
        sys.executable,
        "-c",
        f"from pathlib import Path; Path({str(marker)!r}).write_text('x')",
    ]
    mission_path, launch_path = _write_inputs(tmp_path, command)
    mission = load_mission(mission_path)
    binding = load_launchers(launch_path)
    state = tmp_path / "state.json"
    state.write_text(
        json.dumps(
            {
                "mission_digest": mission_digest(mission),
                "launcher_digest": launcher_digest(binding),
                "completed": [],
                "failed": [],
                "in_flight": ["A"],
                "receipts": {},
            }
        ),
        encoding="utf-8",
    )
    base = [
        "run",
        str(mission_path),
        "--launchers",
        str(launch_path),
        "--state",
        str(state),
    ]

    assert main(base) == 2
    capsys.readouterr()
    assert not marker.exists()
    assert main([*base, "--retry-ambiguous"]) == 0
    capsys.readouterr()
    assert marker.exists()


def test_scale_cli_blocked_launch_returns_nonzero_without_claiming_mission_failure(
    tmp_path: Path,
    capsys,
):
    mission, launchers = _write_inputs(
        tmp_path,
        [sys.executable, "-c", "raise SystemExit(7)"],
    )
    state = tmp_path / "state.json"

    code = main(
        [
            "run",
            str(mission),
            "--launchers",
            str(launchers),
            "--state",
            str(state),
        ]
    )

    assert code == 1
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "LAUNCH_BLOCKED"
    assert result["mission_complete"] is False
