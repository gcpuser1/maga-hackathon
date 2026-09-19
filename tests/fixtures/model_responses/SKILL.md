---
name: vite-safe-dev-server
description: Use when the user wants to start the web frontend, run the dev server, start Vite, check that the backend accepts requests, or fix a CORS or port problem. Never start vite by hand.
---

## When to use

- The user asks to start the web frontend, the dev server, or Vite.
- The user asks whether the backend accepts requests from the frontend.

## Run

Run this exact command from the repository root.

```bash
python .claude/skills/vite-safe-dev-server/scripts/start.py
```

## Output

The last line of stdout is one JSON object.

- Ready: `{"status": "ready", "port": 5173, "pid": 4242}`. Tell the user the port.
- Error: `{"status": "error", "reason": "precondition_failed"}`, with one of these reasons.
  Report the reason to the user and stop. Never work around it.
  - `all_permitted_ports_exhausted`: ports 5173 and 5174 are busy. Never pick another port.
  - `cors_origin_rejected`: the backend refused the Origin. Never edit the CORS whitelist.
  - `precondition_failed`: a precondition is absent. Never start the backend yourself.

## Rules

- Never bind a port outside 5173 and 5174.
- Never modify the CORS whitelist in apps/api/src/server.js.
- Never terminate an unrelated process.

## Stop

```bash
python .claude/skills/vite-safe-dev-server/scripts/start.py stop
```
