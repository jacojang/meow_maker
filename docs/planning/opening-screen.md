---
status: deployed
updated: 2026-09-16
---

# Opening Screen

## Goal

Replace the current blank `BootScene` with a real title/opening screen: the
game's title, a composited illustration background (the player character
"mom" and the cat "Mimi" over an apartment-complex background), and a
"시작" (Start) button. This is the player's first impression of the game.

## Scope

**In**

- A Phaser scene showing:
  - The game title as text
  - A "시작" button
  - A background illustration composited from the sample assets in
    `docs/design/character_and_background_samples/` (`background_02.png`,
    `mom_of_cats_01.png`, `cat_mimi_01.png`)
- A small dev tool (`tools/asset-gen/`) that calls the OpenAI Images API
  (`gpt-image-1`) to composite the three reference images into one cohesive
  illustration, since no image-generation capability exists in this
  session otherwise (see `docs/development/README.md` for why and how it's
  set up)
- The generated background exported as a real game asset under `web/`

**Out**

- Any behavior when "시작" is pressed — clicking it does nothing yet. That's
  a separate future task once there's a next screen to go to.
- Runtime/in-game image generation — the tool is a one-off dev-time asset
  step, not something the shipped game calls.
- Character creation, name input, or any other pre-game flow.

## Mechanics

- Scene: replaces `BootScene` as the game's initial scene (or is added as a
  new `OpeningScene` set first in the scene list — decided during Coding
  based on what reads more cleanly).
- Background: a single composited illustration image, sized to the game's
  960×600 canvas (see `AGENTS.md`/`web/src/main.js`).
- Title text: rendered with Phaser text (not baked into the background
  image), so it stays crisp and editable.
- Start button: a clickable UI element (Phaser text or a simple rectangle +
  label) with a hover/pressed visual state, but the click handler is a no-op
  for now.

## Open questions

None outstanding — resolved before this doc was written: image generation
via OpenAI's `gpt-image-1` (no AWS Bedrock access on the current AWS
account, and it would need an IAM/model-access change either way), and
`background_02.png` as the base reference for composition.

## Next stage

Background generated via `tools/asset-gen` (OpenAI `gpt-image-1`, composited
from `background_02.png` + `mom_of_cats_01.png` + `cat_mimi_01.png`),
reviewed and approved 2026-09-16 on the second attempt (first draft had too
little sky at the top for the title). Saved as
`web/public/assets/opening-background.jpg`. Design spec written — see
`docs/design/opening-screen.md`.

`BootScene`/`OpeningScene`/`main.js` implemented (coding-agent/review-agent,
PASS on first pass). Testing done: `npm run build` succeeds, a manual
integration check against the real `server/` confirmed `/` returns 200 and
`/assets/opening-background.jpg` is served correctly (200, `image/jpeg`,
541066 bytes), and a real-browser check (Chrome via `npm run dev`) rendered
the scene and exercised the Start button (hover state visible, click
confirmed as a true no-op with no console errors).

The browser check caught a real bug the automated review missed: plain
white "시작" text at 85% down sat directly on the cat's white fur and was
essentially unreadable. Fixed by giving the button a dark semi-transparent
pill background (see `docs/design/opening-screen.md`) and moved to 90%
down; re-verified in the browser after the fix.

Merged to `main` and deployed to the real EC2 instance on 2026-09-16 via
`deploy/deploy.sh`. Confirmed live at `http://54.116.51.0:8000` — verified
both by `curl` (`/` and `/assets/opening-background.jpg` both 200) and by
opening it in an actual browser (title, background and Start button all
render correctly).
