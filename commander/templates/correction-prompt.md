# Focused Correction Prompt Template

Use when a delegated deliverable fails one or more acceptance criteria and the same executor has a clear path to fix it (max 2 substantive correction rounds on the same gap).

```text
[Correction for: <executor role or channel>]

Previous deliverable: <file path or reference>

Acceptance gap: <specific failed criterion and observed failure evidence>

Change only: <smallest bounded fix required>

Keep unchanged: <parts already verified and accepted>

Return the corrected deliverable and an updated completion report stating exactly what changed and which checks were re-run. Do not mark the criterion as Pass without new observed evidence.
```
