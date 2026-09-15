# Deployment (배포)

Deploying and running the game on AWS EC2.

## What goes here

- The deployment runbook (step-by-step, kept current)
- Environment/instance setup notes (OS, installed dependencies, ports)
- Release notes per deployment

## The instance

- OS: Amazon Linux 2023 (dnf-based)
- SSH: `ssh -i ~/.ssh/jacojang_new_key.pem ec2-user@54.116.51.0`
- Public DNS (may be more stable across restarts than the raw IP):
  `ec2-54-116-51-0.ap-northeast-2.compute.amazonaws.com`
- 913MB RAM, no swap (see below for why that matters)
- Deploy target directory: `/home/ec2-user/meow-maker`
- Security group already allows inbound TCP 22 and 8000 from 0.0.0.0/0

This instance is real and running; it's not a placeholder.

## Why the frontend is built locally, not on the instance

`web/` is never built on the instance:

- Vite requires Node `^20.19.0 || >=22.12.0`, but the instance's dnf-provided
  `nodejs` is only 18.20.8.
- The instance has just 913MB RAM and no swap, which is too tight/risky for
  running `npm install`/`vite build` there anyway.

So Node.js is intentionally never installed on the instance. Instead:

- `web/` is built on the local dev machine (`npm run build` → `web/dist/`),
  and only the built `web/dist/` directory is rsynced over.
- `server/` is plain Python source with no build step, so it's updated on
  the instance itself via `git pull`, and `uv sync` (run on the instance)
  installs the right Python/deps for that instance's own architecture. A
  locally-built venv is never copied over.

## One-time setup

Run once, locally: `deploy/setup-instance.sh`. It SSHes into the instance
and, idempotently:

1. Adds a 1GB swap file (`/swapfile`), persisted via `/etc/fstab`.
2. Installs `uv` for `ec2-user` (`~/.local/bin`, no root/dnf needed).
3. Clones the repo to `/home/ec2-user/meow-maker` if not already present.
4. Installs `deploy/meow-maker.service` to `/etc/systemd/system/`, then
   `daemon-reload` and `systemctl enable meow-maker` (not started yet —
   nothing's built/synced until the first deploy).

## Routine deploys

Run, locally, after the one-time setup has been done: `deploy/deploy.sh`. It:

1. Builds `web/` locally (`npm --prefix web ci && npm run build`).
2. Rsyncs `web/dist/` to `/home/ec2-user/meow-maker/web/dist/` on the
   instance.
3. SSHes in, runs `git pull` in the repo, `uv sync --project server`, and
   `sudo systemctl restart meow-maker`.
4. Curls `http://54.116.51.0:8000/health` and prints the result so it's
   obvious whether the deploy worked.

## Status

`deploy/setup-instance.sh`, `deploy/deploy.sh`, and
`deploy/meow-maker.service` are authored and reflect the real instance, but
have not yet been executed — running them is a separate follow-up step for
a human/orchestrator to trigger explicitly (per `AGENTS.md` Boundaries on
state-changing AWS actions). Update this section with what was actually run
once that happens.

## Next stage

This is the last stage in the loop; the next task typically returns to
[`../planning/`](../planning/README.md) for the next feature.
