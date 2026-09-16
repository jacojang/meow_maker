# Roadmap — the game itself

How to get from "opening screen only" to a playable cat-raising game,
modeled on [Princess Maker 2](references/princess-maker-2/README.md).

This is the map, not a feature spec. Each phase gets its own
`docs/planning/<slug>.md` when it's actually started.

## Fixed decisions

- **Game rules live on the server** (Python/FastAPI). Phaser handles
  rendering and input only. Rules stay testable with `pytest`, no browser
  needed, and sit next to the DB.
- **One run = 12 in-game months** (36 slots) for v1. Length is a constant,
  so extending it later is a one-line change, not a redesign.
- **Saves are identified by a session cookie** for now, with accounts added
  later — see [Designing for accounts](#designing-for-accounts-later).
- **SQLite**, introduced in Phase 2 — after the data model settles.

## Phase 0 — Domain model

Pure Python. No HTTP, no DB, no Phaser.

- Cat stats, calendar (month + 3 slots), a few activities, stress.
- Applying an activity produces stat deltas; advancing a month resolves them.
- Stress crossing a threshold sets a "sick" state.
- **Seed the RNG from the start** so tests are deterministic later.
- Keep saving behind a repository interface (in-memory implementation for
  now) so Phase 2 swaps the implementation, not the callers.

**Tested by**: `pytest` only. Every rule.
**Done when**: a test can simulate a full 12-month run end to end.

## Phase 1 — Vertical slice

The first actually-playable version.

- API: new game / read state / assign the month's slots / advance a month.
- Web: stats display, activity picker, month result. The "시작" button
  finally does something.
- Still in-memory — a server restart loses the run. That's fine here.

**Tested by**: `pytest` with `TestClient` for the API, Vitest for any pure
client helpers, plus a browser pass.
**Done when**: you can play 12 months in the browser and reach an end state.

## Phase 2 — SQLite

Now that the model is stable, give it a schema.

- Swap the repository's in-memory implementation for SQLite.
- Session cookie resolves to a `player` row; the run hangs off `player_id`.
- Sketch: `player(id, session_id, created_at)` and
  `game(id, player_id, month, slot_states, stats…, status)`. Stats can start
  as columns and split out only if they need history.

**Tested by**: `pytest` against a temp DB file — save, reopen, restore.
**Done when**: a reload or server restart keeps your run.

## Phase 3 — Content as data + status effects

- Move activity/stat tables out of code into a data file, so balancing
  doesn't need a code change.
- Status effects beyond sick (PM2's delinquency equivalent), and the
  actions that recover from them.

**Tested by**: `pytest` — data file loads and validates, each effect's
trigger and recovery.
**Done when**: adding an activity means editing data only.

## Phase 4 — Events and a yearly milestone

- Random monthly events (visitors, mood swings, small incidents).
- One end-of-year milestone — PM2's Harvest Festival contests, scaled down.

**Tested by**: `pytest` with a fixed seed, so event rolls are reproducible.

## Phase 5 — Endings and score

- Final stats decide which ending the cat gets, plus a score.

**Tested by**: table-driven `pytest` — given stats, expect an ending.
**Done when**: a full run ends with a real result screen.

## Phase 6 — Optional: outings

PM2's errantry/combat equivalent. Biggest scope, least essential. Only
after Phases 0–5 feel good.

## Designing for accounts later

Session-only now, real accounts eventually. Two rules keep that migration
cheap:

1. **Saves reference `player_id`, never `session_id`.** The session is just
   one way to look up a player row.
2. **One seam in code**: a single `get_current_player()` resolves a request
   to a `player_id`. Cookie today, login token later — only that function
   changes.

Adding accounts then means: nullable `email`/`password_hash` columns on
`player`, a login endpoint, and letting an existing session-only player
claim their row by registering.

Accepted tradeoff until then: clearing cookies loses the save, with no
recovery path.
