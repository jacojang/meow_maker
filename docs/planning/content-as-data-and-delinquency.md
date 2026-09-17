---
status: review
updated: 2026-09-17
---

# Content as Data + Delinquency Status (Roadmap Phase 3)

## Goal

Two independent items from `docs/planning/roadmap.md`'s Phase 3:

1. Balancing an existing activity or diet option currently means editing
   a Python dict and shipping a code change. Move those tables into data
   files so tuning numbers doesn't need one.
2. `is_sick` (`stress > health`) is currently the only status effect.
   PM2 has a second one — delinquency (misbehaving beyond a threshold) —
   with its own penalty and its own recovery path. Add the Meow Maker
   equivalent.

## Scope

**In**

- `ACTIVITY_EFFECTS` (`server/app/game/activities.py`) and `DIET_EFFECTS`
  (`server/app/game/diet.py`) load from JSON data files instead of being
  Python dict literals, validated at load time against the `Activity`/
  `Diet` enums and against `STAT_NAMES`.
- A new derived status, `is_delinquent`, mirroring `is_sick`'s exact
  shape (`stat > stat`, not a new stored field), plus one recurring
  penalty while it holds and a natural in-game recovery path.
- `is_delinquent` exposed via `GameRun`/the `/api/game` state, same as
  `is_sick`/`is_overweight`.

**Out**

- Any frontend change. Phase 3 is backend/data only per the roadmap's own
  "Tested by: pytest" line (no Vitest/browser-check line, unlike phases
  that touch `web/`). `is_overweight` already shipped one phase ahead of
  its own frontend badge (part of the diet-weight-consequence phase); the
  same gap here is consistent, not an oversight, and a fast follow if the
  user wants a badge later.
- Making the *set* of activities/diets themselves data-driven (i.e. truly
  "add a sixth activity by editing data only"). A brand-new activity still
  needs a Korean label, a color, a flavor line, and — since the
  action-in-progress animation phase — a piece of scene art in
  `web/src/scenes/GameScene.js`/`web/public/assets/scenes/`, none of which
  can come from a data file alone, and new art means another `tools/asset-gen`
  cost the user must confirm separately. This phase's "data" claim is
  scoped to *balancing the existing five activities and three diets*,
  which is what actually required a code change before and is what the
  roadmap's phrasing ("balancing doesn't need a code change") is about.
- Any change to `effects_for`'s sickness-halving mechanism, or to the
  overweight penalty — both stay exactly as they are; delinquency is a
  new, separate penalty, not a modification of either.

## Mechanics

**Content as data**: two new files, `server/app/game/data/activities.json`
and `server/app/game/data/diets.json`, holding exactly the same shape as
today's Python dicts (`{"<enum value>": {"<stat>": <delta>, ...}}`). A
small loader in each module (`activities.py`/`diet.py`) reads its file
relative to its own directory, validates the top-level keys exactly match
the enum's values and every nested key is a real stat name (raising
`ValueError` on either mismatch), and wraps the result in the same
`MappingProxyType` nesting `ACTIVITY_EFFECTS`/`DIET_EFFECTS` already used
— so every existing call site (`effects_for`, `apply_activity`,
`apply_diet`, and every test that imports these names) is unaffected.
The loader itself is a small pure function (`load_activity_effects(path)`
/ `load_diet_effects(path)`) so the validation logic is directly
unit-testable against a temp file, per AGENTS.md's testable-logic
convention, rather than only being exercised as an unobservable
module-import side effect.

**Delinquency**: `is_delinquent = stress > discipline` on `CatStats`,
identical shape to `is_sick = stress > health` and `is_overweight =
weight > OVERWEIGHT_THRESHOLD`. Discipline is the natural threshold stat
— it's literally the stat that represents behavioral control, and it's
also the stat `TRAIN` builds — so recovery is already a built-in action,
not a new one to invent: playing `TRAIN` raises discipline back above
stress, ending delinquency, mirroring how `REST` already recovers from
sickness by lowering stress back under health.

Penalty, applied once per month while delinquent (same point in
`advance_month()` as the overweight penalty, i.e. after slot resolution
and diet, before the age increment): `discipline -1`. Deliberately small
and deliberately the *same* stat as the threshold, which makes it a mild,
self-reinforcing spiral — a delinquent cat drifts slightly more
delinquent each month it's ignored — without being so harsh that one bad
month is unrecoverable (a single `TRAIN` slot's `+5` easily outpaces a
`-1` drift). This mirrors PM2's actual delinquency risk (it can spiral if
ignored) while keeping the fix trivially in the player's existing
toolkit.

Why not reuse `affection` (already the overweight penalty's stat)?
Keeping each status effect's penalty on a different stat keeps the
player's readout legible — seeing `discipline` drift down time. specifically
signals "the delinquency spiral," not "generic bad month."

## Open questions

None — resolved above.

## Next stage

Straight to Coding — both pieces are backend-only, matching the roadmap's
own scope for this phase (no Design doc, no new screen).

Testing: `server/tests/game/test_activities.py`/`test_diet.py` gain
loader-specific tests (valid file loads correctly, a file missing an enum
value raises, a file with an unknown stat name raises). New
`server/tests/game/test_delinquency.py` (or extending `test_stats.py`/
`test_run.py`, matching how `is_overweight` was tested) covering the
threshold boundary, the monthly penalty, and recovery via `TRAIN`.
