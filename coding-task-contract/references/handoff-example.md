# CSV Export Contract (Illustrative Example)

## Task
- Task ID: CSV-17
- Status: active

## Goal and context
- User reports downloading an empty list yields a zero-byte file. Ticket specifies two columns (`id`, `name`) and requires exporting the header row even when empty. Baseline output not yet captured locally.

## Scope
### In scope
- Handle empty lists in the CSV exporter and verify existing column order on a non-empty input.
### Out of scope
- Changing the download button, filename, or upstream data source.

## Acceptance criteria
- [ ] CSV-17-A | Given an empty list, when exported to CSV, then parsing the output yields exactly one row with headers `id,name`.
- [ ] CSV-17-B | Given one record `{id: 7, name: "Lin"}`, when exported to CSV, then parsing yields header `id,name` followed by `7,Lin`.

## Verification plan
- Baseline: Run both inputs through the existing export entry point and record actual rows (currently user-reported only).
- Checks: Repeat both exports after patching and compare parsed rows/columns with a CSV reader, mapping evidence to `CSV-17-A` and `CSV-17-B`.

## Change and recovery boundaries
- Modify only the exporter and its regression test; preserve caller signatures and unrelated working-tree changes. Roll back by reverting only this task's diff.

## Handoff
- Owner: Assigned implementer.
- Next action: Obtain the target source revision, locate the export entry point, and capture baseline output. If working only from this text, request the source snapshot first.
