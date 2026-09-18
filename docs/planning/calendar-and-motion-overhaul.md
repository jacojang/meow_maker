---
status: coding
updated: 2026-09-18
---

# Calendar-and-motion overhaul

## Goal

User feedback on the current UI/UX ("정말 맘에 들지 않거든"), four asks:

1. The resolution-animation vignette (`renderResolutionOverlay`) only scale-pulses
   the static scene image. Wanted instead: the character/cat actually move within
   the frame (walk-cycle-like), and the calendar advances a day at a time while
   it plays. Animation getting longer is explicitly fine.
2. The month counter ("1/12개월") should be a real calendar date
   ("2026/01/01") that increments day by day, not an abstract month index.
3. The cat-status portrait panel should have a background that changes with
   the season (winter indoors by a heater, spring in a flowering field, etc.).
4. The "이번 달 일정" schedule should look like an actual calendar grid
   (weekday columns, week rows), per the PM2 reference screenshot the user
   attached, not the current three stacked day-number rows.

## Decisions

- **Fixed calendar year, real month lengths.** A run's 12 months map directly
  onto a fixed year — `state.month` (1-12) is the real month index into
  `2026-01` .. `2026-12`. This is purely a frontend interpretation of the
  existing `month` field; the backend's month-counter mechanic doesn't
  change. `DAYS_PER_MONTH` (currently a flat 30) is replaced by the real
  number of days in that calendar month (28-31), computed via
  `new Date(2026, month, 0).getDate()`. `daySlots(daysPerMonth, slotCount)`
  already handles a variable `daysPerMonth` (the last slot absorbs the
  remainder), so the existing 3-slot mechanic is untouched — slots are just
  10/10/11 in a 31-day month instead of always 10/10/10.
- **Season follows the real month directly**: Dec/Jan/Feb = winter,
  Mar-May = spring, Jun-Aug = summer, Sep-Nov = autumn. No new stat, purely
  derived from `state.month`.
- **New art, confirmed with the user before generating**: 4 seasonal
  backgrounds for the status panel, and 2 extra motion frames per activity
  (3 frames total per activity, ping-ponged during resolution) — including
  outing, which had no scene art yet. 5 existing activities × 2 new frames +
  outing × 3 new frames = 13 activity frames, + 4 season backgrounds = **17
  new images total**, generated via `tools/asset-gen` using the existing
  character/cat reference sheets so style stays consistent. Confirmed with
  the user (chose the higher-cost option for both) before spending.
- **No backend/mechanic changes anywhere in this doc.** Everything is a
  presentation change over data the API already returns.

## Parts, in order

1. **Real calendar dates** — replace the "N/12개월" header with a real date
   (`2026/01/01` format), computed client-side from `state.month` + a day
   counter. Foundation for parts 2 and 4. No new art. **Done** —
   `web/src/utils/gameCalendar.js` (`daysInMonth`/`dateForDay`/`formatDate`/
   `seasonForMonth`, unit-tested); `DAYS_PER_MONTH` constant removed from
   `GameScene.js` in favor of `daysInMonth(this.state.month)` everywhere it
   was used (the calendar picker and the resolution-step builder), so the
   existing 3-slot mechanic now runs against real month lengths (28-31
   days) with no mechanic change — `daySlots`'s existing remainder-folding
   already handles the variable length. Verified live in browser: header
   shows `2026/01/01` on a fresh run and correctly advances to
   `2026/02/01` after a month resolves.
2. **Calendar-grid schedule** — redraw "이번 달 일정" as an actual
   week-row/weekday-column grid (`daySlots` unchanged, new pure util for
   weekday-of-month-start and day→slot lookup), matching the reference
   screenshot's layout. No new art. **Done** —
   `web/src/utils/calendarGrid.js` (`calendarWeeks`, `slotIndexForDay`,
   `WEEKDAY_LABELS`, unit-tested including leading/trailing blank-padding
   and cross-week slot boundaries) plus `GameScene.js`'s `renderCalendar`
   split into `renderCalendarLegend` (the three slot/activity chips,
   replacing the old per-row label), `renderCalendarWeekdayHeader`, and
   `renderCalendarGrid` (the actual 7-column day grid, colored and
   clickable per day exactly like the old per-row cells were). Verified
   live: January renders 5 rows starting on Thursday (correct weekday for
   2026-01-01), February renders 4 rows starting on Sunday with 28 days
   and no padding, and clicking a day / legend chip still focuses the
   right slot and recolors only that slot's days, including across a
   week-row boundary (e.g. an 11-20 slot spanning two grid rows). Merged
   (#36) and deployed to production; re-verified live at
   `http://54.116.51.0:8000` after deploy.
3. **Seasonal status backgrounds** — 4 new illustrations, one per season,
   behind the existing cat portrait in the status panel. Needs asset-gen.
   **Done** — 4 illustrations generated via `tools/asset-gen`
   (`web/public/assets/seasons/season-{winter,spring,summer,autumn}.jpg`),
   plain/minimal compositions (no characters) matching the existing
   portrait art's flat style, so they don't compete visually with the cat
   in the small status panel. `BootScene.js` preloads them
   (`season-<id>`); `GameScene.js`'s `renderPortrait()` draws the season
   image (picked via `seasonForMonth(this.state.month)`, already written
   and tested in part 1) as a cover-fit background clipped to the status
   panel's content area with a geometry mask, then draws the existing cat
   portrait on top unchanged — the cat image only fills part of the area
   (contain-fit), so the season art is visible in the margins around it.
   No new mechanic, no new tests (pure wiring over an already-tested
   function); verified live in browser for winter and spring, including
   alongside the sick-cat portrait variant and the stress badge, with no
   layout regression.
4. **Day-by-day motion animation** — the resolution vignette steps through
   each day in the activity's range (ticking the header date once per day)
   while ping-ponging between that activity's 3 motion frames, instead of
   one static image for the whole slot. Needs asset-gen (13 frames) and the
   biggest animation-loop rework of the four.

## Why this order

Parts 1 and 2 are pure frontend date/layout math, no art, and part 2 depends
on part 1's real month-length dates for a correct weekday grid. Parts 3 and
4 both need new art and are independent of each other, but 4 also reuses
part 1's per-day date-ticking, so it's last.

## Open questions

None on mechanism. Exact prompts/reference images for the 17 new
illustrations will be drafted immediately before each asset-gen part and
shown before running, per the tool's own "check the prompt before running"
guidance.
