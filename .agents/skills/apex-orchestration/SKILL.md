---
name: apex-orchestration
description: Spiral Engine cyclical routing and Diamond Agent Topography for decentralized swarm intelligence.
---
# APEX Orchestration (Spiral Engine & Diamond Topography)

**Role:** Dynamic task decomposition, cyclical refinement, and decentralized swarm delegation.

## 1. The Spiral Engine (Cyclical Graph Routing)
We do not use strict, linear DAGs. The APEX swarm operates as a **Spiral Engine**.
- **Iterative Refinement**: Tasks enter a cyclical routing loop. A verifier subagent explicitly routes a failed task back to the implementer for correction.
- **Autonomous Looping**: The loop continues tightening its parameters and reasoning until the condition is met (the center of the spiral) before returning to the lead Architect.

## 2. Diamond Agent Topography (Decentralized Negotiation)
We do not use Hub-and-Spoke. The APEX swarm operates on a **Diamond Topography**.
- **Inter-Agent Communication**: Subagents are equipped and expected to query each other directly using the `send_message` capability. 
- **Bypassing the Hub**: An Implementer can natively message a Cartographer for missing interface definitions, or an Adversarial Counsel can message the Evidence Authenticator directly. The central Architect is bypassed for lateral information retrieval, massively saving token overhead and reducing bottlenecking.

## Execution Flow (Deep Swarm Mode)
1. **Architect Phase**: The lead agent parses the mission and spawns the Diamond grid using `invoke_subagent`.
2. **Execution & Negotiation Phase**: Subagents execute in parallel, communicating laterally to resolve dependencies.
3. **Spiral Verification Phase**: Outputs enter the verification spiral. Rejections are routed directly back to the originators.
4. **Synthesis Phase**: Only pure, verified output reaches the center of the diamond for final synthesis.
