---
name: gh-fix-ci
license: Apache-2.0
description: |
  Investigate or fix failing GitHub Actions CI checks on a specified GitHub Pull Request by inspecting check runs, job logs, commit context, and local code.
  Use when diagnosing or fixing a failing GitHub PR CI run. Skip for general Git/CI concepts or unrelated GitHub Q&A.
---

# GitHub Fix CI

Confirm the target repository and PR first. Diagnose failures read-only; **modify code only when the user asks to fix the issue**.

## Path Contract

Resolve `SKILL_DIR` from the directory containing this `SKILL.md` (never assume `pwd` is `SKILL_DIR`). Run commands from the **target Git repository root**.

## 3-Step Read-Only Triage Pipeline

1. **Verify GitHub CLI authentication** (needs `repo` and `workflow` scopes):
   ```bash
   gh auth status
   ```
   If unauthenticated, stop and ask the user to run `gh auth login`, while noting any local checks you can still perform.
2. **Resolve the PR** (current branch PR, or use the user-supplied PR number/URL):
   ```bash
   gh pr view --json number,url,headRefOid
   ```
3. **Inspect failing checks and extract log snippets** via the read-only helper script (run `--help` for full flags):
   ```bash
   python3 "$SKILL_DIR/scripts/inspect_pr_checks.py" --pr <PR_NUMBER> --json
   ```

For external (non-GitHub Actions) CI providers, inspect via available authorized interfaces or report the check URL and access limitations honestly.

## Diagnosis & Fix Deliverable Checklist

Always include:
- Failing workflow / job name(s), trigger event, and exact commit SHA.
- The **first actionable root-cause error line** (not just a trailing summary dump) mapped to local source files.
- A local reproduction command (when reproducible locally).
- If authorized to fix: minimal targeted patch, local verification results, and any CI-only checks that remain unverified until re-run on GitHub.

See `UPSTREAM.md` for full escalation and multi-check handling guidance.

Upstream: [openai/skills/skills/.curated/gh-fix-ci](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/gh-fix-ci), commit `49f948faa9258a0c61caceaf225e179651397431`; license in [LICENSE.txt](LICENSE.txt).
