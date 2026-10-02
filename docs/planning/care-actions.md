---
status: deployed
updated: 2026-10-02
---

# Care actions and delinquency recovery (backlog slice S6a: A3)

Request: Type: new feature. Name: care actions. Part of [`feature-backlog.md`](feature-backlog.md).
Needs [`money-economy.md`](money-economy.md) (paid treat). Counter-play for the states in [`sickness-stakes.md`](sickness-stakes.md).
Design: [`../design/care-actions.md`](../design/care-actions.md).

## Goal

The only pre-schedule choice today is diet, and delinquency has no counter-play
(a flat -1 discipline tax). Add once-a-month care actions so the player can
spend money or a tough choice to manage stress and win back a delinquent cat.

## Scope

**In**

- Three care actions: pet (쓰다듬기), treat (간식 주기), scold (혼내기).
- At most one care action per month, enforced on the server.
- A care step in the advance request, next to diet.
- Result shown in the month summary.

**Out**

- New stats. Affection stands in for PM2's father-relationship value.
- Supervised free time and vacation slots (backlog A12).
- Cat portrait reactions (text first).

## Mechanics

PM2 (`references/princess-maker-2/raising-system.md`, Stress relief): pocket money (20 G) gives
stress -20 once a month but does not work when sick or delinquent. Scolding is free; when
delinquent it cuts stress and raises the relationship, otherwise it lowers the relationship, and if
sick it raises stress. Departure: a free pet is added as a small safety valve; money is plain money.

| Action | Cost | Works when | Effect |
|---|---|---|---|
| Pet | 0 | always | stress -8 |
| Treat | 20 | not sick, not delinquent | stress -20 |
| Scold | 0 | delinquent | stress -15, discipline +2 |
| Scold | 0 | not delinquent | affection -3, stress +3 (sick: stress +5) |

All values are placeholders in a JSON data file. The cap of one care action per month keeps a free pet from
neutralizing stress, since stress is the single lever for both sick and delinquent.

**Flow**: `advance` accepts an optional `care`, like `diet`. Applied at the start of `advance_month`, before the
slots, so stress relief affects sick-halving and day rolls that month. Affordability is checked at assignment
(treat). A non-working action is still allowed but does nothing (and charges nothing). Show that outcome clearly so the player learns the rule.

**State**: `last_care` (action and whether it worked) for the summary, read with `.get()`. No month-use flag is needed because one action is
passed per advance. No `db.py` change.

**Early ending moved here (Round 6)**: RAN_AWAY (delinquent for a run of months) used to sit in S3, before scold existed.
It now ships with this slice, together with its `delinquent_streak` counter and the `runaway_risk` warning ([`events-visible.md`](events-visible.md)).
The cat starts with discipline 10 and one PLAY slot adds 12 stress, so most non-rest first months end delinquent. The streak length, or a stricter
trigger such as stress exceeding discipline by a margin, must be chosen from the shared simulation so that `careless`, `grinder` and `random` strategies do not hit it by default and a `careful` one never does.

**Interactions**: bedridden months ([`sickness-stakes.md`](sickness-stakes.md)) still allow care: pet works and is free; treat does not work while sick and charges nothing.
Care effects are flat like diet (not halved by sickness).

**Tests**: pytest per action per state (healthy, sick, delinquent), cost charging and rejection, cap behavior, summary field, old-save default. RAN_AWAY at its streak boundary and boundary - 1, the `runaway_risk` code, the `delinquent_streak` counter transitions, and the old-save default (0) for `delinquent_streak`.

## Open questions

Resolved (Round 9): one care action per month in total, confirmed by the user.

Still open, none for the user to decide now:
- Final numbers (placeholders above), to tune after S5 and S4.
- Scold copy and tone for a cat game (kept gentle?). Draft at design.

## Notes / Decisions (S6a implementation)

- Code: `server/app/game/care.py` (`Care` enum, validated loader, `care_outcome`), data in `server/app/game/data/care.json` (cost, `works_when` always/healthy/delinquent, effects, backfire effects). Table values are the doc's placeholders, unchanged.
- API: `advance` takes optional `care` (unknown id is a 400). `GET /api/care` lists id, cost, `works_when`, effects. State gains `delinquent_streak` and `last_care` (`{action, worked, cost, effects}`, reset every month, `null` when no care).
- Flow: care is passed to `advance_month(care=...)` and applied before the slots. Affordability is checked up front with the schedule: schedule cost plus the treat charge (only if the treat would work) must fit in money, otherwise `InsufficientMoneyError` (400) and nothing changes. A treat that cannot work is free and never rejected for money. One care per advance is the "once a month" cap.
- Scold: only the doc table is implemented (delinquent: stress -15, discipline +2; otherwise affection -3, stress +3, sick stress +5). The PM2 "raises the relationship" on a good scold is not in the table, so it is not built. Pet and treat have no affection effect.
- Bedridden: care still works. Pet is free and works; treat does nothing and charges nothing while sick (so always while bedridden). Care effects are flat.
- RAN_AWAY: `Ending.RAN_AWAY = "ran_away"`, early ending like HOSPITALIZED (score capped at `early_end_score_cap`, month unchanged, finished at once). HOSPITALIZED wins if both trigger together.
- **Trigger chosen (stricter than the plain streak)**: `delinquent_streak` +1 when the cat ends the month delinquent **and not sick** (stress above discipline, at most health), else reset to 0. `runaway_streak` = 8 (`endings.json`, `delinquency.runaway_streak`).
- `runaway_risk` warning: delinquent, not sick, not finished, `delinquent_streak == runaway_streak - 1`. It is the last actionable month: staying delinquent that month ends the run.
- Old saves: `delinquent_streak` read with `.get(..., 0)`, `last_care` with `.get()`. No `db.py` change.
- Client: `utils/care.js` (works/charge/affordability/hint/result copy, Vitest). Right picker column is split: diet (3 compact buttons) on top, care (안 함 / 쓰다듬기 / 간식 -20 / 혼내기, 2x2) below with a hint line. Care resets to 안 함 each month. A treat that no longer fits the schedule is dropped before sending. The month result adds a care card first in the card queue. `runaway_risk` advisor line, `ran_away` label and flavor (client already tolerated unknown ids). Art: none needed.

**Calibration (harness `server/tests/simulation.py`, 500 seeds, longest run of consecutive delinquent months, no RAN_AWAY applied)**

| Strategy | Plain delinquent streak | Delinquent and not sick |
|---|---|---|
| careless | 10 in 100% (hospitalized first, month 10) | max 1 |
| grinder | max 4 (one run 6) | max 2 |
| random | 7+ in 21%, 10+ in 8%, 12 in 3% | max 8 (1 run in 500), 7+ in 2.4% |
| balanced (rotation) | 7+ in 76% | max 7 (2 runs) |
| careful | max 6 | max 6 |
| targeted | max 7 (2 runs) | max 7 (2 runs) |

- A plain streak cannot satisfy the acceptance: `careless` is delinquent for 10 months straight, so any constant below 10 turns its 100% HOSPITALIZED into RAN_AWAY, and 11 or more almost never fires. A margin on stress minus discipline did not help (careless still 10 at margin 20).
- The "delinquent and not sick" trigger fixes this: a sick cat is on the hospital path, a healthy delinquent one on the runaway path. With 8 the measured RAN_AWAY rates (1000 seeds, default no-care play) are: careless 0, grinder 0, balanced 0, careful 0, random 3 (0.3%), targeted 4 (0.4%).
- New harness strategies: `neglectful` (all PLAY, REST only to stay under health: delinquent, never sick) hits RAN_AWAY in 100% of runs; `attentive` (same schedule plus SCOLD whenever delinquent) 0% (mean score 527 vs 300).
- Existing test edits: `test_serialization.py` exact dict gained `delinquent_streak` and `last_care` (State paragraph); `endingText.test.js` used `ran_away` as its example of an unknown future ending, now `future_ending` (Early ending paragraph: RAN_AWAY gets its label in this slice).
- Not built: festival (S6b), cat portrait reactions for care, the optional pet/treat/scold scenes.
