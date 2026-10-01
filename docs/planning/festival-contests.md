---
status: review
updated: 2026-10-02
---

# Harvest festival contests (backlog slice S6b: A7)

Request: Type: modify (replaces the placeholder in [`events-and-festival.md`](events-and-festival.md)). Part of [`feature-backlog.md`](feature-backlog.md).
Needs [`events-visible.md`](events-visible.md) (result card), [`money-economy.md`](money-economy.md) (prizes), [`daily-variance.md`](daily-variance.md) (RNG convention).
Design: [`../design/festival-contests.md`](../design/festival-contests.md).

## Goal

The yearly peak is a silent +5 stat in month 10. Make it a contest the
player prepares for, can win or lose, and gets paid for.

## Scope

**In**

- Four contests, each keyed to one stat, scored against rival cats.
- Festival month replaces that month's three slots when the player enters (user decision, Round 4).
- Prize money by rank and a ribbon record.
- Contest choice in the advance request, and a result screen using the S1 card.

**Out**

- Prepared entries or items (PM2's painting, dress). No items exist.
- Rival storylines or recurring rival encounters.
- Moving the festival month (stays month 10, `FESTIVAL_MONTH`).
- Bespoke contest art (text-first, asset list in the design doc).

## Mechanics

PM2 (`references/princess-maker-2/mini-games.md`, Harvest Festival): four contests, one entry per year,
scores are a stat times a random factor of about 0.7 to 1.3, prizes are money plus items and reputation,
a named rival in some contests. Skipping turns October into free time. Departure: no items, no
reputation, three generic rival cats per contest.

**Contests** (stat choices reuse the current `FESTIVAL_STATS`; names are drafts):

| Contest | Stat |
|---|---|
| 재롱 대회 | affection |
| 복종 대회 | discipline |
| 탐험 대회 | curiosity |
| 기품 대회 | refinement |

**Score**: `stat x rand(0.7 to 1.3)`. Each contest has three rivals with data-defined base values, scored the same way. The
cat's rank is its place among four. Rival strength is data, tuned by simulation.

**Month flow**: in month 10, `advance` takes a `contest` (or skip). If entered, the three slots are not used
and are cleared; the month's effect is a small entry stress (placeholder +5). If skipped, a normal schedule month (PM2's free time).
The old flat +5 winner bonus is removed.

**Prizes**: money by rank (placeholders 1st 300, 2nd 150, 3rd 50, 4th 0) and a ribbon.
Ribbons add to the score by rank so that entering can beat skipping (Round 6, accepted by the user in Round 9): 1st +40, 2nd +25, 3rd +10, 4th 0.
One score point is half a stat point, and three growth slots are worth roughly 30 score points, so 1st and 2nd beat skipping,
3rd roughly breaks even, 4th loses. Money prizes are on top. Values are proposals, tuned in the simulation, still under the 1000 clamp.

**State**: `festival_result` (contest, rank, prize), `ribbons`. Read with `.get()` defaults. `festival_result` and `ribbons` persist for the rest of the run (they feed the ending reveal and score). `last_festival_winner` is removed from
serialization; old saves that contain it simply have the key ignored on load. Until this slice, S1 leaves the field's current behavior unchanged (Round 10).
No `db.py` change.

**Interactions**: a bedridden cat ([`sickness-stakes.md`](sickness-stakes.md)) cannot enter. Forced rest wins.
RNG uses the injected source, with a `NeverRng`-safe order so tests stay deterministic.

**Breaking change to tested behavior**: `festival.py` and its tests encode the old winner-gets-+5 rule. Those tests describe a mechanic being replaced on purpose, so
they are rewritten for the new rule rather than bent to pass. Flag this at coding time.

**Acceptance (named simulation)**: with the shared harness, a prepared cat (high keyed stat) should gain more by entering than by skipping, and an unprepared cat (4th place) should not. If skipping dominates for everyone, raise ribbon value before adding anything else.

**Tests**: pytest for scoring at boundaries, ranking with ties, prize by rank, skip flow, bedridden block, old-save default.

## Open questions

Resolved (Round 9): skipping the festival is allowed (a normal month), and ribbon score values 1st +40, 2nd +25, 3rd +10 are accepted.

Still open, none for the user to decide now:
- Contest names and rival cat names (drafts above for review).
- Rival strength curve and prize amounts are placeholders pending S5 balance.
- Rival cat portraits (3 to 4 assets): generate or text-only?

## Notes / Decisions (S6b implementation)

- Code: `server/app/game/festival.py` (validated loader, `resolve_contest`, `rank_among`, prize/ribbon lookups), data in `server/app/game/data/festival.json` (variance 0.7 to 1.3, entry stress 5, prizes, ribbon scores, 4 contests with 3 rivals each). No `db.py` change.
- Contest ids: `charm` (affection), `obedience` (discipline), `exploration` (curiosity), `grace` (refinement). Korean names live in the client (`web/src/utils/festival.js`): 재롱 / 복종 / 탐험 / 기품 대회. Rivals (text only, 12 names, 3 per contest, ids are server data): 나비 치즈 보리 / 두부 먹물 고미 / 고등어 바둑이 토리 / 삼색이 유리 누리. Rival base values, same in every contest: 35 / 55 / 75.
- API: `advance` takes optional `contest`. With a contest, `activities` may be omitted (the body is rejected with 422 only if both are missing). `GET /api/festival` returns month, entry stress, prizes, ribbon scores, contests with rival ids and bases. State gains `festival_result` and `ribbons`, loses `last_festival_winner` (old saves: key ignored, new keys default via `.get()`).
- Flow: entering clears the slots (no slot cost, empty `last_month_log`), adds the entry stress, then the event, diet and penalties still run, and the contest resolves after them (the old festival position). Care still applies and its cost is still checked. Skipping is a normal month with no result. A contest outside month 10 or an unknown id raises `InvalidContestError` (400, nothing changes). A bedridden cat ignores the contest (forced rest wins, no error).
- RNG: the injected `rng` (not the day rng). The player rolls first, then rivals in data order, one `random()` each, after the event roll, so months without a contest keep their old random sequence. `NeverRng` gives every entrant the 1.3 factor. Scores are rounded to ints.
- Ties: the player takes the better place (rank = 1 + rivals strictly higher).
- Ribbons: a ribbon is recorded for rank 1 to 3 only (4th scores 0, so none). `ribbons` is `[{contest, rank}]`. `RunSummary.ribbon_ranks` feeds `compute_score` (+40/+25/+10 before the 1000 clamp, early-ending cap still applies after). Leftover money is still not in the score.
- Prize money is paid when the contest resolves.
- Client: `utils/festival.js` (stage, rows, card copy, Vitest). Month 10 shows a contest list (4 rows with the keyed stat value plus 불참) in place of the calendar; 불참 shows the normal calendar with a back link; a bedridden cat sees the list dimmed with the forced-rest line. The play button reads "대회 참가" when entering and is disabled until a choice is made. The S1 festival card now reads `festival_result` and `ribbons` (rank line, ranked scores with the player marked, prize, ribbon). The scene fetches `/api/festival` at start; if that fails, no festival UI is shown.
- Existing test edits (each replaces a rule this slice removes, or an exact key list):
  - `tests/game/test_festival.py`: rewritten. Old tests asserted the highest stat wins +5 and ties break to the first listed stat (Mechanics: "The old flat +5 winner bonus is removed"; Breaking change paragraph). New tests cover scoring boundaries, ranking with ties, prizes, ribbon scores, loader validation.
  - `tests/game/test_run.py::test_festival_fires_at_the_fixed_month_and_rewards_the_best_stat` and `test_no_festival_outside_the_fixed_month`: replaced by skip-is-normal and no-result-outside-month tests (Month flow: skipped is a normal month, no bonus). `test_full_twelve_month_simulation`: skipped festival, so discipline 75 becomes 70 and the `last_festival_winner` assert becomes `festival_result is None` (same lines).
  - `tests/game/test_warnings.py::test_advance_month_clears_event_and_outing_but_keeps_festival_winner`: now keeps `festival_result` (State: persists for the rest of the run).
  - `tests/game/test_serialization.py`: exact dict loses `last_festival_winner`, gains `festival_result`, `ribbons`; the "defaults last_event and festival_winner" test lost its festival half (State paragraph).
  - `tests/test_api.py::test_start_game_returns_a_fresh_run`: asserts `festival_result` / `ribbons` instead of `last_festival_winner`.
  - `web/src/utils/resultCards.test.js`: two festival cases moved from `last_festival_winner` to `festival_result` (events-visible.md: S6b deletes the field).
- Harness: `server/tests/simulation.py` gained `MonthPlan.contest`, `enter_festival(base)`, `best_contest`, `RunResult.festival_rank`. Acceptance tests: `server/tests/test_simulation_festival.py` (150 seeds, loose ranges).

**Measured (paired seeds, same strategy skipping vs entering the best-fit contest; 1000 seeds, score delta = enter minus skip)**

| Strategy | Skip score | Enter score | Delta | Rank 1 / 2 / 3 / 4 | Notes |
|---|---|---|---|---|---|
| grinder (discipline ~100) | 299.7 | 301.7 | +2.0 | 70 / 26 / 4 / 0 % | prepared; prize +312 gold |
| random | 419.3 | 423.2 | +3.9 | 23 / 35 / 23 / 2 % | 18% died before month 10 |
| careful | 488.1 | 485.2 | -2.8 | 20 / 48 / 31 / 1 % | |
| targeted (balanced build) | 614.5 | 585.0 | -29.5 | 5 / 31 / 54 / 11 % | skipping wins |
| mixed (money-tight) | 472.6 | 457.9 | -14.7 | 1 / 16 / 57 / 26 % | |
| all_train (money-tight) | 328.7 | 376.5 | +47.8 | 6 / 34 / 51 / 9 % | prize funds slots in months 11-12 |
| spend_everything | 332.0 | 359.6 | +27.6 | 1 / 12 / 60 / 28 % | |

Pooled over 500 seeds each, by placed rank (score delta vs skipping): 1st +18.3, 2nd +16.0, 3rd +1.7, 4th -20.3. By strategy at 500 seeds (strategies that stay alive to month 10): grinder +2.2, careful -1.9, random +3.7, targeted -26.5, mixed -14.9, all_train +48.4, spend_everything +27.7, a pure-outing specialist +24.8. Keyed stat 80 to 100: +14.2 and 57% better off; keyed stat 60 to 79: +2.3.

- Acceptance: 1st and 2nd place beat skipping, 3rd breaks even, 4th loses, as the doc predicted. The prepared (specialist) cat gains by entering and wins first place 70% of the time. A deliberately balanced build (targeted, mixed) is better off skipping, because its three slots are worth more than a 3rd place. It does not dominate everywhere, so ribbon values stay at the confirmed 40/25/10.
- The margin for an already-capped specialist (grinder) is small in score (+2) because 40 ribbon points about equal three training slots. Money prize (+300) is the real gain, and it matters most to money-tight strategies.
- Not done: festival art (banner, 4 contest scenes, rival portraits, ribbon icon), rival storylines, items. Rival portraits are text-only by default (names only).
