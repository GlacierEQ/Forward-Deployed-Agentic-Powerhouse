"""Unit tests for Smithery & holographic MCP mesh bridge."""

from pathlib import Path

from fde_powerhouse.bridges.mcp_mesh import MCPMeshBridge


def test_mcp_mesh_discover_servers():
    bridge = MCPMeshBridge()
    servers = bridge.discover_servers()
    assert "mem0-gateway" in servers
    assert "supermemory" in servers
    assert "notion" in servers
    assert "github" in servers
    assert servers["mem0-gateway"]["tool_count"] >= 3


def test_mcp_mesh_resolve_tool():
    bridge = MCPMeshBridge()
    res1 = bridge.resolve_tool("mem0__search_memories")
    assert res1 is not None
    assert res1["server"] == "mem0-gateway"

    res2 = bridge.resolve_tool("search_memory")
    assert res2 is not None
    assert res2["server"] == "supermemory"

    assert bridge.resolve_tool("nonexistent_tool_12345") is None


def test_mcp_mesh_format_tool_definition():
    bridge = MCPMeshBridge()
    tool_def = bridge.format_tool_definition(
        server="supermemory",
        tool_name="list_memories",
        schema={"type": "object", "properties": {"limit": {"type": "integer"}}},
    )
    assert tool_def["name"] == "supermemory__list_memories"
    assert "inputSchema" in tool_def


def test_mcp_mesh_probe():
    bridge = MCPMeshBridge()
    probe = bridge.probe()
    assert probe["available"] is True
    assert probe["mesh_topology"] == "holographic"
    assert probe["server_count"] >= 8
    assert probe["tool_count"] >= 20
    assert "supermemory" in probe["servers"]


def test_mcp_mesh_custom_config(tmp_path: Path):
    custom_cfg = tmp_path / "custom_mcp.json"
    custom_cfg.write_text(
        '{"mcpServers": {"custom-relay": {"transport": "stdio", "tools": ["echo", "ping"]}}}',
        encoding="utf-8",
    )
    bridge = MCPMeshBridge(config_paths=[custom_cfg])
    discovered = bridge.discover_servers()
    assert "custom-relay" in discovered
    assert discovered["custom-relay"]["status"] == "custom_configured"
