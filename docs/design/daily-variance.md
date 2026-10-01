# Design: live schedule scene

## Reference

[`../planning/daily-variance.md`](../planning/daily-variance.md)

## Visual spec

- Layout: the existing resolution overlay (4:3 panel, 5-frame activity image). Add a result strip and a gauge block.
- Result strip: `N일째 - <one line>`. Color by outcome: fail muted red, normal neutral, great gold.
- Gauges: reuse the stat bar graph component, only for stats the activity changes, ticking by each day's delta.
- Reserved spot (empty until S5): money box top right.
- Assets needed: none. Failed and great days are shown by tint and text on the existing frames.

## Interaction

- Plays automatically, one day at a time, slot by slot. Tap to speed up; a skip button jumps to the month summary.
- The speed choice (normal, fast, skip) is remembered after the first month (`localStorage`).
- Length grows to about 30 day-steps. Keep each step short (about 250 ms) so a month stays near its current duration, and let speed-up shorten it more.

## Handoff notes

- Input is the server's `last_month_log`. Convert it to timed steps in a Phaser-free util (`web/src/utils/`) with a Vitest test.
- Existing `FRAME_SUFFIXES` and `FRAME_PING_PONG` stay as they are.
- Day date labels still come from the client calendar. The day numbers in the log must match; keep the parity test.
