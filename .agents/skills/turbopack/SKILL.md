---
name: turbopack
description: Optimized builds with Turbopack for Next.js projects.
---
# Turbopack

## When to Use
- Development builds: `next dev --turbopack` for instant HMR.
- Production builds: `next build` with Turbopack-optimized bundling.

## Benefits
- 10x faster cold starts vs Webpack.
- Incremental computation — only rebuilds changed modules.
- Native TypeScript/JSX support without separate transpilation.
