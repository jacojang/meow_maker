---
status: deployed
updated: 2026-09-15
---

# Initial Release — Empty Skeleton

## Goal

Ship the first deployable version of Meow Maker: a FastAPI server that
serves a Phaser 3 frontend showing an empty/blank screen, with no game
features yet. This exercises the full pipeline (Coding → Review → Testing →
Deployment) end-to-end before any real game content exists, and gives the
project a running baseline to build features on top of.

## Scope

**In**

- `server/`: FastAPI app scaffold, dependencies managed with `uv`, serving
  `web/`'s built static output
- `web/`: Phaser 3 + Vite scaffold, dependencies managed with `npm`, boots a
  single empty Scene (blank canvas, no sprites/UI)
- Local dev instructions (`docs/development/README.md` updated with the
  actual setup/run commands)
- Basic tests: backend smoke test (server starts, root route serves the
  page, a `/health` endpoint returns 200) and a frontend build check
- Deployment: `docs/deployment/README.md` runbook plus a deploy script for
  AWS EC2 (Ubuntu, single process)

**Out**

- Any game mechanics, stats, cat sprite, UI, or sound
- CI/CD automation (GitHub Actions etc.)
- HTTPS/domain/reverse proxy — v1 serves plain HTTP on a single port
- Actually provisioning or running on a real EC2 instance — that's a
  separate follow-up requiring explicit confirmation before any AWS
  state-changing action (per `AGENTS.md` Boundaries)

## Mechanics

No gameplay yet — technical shape only:

- `server/` is a FastAPI app with two routes: `/health` returns
  `{"status": "ok"}`, and `/` (plus static assets) serves `web/dist`, the
  Vite production build, so one process serves both API and frontend.
- `web/` is a Vite + Phaser 3 project with a single `BootScene` that sets a
  background color and renders nothing else.
- `uv` manages `server/pyproject.toml`; `npm` manages `web/package.json`.

## Open questions

None outstanding — resolved before this doc was written: `uv` + `npm`/Vite
as the toolchain, single-process static serving via FastAPI, and this task
stops at deploy scripts/runbook (no real EC2 instance yet).

## Next stage

No design doc needed — there are no visual/UX decisions beyond "blank
screen." Proceeded directly to Coding.

`server/` and `web/` were scaffolded and reviewed (coding-agent/review-agent,
all PASS on first pass — no retries needed). Testing done: `uv run pytest`
(2 passed), `npm run build` succeeds, and a manual smoke run confirmed
`/health` returns `{"status": "ok"}` and `/` serves the built Phaser page.

Deployed successfully on 2026-09-15 to the real instance (Amazon Linux
2023, t3.micro, `54.116.51.0`) with the user's explicit go-ahead:
`deploy/setup-instance.sh` then `deploy/deploy.sh`. Verified with
`systemctl is-active`/`is-enabled` (both healthy) and `curl` against both
`/health` and `/`.

One real-world snag, resolved: port 8000 was already in use by an
unrelated pre-existing process on the instance (`jaco_ai_testbed/leaderboard`,
not managed by systemd/cron). Per the user's explicit choice, that process
was stopped rather than moving `meow-maker` to a different port. See
`docs/deployment/README.md` for the note this leaves for future deploys to
this shared instance.
