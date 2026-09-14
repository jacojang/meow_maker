# Coding (코딩)

Implementation: backend (`server/`, FastAPI) and frontend (`web/`, Phaser 3).

## What goes here

- Architecture decisions and why they were made
- Setup and local run instructions for `server/` and `web/`
- Coding conventions specific to this project (beyond `AGENTS.md`)

## Setup and running locally

### `server/` (FastAPI, managed with `uv`)

```
cd server
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

The server serves `/health` (returns `{"status": "ok"}`) and mounts
`web/dist` (the Vite production build) at `/`. It will fail to start (or
serve nothing) unless `web/dist` exists — see below.

### `web/` (Phaser 3 + Vite, managed with `npm`)

```
cd web
npm install
npm run dev     # local dev server with hot reload, not served by server/
npm run build   # produces web/dist, which server/ serves as static files
```

For day-to-day frontend work, use `npm run dev`. For `server/` to serve the
real frontend (e.g. to check the full integrated app), run `npm run build`
first so `web/dist` exists, then start/restart the server.

## Next stage

Once a change is implemented, it hands off to [`../review/`](../review/README.md).
