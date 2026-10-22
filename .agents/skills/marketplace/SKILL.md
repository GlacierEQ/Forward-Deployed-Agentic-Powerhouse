---
name: marketplace
description: Skill marketplace and capability discovery across the APEX estate.
---
# Marketplace & Capability Discovery

**Role:** The engine powering the `cartographer` persona.

## Discovery Protocol (Upgraded for Diamond Topography)
The marketplace is no longer limited to `.agents/skills/`. It aggressively scans the entire APEX estate for `apex.capabilities.yaml` manifests.

1. **Manifest Ingestion**: Scans `/root/` for `apex.capabilities.yaml`.
2. **Persona Binding**: Extracts the `owner_intent.role` and `owner_intent.topography` fields to bind the repository to a specific Diamond node.
3. **Graph Construction**: Builds the `capability_graph` mapping which repo handles which domain.

## Active Discovered Endpoints
- `computer-user` bound to `connector` (Diamond Node)
- `repo_excellence` bound to `verify` (Spiral Engine Center)
- `legal_mesh_worm` bound to `forensics` (Diamond Node)

## When to Use
Invoked automatically by the `cartographer` during the bootup sequence to map the grid.
