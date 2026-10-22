---
name: arcade-mcp
description: "Arcade Engine MCP tools: search, parameter inspection, and cloud tool execution across 1000+ API integrations."
---

# Arcade MCP Integration

Arcade provides access to 1000+ cloud tools (Apollo, Airtable, Asana, Box, Clickup, Confluence, Slack, GitHub, Brightdata, etc.) via the Model Context Protocol.

## Available MCP Tools

1. `arcade_search_tools`: Discover tools across Arcade by keyword or toolkit.
2. `arcade_get_tool_info`: Inspect parameters, required types, and input schema for any tool.
3. `arcade_authorize_tool`: Generate an OAuth authorization link for tools requiring user credentials.
4. `arcade_execute_tool`: Execute any tool with inputs and user ID.

## Quick CLI Usage

```bash
# Direct test execution via python
python3 -c "
from bin.arcade_mcp_server import handle_search_tools
print(handle_search_tools({'query': 'Apollo'}))
"
```
