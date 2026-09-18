---
status: deployed
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
   layout regression. Merged (#38) and deployed to production; re-verified
   live at `http://54.116.51.0:8000` after deploy.
4. **Day-by-day motion animation** — the resolution vignette steps through
   each day in the activity's range (ticking the header date once per day)
   while ping-ponging between that activity's 3 motion frames, instead of
   one static image for the whole slot. Needs asset-gen (13 frames) and the
   biggest animation-loop rework of the four. **Done** — 13 new frames
   generated via `tools/asset-gen` (2 extra poses for each of the 5
   existing activities, reusing their existing frame as pose A; a full new
   3-pose set for outing, which had no art yet), resized/recompressed to
   the same 640x640/~100KB convention as every other scene image (learned
   from part 3's review). `resolutionSteps.js` now carries each activity
   step's real `days` array (from the existing `daySlots` ranges) so
   playback can iterate real days — one new field, existing pure-function
   contract, test updated accordingly. `GameScene.js`'s
   `playResolutionAnimation()` now loops each activity step's real days
   (`RESOLUTION_DAY_MS` = 200ms/day) instead of holding one static frame
   for `RESOLUTION_STEP_MS`; each day picks a frame via a 4-value
   ping-pong pattern (`[0,1,2,1]`) mapped to `scene-<id>`, `scene-<id>-b`,
   `scene-<id>-c`. The old scale-pulse tween is gone — replaced entirely
   by the frame swap, per the user's explicit ask (movement, not
   resizing). The header (`renderHeader`) shows the real ticking date
   during animation via a new `this.animationDay`, falling back to day 1
   (in progress) or the month's last day (finished) otherwise — same
   `dateForDay`/`formatDate` from part 1. The diet step (no day range)
   keeps its original single-frame hold, unchanged. `BootScene.js`
   preloads all 3 frames for all 6 activities (fixing a pre-existing gap
   where `outing` wasn't in the preload list at all, from before it had
   any art). Verified live end-to-end: an outing month's resolution shows
   the header ticking `2026/01/01` → `2026/01/16` day by day, the cat/girl
   pose visibly cycling frame-to-frame, correctly lands on `2026/02/01`
   after the month completes, and the resulting stats match the outing
   success-roll math exactly as before.

## Follow-up: transparent cat portraits (fixing part 3's regression)

Part 3 shipped the cat portrait layered over a season background, but the
cat portrait JPGs each had their own solid beige backdrop baked in (JPG has
no alpha channel) — so every season showed a visible rectangular "frame"
around the cat where its own flat background clashed with the season art
behind it. Confirmed with the user this needed fixing, and that regenerating
all 12 portraits with a real transparent background (rather than reverting
part 3) was worth the extra asset-gen cost.

Fix: `tools/asset-gen/generate_image.py` gained a `--background` flag
(`auto`/`opaque`/`transparent`, passed straight through to the OpenAI
Images API's own `background` parameter on both `images.edit` and
`images.generate`) — a small, reusable capability addition, not
one-off scope creep. All 12 existing portraits (`web/public/assets/cats/`)
were regenerated from their old JPGs as `--ref`, prompted to keep the exact
same cat/pose/style but with `--background transparent`, output as PNG
(verified with Pillow that every file has a real 0-255 alpha range, not a
baked-in checkerboard or solid color), resized to the same 640x640
convention, and the old opaque JPGs deleted. `BootScene.js`'s loader
extension changed from `.jpg` to `.png` for the `cat-*` keys; no other code
changed — `renderPortrait()`'s compositing logic was already correct, it
just needed real transparency to composite against. File sizes landed at
~325-425KB each (vs. ~90-110KB for the old JPGs) — expected and accepted,
since lossless PNG-with-alpha is a genuinely different format requirement,
not the same bloat problem as parts 3/4's oversized JPGs. Verified live:
the fireplace's silhouette is now visible right up to the cat's edge in
winter, and the sick-portrait variant also composites cleanly over spring.
Merged (#40) and deployed to production; re-verified live at
`http://54.116.51.0:8000` after deploy.

## Follow-up: season-background aspect ratio and portrait scale

Once live, the user flagged a second visual issue with the seasonal
backgrounds: the season art was generated square (1024x1024, later resized
to 640x640), but the status panel's content area is a wide short rectangle
(~408x156, aspect ratio ~2.6:1). `coverScale` scales a square image up
until it fills both dimensions, so at that aspect ratio it zoomed in
heavily and only a thin horizontal sliver of each square scene was ever
visible.

Fix: regenerated all 4 season backgrounds at `1536x1024` (the widest size
`tools/asset-gen` supports) with prompts explicitly asking for a "wide
panoramic banner" composition with key motifs kept inside a shallow
horizontal band, then cropped each to `1536x587` (matching the panel's
~2.6:1 aspect almost exactly) via `sips -c 587 1536` before the usual
640-wide resize. Result: 640x244 files, 28-45KB each — smaller than
before despite looking better, since the wide-short crop simply has far
fewer total pixels than a 640x640 square. No code change was needed for
this part; `renderPortrait()`'s existing `coverScale`-based compositing
already does the right thing once the source image's aspect ratio roughly
matches the target area.

Separately, the user asked for the cat portrait itself to be a little
smaller so it reads less like a flat cutout pasted onto the (now much more
detailed) background. Added a `PORTRAIT_SCALE = 0.8` constant in
`GameScene.js`, applied as a multiplier on top of the existing contain-fit
scale in `renderPortrait()` — the only code change in this follow-up.
Verified live: winter's full room (fireplace, armchairs, lamp, curtain)
and spring's blossom-branch-and-field composition are both now visible in
full within the panel, with the smaller cat sitting naturally inside the
scene instead of dominating a heavily-cropped square. Merged (#42) and
deployed to production; re-verified live at `http://54.116.51.0:8000`
after deploy.

## Follow-up: ground-anchor the cat portrait

Fixing the aspect ratio (previous follow-up) made the backgrounds much
richer, but it surfaced a third issue: the cat portrait was still
vertically centered in the content area regardless of where each
background's actual floor/ground line sits, so the cat visually floated
disconnected from the scene — unlike `opening-background.jpg`, where the
character and cat are composited standing on the ground.

Fix, in `GameScene.js`'s `renderPortrait()`: instead of centering the cat
image vertically, it's now anchored to the bottom of the content area — a
new `PORTRAIT_GROUND_MARGIN = 6` constant, with `image.setOrigin(0.5, 1)`
and its Y position set to `areaTop + areaHeight - PORTRAIT_GROUND_MARGIN`
(horizontal centering unchanged). This isn't pixel-perfect floor alignment
per season (each of the 4 backgrounds has its ground line at a different
height — winter's floor is near the very bottom, spring's grass starts
partway up), but bottom-anchoring reads as "standing on the ground" for
all of them, since every background has visible ground/floor in its lower
portion. No background art changed, no per-season code branching — a
single shared anchor rule. Verified live: winter's cat now sits directly
in front of the fireplace at floor level; spring's cat sits in the grass
with blossom branches framing above — both read as grounded in the scene
instead of floating in a dead-center box. Merged (#44) and deployed to
production; re-verified live at `http://54.116.51.0:8000` after deploy.

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
