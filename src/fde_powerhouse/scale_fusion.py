"""Capability-fusion preflight and Faraway Party durable projection for Scale FDE."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import zipfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

FUSION_SCHEMA = "glaciereq.scale-fde-fusion.v1"
FUSION_RECEIPT_SCHEMA = "glaciereq.scale-fde-fusion-receipt.v1"
EXPECTED_ROLES = {
    "computer_user": "durable_execution_plane",
    "mega_pipeline": "capability_composition_and_sequencing",
    "faraway_party": "long_horizon_continuity",
    "make_it_heavy": "conditional_parallel_reasoning",
    "apple_mcp": "macos_native_provider",
}
_TRUE = {"1", "true", "yes", "on"}


class FusionContractError(ValueError):
    """Raised when a fusion profile or configured capability fails closed."""


def _canonical_digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        dict(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def fusion_digest(profile: Mapping[str, Any]) -> str:
    if not isinstance(profile, Mapping):
        raise FusionContractError("fusion profile must be a mapping")
    return _canonical_digest(profile)


def load_fusion(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        raw = yaml.safe_load(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FusionContractError(f"fusion profile not found: {source}") from exc
    except yaml.YAMLError as exc:
        raise FusionContractError(f"invalid fusion profile YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise FusionContractError("fusion profile YAML must contain a mapping")
    return raw


def validate_fusion(profile: Mapping[str, Any]) -> None:
    if profile.get("schema") != FUSION_SCHEMA:
        raise FusionContractError(
            f"fusion schema must be {FUSION_SCHEMA!r}, got {profile.get('schema')!r}"
        )
    components = profile.get("components")
    if not isinstance(components, Mapping):
        raise FusionContractError("fusion components must be a mapping")

    missing = sorted(set(EXPECTED_ROLES) - set(components))
    if missing:
        raise FusionContractError(f"missing fusion components: {missing}")

    for name, expected_role in EXPECTED_ROLES.items():
        component = components[name]
        if not isinstance(component, Mapping):
            raise FusionContractError(f"{name} fusion component must be a mapping")
        role = component.get("role")
        if role != expected_role:
            raise FusionContractError(
                f"{name} role must be {expected_role!r}, got {role!r}"
            )

    mega = components["mega_pipeline"]
    includes = mega.get("includes") or []
    if not isinstance(includes, Sequence) or isinstance(
        includes, (str, bytes, bytearray)
    ):
        raise FusionContractError("mega_pipeline includes must be an ordered collection")
    if "faraway_party" not in includes:
        raise FusionContractError(
            "Mega Pipeline must compose Faraway Party rather than duplicate it"
        )

    faraway = components["faraway_party"]
    if faraway.get("via") != "mega_pipeline":
        raise FusionContractError("Faraway Party must be composed via Mega Pipeline")
    if faraway.get("direct_command"):
        raise FusionContractError(
            "Faraway Party must not have a duplicate direct launch command"
        )

    apple = components["apple_mcp"]
    if apple.get("routed_via") != "workstream_D_sigma_glue":
        raise FusionContractError(
            "apple_mcp must route through Workstream D / sigma-glue"
        )
    expected_sha = str(apple.get("expected_sha256") or "")
    if len(expected_sha) != 64 or any(
        char not in "0123456789abcdef" for char in expected_sha.casefold()
    ):
        raise FusionContractError("apple_mcp expected_sha256 must be a SHA-256 hex digest")


def _env_enabled(env: Mapping[str, str], key: str | None) -> bool:
    if not key:
        return False
    return str(env.get(key, "")).strip().casefold() in _TRUE


def _run_preflight(
    command: Sequence[str],
    *,
    cwd: Path,
    timeout_seconds: float,
) -> dict[str, Any]:
    if not cwd.is_dir():
        raise FusionContractError(f"configured fusion root does not exist: {cwd}")
    argv = [str(part) for part in command]
    if not argv or any(not part for part in argv):
        raise FusionContractError("fusion preflight command cannot be empty")
    try:
        completed = subprocess.run(
            argv,
            cwd=str(cwd),
            timeout=timeout_seconds,
            capture_output=True,
            text=True,
            shell=False,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise FusionContractError(
            f"fusion preflight failed to execute in {cwd}: {exc}"
        ) from exc
    receipt = {
        "command_sha256": _canonical_digest({"argv": argv}),
        "returncode": completed.returncode,
        "stdout_sha256": "sha256:"
        + hashlib.sha256((completed.stdout or "").encode("utf-8")).hexdigest(),
        "stderr_sha256": "sha256:"
        + hashlib.sha256((completed.stderr or "").encode("utf-8")).hexdigest(),
        "stdout_preview": (completed.stdout or "")[:1500],
        "stderr_preview": (completed.stderr or "")[:1500],
        "shell": False,
    }
    if completed.returncode != 0:
        raise FusionContractError(
            f"fusion preflight command failed in {cwd} with "
            f"return code {completed.returncode}"
        )
    return receipt


def _apple_mcp_preflight(
    component: Mapping[str, Any],
    *,
    env: Mapping[str, str],
    platform_name: str,
) -> dict[str, Any]:
    required_platform = str(component.get("platform") or "")
    if platform_name != required_platform:
        raise FusionContractError(
            f"apple_mcp requires {required_platform}; observed {platform_name}"
        )
    file_env = str(component.get("file_env") or "")
    path_value = str(env.get(file_env, "")).strip()
    if not path_value:
        raise FusionContractError(f"apple_mcp requires {file_env}")
    package = Path(path_value).expanduser()
    if not package.is_file():
        raise FusionContractError(f"apple_mcp package not found: {package}")

    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    expected = str(component.get("expected_sha256") or "")
    if digest != expected:
        raise FusionContractError(
            f"apple_mcp sha256 mismatch: expected {expected}, observed {digest}"
        )

    try:
        with zipfile.ZipFile(package) as archive:
            manifest_raw = archive.read("manifest.json")
            names = set(archive.namelist())
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        raise FusionContractError(f"apple_mcp DXT is unreadable: {exc}") from exc

    try:
        manifest = json.loads(manifest_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FusionContractError(f"apple_mcp manifest is invalid: {exc}") from exc
    if not isinstance(manifest, Mapping):
        raise FusionContractError("apple_mcp manifest must be a mapping")
    if manifest.get("name") != "apple-mcp":
        raise FusionContractError("apple_mcp manifest name is not apple-mcp")

    server = manifest.get("server")
    if not isinstance(server, Mapping):
        raise FusionContractError("apple_mcp manifest server contract is missing")
    entry_point = str(server.get("entry_point") or "")
    if server.get("type") != "node" or not entry_point:
        raise FusionContractError("apple_mcp must expose a node server entry point")
    if entry_point not in names:
        raise FusionContractError(
            f"apple_mcp server entry point missing from package: {entry_point}"
        )

    manifest_tools = manifest.get("tools") or []
    if not isinstance(manifest_tools, Sequence) or isinstance(
        manifest_tools, (str, bytes, bytearray)
    ):
        raise FusionContractError("apple_mcp manifest tools must be a collection")
    tool_names = [
        str(item.get("name"))
        for item in manifest_tools
        if isinstance(item, Mapping) and item.get("name")
    ]
    required_tools = [str(item) for item in component.get("required_tools") or []]
    missing_tools = [item for item in required_tools if item not in tool_names]
    if missing_tools:
        raise FusionContractError(
            f"apple_mcp is missing required tools: {missing_tools}"
        )

    compatibility = manifest.get("compatibility") or {}
    manifest_platforms = (
        compatibility.get("platforms", [])
        if isinstance(compatibility, Mapping)
        else []
    )
    if required_platform not in manifest_platforms:
        raise FusionContractError(
            f"apple_mcp manifest does not declare {required_platform} compatibility"
        )

    return {
        "state": "ready",
        "sha256": digest,
        "package": str(package),
        "manifest": {
            "name": manifest.get("name"),
            "version": manifest.get("version"),
            "dxt_version": manifest.get("dxt_version"),
            "server_type": server.get("type"),
            "entry_point": entry_point,
        },
        "tools": tool_names,
        "routed_via": component.get("routed_via"),
    }


def preflight_fusion(
    profile: Mapping[str, Any],
    *,
    live: bool,
    env: Mapping[str, str] | None = None,
    platform: str | None = None,
) -> dict[str, Any]:
    validate_fusion(profile)
    environment = dict(os.environ if env is None else env)
    platform_name = platform or os.sys.platform
    components = profile["components"]
    observed: dict[str, Any] = {}
    deferred: list[str] = []

    for name in EXPECTED_ROLES:
        component = components[name]
        activation = str(component.get("activation") or "")

        if name == "faraway_party":
            observed[name] = {
                "state": "composed_via_mega_pipeline",
                "via": component.get("via"),
                "direct_launch": False,
            }
            continue

        if activation == "opt_in":
            enable_env = str(component.get("enable_env") or "")
            if not _env_enabled(environment, enable_env):
                observed[name] = {
                    "state": "disabled",
                    "enable_env": enable_env,
                }
                continue

        if name == "apple_mcp":
            observed[name] = _apple_mcp_preflight(
                component,
                env=environment,
                platform_name=platform_name,
            )
            continue

        root_env = str(component.get("root_env") or "")
        root_value = str(environment.get(root_env, "")).strip()
        if not root_value:
            observed[name] = {
                "state": "not_configured",
                "root_env": root_env,
            }
            if activation == "required_live":
                deferred.append(name)
            continue

        root = Path(root_value).expanduser()
        command = component.get("preflight") or []
        if not isinstance(command, Sequence) or isinstance(
            command, (str, bytes, bytearray)
        ):
            raise FusionContractError(
                f"{name} preflight must be an argv collection"
            )
        receipt = _run_preflight(
            command,
            cwd=root,
            timeout_seconds=float(component.get("preflight_timeout_seconds", 120)),
        )
        observed[name] = {
            "state": "ready",
            "root": str(root),
            "role": component.get("role"),
            "preflight": receipt,
        }

    if live and deferred:
        raise FusionContractError(
            "required live fusion component(s) not configured: "
            + ", ".join(sorted(deferred))
        )

    return {
        "schema": FUSION_RECEIPT_SCHEMA,
        "fusion_digest": fusion_digest(profile),
        "status": "READY_WITH_DEFERRED_COMPONENTS" if deferred else "READY",
        "live": live,
        "platform": platform_name,
        "deferred_required_live": sorted(deferred),
        "components": observed,
    }


def _sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write_faraway_projection(
    root: str | Path,
    *,
    mission: Mapping[str, Any],
    mission_digest: str,
    launcher_digest: str,
    fusion_receipt: Mapping[str, Any],
    launcher_state: Mapping[str, Any],
) -> dict[str, Any]:
    target = Path(root)
    target.mkdir(parents=True, exist_ok=True)
    mission_id = str(mission.get("id") or mission.get("mission_id") or "unknown")
    objective = str(mission.get("objective") or "")
    completed = [str(item) for item in launcher_state.get("completed") or []]
    failed = [str(item) for item in launcher_state.get("failed") or []]
    blocked = [str(item) for item in launcher_state.get("blocked") or []]
    in_flight = [str(item) for item in launcher_state.get("in_flight") or []]
    waves = launcher_state.get("waves") or []

    contents = {
        "MISSION.md": (
            "# Mission\n\n"
            f"- Mission ID: {mission_id}\n"
            f"- Objective: {objective}\n"
            f"- Mission digest: {mission_digest}\n"
            f"- Launcher digest: {launcher_digest}\n"
            "- Authority: canonical mission + ScaleControlPlane; this projection is additive.\n"
        ),
        "ROADMAP.md": (
            "# Roadmap\n\n"
            + "\n".join(
                f"- Wave {index + 1}: {', '.join(map(str, wave))}"
                for index, wave in enumerate(waves)
            )
            + "\n"
        ),
        "CONTEXT.md": (
            "# Context\n\n"
            f"- Launcher status: {launcher_state.get('status')}\n"
            f"- Fusion status: {fusion_receipt.get('status')}\n"
            f"- Completed: {', '.join(completed) or '(none)'}\n"
            f"- Failed: {', '.join(failed) or '(none)'}\n"
            f"- Blocked: {', '.join(blocked) or '(none)'}\n"
            f"- In flight: {', '.join(in_flight) or '(none)'}\n"
        ),
        "EVIDENCE.md": (
            "# Evidence\n\n"
            f"- Mission digest: {mission_digest}\n"
            f"- Launcher digest: {launcher_digest}\n"
            f"- Fusion digest: {fusion_receipt.get('fusion_digest')}\n"
            "- Completion claims remain subordinate to machine receipts and Workstream E.\n"
        ),
        "HANDOFF.md": (
            "# Handoff\n\n"
            f"- Last launcher status: {launcher_state.get('status')}\n"
            f"- Completed: {', '.join(completed) or '(none)'}\n"
            f"- In flight: {', '.join(in_flight) or '(none)'}\n"
            f"- Blocked: {', '.join(blocked) or '(none)'}\n"
            f"- Failed: {', '.join(failed) or '(none)'}\n"
            "- Resume from the durable launcher checkpoint; do not reconstruct completed work.\n"
        ),
    }

    files: dict[str, Any] = {}
    for name, body in contents.items():
        path = target / name
        path.write_text(body, encoding="utf-8")
        files[name] = {
            "path": str(path),
            "sha256": _sha256_file(path),
        }

    return {
        "schema": "glaciereq.scale-fde.faraway-projection.v1",
        "mission_id": mission_id,
        "files": files,
    }
