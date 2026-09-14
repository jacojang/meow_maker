# Docs

This project develops through a repeating loop:

**Planning → Design → Coding → Review → Testing → Deployment**

Each stage below owns a folder for its artifacts. A task usually starts in
one folder and produces the input the next folder needs.

| Stage | Folder | Produces |
|---|---|---|
| Planning (기획) | [`planning/`](planning/README.md) | Feature specs, game mechanics, scope decisions |
| Design (디자인) | [`design/`](design/README.md) | Art direction, animation specs, UI/UX mockups |
| Coding (코딩) | [`development/`](development/README.md) | Architecture notes, setup/run instructions, conventions |
| Review (리뷰) | [`review/`](review/README.md) | Review checklists, review notes |
| Testing (테스트) | [`testing/`](testing/README.md) | Test strategy, test plans, QA checklists |
| Deployment (배포) | [`deployment/`](deployment/README.md) | EC2 deployment runbook, environment/release notes |

See [`AGENTS.md`](../AGENTS.md) at the repo root for the overall tech stack
and contribution conventions.

## Subagents

Coding and Review are also implemented as Claude Code subagents
(`.claude/agents/coding-agent.md`, `.claude/agents/review-agent.md`) that run
a conditional feedback loop instead of a single fixed pass — see
[`development/dynamic-workflow.md`](development/dynamic-workflow.md).
