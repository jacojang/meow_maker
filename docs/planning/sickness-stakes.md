---
status: review
updated: 2026-10-02
---

# Sickness stakes and early bad ending (backlog slice S3: A4 + B3 bedridden cue)

Request: Type: modify. Name: sickness stakes. Part of [`feature-backlog.md`](feature-backlog.md).
Builds on [`endings-by-build.md`](endings-by-build.md) (run-summary signature and simulation harness). Design: [`../design/sickness-stakes.md`](../design/sickness-stakes.md).

## Goal

Sickness today only halves growth that month. A cat sick for 11 months and
healed in month 12 pays nothing. Give sickness a real cost, keep it
forgiving enough for a casual game, and add one non-fatal early ending. No death.

## Scope

**In**

- Counters on `GameRun`: consecutive sick months, total sick months, months spent bedridden.
- A bedridden state with forced rest that takes the month's slots.
- Ending and score cost from total sick months, not just the month-12 state.
- One non-fatal early ending, HOSPITALIZED, that ends the run before month 12.
- Visible bedridden cue (badge now, portrait art cost-gated).
- Warning codes `bedridden` and `hospital_risk` for the S1 advisor.

**Out**

- Death or any irreversible loss. Confirmed by the user in Round 4.
- RAN_AWAY and the delinquent streak. Moved to [`care-actions.md`](care-actions.md) (Round 6, see Mechanics).
- Hospital/vet as a paid action (needs [`money-economy.md`](money-economy.md); revisit after S5).
- Changing the sick or delinquent definitions (stress > health, stress > discipline).

## Mechanics

PM2 (`references/princess-maker-2/status-system.md`): sick if stress > constitution; above 90% sickness she is
bedridden; bedridden more than 2 months in a row is death, the only game over.
Departures:
- No death. The same ladder ends in a non-fatal early ending.
- Sickness percent is replaced by month counters (no sickness percent exists here).
- **Cumulative, not consecutive.** PM2 counts consecutive bedridden months. Here three forced RESTs (-60 stress) usually cure the cat in one month, so
  a consecutive rule would almost never trigger. HOSPITALIZED counts bedridden months across the whole run instead.

**Counters** (updated once per `advance_month`, after all stat effects and before the age step):

| Field | Rule |
|---|---|
| `sick_streak` | +1 if sick at month end, else 0 |
| `sick_months_total` | +1 if sick at month end |
| `bedridden_months` | +1 for each month played under forced rest |

**Bedridden**: `is_bedridden` when `sick_streak >= BEDRIDDEN_STREAK`. At the start of such a month
the server overwrites all three slots with REST, whatever the client sent (a message alone would not
bind the player). The state exposes the forced slots, and the client locks the picker. Diet stays selectable.
Care actions still work (pet only; see [`care-actions.md`](care-actions.md)).
Forced rest is almost a free cure, so the cost is mostly lost growth. The simulation below must confirm that is not too soft.

**Ending and score cost**:

- NEGLECTED also applies when `sick_months_total >= NEGLECT_TOTAL`, even if healed at month 12.
- Score loses `SICK_MONTH_PENALTY` per sick month, floored at 0.
- Both live in the S2 data file.

**Early ending** (non-fatal; the run finishes at once with `finished = true`, month unchanged):

| Ending | Trigger | Meaning |
|---|---|---|
| HOSPITALIZED | `bedridden_months >= HOSPITAL_LIMIT` | The cat is taken to a hospital and the run ends. |

Early-ending score = the normal score capped at `EARLY_END_SCORE_CAP`. A neglected run may fail hard (Round 4).

**Why RAN_AWAY moved (Round 6, verified in code)**: the cat starts at discipline 10 and stress 0, and one PLAY slot adds 12 stress,
so almost any first month without REST ends delinquent. A rule of "delinquent three months in a row" would fire on default play, and S3 ships before
scold and treat exist, so REST would be the only counter. HOSPITALIZED starts far from its trigger (health 50 against stress 0). RAN_AWAY ships with S6a, with a streak tuned by simulation.

**Warnings (S1 codes)**: `bedridden` while `is_bedridden`. `hospital_risk` when the cat is sick, not yet bedridden, and one more bedridden month would reach
`HOSPITAL_LIMIT` (`bedridden_months == HOSPITAL_LIMIT - 1` and `sick_streak == BEDRIDDEN_STREAK - 1`).
This is the notice for the **last actionable month**, not a one-month-ahead notice. Counter trace (with 2 and 3): the warning fires while planning month M, with `sick_streak` 1.
If the cat is still sick at the end of M, `sick_streak` becomes 2, so month M+1 is forced rest. At the end of M+1 `bedridden_months` reaches 3 and the run ends.
The ending lands two months after the warning, and month M is the last one where the player can still avoid it (rest, pet, skip risky activities).

Proposed starting numbers (data file, tune with the harness, not final): `BEDRIDDEN_STREAK` 2, `HOSPITAL_LIMIT` 3,
`NEGLECT_TOTAL` 6, `SICK_MONTH_PENALTY` 15, `EARLY_END_SCORE_CAP` 300.

**Order inside a month**: slots, event, diet, penalties, festival, counters, age, early-ending check, normal month-12 finish.
The festival month interacts: a bedridden cat cannot enter the contest ([`festival-contests.md`](festival-contests.md)).

**Save compatibility**: new fields read with `.get()` defaults (0). No `db.py` change. Old saves start with zero counters.

**Client**: `portraitKey(stats, isSick)` gains a bedridden variant; the badge shows bedridden. The early ending reuses the S2 reveal.

**Acceptance (named simulation, harness from S2)**: report, per strategy over many seeds, the rate of HOSPITALIZED, NEGLECTED and each normal ending.
Targets to confirm: `careful` about 0% early or NEGLECTED; `random` low (about under 15%); `careless` and `grinder` may fail hard (the user allows a
neglected run to fail big). Also check that forced rest is not a free reset: if bedridden months cost almost nothing, lower `HOSPITAL_LIMIT` or weaken REST while bedridden.

**Tests**: pytest for each counter transition, forced-rest overwrite (including a hostile client payload), HOSPITALIZED at boundary and boundary - 1, the two warning codes, score floor, old-save defaults.

## Open questions

- Should HOSPITALIZED show its own illustration (cost-gated) or reuse the S2 text reveal? Default: text reveal.
- All numbers above are placeholders pending the simulation. Proposed defaults, no user action needed unless the results feel wrong.

## Notes / Decisions (S3 implementation)

- Constants kept at the proposed values, in `server/app/game/data/endings.json` under `sickness`: `bedridden_streak` 2, `hospital_limit` 3, `neglect_total` 6, `sick_month_penalty` 15, `early_end_score_cap` 300. Missing keys fall back to these defaults in `EndingRules`.
- Counters `sick_streak`, `sick_months_total`, `bedridden_months` are saved in `GameRun.to_dict` and read with `.get(..., 0)`. No `db.py` change.
- `advance_month` overwrites the slots with REST before the completeness check, so even a partial or hostile payload is ignored. State adds `is_bedridden` and `forced_slots` (null or three `rest`).
- `determine_ending` checks HOSPITALIZED first (`bedridden_months >= hospital_limit`), then the S2 order. NEGLECTED also fires on `sick_months_total >= neglect_total`. `compute_score` subtracts the per-sick-month penalty, floors at 0, then caps hospitalized runs.
- Order inside a month follows the doc. A run hospitalized in month 12 is still HOSPITALIZED.
- Warnings: `bedridden` replaces `hospital_risk` once forced rest starts. Both are only emitted for unfinished runs.
- Client: bedridden chip, locked picker with "푹 쉬어야 해요", `hospital_risk` advisor line, `portraitKeyCandidates` falls back to the sick portrait (no bedridden art yet). `bedridden` is deliberately not in `topWarning` severity (the badge and picker line cover it).
- RAN_AWAY is not in S3.

**Measured (1000 seeds each, with S3 rules)**

| Strategy | HOSPITALIZED | NEGLECTED | Other notes |
|---|---|---|---|
| careless | 100% (ends month 10) | 0% | mean score 300 (cap) |
| grinder | 100% (ends month 11) | 0% | mean score 300 (cap) |
| random | 6% | 36% | delinquent 15%, rest normal endings |
| balanced (rotation) | 0% | 0.3% | delinquent 16%, rest beloved/pair |
| careful | 0% | 0% | beloved 98% |
| targeted | 0% | 0.4% | balanced 85% |

- Before S3, careless, grinder and rotation `balanced` were 100% NEGLECTED, and `random` 93%. Forced rest now breaks the rotation cycle (balanced 100% to 0.3% neglected), and hard failures end early.
- Limit levers tried (neglect_total 6 vs 8, hospital_limit 3 vs 4): `neglect_total` barely matters (random neglected 358 vs 355 of 1000) because nearly all NEGLECTED runs are sick at month 12, not over the total. `hospital_limit` 4 turns careless into 100% NEGLECTED at month 12 instead of HOSPITALIZED, so 3 stays. Forced rest is not a free reset: careless gains nothing (100% fail, score capped), so the weaker-REST lever was not needed.
- Target miss: `random` early-or-NEGLECTED is 42%, above the "under 15%" target. The cause is sick-at-month-12 from the existing activity stress balance. S3 mechanics (forced rest, cumulative cost) do not fix it. A fix would need a change to the activity numbers or to the sick definition, both out of S3 scope.
- Existing assertions edited: `test_serialization.py` exact dict gained the three counters; `test_simulation.py::test_careless_and_grinder_runs_end_neglected` became "fail hard" (NEGLECTED or HOSPITALIZED over 90%), as the Acceptance paragraph allows careless and grinder to fail hard.
- Art needed (not generated): `cat-<age>-bedridden` portraits x3 (kitten, young, adult), optional delinquent portraits x3, optional hospitalized illustration x1.
