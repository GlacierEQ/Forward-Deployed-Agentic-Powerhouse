from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from fde_powerhouse.scale_fusion import (
    FusionContractError,
    fusion_digest,
    load_fusion,
    preflight_fusion,
    validate_fusion,
    write_faraway_projection,
)


def fusion_profile() -> dict:
    return {
        "schema": "glaciereq.scale-fde-fusion.v1",
        "components": {
            "computer_user": {
                "role": "durable_execution_plane",
                "activation": "required_live",
                "root_env": "SCALE_FDE_COMPUTER_USER_ROOT",
                "preflight": ["python3", "-m", "computer_user.cli", "doctor"],
            },
            "mega_pipeline": {
                "role": "capability_composition_and_sequencing",
                "activation": "required_live",
                "root_env": "SCALE_FDE_MEGA_SKILLS_ROOT",
                "preflight": [
                    "python3",
                    "scripts/run_deep_work_pipeline.py",
                    "--pipeline",
                    "control-plane",
                    "--validate-only",
                ],
                "includes": ["faraway_party"],
            },
            "faraway_party": {
                "role": "long_horizon_continuity",
                "activation": "composed",
                "via": "mega_pipeline",
                "direct_command": None,
            },
            "make_it_heavy": {
                "role": "conditional_parallel_reasoning",
                "activation": "opt_in",
                "enable_env": "SCALE_FDE_ENABLE_HEAVY",
                "root_env": "SCALE_FDE_MAKE_IT_HEAVY_ROOT",
                "preflight": ["python3", "-c", "import orchestrator; print('ready')"],
            },
            "apple_mcp": {
                "role": "macos_native_provider",
                "activation": "opt_in",
                "enable_env": "SCALE_FDE_ENABLE_APPLE_MCP",
                "file_env": "SCALE_FDE_APPLE_MCP_DXT",
                "platform": "darwin",
                "routed_via": "workstream_D_sigma_glue",
                "expected_sha256": "0" * 64,
                "required_tools": [
                    "contacts",
                    "notes",
                    "messages",
                    "mail",
                    "reminders",
                    "calendar",
                    "maps",
                ],
            },
        },
    }


def test_fusion_digest_is_mapping_order_independent():
    left = fusion_profile()
    right = {
        "components": left["components"],
        "schema": left["schema"],
    }

    assert fusion_digest(left) == fusion_digest(right)
    assert fusion_digest(left).startswith("sha256:")


def test_validate_fusion_requires_exact_roles_and_no_duplicate_faraway_launch():
    profile = fusion_profile()
    validate_fusion(profile)

    assert profile["components"]["faraway_party"]["via"] == "mega_pipeline"
    assert profile["components"]["faraway_party"]["direct_command"] is None

    broken = fusion_profile()
    broken["components"]["faraway_party"]["direct_command"] = ["python3", "run.py"]
    with pytest.raises(FusionContractError, match="Faraway Party"):
        validate_fusion(broken)

    broken = fusion_profile()
    broken["components"]["computer_user"]["role"] = "generic_runner"
    with pytest.raises(FusionContractError, match="computer_user"):
        validate_fusion(broken)


def test_non_live_preflight_preserves_missing_required_live_components_without_failure():
    receipt = preflight_fusion(
        fusion_profile(),
        live=False,
        env={},
        platform="linux",
    )

    assert receipt["status"] == "READY_WITH_DEFERRED_COMPONENTS"
    assert receipt["components"]["computer_user"]["state"] == "not_configured"
    assert receipt["components"]["mega_pipeline"]["state"] == "not_configured"
    assert receipt["components"]["make_it_heavy"]["state"] == "disabled"
    assert receipt["components"]["apple_mcp"]["state"] == "disabled"
    assert receipt["components"]["faraway_party"]["state"] == "composed_via_mega_pipeline"


def test_live_preflight_fails_closed_when_required_core_is_missing():
    with pytest.raises(FusionContractError, match="required live fusion component"):
        preflight_fusion(
            fusion_profile(),
            live=True,
            env={},
            platform="darwin",
        )


def test_apple_mcp_preflight_verifies_dxt_hash_manifest_and_tools(tmp_path: Path):
    package = tmp_path / "apple-mcp.dxt"
    manifest = {
        "dxt_version": "0.1",
        "name": "apple-mcp",
        "version": "1.0.0",
        "server": {"type": "node", "entry_point": "dist/index.js"},
        "tools": [
            {"name": name, "description": name}
            for name in [
                "contacts",
                "notes",
                "messages",
                "mail",
                "reminders",
                "calendar",
                "maps",
            ]
        ],
        "compatibility": {"platforms": ["darwin"]},
    }
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("manifest.json", json.dumps(manifest))
        archive.writestr("dist/index.js", "console.log('mcp')")
    digest = hashlib.sha256(package.read_bytes()).hexdigest()

    profile = fusion_profile()
    profile["components"]["apple_mcp"]["expected_sha256"] = digest
    receipt = preflight_fusion(
        profile,
        live=False,
        env={
            "SCALE_FDE_ENABLE_APPLE_MCP": "1",
            "SCALE_FDE_APPLE_MCP_DXT": str(package),
        },
        platform="darwin",
    )

    apple = receipt["components"]["apple_mcp"]
    assert apple["state"] == "ready"
    assert apple["sha256"] == digest
    assert apple["manifest"]["name"] == "apple-mcp"
    assert apple["manifest"]["version"] == "1.0.0"
    assert apple["tools"] == [
        "contacts",
        "notes",
        "messages",
        "mail",
        "reminders",
        "calendar",
        "maps",
    ]
    assert apple["routed_via"] == "workstream_D_sigma_glue"


def test_apple_mcp_fails_closed_on_hash_or_platform_mismatch(tmp_path: Path):
    package = tmp_path / "apple-mcp.dxt"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr(
            "manifest.json",
            json.dumps(
                {
                    "name": "apple-mcp",
                    "version": "1.0.0",
                    "server": {"type": "node", "entry_point": "dist/index.js"},
                    "tools": [],
                    "compatibility": {"platforms": ["darwin"]},
                }
            ),
        )

    profile = fusion_profile()
    env = {
        "SCALE_FDE_ENABLE_APPLE_MCP": "1",
        "SCALE_FDE_APPLE_MCP_DXT": str(package),
    }

    with pytest.raises(FusionContractError, match="sha256"):
        preflight_fusion(profile, live=False, env=env, platform="darwin")

    profile["components"]["apple_mcp"]["expected_sha256"] = hashlib.sha256(
        package.read_bytes()
    ).hexdigest()
    with pytest.raises(FusionContractError, match="darwin"):
        preflight_fusion(profile, live=False, env=env, platform="linux")


def test_faraway_projection_writes_five_durable_files_with_source_digests(
    tmp_path: Path,
):
    mission = {
        "schema": "glaciereq.scale-fde-mission.v1",
        "id": "SCALE-FDE-DEMO-001",
        "objective": "prove the mission",
    }
    launcher_state = {
        "status": "LAUNCH_RUNNING",
        "completed": ["A"],
        "failed": [],
        "blocked": [],
        "in_flight": ["B", "C", "D", "E"],
        "waves": [["A"], ["B", "C", "D", "E"]],
    }
    fusion_receipt = {
        "schema": "glaciereq.scale-fde-fusion-receipt.v1",
        "status": "READY_WITH_DEFERRED_COMPONENTS",
        "fusion_digest": "sha256:" + "1" * 64,
    }

    result = write_faraway_projection(
        tmp_path,
        mission=mission,
        mission_digest="sha256:" + "2" * 64,
        launcher_digest="sha256:" + "3" * 64,
        fusion_receipt=fusion_receipt,
        launcher_state=launcher_state,
    )

    assert set(result["files"]) == {
        "MISSION.md",
        "ROADMAP.md",
        "CONTEXT.md",
        "EVIDENCE.md",
        "HANDOFF.md",
    }
    for name, metadata in result["files"].items():
        path = tmp_path / name
        assert path.exists()
        assert metadata["sha256"].startswith("sha256:")
        assert hashlib.sha256(path.read_bytes()).hexdigest() == metadata["sha256"].split(":", 1)[1]

    assert "SCALE-FDE-DEMO-001" in (tmp_path / "MISSION.md").read_text()
    assert "B, C, D, E" in (tmp_path / "HANDOFF.md").read_text()
    assert "sha256:" + "2" * 64 in (tmp_path / "EVIDENCE.md").read_text()


def test_checked_in_fusion_profile_is_valid_and_pins_uploaded_apple_mcp():
    profile = load_fusion(Path("configs/scale_fusion.yaml"))
    validate_fusion(profile)

    assert profile["components"]["computer_user"]["preflight"] == [
        "python3",
        "-m",
        "computer_user.cli",
        "health",
    ]
    assert profile["components"]["mega_pipeline"]["includes"] == ["faraway_party"]
    assert profile["components"]["faraway_party"]["via"] == "mega_pipeline"
    assert (
        profile["components"]["apple_mcp"]["expected_sha256"]
        == "5e2b97363f3b6ad9d62f0c82d32d6af94ffbab83c8e39e0922766025b59dead5"
    )
    assert profile["components"]["apple_mcp"]["routed_via"] == "workstream_D_sigma_glue"
