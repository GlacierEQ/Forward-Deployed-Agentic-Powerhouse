---
name: knowledge-update
description: Continuous knowledge refresh from connected sources.
---
# Knowledge Update

## Refresh Sources
- GitHub repositories (commits, releases, README changes)
- Notion databases and pages
- Legal databases (case law updates, rule amendments)
- Connected MCP servers (capability discovery refresh)

## Protocol
1. Query each source for changes since last refresh timestamp.
2. Ingest new data into the memory substrate.
3. Update pointer indices in Aspen Grove.
4. Record refresh timestamp and delta summary.
