# Design: festival screen

## Reference

[`../planning/festival-contests.md`](../planning/festival-contests.md)

## Visual spec

- Month 10 picker is replaced by a contest list: four rows (name, keyed stat with current value) plus a "불참" row. No slot calendar for an entered month.
- Result: the generic result card from [`events-visible.md`](../planning/events-visible.md) with a rank line, the rival scores, prize chip and ribbon.
- Text-first. Assets are optional and additive.

**Asset list (not started)**

| Asset | Count | Notes |
|---|---|---|
| Festival banner/background | 1 | Reuse the 4:3 panel. Autumn variant of the existing seasonal look. |
| Contest scenes | 4 | One per contest, cat and player in the usual style. |
| Rival cat portraits | 3 to 4 | Different coats, same art style. Breed unchanged. |
| Ribbon icon | 1 | Small. |

**Consistency plan**: follow the asset policy in [`../planning/feature-backlog.md`](../planning/feature-backlog.md#asset-generation-policy-applies-to-every-slices-design-doc). Anchor each scene on `scene-play.jpg`/`scene-train.jpg` for framing and on `web/public/assets/cats/*.png` for the cat; use one anchor per asset class, not chained generations; pilot one image on the smaller model and check framing before a batch. Rivals must not be the player's cat, so give them different coat colors in the prompt and verify visually.

## Interaction

- Choose a contest and confirm, or choose 불참. A bedridden cat sees the list locked with the forced-rest line.
- Then advance. Result card, then the normal summary.

## Handoff notes

- Contest ids, stats and rival data come from the server (`GET /api/festival` mirroring other data endpoints). Names and copy live in the client.
- The result card payload is the generic `title`, `body`, `chips[]` from S1.
