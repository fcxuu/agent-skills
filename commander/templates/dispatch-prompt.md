# Dispatch Prompt Template

Use when delegating a bounded work package to an independent subagent or preparing a copy-paste prompt for an external client. Include only minimum necessary context; exclude secrets and unrelated private data.

```text
[Task for: <executor role or channel>]

Goal
<One concrete outcome and why it is needed>

Context & Inputs
<Relevant background, exact file paths or source text, assumptions, dependencies>

Scope & Ownership
<What to do; files/sections you own; what NOT to change or decide; whether edits are permitted>

Constraints
<Format, style, compatibility, privacy, safety, budget/retry limits, source-of-truth rules>

Deliverables
<Exact files, patch, findings, or output format required>

Acceptance Criteria
<Observable checks defining a satisfactory result>

Completion Report
Return:
1. Completed items and exact deliverable locations.
2. Specific changes made (file/section references).
3. Checks actually executed and their observed output (include commands when useful).
4. Material assumptions, unresolved issues, blockers, and anything not verified.
5. Effort/usage only if accurately observed.

Rules: Do not claim an unrun check passed. Do not expand scope without explanation. Stop and report if blocked after 2 substantive attempts on the same error.
```
