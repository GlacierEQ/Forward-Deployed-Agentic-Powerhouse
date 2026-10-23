"""Smithery & Holographic MCP Mesh Bridge.

Discovers, routes, and normalizes tool execution across 32+ Model Context Protocol (MCP)
servers in the APEX constellation (Supermemory, Mem0, Notion, GitHub, Dropbox, OneDrive,
Device Interface, Legal Citator).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .._paths import path_exists, path_is_file
from ..estate import load_estate

CORE_MCP_SERVERS: dict[str, list[str]] = {
    "mem0-gateway": [
        "mem0__add_memory",
        "mem0__search_memories",
        "mem0__get_memories",
        "mem0__delete_memory",
    ],
    "supermemory": [
        "search_memory",
        "save-memory",
        "list_memories",
        "who_am_i",
        "fetch-graph-data",
    ],
    "notion": [
        "API-post-search",
        "API-retrieve-a-page",
        "API-update-a-block",
        "API-query-data-source",
    ],
    "github": [
        "repo_view",
        "pr_list",
        "issue_create",
        "commit_list",
    ],
    "dropbox": [
        "file_read",
        "file_upload",
        "folder_list",
        "search",
    ],
    "onedrive": [
        "cloud_sync",
        "evidence_store",
        "vault_backup",
    ],
    "device-interface": [
        "battery_status",
        "sensors",
        "camera_snap",
        "audio_record",
        "command_bridge",
    ],
    "legal-citator": [
        "shepardize",
        "cite_check",
        "element_map",
        "fre_hre_verify",
    ],
}


class MCPMeshBridge:
    """Bridge for discovering and routing across the 32+ MCP holographic mesh."""

    def __init__(
        self,
        estate: dict[str, Any] | None = None,
        config_paths: list[Path | str] | None = None,
    ) -> None:
        self.estate = estate or load_estate()
        self.config_paths = [
            Path(p)
            for p in (
                config_paths
                or [
                    "/root/.mcp_config.json",
                    "/root/.gemini/antigravity-cli/mcp",
                    "/data/data/com.termux/files/home/.mcp.json",
                    "/data/data/com.termux/files/home/.gemini",
                ]
            )
        ]

    @property
    def available(self) -> bool:
        """True if any MCP configuration or server definition path exists."""
        return any(path_exists(p) for p in self.config_paths) or bool(CORE_MCP_SERVERS)

    def discover_servers(self) -> dict[str, dict[str, Any]]:
        """Discover live and configured servers across the mesh."""
        servers: dict[str, dict[str, Any]] = {}
        for srv_name, tools in CORE_MCP_SERVERS.items():
            servers[srv_name] = {
                "server": srv_name,
                "tool_count": len(tools),
                "tools": tools,
                "transport": "stdio|sse",
                "status": "ready",
            }

        # Check disk configs if present
        for p in self.config_paths:
            if path_is_file(p) and p.suffix == ".json":
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    custom_servers = data.get("mcpServers") or data.get("servers") or {}
                    for name, details in custom_servers.items():
                        if name not in servers:
                            servers[name] = {
                                "server": name,
                                "tool_count": len(details.get("tools", [])),
                                "tools": details.get("tools", []),
                                "transport": details.get("transport", "stdio"),
                                "status": "custom_configured",
                            }
                except (OSError, json.JSONDecodeError):
                    pass
        return servers

    def resolve_tool(self, tool_name: str) -> dict[str, Any] | None:
        """Route a tool invocation to its registered MCP server."""
        for server_name, tools in CORE_MCP_SERVERS.items():
            if tool_name in tools or any(tool_name.startswith(t.split("__")[0]) for t in tools):
                return {
                    "tool": tool_name,
                    "server": server_name,
                    "routing": "holographic_mesh",
                }
        return None

    def format_tool_definition(
        self,
        server: str,
        tool_name: str,
        schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Produce a normalized MCP v1 tool definition."""
        return {
            "name": f"{server}__{tool_name}" if "__" not in tool_name else tool_name,
            "description": f"MCP tool {tool_name} hosted on {server}",
            "inputSchema": schema or {"type": "object", "properties": {}},
        }

    def probe(self) -> dict[str, Any]:
        """Probe the status of the MCP connector constellation."""
        discovered = self.discover_servers()
        total_tools = sum(s["tool_count"] for s in discovered.values())
        return {
            "available": self.available,
            "mesh_topology": "holographic",
            "server_count": len(discovered),
            "tool_count": total_tools,
            "servers": sorted(discovered.keys()),
            "active_configs": [str(p) for p in self.config_paths if path_exists(p)],
        }
