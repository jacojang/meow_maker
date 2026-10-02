---
status: planning
updated: 2026-10-02
---

# Feature backlog (post-v1, vs PM2)

## Goal

Agree on what to build next and in what order. This is a list, not a spec.
Each item that gets picked up becomes its own `docs/planning/<slug>.md`
(and a `docs/design/` doc if it needs UI/art).

Source: critic-agent round 0 report, answered item by item below. PM2
parallels come from `references/princess-maker-2/` (raising-system,
status-system, mini-games, characters-and-layout, endings).

## Scope

**In**: a prioritized backlog (21 items), dependencies, risks, slice
proposal, open questions.

**Out**: per-feature mechanics, numbers, UI layouts, art. No code, no data
changes. Not changed: 12-month run, server-authoritative rules, minimal
outing scope, no PM2-size ending catalog, no bespoke ending art.

## Verified facts (checked against code)

| Claim | Result |
|---|---|
| `last_event`, `last_festival_winner`, `last_outing_result` unread in `web/src` | True. grep matches only `server/app/game/run.py`. The state API already exposes them (`run.py` `to_dict`). |
| No camera/audio calls in the scene | True. No `cameras`, `fade`, `shake`, `flash`, `sound`, `audio` in `web/src`. |
| Sick = stress > health, delinquent = stress > discipline | True (`stats.py`). Stress is the single lever for both. Matters for A3/A4 balance. |
| Delinquency is only -1 discipline | True (`delinquency.py`). |
| Ending = argmax of 5 stats, sick/delinquent override | True (`endings.py`). Sick check uses month-12 state only. |
| "3 days per slot" (A5) | Wrong. The calendar uses real month lengths, so a slot is about 10 days (`daySlots(30, 3)` = 10/10/10). Per-day rolls mean ~10 per slot. |
| Schema blocker for new fields | None. Run state is one `state_json` blob (`db.py`). New `GameRun` fields read with `.get()` defaults need no schema change. |

Note: `events-and-festival.md` and `outings.md` list money as "Out". A2
reverses that scope on purpose, so those docs stay as history.

## Decisions on the critic's points

| # | Item | Decision | Reason |
|---|---|---|---|
| A1 | Events/festival/outing invisible | adopt | Verified. Data already exists server-side. Cheapest high-value fix. |
| A2 | Money economy | adopt | Round 4: plain money (not cat-themed). Income = part-time job + festival prizes. Spec: `money-economy.md`. |
| A3 | Care actions + delinquency recovery | adapt | Adopt. Needs A2 for cost. Split: free "pet" action first is possible, paid actions after A2. |
| A4 | Sickness stakes | adapt | Round 4: no death; non-fatal early bad endings approved. Sick counters, forced rest, ending/score cost. Spec: `sickness-stakes.md`. |
| A5 | Per-day variance | adapt | Adopt. Fix: ~10 days per slot, not 3. Round 4: visibly swingy is fine. Numbers re-tuned after S5. Spec: `daily-variance.md`. |
| A6 | Richer endings | adapt | Adopt as data-level rules: balanced ending, top-two combo, score penalties. Keep the 7 base endings. Move earlier than critic's order (cheap, no deps). |
| A7 | Real festival | adopt | Round 4: festival month replaces the slots (PM2). Money prizes + ribbon. Spec: `festival-contests.md`. |
| A8 | Conditional events | adopt | Data-driven conditions in events data. Include season as a condition (absorbs most of A12). |
| A9 | Mentor visits | adapt | Adopt, merged with A10 into one "mastery" slice (shared session counters). Needs A1 popup. |
| A10 | Class levels | adapt | Adopt. Payoff growth works without A2. Cost scaling needs A2. |
| A11 | Starting variation | adapt | Round 4: breed is fixed and must not change. Vary birth month (stat offsets) and cat name only. New start screen approved. Spec at S7 time. |
| A12 | Seasonal rules, vacation slot | adapt | Season-keyed events folded into A8. Vacation slot deferred until A2 exists. |
| A13 | Age gating | adapt | Adopt for events only first. Do not gate OUTING: that changes shipped behavior and the schedule UI. |
| A14 | Fortune teller | adapt | Adopt as an event (free) first. Paid version after A2. Low priority. |
| B1 | Live schedule scene | adopt | Depends on A5. |
| B2 | Event illustration scene | adapt | Text card + portrait ships inside A1. Illustrations are a separate, cost-gated item. |
| B3 | Status badges/portraits | adapt | Adopt badge (delinquent, overweight) now. Delinquent portrait deferred (asset cost). |
| B4 | Ending sequence | adopt | Stepwise reveal, no new art. Pairs with A6. |
| B5 | Month transition/growth card | adapt | Adopt a simple fade and an age-stage growth card. Low. |
| B6 | Advisor warnings | adapt | One-line warnings. Round 3: server computes them and exposes a field, so S1 is not frontend-only. |
| B7 | Audio | defer | Round 9: SFX removed from the priority list. Deferred (see Deferred section). No music, ever, per Round 4. |

Acceptable divergences (errantry map/combat, jobs, shops, equipment,
marriage): agreed, no action. Jobs revisit only if A2 ships and feels thin.

## Backlog

Cost: S = days, M = about a week, L = multi-week. Touch points are the
current files the change would hit.

### Tier 1: core loop

| ID | Item | Plugs in at | Depends on | Risk | Cost |
|---|---|---|---|---|---|
| A1 | Show events, festival, outing result | `GameScene.js` after resolution overlay; reads existing `last_*` | none | Frontend only. No rules change. | S |
| B6 | Advisor warnings | server computes warnings (new additive `warnings` field in state); `GameScene.js` message line shows them | none | Single source of rules on the server. Small API addition. | S |
| B3 | Status badges | `GameScene.js` near existing sick badge (line ~324) | none | None. | S |
| A6 | Build-aware endings + score | `endings.py`, a data table for combos | none | Score range 0-1000 clamp. Ending test table grows. Old runs unaffected (ending computed at finish). | S |
| B4 | Ending reveal sequence | `GameScene.js` finish panel (~735-765) | A6 for new text | Frontend only. | S |
| A4 | Sickness stakes | `run.py`, `stats.py` or new module; counters on `GameRun`; `endings.py` | none; B3 bedridden cue ships with it | Stress is the lever for sick AND delinquent. Easy to over-punish. Playtest. Save compat via `.get()` default. | M |
| A5 | Per-day variance | `activities.py`, `run.py`; injected `Random` (existing pattern) | none | Balance: keep expected value. Existing tests assume deterministic deltas; `NeverRng` pattern already exists. API response grows (additive). | M |
| B1 | Live schedule scene | `GameScene.js` 639-694; consumes per-day results | A5 | Frontend must not invent results. | M |

### Tier 2: economy

| ID | Item | Plugs in at | Depends on | Risk | Cost |
|---|---|---|---|---|---|
| A2 | Money economy | new field on `GameRun`; costs/income in JSON data files; HUD | none (blocks A3 paid, A7 prizes, A10 cost, A12, A14 paid) | Biggest balance change: every activity gets a price. Needs one earning path. No schema change (JSON blob). | L |
| A3 | Care actions (pet / treat / scold) | pre-schedule step beside diet; `delinquency.py` | A2 (paid parts) | Once-per-month cap server-side. "Scold" must be risky when not delinquent. Reuses affection as bond stat, so no new stat. | M |
| A7 | Harvest contests | `festival.py`; festival screen reuses A1 display | A1, A2 | Rival strength and prize values need tuning. Festival month rule (suspend slots) changes month flow. Ask before. | L |

### Tier 3: depth

| ID | Item | Plugs in at | Depends on | Risk | Cost |
|---|---|---|---|---|---|
| A8 | Conditional events (incl. season) | `events.py`, events data file | A1 | Condition schema must be validated at load (existing loader pattern in `content.py`). | M |
| A9 | Mentor visits | session counters on `GameRun`; event | A1 | Thresholds scaled to 36 slots (about 3/6/10), not PM2's 5/10/20/40. Rewards are stat grants, balance with A10. | M |
| A10 | Activity levels | `activities.py` lookup by session count | A9 counters; A2 for cost | Level thresholds about 3/6/10 sessions. Total growth must keep the score under the 1000 cap. | M |
| A11 | Starting variation + cat naming | `GameRun` constructor, new-game route, web start flow | none | Needs UI. Offsets must keep all starts viable. Name is a new string on `GameRun` (`.get()` default); validate length/characters on the server. | M |

### Tier 4: flavor

| ID | Item | Plugs in at | Depends on | Risk | Cost |
|---|---|---|---|---|---|
| A13 | Age-gated events | event conditions (A8) | A8 | Low. | S |
| A14 | Fortune teller | event + `determine_ending` | A1 (paid: A2) | Preview must use the same function as the final ending. | S |
| B5 | Fade + growth card | `GameScene.js` | none | Low. | S |
| B7 | SFX (deferred) | new audio loader in `BootScene.js` | user decision to revive | Asset license/cost, autoplay policy. | M |
| B2+ | Event illustrations | art | A1 | Real asset-gen cost. | M |
| A12 | Vacation slot | schedule options | A2 | Adds a 7th option to the picker UI. | M |

## Priority order and reasons

1. **A1 (+B6, B3)**: step 4 of the loop is invisible today. No rules change, uses data the server already sends. Highest value per cost.
2. **A6 (+B4)**: pure data and text. No dependencies. Makes the 12-month goal meaningful. Critic ranked it 7th. Moved up because it is cheap and independent.
3. **A4**: gives stress real stakes. No economy needed.
4. **A5 then B1**: variance and the animation that shows it. A5 first because B1 needs real per-day data.
5. **A2 then A3, A7**: economy is the biggest change and most blocked on user answers, so it comes after the no-input work. It unblocks the most items.
6. **A8, A9/A10, A11**: depth once the core loop is solid.
7. **Flavor tier**: A13, A14, B5, illustrations, vacation. (B7 deferred.)

Differences from the critic's order (A1, A4, A5, A2, A3, B1, A6, A7):
A6 up (cheap), A2 after A4/A5/B1 (needs user input, large), B1 stays right
after A5.

## Slice proposal

Each slice is shippable alone and gets one planning doc when picked up.

| Slice | Contents | Backend | Frontend |
|---|---|---|---|
| S1 Make it visible (`events-visible.md`) | A1, B6, B3 | small (B6 `warnings` field) | yes |
| S2 Meaningful endings (`endings-by-build.md`) | A6, B4 | yes (data + rules) | yes |
| S3 Sickness stakes (`sickness-stakes.md`) | A4 (HOSPITALIZED only), B3 bedridden cue | yes | small (portrait/badge) |
| S4 Variance + live scene (`daily-variance.md`) | A5, B1 | yes | yes |
| S5 Economy (`money-economy.md`) | A2, part-time job | yes | yes (HUD) |
| S6a Care actions (`care-actions.md`) | A3 + RAN_AWAY ending | yes | yes |
| S6b Festival contests (`festival-contests.md`) | A7 | yes | yes |
| S7 Depth | A8, A9, A10, A11 | yes | small |
| S8 Flavor | A13, A14, B5, A12 | mixed | mixed |

S6 is split into two docs (one change per doc). S6a and S6b both need S5 and are independent of each other.

S1 and S2 can run in parallel (different files). S3 before S4 so variance
is tuned on top of the final sickness rules.

S4 note: A5 numbers get re-tuned after S5 (economy) lands. B1's UI has
no dependency on S5. S5 may also move before S4's tuning if the user
answers the money questions early.

## Cross-cutting rules for every item

- Rules live on the server. The client shows, never decides (B6 warnings read API fields).
- New state goes on `GameRun` with `.get()` defaults. No `db.py` change is planned for any item. If one is needed, it must be additive.
- Numbers go in JSON data files, per Phase 3.
- Randomness uses the injected `Random`. Tests use `NeverRng` or a seeded one.
- Every item needs a PM2 note in its own doc.

## Round 3 additions (critic, non-blocking)

| # | Point | Decision | Result |
|---|---|---|---|
| 1a | A4 cost only checks month 12 | adopt | Track consecutive and total sick months on `GameRun`. Both feed ending choice and score. A cat sick 11 months then healed still pays. |
| 1b | Forced rest must take slots | adopt | Server overwrites slots with REST when severe (not a message). Defines the player-visible rule in the A4 doc. |
| 1c | Non-fatal alternative to death | adopt | Offer as data-level options: hospitalized run end, ran-away ending. User picks (Open questions). |
| 1d | Bedridden needs a visual cue | adopt | B3 bedridden badge ships with A4 in S3. Bedridden portrait is cost-gated. |
| 2 | Send A2/festival questions now | adopt | Done. Answered in Round 4. |
| 3 | A5 retune after economy; free pet monthly | adopt | One line added to S4. A3 free pet limited to once per month, server-enforced, so stress is not neutralized. Slice order unchanged. |
| 4 | A9/A10 thresholds | adopt | Scale to about 3/6/10 sessions (36 slots). Keep total growth under the 1000 score cap. |
| 5 | B6 logic location | adapt | Chose server-computed `warnings` field (single rule source) over a mirrored client util. S1 backend corrected to "small". |
| 6a | A11 cat naming | adopt | Name entry added to the new-game screen with A11. |
| 6b | Festival replaces slots (PM2) | adapt | User confirmed in Round 4. |

## Round 4: user answers (resolved)

| # | Topic | Answer | Effect |
|---|---|---|---|
| 1 | Money (A2) | Plain money. Income: part-time job like PM2, plus festival prizes. | `money-economy.md`. No allowance, no cat-themed currency. |
| 2 | Festival (A7) | Festival month replaces the month's slots (PM2 way). | `festival-contests.md`. Includes PM2's "skip" (see its open questions). |
| 3 | Sickness (A4) | No death. Non-fatal early bad endings are wanted. | `sickness-stakes.md`. |
| 4 | Difficulty | A neglected run may fail hard. | Penalties in S3/S2 can be severe. Score floor stays 0. |
| 5 | Variance (A5) | Visibly swingy is fine. | `daily-variance.md`. |
| 6 | Assets | Generation allowed, but switch asset-gen to a smaller model. Character/scene consistency must hold. | Asset policy below. Nothing is generated until the user confirms each batch. |
| 7 | Audio | SFX only. | Superseded by Round 9: B7 deferred. The on-by-default-after-first-click proposal is kept below for when it is revived. |
| 8 | Replay (A11) | New start screen OK. Breed fixed. Birth month and name may vary. | A11 row updated. |

## Asset generation policy (applies to every slice's design doc)

- Nothing here runs `tools/asset-gen`. Each batch needs user confirmation with the prompt shown first (AGENTS.md).
- **Model (confirmed, Round 9)**: `gpt-image-1-mini` at `--quality medium`. Checked in `tools/asset-gen/generate_image.py`: `--model` is a free-form string (no `choices`), and `--quality` accepts `medium` (`VALID_QUALITIES` includes it). So every batch passes `--model gpt-image-1-mini --quality medium` explicitly. The tool's `--model` default is now `gpt-image-1-mini` (`--quality` stays `low`, so batches still pass `--quality medium`). A one-image test (no refs, 1024x1024, medium) succeeded on 2026-10-02; the edit endpoint with references is not yet verified. The pilot also confirms that the account can use this model and that the other flags the tool sends (size, background) are accepted by it. The tool is never run without user confirmation of each batch.
- **Why consistency is at risk**: `calendar-and-motion-overhaul.md` records zoom drift when frames were chained frame-to-frame, and one outlier (`scene-outing-d`) that was only fixed after changing both model and reference. The model-vs-reference cause was never separated.
- **Consistency method (carry over, proven there)**:
  1. Pilot first: one image per asset class on the new model, compared against an existing shipped asset. Go/no-go before any batch.
  2. Generate every variant from one fixed anchor image, never chained from the previous output.
  3. Prompt with the explicit framing lines used before ("WIDE SHOT, NOT a close-up", same margins, full figure, only change X).
  4. Existing cat sheets and `web/public/assets/cats/*.png` are the identity refs. Breed is fixed, so no new breed refs are introduced.
  5. Output follows the existing convention (640x640 JPEG for scenes, PNG for cat portraits).
  6. Verify with the bounding-box measurement plus eyeballing. Neither alone is enough (the earlier doc shows both failure modes).
  7. If the smaller model fails the pilot, report it. Don't silently fall back to a costlier model.
- Every slice is text-first. Art is additive and the game must work with `this.textures.exists()` fallbacks, as it does today.

## Round 6: critic review of slice docs

Facts checked in code: start stats discipline 10, stress 0, health 50 (`stats.py`); PLAY stress +12 (`activities.json`); delinquent = stress > discipline.
So one non-rest slot makes a fresh cat delinquent, and a shared warning margin of 15 would light on turn 1. Critic's P1 is correct.

| # | Point | Decision | Result |
|---|---|---|---|
| P1 | Runaway too easy; warning noise | adopt | RAN_AWAY moved from S3 to S6a. S1 margins split (sick 15, delinquent 5), quiet on turn 1. |
| P2 | S4 multiplier vs S5 job rule conflict | adopt | Job stat effects exempt from the multiplier. Only pay uses the outcome. |
| P3 | S5 not codable | adopt | Default job named (쥐잡이 알바), trade, income and sick rule written. User may rename. |
| P4 | Money may not be tight | adopt | Simulation acceptance in S5. If loose, raise costs, no shops. Money-in-score is conditional on it. |
| P5 | Skip beats entering | adopt (option 1) | Ribbons add to score by rank (1st +75, 2nd +60, 3rd +50; retuned from 40/25/10 after S6b review, user decision). Skip still allowed. |
| minor | Negative deltas multiplied | adopt | Multiplier applies to positive deltas only. |
| minor | `last_festival_winner` conflict | adopt | Round 10 (user): not reset in S1, current behavior kept. Client shows the festival card only for the festival month. Deleted in S6b in favor of persistent `festival_result` and `ribbons`. |
| minor | Warnings lack S3 codes | adopt | Extensible code list. S3 adds `bedridden`, `hospital_risk`. S6a adds `runaway_risk`. |
| minor | Cumulative vs consecutive bedridden | adapt | Kept cumulative on purpose (forced rest cures in a month). Difference from PM2 now stated in S3. |
| minor | Forced rest may be too soft | adopt | S3 simulation acceptance, with a lever (lower limit or weaker REST). |
| minor | 7.5 s per month playback | adopt | Remember speed choice after month 1 (S4 design). |
| minor | Numbers wait on simulation | adopt | Shared simulation harness is a named deliverable of S2, reused by S3 to S6b. |

## Round 9: user answers (resolved)

| # | Topic | Answer | Effect |
|---|---|---|---|
| 1 | Image model | `gpt-image-1-mini`, `--quality medium` | Asset policy updated. Flags verified in the tool. |
| 2 | Part-time job | 쥐잡이 알바 as proposed | Confirmed in `money-economy.md`. |
| 3 | Ribbon score | 1st +75, 2nd +60, 3rd +50 | Retuned from 40/25/10 after S6b review so balanced builds gain from entering (user decision). See `festival-contests.md`. |
| 4 | Festival skip | Allowed | Confirmed in `festival-contests.md`. |
| 5 | Care actions | One per month in total | Confirmed in `care-actions.md`. |
| 6 | SFX | Removed from priorities | B7 deferred. S8 no longer includes it. |
| 7 | Leftover money in score | No | Stays conditional on the S5 simulation checks. |

## Deferred

- **B7 audio (SFX)**: not planned. If revived: SFX only, no music. Proposal at that time: on after the first click with a persistent mute toggle (autoplay-safe). Questions to answer then: SFX source and license (generated, CC0 pack, or commissioned) and which events get a sound. No other doc mentions sound beyond this item.

## Open questions

None for the user. All earlier global questions are resolved above.

What remains is settled during design and coding, not by the user:

- Numbers set by the shared simulation: S2 gaps, S3 limits, S6a runaway streak, S5 costs, S4 weights.
- Copy and names to draft at design time and review then: pair-ending labels, contest and rival names, advisor lines.
- Per-slice defaults noted in each doc (for example hospitalized ending as text only).
- Art is optional and additive. Any asset batch still needs a user go-ahead with the prompt shown.
