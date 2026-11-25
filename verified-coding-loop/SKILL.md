---
name: verified-coding-loop
description: |
  Implement features, fix bugs, or validate code changes against a ticket, contract, or trustworthy baseline with concrete before/after evidence, targeted regression checks, and honest unverified-scope reporting.
  Use when reproducing bugs, verifying patches, or producing evidence-backed coding results. Skip for conceptual programming Q&A or non-code tasks.
---

# Verified Coding Loop

Choose observations that distinguish **"behavior is correct"** from **"the process exited 0"** (for example, read back exported CSV headers and column order). For small tasks, stating input, expected outcome, and observed result inline in chat is enough.

**Stop debugging a branch when retries stop adding information.** New inputs, logs, or falsifiable hypotheses justify another try; if repeated runs yield the same error or a missing environment dependency is clear, save your current patch, record the latest valid observation, tried steps, and resume condition, verify all independent scope, and deliver honestly. Never fabricate a pass to finish a loop.

## Path Contract

Resolve `SKILL_DIR` from the directory containing this `SKILL.md` (never assume `pwd` is `SKILL_DIR`).

## Adapt to the Task

- **Bug fix:** Compare the same input before and after the change (use user reports or existing tests when baseline cannot run). **Feature:** Derive oracles from API/spec examples. **Refactor:** Cross-check at least one real caller against pre-refactor behavior.
- **Small steps:** Make minimal, focused edits that preserve existing runtime compatibility and unrelated user changes. If asked only to verify, inspect the received build directly.
- **Fit evidence to capabilities:** Run commands in terminal, exercise real UI flows in browser, or perform static code/artifact checks in text-only sessions—always separate *directly observed facts* from *user/author-reported claims*. See `$SKILL_DIR/references/test-oracles.md`.

## Reporting & Optional Consistency Check

Reuse ticket/contract AC IDs (`AC-1`, `CSV-17-A`). Standard states:
- Per-evidence: `pass` | `fail` | `blocked` (missing env/input) | `not_run` (runnable but not yet tried).
- Overall: `pass` | `fail` | `partial` | `not_verified`.

For formal archival, use `$SKILL_DIR/templates/verification-report.md` (map criteria in `## Acceptance mapping` as `- CSV-17-A: E1, E2`) and run the read-only validator:

```bash
python3 "$SKILL_DIR/scripts/check_verification.py" path/to/report.md [--contract path/to/contract.md] [--json] [--strict]
```

Passing `--contract` cross-checks that every AC ID defined in the contract is mapped in the verification report (flagging missing coverage before claiming `Overall: pass`). Default exit is `0` (suggestions); pass `--strict` for exit `1`.

**Workflow handoff:** Accepts AC IDs from `coding-task-contract`; hand finished evidence to `agent-code-handoff` when transferring for independent review.
