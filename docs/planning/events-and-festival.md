---
status: deployed
updated: 2026-09-18
---

# Events and a Yearly Milestone (Roadmap Phase 4)

## Goal

Two items from `docs/planning/roadmap.md`'s Phase 4: random monthly
events, and one end-of-year milestone (PM2's Harvest Festival, scaled
down). Both are the first things in this project that need randomness —
Phase 0 flagged this explicitly ("inject a `Random` rather than calling
module-level `random`"), so this phase is also where that convention
actually gets used for the first time.

## Scope

**In**

- A small pool of random monthly events (visitor / good mood / bad mood /
  minor mishap / small gift), each a flat stat effect, one optional roll
  per month.
- `GameRun.advance_month()` accepts an optional `rng: random.Random`,
  defaulting to a fresh unseeded instance — production never needs
  reproducibility, tests inject a seeded one.
- One milestone, fixed at a specific month within the run, that rewards
  the cat's current best stat among a subset — a deliberately small
  stand-in for the Harvest Festival's four contests.
- Both surfaced on `GameRun`/the `/api/game` state (`last_event`,
  `last_festival_winner`), following the precedent set by `is_overweight`
  shipping ahead of any frontend display for it.

**Out**

- Any frontend change — backend/data only, per the roadmap's own
  "Tested by: pytest" line for this phase.
- A real Harvest-Festival-equivalent with four distinct contests, entry
  requirements, or unique prize items. PM2's version assumes systems Meow
  Maker doesn't have yet (money, items, multiple reputations) — building
  a faithful version now would mean inventing most of Phase 5/6's content
  early. What ships here is intentionally the simplest version that still
  gives the run *a* distinct, stats-driven yearly beat, named as a
  placeholder for a real festival system later.
- Any change to the sickness/overweight/delinquency mechanics or their
  penalties — events are a new, independent effect source, flat like diet
  (not halved by sickness), applied alongside the existing penalties.

**A note on how this phase was authored**: normally a piece with this
much creative surface (which events exist, what the festival actually
is) is exactly the kind of thing to check with the user before building,
per this project's own conventions. This one shipped without that
checkpoint because the user explicitly asked to keep moving through the
roadmap phases overnight without stopping for confirmation. Scope was
kept deliberately small and every event's effect is a one-line change in
a data file specifically so this is cheap to retune or replace once
reviewed, rather than because the design is expected to be final.

## Mechanics

**RNG injection**: `GameRun.advance_month(self, rng: random.Random |
None = None)`. `rng = rng or random.Random()` at the top — a fresh
instance per call when the caller doesn't care (production), or a
caller-seeded one for reproducible tests. No module-level `random` calls
anywhere in `server/app/game/`.

At the API layer, `server/app/api.py`'s `advance_game` takes `rng:
random.Random = Depends(get_rng)` (new `server/app/rng.py`, mirroring the
existing `GameRepository`/`SessionPlayers` provider pattern exactly) and
passes it through to `advance_month`. This turned out to matter more than
expected: every existing test that calls `advance_month()` (directly, or
through the API) and asserts an exact stat value predates events entirely
and would otherwise become flaky (~40% chance per call of an unplanned
event throwing off the numbers). Fixed by adding `NeverRng` — a
`random.Random` subclass whose `.random()` always returns `1.0` — to
`server/app/rng.py`, used as `conftest.py`'s default `get_rng` override
for every API test and as the default `rng` in `test_run.py`'s
`play_month()` helper, so existing tests stay exactly as deterministic as
before this phase; only the small number of tests that specifically
exercise events/the festival opt into a real roll (a hand-written fake
exposing `.random()`/`.choice()`, or a real seeded `random.Random(seed)`
for the reproducibility bar).

**Events** (`server/app/game/events.py`, effects data-driven in
`server/app/game/data/events.json`, following Phase 3's content-as-data
pattern):

| Event | Effect |
|---|---|
| `visitor` (방문객) | `affection +3` |
| `good_mood` (기분 좋은 날) | `stress -5` |
| `bad_mood` (기분 나쁜 날) | `stress +5` |
| `mishap` (작은 사고) | `stress +5`, `discipline -1` |
| `gift` (작은 선물) | `affection +2`, `weight +1` |

`EVENT_CHANCE = 0.4` — a 40% chance *some* event fires each month; if one
does, it's chosen uniformly from the pool. Two separate rolls
(`rng.random() < EVENT_CHANCE`, then `rng.choice(...)`) rather than one
weighted roll, so "does anything happen" and "which one" are each
independently testable. Applied once per month, right after slot
resolution and before diet/overweight/delinquent — flat, not halved by
sickness (same treatment as diet), and early enough that if an event
pushes weight or stress over a threshold, the same month's
overweight/delinquent checks already see it (matching the existing
diet-then-overweight-same-month behavior).

**Festival** (`server/app/game/festival.py`): `FESTIVAL_MONTH = 10`
(fixed — a run is exactly one year/12 months, so this fires exactly once
per run, with 2 months of runway left afterward, distinct from the
eventual Phase 5 ending). When `self.month == FESTIVAL_MONTH` during
`advance_month()`, the highest of `{affection, discipline, curiosity,
refinement}` gets `+5`; the winning stat's name is recorded. Deliberately
excludes `health`/`weight`/`age`/`stress` (not achievement-flavored
stats) — this mirrors PM2's contests only very loosely (a "best trait"
recognition rather than four separate skill contests), which is the
explicit simplification named above.

**State**: `GameRun` gains `last_event: Event | None` (overwritten every
month, `None` if no event fired that month) and `last_festival_winner:
str | None` (set once at month `FESTIVAL_MONTH`, kept thereafter as a
permanent record of the run). Both serialize in `to_dict()`/`from_dict()`
and appear in `/api/game`'s state alongside `is_sick`/`is_overweight`/
`is_delinquent`.

**Schema evolution note**: `from_dict()` currently raises if any of a
fixed set of keys is missing — appropriate when every field was there
from Phase 0. These two are the first fields added to `GameRun`'s shape
*after* Phase 2 gave saves a real lifetime across restarts, so
`from_dict()` reads them with `.get(...)`/a default instead of requiring
them, so a save written before this phase still loads. Future additions
to `GameRun`'s persisted shape should follow the same `.get()`-with-default
pattern, not the original all-required one.

## Open questions

None for the mechanism (RNG injection, data-driven events, state
plumbing) — resolved above. The specific events and the festival's exact
shape are the part flagged above as a placeholder pending the user's
actual review.

## Next stage

Straight to Coding — backend/data only.

Testing: `server/tests/game/test_events.py` (roll-fires vs. roll-skips
via a hand-written fake rng exposing `.random()`/`.choice()`, plus one
real-`random.Random(seed)` test confirming a fixed seed reproduces the
same `last_event` across two fresh runs from the same start — the
roadmap's explicit bar for this phase). `server/tests/game/test_festival.py`
(winner selection among ties/distinct values, bonus applied, fires
exactly at month 10 and not other months). `server/tests/game/test_run.py`
gains integration coverage threading an injected `rng` through
`advance_month()`. `server/tests/test_api.py` gains a state-shape check
for `last_event`/`last_festival_winner`.
