# Design (디자인)

Turns a confirmed planning doc into concrete visual and interaction design:
art direction, character/sprite animation specs, and screen/UI layout.

## What goes here

- Art direction and style references (2D animation, Princess-Maker-style
  static backgrounds + character sprite animation)
- Character sprite sheets specs (states, frame counts, transitions)
- Screen/UI mockups and flows
- Animation state diagrams (e.g. idle → reaction → idle)

## Doc template

Each design doc lives at `docs/design/<slug>.md`, using the same `<slug>`
as its planning doc (`docs/planning/<slug>.md`). It carries no status field
of its own — progress is tracked in the planning doc only (see
[`../planning/README.md`](../planning/README.md#status-tracking)).

It should cover:

1. **Reference** — the planning doc it implements
2. **Visual spec** — assets needed, dimensions, states/variants
3. **Interaction** — how the player triggers each visual state
4. **Handoff notes** — anything the Coding stage needs to know to implement it

Skip this doc for features with no visual/UX component (e.g. a pure backend
calculation) — note that directly in the planning doc instead of creating an
empty design doc.

## Next stage

Once a design doc is confirmed, it hands off to [`../development/`](../development/README.md).
