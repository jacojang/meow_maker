# Design: money HUD and job activity

## Reference

[`../planning/money-economy.md`](../planning/money-economy.md)

## Visual spec

- HUD: a money readout (coin icon plus amount) in the status panel header. Text-only fallback if the icon is missing.
- Picker: seven options now. Each shows its cost (or income). Unaffordable options are dimmed with the price in red. Check the layout still fits the existing activity strip.
- Schedule scene: the money box sits in the spot reserved by [`daily-variance.md`](daily-variance.md). It ticks up on successful job days and down when tuition is charged.

**Asset list (not started)**

| Asset | Count | Notes |
|---|---|---|
| Job scene frames | 5 (`scene-job`, `-b` to `-e`) | Same 640x640 JPEG convention and 5-frame ping-pong as other activities. |
| Coin icon | 1 | Small, optional. |

**Consistency plan**: follow the asset policy in [`../planning/feature-backlog.md`](../planning/feature-backlog.md#asset-generation-policy-applies-to-every-slices-design-doc). Frame A is generated from the existing player-and-cat sheets, frames B to E each from frame A (not chained) with the explicit wide-shot, same-framing prompt. Pilot on the smaller model first and measure against an existing scene such as `scene-train.jpg`. Fallback: no image, the text panel already handles a missing texture.

## Interaction

- Choosing an unaffordable option does nothing and shows a short advisor line.
- The server rejection (HTTP 400) is shown through the existing error message line if it ever reaches the client.

## Handoff notes

- Add `job` to `ACTIVITY_SCENE_IDS` in `BootScene.js` and to the label/color/flavor maps in `GameScene.js`, guarded by `textures.exists`.
- Cost display values come from `/api/activities`, not hardcoded.
