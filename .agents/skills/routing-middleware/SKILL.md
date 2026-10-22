---
name: routing-middleware
description: Request routing and middleware chain management.
---
# Routing Middleware

## Architecture
Manages the middleware chain that processes incoming requests before they reach a handler:
1. Authentication middleware (verify credentials)
2. Rate limiting middleware (prevent abuse)
3. Logging middleware (record request/response)
4. Routing middleware (dispatch to correct handler)
5. Error handling middleware (catch and format errors)

## Integration
Consumed by `apex-command-core` to manage the request pipeline for multi-protocol operations.
