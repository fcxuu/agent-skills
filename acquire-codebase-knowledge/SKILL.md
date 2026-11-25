---
name: acquire-codebase-knowledge
license: MIT
description: |
  Map and document an existing codebase—entry points, module boundaries, dependencies, data flow, conventions, tests, and risks—backed strictly by inspected files and command output.
  Use when onboarding to, surveying, or documenting a repository. Skip for general programming Q&A or explaining a single snippet.
---

# Acquire Codebase Knowledge

## Path Contract

Resolve `SKILL_DIR` from the directory containing this `SKILL.md` (never assume `pwd` is `SKILL_DIR`). Always run commands from the **target repository root**.

## Output Modes

Confirm the requested scope first:
- **Concise onboarding map (default):** A single structured guide covering entry points, module relationships, data flow, key configs, test locations, and open unknowns.
- **Full 7-document pack (on explicit request):** Populate `docs/codebase/{STACK,STRUCTURE,ARCHITECTURE,CONVENTIONS,INTEGRATIONS,TESTING,CONCERNS}.md` using `$SKILL_DIR/assets/templates/` and `$SKILL_DIR/UPSTREAM.md`.

## Scan-First Workflow

1. **Scan before wandering:** From the target repo root, run the deterministic scanner first instead of running many ad-hoc `find`/`ls` commands:
   ```bash
   python3 "$SKILL_DIR/scripts/scan.py"
   ```
   (Pass `--output <file>` only if the user wants the scan report saved to disk.)
2. **Verify against source & config:** Cross-check manifests (`package.json`, `pyproject.toml`, `go.mod`, etc.), real entry points, tests, and key source files. Consult `references/stack-detection.md` for stack signals and `references/inquiry-checkpoints.md` when scoping deep dives.
3. **Trace every claim:** State only facts backed by inspected files or command output; explicitly mark unknowns as `[TODO]` / unverified.

## Critical Anti-Patterns (Never Do These)

- **Do not trust an outdated README:** Always verify architecture, frameworks, and commands against actual directory structure and dependency manifests.
- **Do not flatten Monorepos:** Check root configs for `workspaces`, `packages/`, or `apps/`; map each sub-package's stack, entry point, and tests separately.
- **Do not invent architecture labels:** Never claim "Clean Architecture" or "Domain/Data layers" unless those structures actually exist in the repository.

See `UPSTREAM.md` for the full 4-phase investigation contract and validation checklist.

Upstream: [github/awesome-copilot/skills/acquire-codebase-knowledge](https://github.com/github/awesome-copilot/tree/f10fdb8b2660ce85c98f220b2f1ca24653768a5c/skills/acquire-codebase-knowledge), commit `f10fdb8b2660ce85c98f220b2f1ca24653768a5c`; license in [LICENSE.txt](LICENSE.txt).
