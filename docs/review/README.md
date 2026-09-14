# Review (리뷰)

Code review before a change moves to testing.

## What goes here

- Review checklists (correctness, scope creep, test coverage)
- Notable review findings/decisions worth keeping as project history

## Checklist (starting point)

- [ ] Change is scoped to what was asked — no unrelated refactors
- [ ] Matches the confirmed planning/design docs it implements
- [ ] Test code wasn't modified just to make tests pass
- [ ] No unnecessary comments; code reads clearly on its own
- [ ] New code is structured to be testable

## Subagent

Review is implemented as the `review-agent` subagent
(`.claude/agents/review-agent.md`), which runs a conditional loop against
`coding-agent` rather than a single pass — see
[`../development/dynamic-workflow.md`](../development/dynamic-workflow.md).

## Next stage

Once review passes, it hands off to [`../testing/`](../testing/README.md).
