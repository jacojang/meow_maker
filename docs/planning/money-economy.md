---
status: deployed
updated: 2026-10-02
---

# Money economy and part-time job (backlog slice S5: A2)

Request: Type: new feature. Name: money economy. Part of [`feature-backlog.md`](feature-backlog.md).
Needs [`daily-variance.md`](daily-variance.md) (day outcomes pay the job). Unblocks [`care-actions.md`](care-actions.md) and [`festival-contests.md`](festival-contests.md).
Design: [`../design/money-economy.md`](../design/money-economy.md).

## Goal

Slots are the only scarce resource today. Add money as a second axis
(money vs stress vs growth), as PM2 does, with plain money earned by a
part-time job and festival prizes.

## Scope

**In**

- `money` on `GameRun`, shown in the HUD.
- Per-activity costs and income in a JSON data file.
- A new 7th activity, part-time job (아르바이트), that earns money.
- Server-side affordability check when assigning the month.
- Money readout in the schedule scene (the spot reserved by S4).

**Out**

- Yearly allowance or stipend. The user chose jobs and prizes only.
- Shops, items, equipment, a vet or hospital purchase (revisit later).
- Several different jobs, job raises, unlock ages (data-only follow-ups).
- Prizes themselves (they arrive with [`festival-contests.md`](festival-contests.md)).
- Money in the score (open question).

## Mechanics

PM2 (`references/princess-maker-2/raising-system.md`): classes charge tuition per day, even on wasted
days. Part-time jobs pay only on successful days, +50% for a perfect session, and always
apply stat changes. A 500 G yearly stipend exists. Departure: plain money, no stipend,
one job in v1, tuition per slot (not per day) charged in full whatever the days' outcomes.

**State**: `money: int`, never negative. Read with `.get("money", START_MONEY)`, so old saves
load with the starting amount. No `db.py` change (state is one JSON blob).

**Data** (`economy.json`, validated at load like the existing tables): per activity `cost` and
`income_per_day`. Starting values (job values confirmed; the rest tuned in playtest and the simulation):

| Item | Value |
|---|---|
| Start money | 200 |
| Cost: educate / train / outing | 40 / 30 / 20 |
| Cost: play / groom / rest | 0 |
| Job: income per successful day | 8 (a slot is about 10 days) |
| Job | 쥐잡이 알바 (confirmed by the user, Round 9): curiosity +2, refinement -2, stress +8 |

**Rules** (server only):

- `assign_month` rejects the schedule if total costs exceed money at month start. Income earned within the month does not count toward affordability (keeps the check order-free). Error is a `GameRuleError`, HTTP 400.
- Cost is charged when its slot resolves, in full, whatever the daily outcomes.
- Job pays per `normal` or `great` day, 0 on `fail`. All days non-fail gives +50% (PM2). Job stat effects apply regardless of outcome, as in PM2, and are exempt from the S4 0/1/2 multiplier ([`daily-variance.md`](daily-variance.md)). Only pay depends on the daily outcome.
- Sick: job stat effects are halved like any activity's non-stress effects (existing rule); income per day is also halved (rounded down). Stress is not halved. Default, to confirm.
- Free options (play, groom, rest) and the job are always available, so money can never softlock a run.
- Forced rest ([`sickness-stakes.md`](sickness-stakes.md)) is free.
- Hospital cost: none in S3. Revisit once money exists.

**Client**: HUD money. Picker shows each activity's cost and disables unaffordable ones as a convenience only. The
server stays the authority. `GET /api/activities` gains `cost` and `income_per_day` (additive fields).

**Balance risk**: every activity gets a price, the biggest balance change so far. Start generous,
simulate typical schedules (all-train, all-educate, mixed, job-heavy), and confirm a mixed schedule beats both extremes.
The S4 variance weights are re-tuned after this slice lands.

**Acceptance (named simulation, harness from [`endings-by-build.md`](endings-by-build.md))**: money must be tight, or it is a decorative HUD.
Over many seeds with named strategies (targets are approximate; the simulation fixes the numbers):
- A mixed strategy (job slots to fund paid slots) occasionally cannot afford the paid slot it wants: roughly 10 to 30% of months. That is the tightness signal.
- A strategy that spends on every paid option (educate, train, outing each month, little or no job) runs out of money.
- A mixed schedule scores higher than all-job and than all-train.
If money is not tight, raise costs. Do not add shops to soak it up. "Money does not count toward the score" stays only while these checks pass; otherwise revisit.

Starting figures to check first: start 200, educate 40, job about 80 per slot (120 with the perfect bonus), festival prizes up to 300.
Those prizes are large next to tuition, so the festival economy is part of the same simulation ([`festival-contests.md`](festival-contests.md)).

**Tests**: pytest for affordability (exact boundary), per-slot charging, job income per outcome and the perfect bonus,
the never-negative invariant, old-save default, data file validation (missing/unknown key).

## Open questions

None for the user. Resolved in Round 9:

- Job: 쥐잡이 알바 as specified (curiosity +2, refinement -2, stress +8, 8 per successful day, halved when sick). Confirmed.
- Leftover money does not count toward the score. The simulation acceptance above stays as the condition for keeping it that way.

Still to settle at coding time, not by the user: start money and costs (placeholders, set by the simulation); job art is generated or text-only per the asset policy (text-first, art additive).

## Notes / Decisions (S5 implementation)

- Code: `server/app/game/economy.py` (loader, validation, helpers), data in `server/app/game/data/economy.json`, `Activity.JOB` and its effects in `activities.json`. `GameRun.money`, saved in `to_dict`, read with `.get("money", START_MONEY)`. No `db.py` change.
- Numbers: start 200, educate 35, train 25, outing 15 (was 40/30/20), play/groom/rest/job 0, job 8 per successful day, perfect bonus +50%, sick income halved (floor). Job: curiosity +2, refinement -2, stress +8. `perfect_bonus_percent` lives in the data file too.
- Costs were lowered from the placeholders because 40/30/20 gave a mixed strategy 32% denied months, above the 10-30% target. Start money barely moves the rate (240: 31%, 300: 28%).
- Rules: `assign_month` and `advance_month` both reject an unaffordable schedule (`InsufficientMoneyError`, API 400). Neither check runs while forced rest is active (forced rest is free and overwrites the slots). Cost is charged when the slot starts; money can never go negative (`GameRun(money<0)` raises).
- Job: rolls day outcomes like a variance activity, but the roll only drives pay. Stat effects use the base share every day (not in `VARIANCE_ACTIVITIES`), so they are exempt from the 0/1/2 multiplier. A fail day pays 0. All days non-fail adds the bonus on the slot total (floor). Sick halves stat effects (not stress) and per-day income, read at slot start.
- Log: each slot entry gains `cost`, `income`, `bonus`; job days gain `income`. Other days keep their old keys. `GET /api/activities` gains `cost` and `income_per_day`.
- Client: `utils/money.js` (price labels, affordability, `affordablePicks`, `buildMoneySteps`). HUD money sits in the stats panel header. The money box is in the resolution overlay (bottom of the text column), green on income, red on tuition. Picker has 7 buttons, each with a price line, dimmed with a red price when unaffordable; clicking one shows an advisor line. Picks that became unaffordable are swapped for the first free option (play) before sending. Job art is text/chip only: `job` is not in `BootScene` `ACTIVITY_SCENE_IDS` (no files exist, so no 404s); the scene already skips missing textures. Coin icon not made.
- Harness: `server/tests/simulation.py` gained `all_job`, `all_train`, `spend_everything`, `mixed` (`ECONOMY_STRATEGIES`), `MonthPlan.fallback`, `RunResult` money fields, `denied_month_rate`, `broke_run_rate`. Existing strategies are unchanged, but `simulate`/`play_run` now default to `unlimited_money_run` so the older strategies and baselines still ignore money; the S5 checks pass `run_factory=GameRun`. `random_strategy` draws from every activity except JOB, so the S2/S3/S4 random baselines reproduce. `all_train` falls back to REST and `mixed` to a JOB when a slot is unaffordable, which is why all_train scores low (forced rests, no job income).
- Leftover money does not count in score (kept).

**Measured (1000 seeds each, start 200, `GameRun` factory)**

| Strategy | Mean score | Denied months | Runs that hit under 15 gold | Mean final money | Endings |
|---|---|---|---|---|---|
| all_job | 309 | 0% | 0% | 1609 | curious 83%, delinquent 17% |
| all_train | 339 | 75% | 100% | 0 | pair_health_discipline 95% |
| spend_everything (educate/train/outing) | 342 | 76% | 69% | 9 | pair_health_curiosity 98% |
| mixed (weakest stat, unaffordable slot becomes a job) | 485 | 28% | 59% | 72 | balanced 23%, pairs and healthy |

- Mixed is denied a wanted paid slot in about 28% of months (target 10-30%). Spend-everything is denied in 76% of months and ends near 0 gold. Mixed beats all-job (309) and all-train (339) on score. All three acceptance checks pass, so money stays out of the score.
- Not built: festival prizes (S6b), care actions (S6a), shops, coin icon, job art. Art still needed if wanted: `scene-job` + `-b` to `-e`, coin icon.
- Existing test edits: `test_serialization.py` exact dict gained `"money": 200` (State paragraph). `test_run.py::test_full_twelve_month_simulation` now starts `GameRun(money=1000)` (the plan trains 12 times, unaffordable from 200; Rules, first bullet). `test_api.py::test_state_reports_overweight_once_hearty_diet_pushes_past_the_threshold` uses free activities (`A_MONTH` includes train, 11 months unaffordable; same rule).
