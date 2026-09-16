---
status: testing
updated: 2026-09-17
---

# Refinement Stat (기품)

## Goal

Add a sixth cat stat, Refinement (기품), raised by education and needed for
the higher-status endings later (Roadmap Phase 5) — PM2's Refinement stat
plays exactly this role, gating the top Social/General endings. Adding it
now, before Phase 2's SQLite schema exists, is free; adding it after means
a column migration.

## Scope

**In**

- A sixth stat, `refinement`, same 0–100 clamping as the others.
- A new activity, `EDUCATE` (교육): raises refinement, costs stress — the
  thing that actually moves the stat, so it isn't a dead number.
- `PLAY` (놀아주기) now costs a small amount of refinement — a stat that
  only ever goes up isn't a real tradeoff, and PM2's pattern is that rough
  or playful activities cost Refinement while calmer ones build it.
- Korean labels for the new stat and activity in the UI.
- Fixing the sickness-halving rule to round non-stress deltas *toward
  zero* rather than floor, now that a real negative delta (PLAY's
  refinement cost) exists. Floor would make sickness *worsen* a penalty
  instead of softening it, which contradicts what halving means everywhere
  else.

**Out**

- Endings/scoring that actually use Refinement — Phase 5.
- The "사교 모임" (social gathering) activity the user mentioned — that's
  event-shaped, not a schedulable activity, and fits Phase 4 (yearly
  events) better than here.
- Any change to the API's response shape — `refinement` just becomes a
  sixth key in the existing `stats` object and a fifth entry in the
  existing activity list.

## Mechanics

**Stat order** (display order too):
`health, affection, discipline, curiosity, refinement, stress`

**Starting value**: 10 — same as Discipline, since it's a trained trait the
cat doesn't start with, not an innate one like Health or Curiosity.

**Activity table changes**:

| Activity | Effect | Stress |
|---|---|---|
| PLAY (놀아주기) | affection +4, curiosity +3, **refinement −2** | +12 |
| EDUCATE (교육) *(new)* | refinement +5 | +8 |
| TRAIN (훈련) | discipline +5 | +8 |
| GROOM (단장) | affection +3, health +1 | +3 |
| REST (휴식) | — | −20 |

**Sickness rounding fix**: `effects_for`'s halving currently does
`value // 2` uniformly. For a positive value that's a floor (4→2, 3→1,
already tested). For a negative value, floor pushes *away* from zero
(-3 // 2 == -2 in Python — a bigger penalty, not a smaller one). Halving a
penalty should shrink it, so the rule becomes: round toward zero for every
non-stress delta, positive or negative. PLAY's `-2` is even and would pass
either way, so this needs a test with an odd negative delta to actually
pin the fix (there isn't one in the current table, so the test can apply
the rule directly rather than through a real activity — see Testing).

## Open questions

None. Confirmed with the user: add the stat now (before Phase 2 makes it
costly), pair it with a real source (EDUCATE) and a real cost (PLAY), leave
"사교 모임" for Phase 4, and fix the halving rounding now that it has a
real case.

## Next stage

No Design pass — same functional UI, just a new column and a new button.
Straight to Coding.

Testing: extend `server/tests/game/` for the new stat/activity/rounding
rule (per Phase 0's own bar — every rule gets a test), and
`web/src/utils/*.test.js` if the label maps move into testable modules.
A browser pass isn't strictly required (no async/structural change), but
worth a quick check given the last two features both shipped a bug that
tests didn't catch.

Built via the coding-agent/review-agent loop, server then web. The web
task's own live-browser check (habit carried over from the last feature's
lesson) caught a real layout overflow: three panels used a fixed row pitch
sized for the old stat/activity counts, and a 6th stat plus 5th activity
overflowed them. Fixed by computing the pitch from the actual count.

First review returned FAIL on a smaller issue: that fix (`fitStep`) was
pure, Phaser-free logic left un-exported inside `GameScene.js` with no
test — exactly what `AGENTS.md` says belongs in `web/src/utils/` instead
(the `coverScale.js` pattern). Moved there with its own test; re-review
passed.

`server/tests/game/test_run.py`'s full-12-month simulation was updated
with a hand-traced expected value, not just whatever the code produced —
confirmed independently in review.
