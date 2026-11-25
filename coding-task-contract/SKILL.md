---
name: coding-task-contract
description: |
  Turn coding requirements, bug tickets, or refactoring goals into explicit scope boundaries, observable acceptance criteria (AC IDs), and a concrete verification plan before implementation or delegation.
  Use when clarifying ambiguous behavior, compatibility guarantees, or handing off specs to another executor. Skip for pure Q&A or trivial, self-evident one-line edits.
---

# Coding Task Contract

Deliver a contract proportional to the task. A small change needs only one concrete "given input X, observe output Y" statement. Reuse existing ticket text and IDs whenever available; add extra repository context when handing off to another implementer.

**Deliver a draft when requirements stall.** If re-reading the same material or asking the same question yields no new facts, lock down every confirmed behavior, isolate the open ambiguity and which criterion it affects, record what you checked and what input unblocks it, and proceed on unambiguous parts.

## Path Contract

Resolve `SKILL_DIR` from the directory containing this `SKILL.md` (never assume `pwd` is `SKILL_DIR`).

## Recommended Authoring Steps

1. **Start from observable behavior.** Turn vague wishes ("empty list should still export CSV") into verifiable criteria ("given an empty list, parsing the exported CSV yields exactly one header row with columns `id,name`"). Pair with a control case (e.g., preserving column order on non-empty input). See `$SKILL_DIR/references/acceptance-patterns.md`.
2. **State evidence and boundaries.** Cite real entry points, callers, and behaviors to preserve. When working only from chat or attachments, label facts as `user-reported`, `observed`, or `provisional assumption`. Surface any binary design fork explicitly while advancing independent scope.
3. **Specify how to verify.** Name concrete project tests, CLI commands, UI actions, or output file inspections. Numbered AC IDs (`AC-1`, `CSV-17-A`) shine on multi-part or delegated work; single-item tasks may reuse the ticket sentence directly.

## Delivery & Optional Structure Check

Deliver inline in chat, inside an existing ticket, or as a Markdown file using `$SKILL_DIR/templates/contract.md` (trim unused fields; see `$SKILL_DIR/references/handoff-example.md`).

When using the full template, run the read-only structure checker:

```bash
python3 "$SKILL_DIR/scripts/check_contract.py" path/to/contract.md [--json] [--strict]
```

By default the script prints suggestions and exits `0` so open drafts never block delivery; pass `--strict` for exit code `1` in automated gates.

**Workflow handoff:** Pass the resulting AC IDs directly into `verified-coding-loop` during implementation/verification (`--contract path/to/contract.md`) and `agent-code-handoff` during cross-agent review.
