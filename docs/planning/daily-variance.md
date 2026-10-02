---
status: review
updated: 2026-10-02
---

# Daily variance and live schedule scene (backlog slice S4: A5 + B1)

Request: Type: modify. Name: daily variance. Part of [`feature-backlog.md`](feature-backlog.md).
Follows [`sickness-stakes.md`](sickness-stakes.md). Numbers are re-tuned after [`money-economy.md`](money-economy.md).
Design: [`../design/daily-variance.md`](../design/daily-variance.md).

## Goal

Every activity gives the same fixed result today, so the best schedule is
solved and the resolution animation shows nominal numbers, not what
happened. Add day-by-day results with real swings, and show them live.

## Scope

**In**

- Per-day outcome rolls inside each slot for play, train, groom and educate. REST and OUTING have no variance. Once the part-time job exists (added by [`money-economy.md`](money-economy.md), not in this slice), it rolls outcomes only to decide pay and its stat effects are exempt. S4 does not need the job to ship.
- A day log returned by the API and persisted on the run.
- A server calendar mirror so the server knows how many days each slot has.
- B1: the resolution scene plays the log, with live stat gauges and a one-line result per day.

**Out**

- The money box in the scene (added by S5; B1 leaves room for it).
- Changing OUTING's existing one-roll success layer ([`outings.md`](outings.md)).
- New art. The 5 existing frames per activity are reused.
- Changing the sick-halving rule.

## Mechanics

PM2 (`references/princess-maker-2/raising-system.md`, `characters-and-layout.md`): classes and jobs
resolve day by day, each day a success or failure; the schedule scene shows a day counter,
one result line per day and gauges ticking. Departure: three outcomes instead of two, no tuition effect yet.

**Days per slot (correction)**: the calendar uses real 2026 month lengths, so a slot is about 10
days (9 to 11), not 3. The split rule is the one in `web/src/utils/calendar.js`: each slot gets
`floor(days / 3)`, the last takes the remainder. The server holds a fixed-year month-length
table and the same split. Parity is guarded by one pytest and one Vitest asserting the same literal 12-month table.

**Outcome per day**: `fail` (multiplier 0), `normal` (1), `great` (2).
Starting weights: fail 0.25, normal 0.50, great 0.25. Mean multiplier = 1.0, so expected totals
match today's numbers. Swings are intentionally visible (user, Round 4).

- Stress above a threshold shifts weight from normal to fail. Exact curve is a data value.
- Sick keeps today's halving. It is not stacked with extra fail weight (avoids double-counting). Revisit in playtest.
- Roll order: `fail` if `u < p_fail`; `great` if `p_fail <= u < p_fail + p_great`; else `normal`.
  So a roll of 1.0 means `normal`. This keeps `NeverRng` (returns 1.0) deterministic and existing tests valid.

**Positive deltas only (Round 6)**: the 0/1/2 multiplier applies only to positive deltas. A negative delta
(for example PLAY refinement -2) keeps its base value, spread across the days, so a `great` day never doubles
a penalty and a `fail` day never cancels one. The mean stays at the base because the positive mean is 1.0.
The part-time job's stat effects are never multiplied; they follow the S5 rule.

**Slot effect**: for each non-stress stat, the per-day yield is `base / days`, times the day's multiplier.
Deltas are accumulated and rounded cumulatively, so the integer deltas sum to the slot total and the
gauge can tick per day. Stress is the fixed base, spread across days the same way, and is not rolled
(variance applies to growth only, so sickness stays predictable). Sickness for halving is read at slot start, not per day.

**Day log**: `last_month_log`, list per slot of `{slot, activity, days: [{day, outcome, deltas}]}`.
Persisted via `to_dict`/`from_dict` with `.get(..., [])`. No `db.py` change. `GameRun.advance_month`
stays the only mutation point.

**RNG**: day rolls need their own injectable source, defaulting like `get_rng`, with a `NeverRng` default
in `conftest.py`. This keeps the call order of the existing outing and event rolls, which scripted-fake tests
depend on, from shifting. Design must confirm this before coding.

**Client (B1)**: replace the nominal step panels with the log. For each slot, play its days in order:
date label, outcome line, gauges for only the stats that activity changes. Frames cycle as today. A skip control ends the scene.
The client never invents results.

**Playback speed**: a month is about 30 day-steps at about 250 ms, roughly 7.5 s. After the first month the
player's speed choice (normal, fast, skip) is remembered in `localStorage` and applied to later months.

**Retune note**: weights and the stress curve are re-tuned after S5 because costs change what a failed day is worth (tuition is still charged on a failed day, as in PM2).

**Tests**: pytest for the roll thresholds, cumulative rounding (sum equals total), the slot-length table, log
round trip and old-save default, `NeverRng` = base deltas. Vitest for log-to-animation-steps as a Phaser-free util.

## Open questions

- Weights (0.25/0.50/0.25) and the stress curve are proposals. Is that level of swing right? The user said visibly swingy is fine, but not how much.
- Should REST and OUTING stay variance-free? Proposed yes for both.
- Copy: one-line day results need text (per activity and outcome). Draft at design time for user review.

## Notes / Decisions (S4 implementation)

- Code: `server/app/game/daily.py` (outcome rolls, `DayYield` cumulative rounding, month table, slot split), data in `server/app/game/data/daily.json`. `GameRun.advance_month(rng, day_rng)`; `get_day_rng` in `app/rng.py`; the API passes it, `conftest.py` overrides it with `NeverRng`.
- If `day_rng` is not passed, `advance_month` falls back to `rng`. With `NeverRng` that means all-normal days, so existing tests keep working. Scripted-fake tests only use REST/OUTING slots, so they draw no day rolls.
- Stress curve: above stress 60, fail weight grows 0.005 per point, capped at +0.20 (fail 0.45, normal 0.30, great 0.25 at the cap). Stress is read at the start of each day. Weights 0.25/0.50/0.25 unchanged.
- REST and OUTING draw no day rolls and log `normal` days. OUTING's one-roll success layer is untouched and runs after the slot's days.
- Log: `last_month_log`, one entry per slot, days numbered 1..N across the month, `deltas` list only non-zero stats. Replaced each month. No `db.py` change.
- Client: `utils/dayLog.js` (steps, copy, gauges), `utils/playbackSpeed.js` (speed, `localStorage` in try/catch). The first month of a session plays at normal; later months use the saved speed. Speed buttons (보통 / 빠르게 / 건너뛰기) sit in the overlay header; skip ends the animation. About 250 ms per day at normal, 80 ms fast. The diet step stays as a closing panel. The money box spot is left empty for S5. `utils/resolutionSteps.js` was unused and has been deleted.
- Day copy lines are a draft in `dayLog.js` for user review.
- Job pay roll is S5. Not built.
- Parity: pytest asserts the literal 12-month table and the slot split; Vitest asserts the same table against `daysInMonth`.

**Measured (500 seeds each, mean final stats, no variance vs variance)**

| Strategy | Mean score | Largest stat drift | Notes |
|---|---|---|---|
| careless | 300 vs 297 | affection -2.9 | hospitalized 100% both |
| grinder | 300 vs 300 | none | hospitalized 100% both |
| random | 427 vs 430 | discipline +0.7 | neglected 36% vs 36% |
| balanced | 435 vs 440 | discipline +1.7 | |
| careful | 492 vs 498 | affection +0.6, discipline +1.7 | |
| targeted | 618 vs 616 | discipline +1.6, stress +2.7 | balanced 86% vs 76%, pair endings 14% vs 19% |

- Means stay within about 3 points of today's, so the "totals near today's" target holds.
- Variance spreads stats more, so the strictly even BALANCED ending is harder for a focused player (86% to 76%). Accepted; re-tune after S5.
- Existing assertion edits: `server/tests/game/test_serialization.py` exact dict gained `"last_month_log": []` (Mechanics, "Day log ... Persisted via to_dict"). `server/tests/conftest.py` gained the `get_day_rng` override (RNG paragraph).
