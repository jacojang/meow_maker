---
status: review
updated: 2026-09-18
---

# Outings (Roadmap Phase 6, minimal slice)

## Goal

Roadmap Phase 6 names PM2's errantry/combat system as the target and
calls it, in its own words, "biggest scope, least essential." PM2's real
version needs a map, turn-based combat, an economy, and items — none of
which Meow Maker has. Confirmed with the user before building: this ships
the smallest version that still gives the schedule a 6th option with a
real risk/reward decision, not a scaled attempt at the real thing.

## Scope

**In**

- A 6th `Activity`, `OUTING` (나들이), added to the existing activity
  system exactly like the other five — same enum, same data-file entry,
  same halving-when-sick treatment, same frontend label/color/flavor
  maps. This is deliberate: every existing piece of UI (calendar picker,
  activity-info popup, resolution animation) already loops generically
  over the activity list, so treating outing as "just a 6th activity"
  means none of those need to change at all.
- Layered on top of its base effect (applied to every slot the same way,
  regardless of activity): a separate success/fail roll, using the same
  RNG-injection pattern Phase 4 established. Success adds a bonus;
  failure adds a further penalty. Recorded on `GameRun` as
  `last_outing_result` for transparency (same `.get()`-optional
  serialization pattern as `last_event`/`last_festival_winner`/`ending`).

**Out**

- A map, movement, or turn-based combat of any kind.
- Money, items, or an inventory — Meow Maker has none of these, and
  adding them for one activity would be a much bigger phase than this.
- New art. The resolution-animation vignette already falls back to
  showing nothing but text when a texture is missing
  (`this.textures.exists(step.textureKey)` in `GameScene.js`), so outing
  works correctly with zero new assets. A dedicated `scene-outing.jpg`
  (matching the other five) is optional polish for later, and — like
  every other asset in this project — needs the user's cost confirmation
  before `tools/asset-gen` runs, so it's not included here.
- Any change to the existing five activities' mechanics.

## Mechanics

**Base effect** (`server/app/game/data/activities.json`, a normal 6th
entry, loaded the same way as the other five): `{"curiosity": 3, "stress":
10}`. Applied via the existing `apply_activity`/`effects_for` path,
including sickness-halving — outing is just another activity as far as
that code is concerned.

**Success/fail layer** (`server/app/game/outing.py`, new): a 70% chance
of success. Success adds `{"curiosity": 5, "discipline": 5}`; failure
adds `{"stress": 5}`. Combined with the base effect, a successful outing
nets `curiosity +8, discipline +5, stress +10`; a failed one nets
`curiosity +3, stress +15`. This layer is flat, not halved by sickness —
same treatment as diet/events/festival (an outcome roll, not a routine
activity's baseline exertion). Resolved once per `OUTING` slot in
`GameRun.advance_month()`'s existing slot-resolution loop, using the same
`rng` already threaded through for events — right after the slot's normal
`apply_activity` call, so a month with multiple `OUTING` slots rolls
independently each time (only the last result is kept in
`last_outing_result`, matching how `last_event` already only keeps the
month's single most-recent occurrence).

**What doesn't need to change**: `server/app/api.py` (the existing
`/api/activities` endpoint already lists every `ACTIVITY_EFFECTS` entry
generically), `web/src/scenes/GameScene.js`'s calendar/picker/popup
rendering (all already loop over `this.activities`), and
`web/src/utils/resolutionSteps.js` (already builds one step per slot from
the same generic activity list). The only frontend edits are three map
entries — `ACTIVITY_LABELS`, `ACTIVITY_COLORS`, `ACTIVITY_FLAVOR` — adding
`outing` alongside the existing five, exactly the same shape as any of
them.

The resolution animation shows the *base* effect during playback (same
simplification already accepted for sickness-halving on the other five —
the animation was never showing exact real-time-computed deltas, just the
nominal table entry); the real outcome, bonus or penalty included, is
what actually lands in the stats and appears in the post-reveal "지난 달
변화" summary. The surprise is intentional and costs nothing extra to get
right, since it falls out of the existing reveal-after-animation design.

## Open questions

None for the mechanism. Whether to eventually generate dedicated outing
scene art is a separate, explicitly-deferred cost decision for the user.

## Next stage

Straight to Coding. Backend: `outing.py`, `activities.json`'s new entry,
`GameRun` wiring, `__init__.py` exports. Frontend: three map entries in
`GameScene.js`. Testing: `server/tests/game/test_outing.py`
(fake-rng-based success/failure, base+bonus/penalty math), `test_run.py`
integration (an `OUTING` slot in `advance_month()` produces the right
combined stats and sets `last_outing_result`), `test_api.py` (state
includes the new field; `/api/activities` lists `outing`). Frontend:
`npm run build` + a manual browser check that the calendar/picker/popup
render correctly with 6 activities instead of 5 (button widths are
already parametric, but confirm no visual regression).
