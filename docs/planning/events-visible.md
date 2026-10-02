---
status: review
updated: 2026-10-02
---

# Make events visible (backlog slice S1: A1 + B6 + B3)

Request: Type: new feature. Name: events visible. Part of [`feature-backlog.md`](feature-backlog.md).
Design: [`../design/events-visible.md`](../design/events-visible.md).

## Goal

Random events, the festival and outing results change stats today, but the
player never sees why. Show them, warn before sickness/delinquency, and mark
status on the portrait panel.

## Scope

**In**

- After a month resolves, one result card per thing that happened: event, outing success/failure, festival.
- Advisor warnings (B6), computed on the server and exposed as a state field.
- Status badges (B3) for delinquent and overweight, next to the existing sick badge.
- Small server fix: clear `last_event` and `last_outing_result` at the start of each `advance_month`. `last_festival_winner` keeps its current behavior (see Mechanics).
- `GET /api/events`, mirroring `GET /api/activities`, so the card can show stat chips from data.

**Out**

- Event illustrations (needs asset budget; separate follow-up).
- A real festival (see [`festival-contests.md`](festival-contests.md)). The card here takes a generic payload so that slice only swaps data.
- New events or conditions (backlog A8).
- Warnings that predict the assigned schedule. Current stats only.

## Mechanics

PM2: events are illustrated scenes with a small stat overlay; the butler warns about sickness
(`references/princess-maker-2/characters-and-layout.md`). Here: text card +
existing portrait, no illustration. Departure: no butler character, one advisor line.

**Verified gap**: `last_event`, `last_festival_winner`, `last_outing_result` are
returned by `/api/game` but unread in `web/src`.

**Stale-state fix**: `last_outing_result` is set only when an outing ran and is never cleared, so it would show
again in later months. `advance_month` resets it and `last_event` at the start, then sets them. This changes shipped
behavior for the outing field. Check existing tests (`test_run.py` around the outing cases) for any that rely on the old persistence.
If one does, it is a real behavior change to confirm, not a test to bend.

**`last_festival_winner` (user decision, Round 10)**: not reset in S1; current behavior stays (set in month 10, kept afterwards), because
existing tests depend on it. The client shows the festival card only when the month just processed was the festival month. S6b deletes
the field in favor of persistent `festival_result` and `ribbons` ([`festival-contests.md`](festival-contests.md)).

**Result card**: shown once, from the advance response, after the resolution
animation and before the summary line. On a page reload the card does not
replay; the summary line still names the event. Order: outing, event, festival.
Event chips come from `/api/events`. Copy (names, one-line text) lives in the
client next to the existing activity labels.

**Warnings** (server, field `warnings`, list of codes, in `_state` or a `GameRun` property):

| Code | When |
|---|---|
| `near_sick` | not sick and `health - stress <= SICK_MARGIN` |
| `sick` | is_sick |
| `near_delinquent` | not delinquent and `discipline - stress <= DELINQUENT_MARGIN` |
| `delinquent` | is_delinquent |
| `overweight` | is_overweight |

**Margins (Round 6, checked against `stats.py` and `activities.json`)**: the cat starts at health 50,
discipline 10, stress 0, and one PLAY slot adds 12 stress. A single shared margin of 15 would light
`near_delinquent` on turn 1 (10 <= 15) and never turn off. So the margins are separate, in data:
`SICK_MARGIN` 15, `DELINQUENT_MARGIN` 5. Intended behavior: a fresh run shows no warning on turn 1.
Because one slot can add 12 stress, almost any non-rest first month ends delinquent, so the plain
`delinquent` code (an accurate state, lower severity than sick) appears from month 2. That is correct,
not noise. The start balance itself is a separate issue for the S3/S6a simulation.

**Extensible codes**: `warnings` is an ordered list of code strings with a severity table in data. Unknown
codes are ignored by the client (shown as nothing), so later slices add codes without a client break.
Codes added later: S3 adds `bedridden` and `hospital_risk`
([`sickness-stakes.md`](sickness-stakes.md)); S6a adds `runaway_risk` ([`care-actions.md`](care-actions.md)).
The risk codes fire in the last month the player can still act to avoid the early ending (for S3 that is two months before the ending itself; see [`sickness-stakes.md`](sickness-stakes.md)).

The client maps code to advisor text and shows at most one line, highest severity first. The client
never recomputes thresholds.

**Badges**: sick (exists), delinquent, overweight. From `is_*` fields already in state. Text chips, no art.

**Save compatibility**: no new persisted fields. `warnings` is derived.

**Tests**: pytest for the reset fix, warning codes at the boundary, `/api/events`. Vitest for any card-ordering helper kept Phaser-free (`web/src/utils/`). Phaser wiring is checked by build + browser.

## Open questions

- Advisor name/voice (a named butler cat, or an unnamed tip line)? Default: unnamed tip line.
- Margins 15 and 5 are defaults to tune in playtest. Proposed defaults, user confirmation not needed unless the feel is off.
