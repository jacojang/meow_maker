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

## Next stage

Once testing passes, it hands off to [`../deployment/`](../deployment/README.md).
