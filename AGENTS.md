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
├── server/          # FastAPI backend (not yet scaffolded)
└── web/             # Phaser 3 frontend (not yet scaffolded)
```

`server/` and `web/` don't exist yet. They get scaffolded during the Coding
stage; see `docs/development/README.md` when that work starts.

## Development workflow

Work repeats through a fixed loop:

**Planning → Design → Coding → Review → Testing → Deployment**

Each stage has a matching folder under `docs/` that holds its artifacts and
process notes. Start any task by identifying which stage it belongs to and
reading that folder first. See `docs/README.md` for the full index.

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

- New features require a matching test once `server/`/`web/` have test
  tooling in place (backend: `pytest`; frontend: TBD, see
  `docs/testing/README.md`).
- Test code is never modified just to make it pass — fix the source instead
  (see Conventions above).

## Boundaries

- Never modify `.env*` files or commit secrets/credentials — ask the user
  instead.
- Never run destructive or state-changing AWS/EC2 commands (deploy, restart,
  terminate, security group/config changes) without confirming with the user
  first.
- More specific off-limits paths (generated code, migrations, etc.) get
  added here once `server/` and `web/` exist and those concepts apply.

## Commands

Not yet defined — `server/` and `web/` don't exist yet. This section gets
filled in as each is scaffolded (see `docs/development/README.md`).

## Reference docs (read only when relevant)

- Workflow stage docs — read only the folder matching the current task:
  `docs/planning/`, `docs/design/`, `docs/development/`, `docs/review/`,
  `docs/testing/`, `docs/deployment/`
- Dynamic coding↔review subagent loop protocol — only relevant when running
  the `coding-agent`/`review-agent` loop: `docs/development/dynamic-workflow.md`
