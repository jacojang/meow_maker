---
implements: ../planning/opening-screen.md
---

# Opening Screen — Design

## Reference

Implements `docs/planning/opening-screen.md`.

## Visual spec

- **Background**: `web/public/assets/opening-background.jpg` (1536×1024,
  generated via `tools/asset-gen` from the character/background samples,
  approved 2026-09-16). Scaled to **cover** the 960×600 canvas (scale =
  `max(960/1536, 600/1024)` = width-bound, ~0.625), centered — crops ~20px
  off the top and bottom, none off the sides. The image was composed with
  open sky in the top third and clear space in the lower-center specifically
  so text/UI can sit over it.
- **Title text**: "Meow Maker", centered horizontally, near the top of the
  sky area (~15% down from the top). Large, bold, white fill with a dark
  stroke/shadow so it reads over a bright sky.
- **Start button**: text label "시작", centered horizontally, in the lower
  third (~85% down). Rendered as interactive text (not an image) with a
  visible hover state (color change on pointer-over) so it reads as
  clickable. No click behavior yet — this is explicitly a no-op per the
  planning doc's scope.

## Interaction

- Start button: `pointerover`/`pointerout` change its color; `pointerdown`
  does nothing (no scene transition, no console output needed beyond what's
  useful for manual testing).

## Handoff notes

- Load the background in `BootScene.preload()`, transition to a new
  `OpeningScene` in `BootScene.create()`. `OpeningScene` builds the
  background image, title text and start button in its own `create()`.
- No new npm dependencies needed — Phaser's built-in Text and Image game
  objects cover this.
