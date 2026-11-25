---
name: agent-code-handoff
description: |
  Package code changes, artifacts, original acceptance criteria, observed results, blockers, and next actions when switching agents/machines, transferring patches, or requesting independent code review—including partial or blocked mid-task handoffs.
  Use when handing coding work to another agent or reviewer, or performing an independent review on a received patch. Skip for general Q&A or self-contained edits with no handoff/review needed.
---

# Agent Code Handoff

First check whether the receiver will **continue implementation** or **perform independent verification**. A short handoff only needs the goal, an accessible artifact, and the next action; for tiny changes, pasting the code inline is fine.

**Hand off early when blocked.** If repeated attempts on the same error produce identical output or a required file/baseline is unavailable, hand off the exact symptom, tried steps, observed results, and concrete resume condition (e.g., receiving the matching base commit, missing fixture, or new log), while completing any independent checks first.

## Path Contract

Resolve `SKILL_DIR` from the directory containing this `SKILL.md` (never assume `pwd` is `SKILL_DIR`).

## Author Checklist (Pick What Fits)

- **Accessible artifact:** Same workspace → project-relative paths & revision. Different machine → accessible commit/branch, patch with base revision, or attached/inline files + untracked files, dependencies, and inputs.
- **Preserved intent:** Forward original ticket/contract AC IDs, scope boundaries, observed results, unverified gaps, and the receiver's exact first step. Never assume the receiver shares chat history or local absolute paths.
- **Proportional format:** Inline paragraph, `$SKILL_DIR/templates/handoff-lite.md` (short), or `$SKILL_DIR/templates/handoff.md` (full). Use `ready` when actionable, `blocked` when missing critical input.

## Receiver & Independent Review

Inspect the actual received artifact first, then choose checks that discriminate pass from fail. With code snippets only, report static findings and mark runtime behavior `not_verified`. Attribute author-reported results separately from your own observations (label self-reviews honestly).

Map original criteria to `pass`, `fail`, or `not_verified` (`not_run` if runnable but not yet attempted; `blocked` if missing environment). For multi-patch merges, prioritize re-verifying shared interfaces. See `$SKILL_DIR/templates/review.md` and `$SKILL_DIR/references/review-protocol.md`.

## Optional Consistency Validator

```bash
python3 "$SKILL_DIR/scripts/check_handoff.py" --kind handoff path/to/handoff.md [--contract path/to/contract.md] [--json] [--strict]
python3 "$SKILL_DIR/scripts/check_handoff.py" --kind review path/to/review.md [--contract path/to/contract.md] [--json] [--strict]
```

Passing `--contract` verifies AC ID alignment against `coding-task-contract` (e.g., catching unreviewed contract criteria before a `pass` verdict). Default exit is `0` (suggestions); pass `--strict` for exit `1`.

**Workflow handoff:** Pairs with `coding-task-contract` (AC IDs), `verified-coding-loop` (author evidence), and `commander` (multi-agent orchestration).
