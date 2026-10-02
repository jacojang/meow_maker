# Design: sickness stakes

## Reference

[`../planning/sickness-stakes.md`](../planning/sickness-stakes.md)

## Visual spec

- Bedridden badge (chip) beside the existing sick badge. Text first.
- Picker locked while bedridden: all three slots shown as REST with a short advisor line ("푹 쉬어야 해요").
- Early ending: reuses the S2 reveal. Title: 입원한 고양이 (draft). The runaway ending moves to S6a.

**Asset list (generation optional, not started)**

| Asset | Count | Notes |
|---|---|---|
| Bedridden portrait | 3 (kitten, young, adult) | Normal weight only. Key `cat-<age>-bedridden`. |
| Delinquent portrait | 3 (same ages) | Optional, completes backlog B3. |
| Early-ending illustration | 1 | Optional. Hospitalized. |

**Consistency plan**: follow the asset policy in [`../planning/feature-backlog.md`](../planning/feature-backlog.md#asset-generation-policy-applies-to-every-slices-design-doc). Anchor each portrait to the matching existing `cat-<age>-sick-normal.png` as the `--ref`, keep breed and framing identical, pilot one image on the smaller model before any batch. Fallback if no art: badge only, and the portrait stays on the sick variant.

## Interaction

- On entering a bedridden month the player sees the locked picker and can still choose a diet, then advances.
- No new buttons.

## Handoff notes

- `portraitKey` lives in a Phaser-free util; extend it there and cover it in Vitest.
- Missing textures must fall back (`this.textures.exists`) so the game ships before art does.
