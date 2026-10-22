---
name: workflow
description: Standard workflow orchestration fallback for non-swarm execution.
---
# Workflow

## Purpose
Provides a simple sequential workflow engine for tasks that don't need full swarm orchestration:
1. Parse the task into ordered steps.
2. Execute each step serially.
3. Verify each step's output before proceeding.
4. Report final status.

## When to Use
- Simple, linear tasks with no parallelizable components.
- Recovery mode when swarm orchestration encounters issues.
- Dry-run mode for previewing execution plans.
