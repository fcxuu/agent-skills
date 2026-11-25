# Cross-Environment Handoff & Independent Review Protocol

## Match Packaging to the Receiver's Environment

| Receiver Environment | Practical Transfer Format |
|---|---|
| Same workspace | Project-relative paths, current revision, uncommitted changes, and exact next step. |
| Repo access, no shared working tree | Accessible commit/branch plus patch with base revision, apply command, and untracked files. |
| Attachments or text only | Attach required inputs or inline short files with reconstruction steps and checksums/digests when version confusion is possible. |

When multiple agents touch overlapping files, designate one integration owner. If a patch fails to apply cleanly, inspect the diff statically, record the exact missing baseline/file and affected checks, and return a concrete resume condition.

## Independent Review Focus

Select at least one discriminating check tied to the ticket's acceptance criteria, expanding to edge or integration checks proportional to blast radius. Label every observation source (`author-run`, `reviewer-run`, `static-inspection-only`). After merging patches that alter shared interfaces, re-verify on the merged tree.

Optional finding severities: `blocker` (cannot proceed/ship), `major` (impacts core acceptance goal), `minor` (localized polish). Handoffs may include unfinished work paired with explicit resume triggers.
