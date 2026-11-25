# Acceptance Checklist & Executor Evaluation Notes

## Complex-Task Acceptance Checklist

Before declaring a multi-part task complete, verify:

- [ ] The integrated deliverable addresses the user's actual goal and requested format.
- [ ] Relevant pre-existing files and unrelated user changes were inspected and preserved.
- [ ] Every delegated artifact was inspected directly (not accepted from a summary alone), and critical criteria carry evidence.
- [ ] Cross-package integration is coherent; required files, links, and dependencies are present with no unresolved conflicts.
- [ ] Every check is labeled accurately (`Pass`, `Fail`, `Not verified`, or `Blocked`); no unrun check is reported as passed.
- [ ] No unapproved destructive, externally visible, or material-cost action occurred.
- [ ] Remaining limitations, assumptions, and required user decisions are stated explicitly.

Apply only the relevant subset for small tasks.

## Evidence-Based Executor Notes (Optional)

Maintain executor observations **only** when the user or project provides a durable location (such as a project note). Never silently edit global configuration or personal memory.

Record observations by **task category**, not a single global score:

- **Channel / capability:** Actual tool, model tier, or execution channel (if known).
- **Task category & scope:** e.g., mechanical refactor, schema extraction, long-form drafting.
- **Outcome & verification:** Completion status, instruction-following, factual/code correctness, independent verification evidence.
- **Cost & rework:** Measured elapsed time, quota/cost (only if observed), handoff overhead, rework iterations.
- **Confidence label:** Mark every claim as **user-reported**, **observed once**, or **repeatedly observed**. Keep unknowns unknown; do not overfit a single run.
