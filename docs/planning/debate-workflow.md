# Critic ↔ Planner Debate

Iterates a feature or improvement through `critic-agent` and `planner-agent`
(`.claude/agents/`) until they agree. Run it with `/debate <scope>`.

## Orchestration

Subagents can't call each other. The orchestrator (the main session)
relays between them, counts rounds, and decides when to stop.

## Protocol

1. **Round 0** — orchestrator dispatches `critic-agent` with the scope.
   Scope is a topic (e.g. "schedule system") or a proposal from the user.
   If the user gave a proposal, dispatch `planner-agent` first and send its
   draft to the critic.
2. **Round N (odd)** — orchestrator sends the critic's full report to
   `planner-agent`. Planner answers each point (`adopt | adapt | reject`)
   and writes or updates `docs/planning/<slug>.md`.
3. **Round N (even)** — orchestrator sends the planner's full reply and
   doc path to `critic-agent`. Critic returns `DESIGN VERDICT` and any
   remaining requests.
4. Repeat 2–3.

Pass reports verbatim, not summarized. Continue the same agent with
`SendMessage` so it keeps its context.

## Stop conditions

- **Agreed** — critic says `APPROPRIATE` and planner ends with
  `DOC CREATED` or `DOC UPDATED`.
- **Round limit** — 10 rounds. List unresolved points for the user.
- **Needs input** — planner returns `NEEDS INPUT`. Ask the user, then
  resume with the answer.

## Rules

- Planner is the only writer of docs. Critic never edits files.
- One planner at a time per planning doc.
- Independent topics may run as parallel critic/planner pairs.
- The user may interrupt between rounds; apply their instruction in the
  next dispatch.

## After agreement

Report to the user: docs written, decisions per point, priority order.
Work then moves on to Design/Coding as usual. Do not start coding from
this workflow.
