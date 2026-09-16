# Planning (기획)

Defines *what* gets built before any design or code work starts: game
concept, mechanics, systems (stats, events, progression), and scope for a
given piece of work.

## What goes here

- Game concept and high-level design pillars
- Feature specs (one doc per feature/system)
- Stat and progression system definitions
- Open questions and decisions that need confirmation before moving to Design

## Roadmap

[`roadmap.md`](roadmap.md) is the multi-phase plan for building the game
itself, plus the decisions that span all of it (server-authoritative rules,
run length, when SQLite arrives, how accounts get added later). Each phase
there becomes its own `docs/planning/<slug>.md` when it's started — the
roadmap is the map, those are the specs.

## Reference material

Meow Maker is modeled on *Princess Maker 2*. Before writing or changing a
planning doc for a game feature, check how PM2 handled the same area in
[`references/princess-maker-2/`](references/princess-maker-2/README.md) —
start with its README and read only the topic files you need (raising
system, status system, mini-games, characters/layout, endings). When a
planning doc borrows from or intentionally departs from PM2, say so in its
Mechanics section.

## Requesting a task

Pick a path based on size — when in doubt, use the full path. A short
planning doc is cheap; redoing an under-planned feature isn't.

**Full path** — new feature, or any change to game mechanics/stats/systems,
or a new screen:

```
## Feature request
- Type: new feature | modify | remove
- Name: <short name>
- What: <1-2 sentence description of what should exist/change>
- Why: <motivation, optional>
```

This creates `docs/planning/<slug>.md` (see template below), then flows
through Design → Coding → Review → Testing → Deployment.

**Lightweight path** — a bug fix, copy change, or small single-purpose tweak
that doesn't touch game mechanics or add scope:

```
## Quick request
- What: <description of the small change>
```

No planning/design doc gets created — this goes straight to Coding under
the usual `AGENTS.md` conventions, with the git commit as the only record.

## Doc template

Each planning doc lives at `docs/planning/<slug>.md`, where `<slug>` is a
kebab-case short name for the feature (e.g. `cat-feeding.md`). It opens with
status metadata, since a fresh session or subagent dispatch has no memory of
prior conversation — this is the only place a feature's progress is
tracked:

```
---
status: planning   # planning | design | coding | review | testing | deployed
updated: YYYY-MM-DD
---
```

Followed by:

1. **Goal** — what problem this feature/system solves for the player
2. **Scope** — what's in, what's explicitly out
3. **Mechanics** — how it works, with enough detail to hand to Design/Coding
4. **Open questions** — anything not yet confirmed

## Status tracking

Update the `status` field in `docs/planning/<slug>.md` at each stage
transition: `planning` → `design` → `coding` → `review` → `testing` →
`deployed`. Design and coding work reference this doc rather than tracking
status anywhere else.

## Next stage

Once a planning doc is confirmed, it hands off to [`../design/`](../design/README.md).
