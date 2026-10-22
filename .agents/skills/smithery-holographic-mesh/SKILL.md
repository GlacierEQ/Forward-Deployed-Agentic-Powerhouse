---
name: smithery-holographic-mesh
description: Hardened Smithery operating plane and holographic mesh proxy connecting 32+ remote MCP servers (GitHub, Google Suite, Notion, Dropbox, Exa, Tavily, Jina) to local AI models.
---

# Smithery Holographic Mesh Skill (Merged into APEX Sovereign Supreme)

This skill provides a unified operating plane, tool truck manifest, and local HTTP proxy bridge for the **Smithery GlacierEQ MCP Server** (`https://mcp.smithery.run/GlacierEQ?mode=smart`).

> [!NOTE]
> This skill has been enhanced and merged into the master **`apex-sovereign-supreme`** skill suite.

## Features & Capabilities

1. **32+ Active Connected Servers**:
   - **Developer**: GitHub, Hugging Face, Microsoft Learn.
   - **Cloud Storage**: Google Drive, Dropbox, OneDrive.
   - **Productivity**: Google Docs, Sheets, Photos, Gmail, Notion, Outlook, Trello.
   - **AI Search**: Exa Search, Tavily, Jina AI, DeepWiki, Parallel Web Search.
   - **Legal & Knowledge**: Case Law Search, Lex Oracle, Omega Memory, LiveDataLink.

2. **Unified Gateway & Proxy Endpoints**:
   - Supreme Connector Gateway: `http://127.0.0.1:9000`
   - Local Smithery JSON-RPC Proxy: `http://127.0.0.1:8999`
   - Sandboxed Execution Engine: `execute` (`connections.<server>.<tool>`)
   - Tool Search Engine: `search_toolbox`

3. **CLI Commands & Utilities**:
   ```bash
   # Unified Connector Gateway status check
   python3 /root/.agents/skills/apex-sovereign-supreme/scripts/connector_hub_supreme.py status

   # Search 32+ MCP Toolbox
   python3 /root/.agents/skills/apex-sovereign-supreme/scripts/connector_hub_supreme.py search -q "github"
   ```
