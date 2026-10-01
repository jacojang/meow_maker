# Design: ending reveal

## Reference

[`../planning/endings-by-build.md`](../planning/endings-by-build.md)

## Visual spec

- Replaces the single panel in `renderEndOfRun()`. Same panel, four steps in place.
- Step 1 stat roll: the five core stats count up one by one.
- Step 2 ending title (large, existing green).
- Step 3 flavor paragraph (2-3 short lines).
- Step 4 score `N / 1000`, then a "다시 시작" button.
- Assets needed: none. Per-ending illustrations are a later, cost-gated item (see the asset policy in [`../planning/feature-backlog.md`](../planning/feature-backlog.md#asset-generation-policy-applies-to-every-slices-design-doc)). Slot an optional image above step 2.

## Interaction

- Each step advances on click, or auto-advances after a short delay. A skip control jumps to the last step.
- Reload on a finished run shows the final step directly (no replay).

## Handoff notes

- Server returns only the ending id and score. Labels and paragraphs live in the client, as `ENDING_LABELS` does today. Move them to a data module so 10 pair entries stay readable.
- Reveal step order is a pure helper under `web/src/utils/` with a Vitest test.
