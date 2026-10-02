---
status: deployed
updated: 2026-10-02
---

# Build-aware endings and ending reveal (backlog slice S2: A6 + B4)

Request: Type: modify. Name: build-aware endings. Part of [`feature-backlog.md`](feature-backlog.md). Extends [`endings-and-score.md`](endings-and-score.md) (deployed).
Design: [`../design/endings-by-build.md`](../design/endings-by-build.md).

## Goal

Today the ending is the single highest stat, so one spammed activity decides
everything and balance is never rewarded. Make the ending read the whole
build, and make the last screen feel like a conclusion.

## Scope

**In**

- Ending rules as data, evaluated top to bottom, first match wins.
- A balanced ending, and pair endings from the top two stats.
- Score adjustments (bonus for balance, penalties for end-state problems).
- Stepwise ending reveal on the client (text only).
- `determine_ending` and `compute_score` take a run summary object (stats plus counters with defaults), so [`sickness-stakes.md`](sickness-stakes.md) adds fields without another signature change.

**Out**

- The PM2-size catalog (~74). Still on record as out of scope.
- Per-ending illustrations (cost-gated, separate decision).
- Sick-month logic and the HOSPITALIZED ending (S3), and the RAN_AWAY ending (S6a). `Ending` gains the RAN_AWAY enum value and label in S6a, so `determine_ending` and the client label table must tolerate new values being added later.
- Money in the score (decided in [`money-economy.md`](money-economy.md)).

## Mechanics

PM2 (`references/princess-maker-2/endings.md`): checked top to bottom; first match wins;
a "General" ending applies when all reputations are within 50 points;
the score has a performance bonus. Departure: Meow Maker has five stats and no
reputations, so the five core stats stand in. Pair endings and score penalties are new.

**Order** (first match wins):

1. NEGLECTED (existing: sick at the end). S3 extends this.
2. DELINQUENT (existing).
3. BALANCED: `max - min` of the five core stats is at most `BALANCE_GAP`.
4. PAIR: second-highest is within `PAIR_GAP` of the highest. Ending = the pair.
5. SINGLE: highest stat (the 5 existing endings).

Ties: use the existing `ENDING_STAT_PRIORITY` order, so results stay deterministic.

Proposed starting numbers (data file, tune by simulation): `BALANCE_GAP` 25, `PAIR_GAP` 5.
These need a simulation over typical schedules before fixing. Rule of thumb:
BALANCED should be reachable by a deliberate mixed schedule but not by default play.
Starting stats are 50/20/10/30/10, so the gap is already 40 at month 1.

**Pair endings**: 10 pairs from 5 stats. Each is a label plus a flavor paragraph. Labels
are drafted at design time and reviewed by the user. They are copy, not rules.

**Score** (still 0-1000 clamp, only the five-stat sum x2 as the base):

- Balance bonus when BALANCED.
- Penalty when overweight at the end, and when stress is above a threshold at the end.
- Bonus never pushes past 1000 because of the clamp. Numbers live in the data file.

**Named deliverable: simulation harness** (`server/tests/`, a helper plus loose range checks, not exact asserts). It runs full 12-month
runs over many seeds for named strategies: `careless` (all PLAY), `grinder` (all TRAIN), `random`, `balanced` (rotates train, play, educate, groom, rest), `careful` (rests when stress nears limits). Later slices
(S3 to S6b) reuse it for their acceptance checks. For this slice it reports ending and score distributions.

Target for the gaps (to confirm by the harness): a deliberate `balanced` strategy reaches BALANCED often (about half or more of seeds);
`careless`, `grinder` and `random` reach it rarely (about under 10%). If not, change the gaps, not the strategy.

**Save compatibility**: ending and score are computed once at finish and stored. Finished
old runs keep their stored values. In-progress old runs get the new rules at month 12.

**Tests**: table-driven pytest per rule and per boundary (gap = limit, gap = limit + 1),
priority order, tie order, score clamp. Reveal-step sequencing as a Phaser-free util.

## Open questions

- Pair-ending labels and copy: draft at design, user reviews. Is 10 pair labels too many to write, or fine?
- Final `BALANCE_GAP` / `PAIR_GAP` values: set from the harness against the targets above, not guessed here.

## Notes / Decisions (S2 implementation)

- `BALANCE_GAP` 15, `PAIR_GAP` 10 (in `server/app/game/data/endings.json`). The proposed 25 / 5 were not kept: 25 made balance too easy for a focused player, and 5 gave almost no pair endings.
- Score numbers (same file): balance bonus +80, overweight -60, stress above 60 at the end -60.
- Harness: `server/tests/simulation.py` (strategies are `(run, rng) -> MonthPlan`, seeded, `simulate(strategy, runs, base_seed, run_factory)`). Strategies: the five named ones plus `targeted`.
- Finding: the five named strategies cannot test the BALANCED target by themselves. Stress is the limit, not the gap. Pure rotation (`balanced`) ends NEGLECTED in 100% of runs, because one REST in five slots does not offset the other four. `careful` (rotation with REST when stress nears health) never gets sick but its stats spread 27-56, so it never reaches 15.
- Added `targeted` (always works the weakest stat, rests near the stress limit) as the "deliberate balanced schedule". Gap values were chosen against it. The named strategies were not changed.
- Measured, 1000 seeds each, with final values (ending shares):

| Strategy | BALANCED | Pair (any) | Other |
|---|---|---|---|
| careless | 0% | 0% | neglected 100% |
| grinder | 0% | 0% | neglected 100% |
| random | 0% | 1% | neglected 93%, delinquent 3%, curious 3% |
| balanced (rotation) | 0% | 0% | neglected 100% |
| careful | 0% | 2% | beloved 98% |
| targeted | 85% | 14% | delinquent 1% |

- Pair endings are rare outside focused play (about 1-2% for non-targeted strategies). Accepted: 10 pair labels are copy, and they still appear for players who push two stats.
- The balance bonus also applies to a very low but even cat (for example all stats at 0). Rule kept exactly as written ("max - min within the gap"). In practice all-zero is unreachable.
- Pair labels (Korean) and flavor text live in `web/src/utils/endingText.js`. Server sends ids `pair_<stat>_<stat>` (stat order: health, affection, discipline, curiosity, refinement) and `balanced`.
- `determine_ending` / `compute_score` accept a `RunSummary` (stats only for now) or bare `CatStats`. `GameRun.summary` builds it.
- Existing assertions replaced per this doc: tie test (pair ending, Order step 4), minimum score (balance bonus), weight-ignoring score test (overweight penalty).
