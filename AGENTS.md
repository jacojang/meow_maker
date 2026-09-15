# AGENTS.md

Guidance for AI agents and contributors working in this repository.

## Project

Meow Maker is a Princess-Maker-style 2D cat-raising simulation web game.
Players raise a cat over time through stat-driven interactions, with a
2D sprite-animated character reacting to their choices.

## Tech stack

- **Backend**: Python, [FastAPI](https://fastapi.tiangolo.com/), tests with `pytest`
- **Frontend**: JavaScript, [Phaser 3](https://phaser.io/) for 2D rendering/animation
- **Repository hosting**: GitHub
- **Deployment target**: AWS EC2, deployed and run directly (no managed PaaS)

These choices are fixed; do not introduce alternative frameworks without
confirming first.

## Repository layout

```
meow_maker/
├── AGENTS.md
├── README.md
├── docs/            # workflow docs, one folder per stage — see docs/README.md
├── deploy/          # deploy script + systemd unit (see docs/deployment/)
├── server/          # FastAPI backend, uv-managed
│   ├── app/         # app.main:app — /health + static-serves web/dist at /
│   └── tests/       # pytest
└── web/             # Phaser 3 + Vite frontend, npm-managed
    └── src/
        ├── main.js         # Phaser.Game setup
        └── scenes/         # BootScene, etc.
```

`server/` serves `web/dist`, so `web/` must be built (`npm run build`)
before `server/` has a real frontend to serve — see Commands below.

## Development workflow

Work repeats through a fixed loop:

**Planning → Design → Coding → Review → Testing → Deployment**

Each stage has a matching folder under `docs/` that holds its artifacts and
process notes. Start any task by identifying which stage it belongs to and
reading that folder first. See `docs/README.md` for the full index.

**Starting a new feature or change?** See
`docs/planning/README.md#requesting-a-task` for the request format (full
vs. lightweight path) and how per-feature status gets tracked in
`docs/planning/<slug>.md`.

## Conventions

- Don't guess. If a requirement, design detail, or technical choice is
  unclear, ask and get confirmation before writing code.
- Keep changes scoped to what was asked. Don't refactor or touch unrelated
  code while completing a task.
- Test code is not modified to make a task easier, and never modified just
  to make a failing test pass. Fix the source instead.
- Keep comments minimal — prefer code that reads clearly on its own. Only
  comment on non-obvious *why*, never on *what*.
- Design with tests in mind: classes and modules should be structured so
  they're straightforward to test in isolation.

## Testing

- Backend: `cd server && uv run pytest`. New backend features require a
  matching test in `server/tests/`.
- Frontend: no test framework yet (see `docs/testing/README.md`) — `npm run
  build` succeeding is the current bar for frontend changes.
- Test code is never modified just to make it pass — fix the source instead
  (see Conventions above).

## Boundaries

- Never modify `.env*` files or commit secrets/credentials — ask the user
  instead.
- Never run destructive or state-changing AWS/EC2 commands (deploy, restart,
  terminate, security group/config changes) without confirming with the user
  first.
- Don't hand-edit generated/build output (`web/dist/`, `server/.venv/`,
  `web/node_modules/`) — regenerate it via the Commands below instead.
- No database exists yet, so no migration boundary applies — add one here
  when a DB is introduced.

## Commands

- `web/`: `cd web && npm install` (install), `npm run dev` (local dev
  server, hot reload), `npm run build` (produces `web/dist`, served by
  `server/`)
- `server/`: `cd server && uv sync` (install), `uv run uvicorn app.main:app
  --reload --port 8000` (run)

To see the real integrated app (not just the Vite dev server), build `web/`
before starting `server/` — `server/` reads `web/dist` at request time, not
at startup, so rebuilding and hitting reload is enough during dev. Verify
it's up with `curl http://localhost:8000/health` → `{"status":"ok"}`.

See `docs/development/README.md` for details.

## Reference docs (read only when relevant)

- Workflow stage docs — read only the folder matching the current task:
  `docs/planning/`, `docs/design/`, `docs/development/`, `docs/review/`,
  `docs/testing/`, `docs/deployment/`
- Princess Maker 2 reference (the game Meow Maker is modeled on) — read its
  index before any Planning or Design work on a game feature, then only the
  relevant topic files: `docs/planning/references/princess-maker-2/README.md`
- Dynamic coding↔review subagent loop protocol — only relevant when running
  the `coding-agent`/`review-agent` loop: `docs/development/dynamic-workflow.md`
