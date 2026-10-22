---
name: memory-connect
description: Memory bridge component connecting local and remote memory layers.
---
# Memory Connect

## Architecture
Acts as the transport layer between:
- Local file-based memory (Aspen Grove pointers, `.horizon` checkpoints)
- Remote vector databases (Pinecone, Qdrant)
- Semantic memory services (Mem0, Supermemory)

## Protocol
- Reads are fanned out to all configured layers.
- Writes are routed to the appropriate persistence tier.
- Results are deduplicated and ranked by relevance score.
