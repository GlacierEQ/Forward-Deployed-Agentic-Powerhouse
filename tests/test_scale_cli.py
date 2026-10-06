from __future__ import annotations

import json
import sys
from pathlib import Path

from fde_powerhouse.scale_cli import main
from fde_powerhouse.scale_orchestrator import load_mission, mission_digest


def _mission_text(command: list[str]) -> str:
    command_json = json.dumps(command)
    return f"""
schema: glaciereq.scale-fde.mission.v1
mission_id: scale-cli-test
orchestrator:
  max_workers: 4
workstreams:
  - id: A
    deps: []
    command: {command_json}
"""


def test_scale_cli_run_executes_and_persists_checkpoint(tmp_path: Path, capsys):
    state = tmp_path / "state.json"
    mission = tmp_path / "mission.yaml"
    mission.write_text(
        _mission_text([sys.executable, "-c", "print('fired')"]),
        encoding="utf-8",
    )

    code = main(["run", str(mission), "--state", str(state)])

    assert code == 0
    saved = json.loads(state.read_text(encoding="utf-8"))
    assert saved["status"] == "COMPLETE"
    assert saved["completed"] == ["A"]
    printed = json.loads(capsys.readouterr().out)
    assert printed["status"] == "COMPLETE"


def test_scale_cli_default_resume_does_not_rerun_completed_work(tmp_path: Path):
    marker = tmp_path / "marker.txt"
    state = tmp_path / "state.json"
    mission = tmp_path / "mission.yaml"
    mission.write_text(
        _mission_text(
            [
                sys.executable,
                "-c",
                (
                    "from pathlib import Path; "
                    f"p=Path({str(marker)!r}); "
                    "p.write_text(p.read_text() + 'x' if p.exists() else 'x')"
                ),
            ]
        ),
        encoding="utf-8",
    )

    assert main(["run", str(mission), "--state", str(state)]) == 0
    assert main(["run", str(mission), "--state", str(state)]) == 0

    assert marker.read_text(encoding="utf-8") == "x"


def test_scale_cli_fresh_reruns_completed_work(tmp_path: Path):
    marker = tmp_path / "marker.txt"
    state = tmp_path / "state.json"
    mission = tmp_path / "mission.yaml"
    mission.write_text(
        _mission_text(
            [
                sys.executable,
                "-c",
                (
                    "from pathlib import Path; "
                    f"p=Path({str(marker)!r}); "
                    "p.write_text(p.read_text() + 'x' if p.exists() else 'x')"
                ),
            ]
        ),
        encoding="utf-8",
    )

    assert main(["run", str(mission), "--state", str(state)]) == 0
    assert main(["run", str(mission), "--state", str(state), "--fresh"]) == 0

    assert marker.read_text(encoding="utf-8") == "xx"


def test_scale_cli_blocked_mission_returns_nonzero(tmp_path: Path, capsys):
    mission = tmp_path / "mission.yaml"
    state = tmp_path / "state.json"
    mission.write_text(
        f"""
schema: glaciereq.scale-fde.mission.v1
mission_id: scale-cli-failure
orchestrator:
  max_workers: 4
workstreams:
  - id: A
    deps: []
    command: {json.dumps([sys.executable, "-c", "raise SystemExit(7)"])}
  - id: B
    deps: [A]
    command: {json.dumps([sys.executable, "-c", "raise SystemExit(0)"])}
""",
        encoding="utf-8",
    )

    code = main(["run", str(mission), "--state", str(state)])

    assert code == 1
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "BLOCKED"
    assert result["failed"] == ["A"]
    assert result["blocked"] == ["B"]



def test_scale_cli_retry_ambiguous_is_explicit(tmp_path: Path):
    marker = tmp_path / "marker.txt"
    state = tmp_path / "state.json"
    mission = tmp_path / "mission.yaml"
    mission.write_text(
        _mission_text(
            [
                sys.executable,
                "-c",
                f"from pathlib import Path; Path({str(marker)!r}).write_text('x')",
            ]
        ),
        encoding="utf-8",
    )
    loaded = load_mission(mission)
    state.write_text(
        json.dumps(
            {
                "mission_digest": mission_digest(loaded),
                "completed": [],
                "failed": [],
                "in_flight": ["A"],
                "receipts": {},
            }
        ),
        encoding="utf-8",
    )

    assert main(["run", str(mission), "--state", str(state)]) == 2
    assert not marker.exists()
    assert (
        main(
            [
                "run",
                str(mission),
                "--state",
                str(state),
                "--retry-ambiguous",
            ]
        )
        == 0
    )
    assert marker.read_text(encoding="utf-8") == "x"


def test_scale_cli_retry_failed_is_explicit(tmp_path: Path):
    marker = tmp_path / "marker.txt"
    state = tmp_path / "state.json"
    mission = tmp_path / "mission.yaml"
    mission.write_text(
        _mission_text(
            [
                sys.executable,
                "-c",
                f"from pathlib import Path; Path({str(marker)!r}).write_text('x')",
            ]
        ),
        encoding="utf-8",
    )
    loaded = load_mission(mission)
    state.write_text(
        json.dumps(
            {
                "mission_digest": mission_digest(loaded),
                "completed": [],
                "failed": ["A"],
                "in_flight": [],
                "receipts": {"A": {"status": "failed", "returncode": 9}},
            }
        ),
        encoding="utf-8",
    )

    assert main(["run", str(mission), "--state", str(state)]) == 1
    assert not marker.exists()
    assert (
        main(
            [
                "run",
                str(mission),
                "--state",
                str(state),
                "--retry-failed",
            ]
        )
        == 0
    )
    assert marker.read_text(encoding="utf-8") == "x"
