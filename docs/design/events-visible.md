# Design: events visible

## Reference

[`../planning/events-visible.md`](../planning/events-visible.md)

## Visual spec

- Result card: reuses the 4:3 panel. Title, one line, stat chips (existing chip style, green up, red down), the current portrait. Dismiss on click.
- Advisor line: the existing message line. One sentence, never stacked.
- Badges: three chips under the portrait (아픔, 말썽, 통통). Hidden when not active. Colors reuse the stress/health palette; no new art.
- Assets needed: none. Optional later: one illustration per event (visitor, good mood, bad mood, mishap, gift) and outing success/failure, generated per the asset policy in [`../planning/feature-backlog.md`](../planning/feature-backlog.md#asset-generation-policy-applies-to-every-slices-design-doc). Not part of S1.

## Interaction

- After the resolution animation ends: card(s) in order outing, event, festival. The festival card shows only when the month just processed was the festival month. A click advances. No card when nothing happened.
- Warnings refresh whenever state refreshes.

## Handoff notes

- Pure display. All thresholds come from the `warnings` field.
- Keep the card generic (`title`, `body`, `chips[]`, optional `imageKey`) so festival results reuse it.
- Keep ordering/label helpers in `web/src/utils/` so they are testable without Phaser.
