---
description: Run a critic-agent ↔ planner-agent debate on a scope or proposal (max 10 rounds)
argument-hint: <scope or proposal>
---

Run the debate workflow for: $ARGUMENTS

Read `docs/planning/debate-workflow.md` and follow its protocol exactly,
acting as orchestrator. If the argument is empty, ask the user for a scope
before dispatching anything.

Keep the user informed with one short line per round (round number, who
spoke, outcome). At the end, report as the "After agreement" section says.
