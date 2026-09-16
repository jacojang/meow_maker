# Testing (테스트)

Verifies a change before deployment.

## What goes here

- Test strategy (backend: `pytest`; frontend: `Vitest`)
- Test plans for larger features
- Manual QA checklists for things automated tests can't cover well (game
  feel, animation timing, visual correctness)

## Status

- Backend: `cd server && uv run pytest`.
- Frontend: `cd web && npm test` (Vitest). Only plain JS logic extracted
  into `web/src/utils/` is unit tested this way (e.g. `coverScale.js`) —
  Phaser scenes themselves need a browser/canvas, so those are checked with
  `npm run build` plus a manual browser pass, not an automated suite.

## CI

`.github/workflows/ci.yml` runs both suites automatically on every PR
targeting `main` (and on push to `main`): `web/`'s `npm test` + `npm run
build` first, then `server/`'s `pytest` against the built `web/dist`
(passed between jobs as an artifact) — `server/`'s app fails to even import
without `web/dist` present, so backend tests always run after a real
frontend build, matching the actual deploy order.

Both jobs are required status checks on `main` (branch protection, admins
included) — a failing PR genuinely cannot be merged, not just flagged.

## Next stage

Once testing passes, it hands off to [`../deployment/`](../deployment/README.md).
