---
status: testing
updated: 2026-09-16
---

# Playable Slice (Roadmap Phase 1)

## Goal

Make the game playable. Put the Phase 0 rules behind an HTTP API, store a
run per browser session, and build a screen that shows the cat, takes the
month's three choices, and reports what happened. The "시작" button finally
does something.

## Scope

**In**

- **API** over the existing rules: start a run, read it, advance a month.
- **Session identity**: a cookie identifies the player. Saves hang off a
  `player_id`, never the session token directly — see
  [`roadmap.md`](roadmap.md#designing-for-accounts-later).
- **Repository interface + in-memory implementation.** This phase is its
  first real caller, which is why it arrives now and not in Phase 0.
- **Game screen**: stats, current month, three activity pickers, a result
  for the month just played, and an end-of-run state.
- The opening screen's "시작" button starts a run and opens the game screen.

**Out**

- Persistence across a server restart — Phase 2. Losing a run on restart is
  expected here.
- Accounts or login — the cookie is the whole identity story for now.
- New content: still the four Phase 0 activities.
- Events, contests, endings, scoring — Phases 4–5.
- Visual polish. Functional Phaser text and shapes are fine.

## Mechanics

**Endpoints** (all under `/api`, registered *before* the static mount —
`app.mount("/", StaticFiles(...))` is a catch-all and would otherwise
swallow them):

| Endpoint | Does |
|---|---|
| `POST /api/game` | Start a run for this session, replacing any existing one |
| `GET /api/game` | The current run, or 404 if there isn't one |
| `POST /api/game/advance` | Take the month's three activities, resolve the month, return the new state |
| `GET /api/activities` | The activity table, so the UI doesn't hardcode it |

Assigning slots and advancing are one call, not two. The player picks three
activities and commits; a half-assigned month has no meaning to them, and
combining avoids a server state that the UI has to keep in sync. The domain
keeps `assign_month()` and `advance_month()` separate regardless — the
endpoint just composes them.

`GET /api/activities` exists so the UI renders from the server's table.
Phase 3 moves that table into a data file, and the UI picks the change up
for free.

**Session**: an `httponly` cookie holds an opaque token, set on first
contact. One resolver function turns a request into a `player_id`; whether
it does that from a cookie or, later, a login token stays its business. No
`secure` flag — the deployment is plain HTTP.

**Screen**: stats with their numbers, the month (e.g. `3 / 12`), a sick
indicator when stress exceeds health, three pickers over the four
activities, and a button to play the month. After advancing, show what
changed. At month 12 the run ends and the screen says so.

## Open questions

None. The decisions this rests on are settled in
[`roadmap.md`](roadmap.md), and the rules themselves are already built and
tested from [`core-domain-model.md`](core-domain-model.md).

## Next stage

No Design pass — this is functional UI, not an art pass; the visual
treatment can come later once there's something to look at.

Testing: `pytest` with `TestClient` for the API (including session
isolation and rejected input), Vitest for the API client's pure logic, and
a real browser pass playing a full run.

Built via the coding-agent/review-agent loop. The first review returned
FAIL: the session cookie was set on the injected `Response`, which FastAPI
discards when an endpoint raises `HTTPException` — so a cookie-less
`GET /api/game` returned 404 with no cookie while still minting an
unreachable `player_id`, growing the session map on every unauthenticated
request. Fixed by moving cookie issuance into middleware that runs after
the response is built; re-review passed.

A browser pass also caught two copy bugs: the end-of-run heading read like
the cat had died, and "아직 보낸 달이 없습니다" showed after months that
simply produced no stat change.

