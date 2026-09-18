---
status: review
updated: 2026-09-18
---

# Endings and Score (Roadmap Phase 5)

## Goal

`docs/planning/roadmap.md`'s Phase 5: final stats decide an ending plus a
score, and — unlike Phases 2-4 — this one's "done when" bar is explicitly
frontend-facing: "a full run ends with a real result screen." Right now
`renderEndOfRun()` in `GameScene.js` is a plain stat dump with no ending
and no score; this phase makes month 12 actually feel like a conclusion.

## Scope

**In**

- `Ending` enum + `determine_ending(stats)`: neglected/delinquent special
  cases checked first, otherwise the highest of the five core stats
  (health/affection/discipline/curiosity/refinement) picks a themed
  ending — mirroring the festival's "best trait" pattern from Phase 4 for
  consistency, and PM2's own highest-reputation-picks-the-ending shape.
- `compute_score(stats)`: sum of the five core stats, scaled to a 0-1000
  range (matching the PM2 reference's "score, max 1000").
- Both computed once, when a run's final month finishes, stored on
  `GameRun` (`ending`, `score`), serialized, and surfaced via `/api/game`.
- `GameScene.js`'s end-of-run panel updated to show the ending's Korean
  label and the score prominently, alongside the existing stat summary.
  No new art — text only, styled with the panel/text helpers already in
  the file.

**Out**

- A real PM2-style ending catalog (~74 endings gated by reputations,
  marriages, career outcomes). Meow Maker has none of the systems that
  make that possible yet (reputations, money, NPCs). Seven endings is the
  honest current ceiling; more endings is really "more systems," not a
  Phase 5 task.
- Any illustration per ending (PM2 shows a full illustration in the
  career's outfit). Text-only for this pass, consistent with how this
  project has generally shipped mechanics ahead of bespoke art and added
  art later when asked (portraits, activity scenes).
- Changing what happens *during* the run — this phase only affects what's
  shown once `finished` is already true.

**Continuing the note from Phase 4's planning doc**: same situation —
authored without the usual design checkpoint on the specific ending
names/themes, because the user asked to keep moving through the roadmap
without stopping overnight. Unlike Phase 4 though, this phase's "done
when" bar is explicitly a frontend result screen, which is exactly the
kind of visual/creative surface that's hardest to self-review without the
user actually looking at it. Kept deliberately text-only and reusing
existing render helpers/panel layout for that reason — smallest possible
footprint to redo or restyle if the user wants something different.

## Mechanics

**Endings** (`server/app/game/endings.py`):

| Ending | Trigger |
|---|---|
| `neglected` (방치됨) | final `is_sick` |
| `delinquent` (말썽꾸러기) | final `is_delinquent` (checked after neglected) |
| `healthy` (튼튼한 고양이) | `health` is the highest of the five core stats |
| `beloved` (사랑받는 고양이) | `affection` highest |
| `disciplined` (모범생 고양이) | `discipline` highest |
| `curious` (호기심 많은 탐험가) | `curiosity` highest |
| `refined` (우아한 고양이) | `refinement` highest |

Ties among the five core stats break toward the first-listed
(`health`, `affection`, `discipline`, `curiosity`, `refinement`, in that
order), matching `max()`'s existing tie-break behavior already used for
the festival.

**Score**: `sum(health, affection, discipline, curiosity, refinement) *
2`, clamped to `[0, 1000]` (five stats × 100 max × 2 = 1000 max, matching
PM2's stated max score exactly). `weight`/`age`/`stress` don't factor in
directly — they already shaped the five core stats all run via every
mechanic that touches them.

**Wiring**: `GameRun` gains `ending: Ending | None = None` and `score:
int | None = None`, both `None` until the run finishes. In
`advance_month()`, right where `self.finished = True` is currently set
(the last month), also set `self.ending = determine_ending(self.stats)`
and `self.score = compute_score(self.stats)`. Serialized via
`to_dict()`/`from_dict()` using the same `.get()`-with-default pattern
Phase 4 established for `last_event`/`last_festival_winner`, so old saves
without these keys still load.

**Frontend**: `GameScene.js`'s `renderEndOfRun()` gains an `ENDING_LABELS`
map (mirroring the existing `ACTIVITY_LABELS`/`DIET_LABELS` pattern) and
displays `${endingLabel(this.state.ending)}` plus
`${this.state.score} / 1000` as the panel's headline, above the existing
per-stat summary line — same panel, same helpers, just more content in
it.

## Open questions

None for the mechanism — resolved above. The ending names/themes and
score formula are, as noted above, the part flagged as a placeholder
pending the user's actual review, not assumed final.

## Next stage

Straight to Coding for the backend half (mirrors Phase 3/4's shape
exactly). The frontend half needs the usual `npm run build` + manual
browser check per `AGENTS.md`'s bar for Phaser scene code, since this
phase's own "done when" is explicitly about what the screen shows.

Testing: `server/tests/game/test_endings.py`, table-driven per the
roadmap's own instruction — given a `CatStats`, expect an `Ending`
(covering each of the 7 triggers and at least one tie-break case) — plus
`test_score.py`-style coverage (0, max, and a mid-range value) and a
`GameRun`-level test confirming `ending`/`score` are `None` until
`finished` and set exactly once, on the final month.
