# Dynamic Coding ↔ Review Loop

The fixed loop in `docs/README.md` treats Coding and Review as one pass
each. In practice a change often needs more than one round — this document
defines the conditional feedback loop that runs between them, using the
`coding-agent` and `review-agent` subagents in `.claude/agents/`.

## Why "dynamic"

The number of coding↔review cycles isn't fixed ahead of time. It's decided
at runtime by `review-agent`'s verdict, not by a predetermined step count.

## Protocol

1. Orchestrator (the main session) dispatches `coding-agent` with a bounded
   task description.
2. Orchestrator dispatches `review-agent` with the files `coding-agent`
   reported as changed.
3. `review-agent` returns `VERDICT: PASS` or `VERDICT: FAIL` plus a
   numbered fix list.
4. **On FAIL**: orchestrator re-dispatches `coding-agent` with the original
   task plus the fix list, and increments a retry counter. Go to step 2.
5. **On PASS**: the change moves on to Testing.
6. **Retry limit**: 3 coding↔review cycles. If it's still FAIL after the
   3rd `review-agent` pass, stop looping and escalate to the user instead
   of continuing indefinitely.

## State carried between iterations

Each retry dispatch to `coding-agent` carries only:

- The original task description (unchanged across retries)
- The latest fix list from `review-agent` (not the accumulated history —
  each list should already be a complete restatement of what's still wrong)

## Out of scope for this doc

This describes the Coding↔Review loop only. Feedback loops involving
Testing or Deployment (e.g. a test failure sending work back to Coding)
aren't defined yet — extend this doc when that's needed rather than
guessing at the protocol now.
