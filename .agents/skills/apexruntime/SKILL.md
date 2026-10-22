---
name: apexruntime
description: Runtime management and daemon control for APEX services.
---
# Apexruntime

## Managed Services
Monitors and controls the 12 core services (ports 3000-9000):
- Colossus Gateway/Gatekeeper/KeyMaster (3000, 4000, 4001)
- Supermemory Brain (4002)
- Memory Bridge (8787), Mastermind (8741), Nexus API (8002), Router (8003)
- Device RPC (8990), Smithery Mesh (8999), Connector Gateway (9000), Google MCP (8888)

## Operations
- `status`: Health check all managed ports.
- `restart <service>`: Kill and restart a specific service.
- `daemon`: Run continuous watchdog (30s interval).

## Integration
Consumed by `apex-command-core` via `runtime_optimizer_supreme.py`.
