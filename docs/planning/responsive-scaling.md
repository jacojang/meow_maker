---
status: testing
updated: 2026-09-17
---

# Responsive Scaling + Fullscreen

## Goal

The game was pinned to a fixed 960×600 canvas regardless of window size —
no scaling, no fullscreen. Make it fill the browser window (letterboxed,
aspect-preserved) and offer a fullscreen toggle.

## Scope

**In**

- Phaser's `Scale.FIT` mode: the 960×600 logical canvas scales up/down to
  fit the browser window, centered, preserving aspect ratio (letterboxed
  bars on mismatched aspects rather than stretching or cropping).
- A small fullscreen toggle button (bottom-right corner, both interactive
  scenes) using Phaser's built-in Fullscreen API wrapper
  (`scale.toggleFullscreen()`).
- Minimal page CSS so the `#game` container and canvas actually fill the
  viewport instead of sitting in a default-margined `<body>`.

**Out**

- `Scale.RESIZE` (filling the window exactly, ignoring aspect ratio) — every
  panel in `GameScene` is laid out in fixed 960×600 pixel coordinates, so
  that mode would need the whole layout rebuilt to be ratio-aware. FIT
  keeps all existing layout code unchanged.
- Any mobile/touch-specific handling beyond what FIT and the button give
  for free.

## Mechanics

- `web/src/main.js`: `scale: { mode: Phaser.Scale.FIT, autoCenter:
  Phaser.Scale.CENTER_BOTH }`, plus `backgroundColor` so the letterbox bars
  match the page background rather than flashing white.
- `web/src/style.css` (new): zero margin on `html`/`body`, both at 100%
  width/height, dark background matching the game so letterboxing is
  invisible against the page.
- `web/src/scenes/fullscreenButton.js` (new): `addFullscreenButton(scene)`,
  a small circular button drawn directly on the scene (outside any
  re-rendered container, so it survives `OpeningScene`'s and `GameScene`'s
  redraw cycles without being recreated). No-ops if
  `scene.scale.fullscreen.available` is false.
- Button position (bottom-right, both scenes) was chosen to clear existing
  UI: `OpeningScene`'s Start button is bottom-center, `GameScene`'s content
  panels end above the button's row — checked by reading actual layout
  constants, not by eyeballing a screenshot.

## Open questions

None — direction confirmed with the user (FIT over RESIZE, given the
layout-rebuild cost of RESIZE isn't justified yet).

## Next stage

No Design pass — mechanical scaling change, no new visual content.

Testing: `npm run build`, then a real browser check at a non-960×600
window size to confirm letterboxing and button placement. The fullscreen
toggle itself couldn't be verified end-to-end in this session's browser
automation sandbox — `requestFullscreen()` is rejected there
("Permissions check failed") independent of any of this code, confirmed by
calling it directly from the page console. Needs a manual check in an
ordinary browser tab before calling this fully verified.
