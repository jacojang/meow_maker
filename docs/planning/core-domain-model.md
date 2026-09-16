---
status: planning
updated: 2026-09-16
---

# Core Domain Model (Roadmap Phase 0)

## Goal

Build the game's rules as plain Python — stats, a calendar, activities,
stress — with no HTTP, no database, and no Phaser. Everything testable with
`pytest` alone. This is the foundation every later phase builds on, so it's
worth getting the shape right before anything depends on it.

## Scope

**In**

- A `server/app/game/` package holding the rules.
- **Cat stats**: a small set of numbers describing the cat (see Mechanics).
- **Calendar**: a run is 12 months; each month has 3 slots.
- **Activities**: a handful, each with per-slot stat effects and a stress
  cost.
- **Stress**: rises from activities, and past a threshold makes the cat
  sick, which degrades how well activities work.
- **Advancing a month**: resolve its 3 assigned slots in order, apply
  effects, then move to the next month.
- **Serializable state**: a run converts to and from a plain dict. That's
  what both the Phase 1 in-memory store and Phase 2's SQLite need, and
  tests use it now.

**Out**

- Any HTTP endpoint or API shape — that's Phase 1.
- Any persistence that survives the process — that's Phase 2.
- UI of any kind.
- Events, contests, endings, scoring — Phases 4–5.
- Content volume. A few activities is enough to prove the loop; the full
  table comes in Phase 3.
- An RNG seam and a repository interface. Nothing here has a use for
  either yet; both arrive with their first real caller (see
  [`roadmap.md`](roadmap.md)).

## Mechanics

Adapted from PM2 (see
[`references/princess-maker-2/status-system.md`](references/princess-maker-2/status-system.md)),
cut down hard for a first pass.

**Stats** — start with five, all integers:

| Stat | Meaning | Rough PM2 analogue |
|---|---|---|
| Health | Stamina; how much the cat can take before getting sick | Constitution |
| Affection | Bond with the player | Father relationship |
| Discipline | How well the cat behaves | Morality |
| Curiosity | Playfulness, drives some events later | Sensitivity |
| Stress | Fatigue; the pressure valve of the whole loop | Stress |

**The loop**

1. The player assigns an activity to each of the month's 3 slots.
2. Advancing the month resolves slots in order: each applies its stat
   deltas and adds its stress.
3. If stress exceeds Health, the cat becomes sick — activities become less
   effective until stress drops back below Health.
4. After 12 months the run ends. (What "ends" means is Phase 5; for now it
   just stops.)

**Activities** — enough to make the tension real, not the full set:

| Activity | Effect | Stress |
|---|---|---|
| Play | Affection up, Curiosity up | high |
| Train | Discipline up | medium |
| Groom | Affection up, small Health up | low |
| Rest | Stress down | none (recovers) |

Exact numbers get tuned during Coding; they belong in one table so Phase 3
can lift them straight out into a data file.

## Open questions

None outstanding. The decisions this depends on are settled in
[`roadmap.md`](roadmap.md): server-authoritative rules, 12-month runs, and
the repository seam that lets SQLite arrive later.

## Next stage

No Design pass needed — nothing visual here. Goes straight to Coding.

Testing is the deliverable as much as the code: a test should be able to
simulate a full 12-month run, and each rule (stress accumulation, the sick
threshold, recovery, each activity's effects) should have its own test.
