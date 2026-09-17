---
status: deployed
updated: 2026-09-17
---

# UI/UX Overhaul

Umbrella doc for a batch of UI/UX work requested against `docs/design/screenshot/main_screen_01.gif` and `main_screen_02.gif` (actual PM2 PC gameplay footage), before Roadmap Phase 2. Same role as `roadmap.md`: this is the map: each part below ships as its own PR, in order.

## Decisions (apply to every part below)

- **Age becomes a real stat**, separate from the month counter — not derived from `month`. Lives in `server/app/game/`, same pattern as Refinement.
- **Weight becomes a real stat with a diet mechanic**, not a proxy off an existing stat — matching PM2's actual system (diet choice moves weight, weight affects appearance).
- **Portrait art**: 12 combinations (3 age stages × 2 health conditions × 2 weight conditions), generated via `tools/asset-gen`. Confirmed with the user before spending on generation.

## Parts, in order

1. **Stat bar graphs** — numbers plus a filled bar per stat in the 능력치 panel, matching the reference's red/blue bar style (simplified to one accent color: green for most stats, red for stress). No new mechanics. **Done** — see commit on `feature/stat-bar-graphs`.

2. **Stateful cat portrait** — age + weight stats and a diet mechanic (server), 12 portrait images (asset-gen), and a central portrait in `GameScene` that picks the right image from current age/health/weight. Biggest part: new mechanics *and* new art. **Done** (2a and 2b both merged and deployed) — see `docs/planning/stateful-portrait.md`.

3. **Calendar-based scheduling** — replace the 3 button-list slot pickers with a calendar-grid UI for assigning the month's activities, per the reference's month-view calendar. **Done** — merged and deployed. Implementation note: Meow Maker's 3-slot mechanic didn't change — the calendar renders the month as 30 days (a constant, independent of real calendar dates) split into 3 equal 10-day ranges, one per existing slot, each row tinted by its assigned activity and clickable to focus it; an activity-choice strip below assigns the focused range. Day-level granularity is purely visual, not a new mechanic. Pure range math extracted to `web/src/utils/calendar.js` (`daySlots`) per AGENTS.md's testable-logic convention.

4. **Action-in-progress animation** — a small animated vignette shown while an activity resolves, per `main_screen_02.gif`'s daycare-scene example. **Done** — merged and deployed. Implementation note: the backend already resolves the whole month in one call (no per-day intermediate state to stream), so this is a purely client-side, post-hoc playback — after `advance_month` returns, the client steps through each of the 3 activity ranges plus the diet choice in turn, holding on a colored vignette with the activity's flavor line and nominal stat effects for `RESOLUTION_STEP_MS` (700ms) each, before revealing the real updated stats/portrait/last-month-summary together at the end. No new mechanics, no backend changes. The step-sequencing logic (day-range/pick pairing, diet-step append) is a pure function in `web/src/utils/resolutionSteps.js`, unit-tested per AGENTS.md's convention; presentation lookups (label/flavor/color) stay in `GameScene.js`. The animation timing deliberately uses a plain `setTimeout`, not Phaser's `Clock`/`delayedCall` — this is a one-shot cosmetic reveal after the real result is already fetched, not a live gameplay timer, so it shouldn't hang if the tab loses rendering focus mid-playback. Verified live end-to-end in a browser: all 4 steps play in order and the final reveal matches the expected stat math exactly.

**Follow-up**: the vignette originally showed only the cat portrait (age/health/weight state) during resolution. The user asked for something closer to PM2's schedule-execution scene, where the character is shown actually doing the activity, not just an icon. Generated 5 new illustrations via `tools/asset-gen` (one per activity: 놀아주기/훈련/단장/휴식/교육, `web/public/assets/scenes/scene-<activity>.jpg`), each showing the player character and cat performing that activity together, in the same style as the existing character/cat reference sheets. The activity steps now show the matching scene image (with the same brief scale tween as before); the diet step still shows the cat portrait, since PM2 doesn't treat diet as its own visual scene either.

## Why this order

Cheapest/lowest-risk first (bars: no new mechanics, no new art). Portrait next because it's the biggest lift and the most central to "make state visible," which was the throughline of the user's ask. Calendar and animation are UI-interaction changes that don't depend on the portrait work and can follow independently.

## Next stage

Straight to Coding per part — no separate Design doc; each part's doc note above (and any follow-up planning note for parts 2-4) carries the visual spec inline since it's a direct translation of the reference GIFs.
