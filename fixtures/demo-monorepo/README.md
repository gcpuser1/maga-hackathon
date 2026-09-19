# demo-monorepo

A constructed demonstration fixture (`ARCHITECTURE.md` 8.1), not a real product.
MAGA generates automation for this repository, and Gate 2 gives a fresh copy of it to the target agent.

- `packages/config/ports.json`: the permitted frontend ports, `[5173, 5174]`.
- `apps/api/src/server.js`: a backend with no dependencies. Its CORS allow-list holds the two permitted origins only, so port 5175 gets `403`.
- `apps/web`: a Vite frontend. `pnpm install` is needed only to run the real Vite by hand.

Gate 1 and Gate 2 put a `vite` stand-in on `PATH` and run a backend stub, so they need no `pnpm install` and no network.
