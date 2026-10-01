# Design: care step

## Reference

[`../planning/care-actions.md`](../planning/care-actions.md)

## Visual spec

- A row of four buttons above the schedule, beside the diet picker: 안 함, 쓰다듬기, 간식 (cost shown), 혼내기. One selected at a time, default 안 함.
- Treat dims when unaffordable. A small hint line explains when an action will not work ("아플 때는 소용없어요"), driven by `is_sick` and `is_delinquent` state, display only.
- Result: one line in the month summary ("간식을 먹고 기분이 좋아졌다" / "혼내도 소용없었다").
- Assets needed: none. Optional later, 3 small scenes (pet, treat, scold). Consistency plan: same as in [`../planning/feature-backlog.md`](../planning/feature-backlog.md#asset-generation-policy-applies-to-every-slices-design-doc), anchored on the existing player-and-cat sheets, pilot on the smaller model first.

## Interaction

- Choose a care action and a diet, then plan the schedule, then advance. The care choice resets to 안 함 each month.

## Handoff notes

- Care id and cost come from a new `GET /api/care` mirroring `/api/diets`, so the UI is generic.
- Layout check: the picker area is already tight after S5 adds a 7th activity.
