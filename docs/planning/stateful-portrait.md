---
status: deployed
updated: 2026-09-17
---

# Stateful Cat Portrait (UI/UX overhaul, part 2 of 4)

## Goal

A central cat portrait, visible on the game screen, that visually reflects
the cat's current age, health condition, and weight — per
`docs/planning/ui-ux-overhaul.md` and the PM2 reference GIFs. Requires two
new real mechanics (age, weight/diet) before the art can respond to them.

Split into two PRs: **2a** (server mechanics — age, weight, diet) and **2b**
(art generation + the portrait itself + a diet picker in the UI).

## Scope — 2a (server)

**In**

- **`age`**: a new stat, same 0–100 clamp as the others. Increases by **+1
  automatically every month**, independent of activities or player choice
  — age is just the passage of time, not something earned. Starts at 1.
- **`weight`**: a new stat, same clamp, starts at **50** (mid-range,
  matching `health`'s default).
- **A diet mechanic**: one choice per month, separate from the three
  activity slots (PM2's diet is a standing monthly setting, not a
  schedulable activity). Three options:

  | Diet | Effect |
  |---|---|
  | NORMAL | weight +1 |
  | LIGHT | weight −1 |
  | HEARTY | weight +3, health +1 |

  Defaults to NORMAL if never set. Applied once per month at full strength
  (not subject to the sickness-halving rule — diet isn't an activity the
  cat performs, it's background care).
- `GameRun` gains a `diet` field (like `slots`) and `assign_diet(diet)`.
  `advance_month()` applies the diet effect and increments age once,
  alongside resolving the three slots.
- API: `POST /api/game/advance`'s body gains an optional `diet` field
  (defaults to `"normal"`); a new `GET /api/diets` mirrors `GET
  /api/activities` so the UI renders diet options generically instead of
  hardcoding them.

**Out (this part)**

- The portrait art and its selection logic — 2b.
- Any diet-picker UI — 2b.
- Endings/scoring using age or weight — Phase 5.

## Scope — 2b (art + UI)

**In**

- **12 portrait images**: 3 age stages × 2 health conditions × 2 weight
  conditions, generated via `tools/asset-gen` (quantity confirmed with the
  user). Age stage from the `age` stat: kitten (1–4), young (5–8), adult
  (9+). Health condition reuses the existing derived `is_sick` (no new
  concept). Weight condition: chubby if `weight > 70`, else normal.
- A central portrait in `GameScene` that picks and displays the matching
  image from current state.
- A diet picker (one choice per month, rendered from `GET /api/diets`,
  alongside the existing three activity-slot pickers).

**Out**

- Animating transitions between portrait states — a plain image swap is
  enough for v1.

## Mechanics detail

Age-stage and weight-condition thresholds (for 2b, recorded here since
they're derived from 2a's stat ranges):

| Axis | Values |
|---|---|
| Age stage | kitten: 1–4, young: 5–8, adult: 9+ |
| Health | sick (`stress > health`) / healthy |
| Weight | chubby (`weight > 70`) / normal |

12 combinations: kitten/young/adult × sick/healthy × normal/chubby.

## Open questions

None — diet options, thresholds, and image count are decisions made here;
flag back if any read wrong once the art exists.

## Next stage

2a: straight to Coding (server-only, no visual decisions).
2b: art generation, then Coding for the picker + portrait wiring.

Testing: 2a extends `server/tests/game/` per Phase 0's bar (age
auto-increment, diet effects, weight clamping, serialization). 2b needs a
browser check for portrait selection across at least a few of the 12
states, not all — the mapping logic itself should be a plain, unit-tested
function.
