# 07 · Batch Execution, State Persistence, Recovery & Delivery

> **Quick Index:** 1. Course Directory Layout · 2. `.build-state.json` Schema & `state_tool.py` · 3. Five-State Matrix · 4. Protected Completed & Controlled Revision · 5. Safe Atomic Writes & Fingerprints · 6. Section Loop & Minimal Recovery Context · 7. Re-anchoring & Final Delivery

## 1. Course Directory Layout

Operate strictly inside the user's existing `VAULT_DIR` and `COURSE_DIR` (never create outer wrapper folders or move/overwrite source slides):

```text
<COURSE_DIR>/
  source1.pdf / source2.pptx / ...   # untouched originals
  .build-state.json                  # machine 5-state, pointers, source SHA-256 fingerprints
  README.md                          # student navigation + checkpoint progress projection
  QA.md                              # audit ledger, ingestion notes, rework history
  raw-markdown/                      # one full Markdown per source + source-map.md
  notes/                             # logical section notes (and optional split topic pages)
  review/                            # exam review hubs embedding ## 核心速览
  assets/original/                   # extracted source figures
  assets/generated/                  # deterministic redraws / schematic plots
  handoffs/                          # optional: created only during real multi-agent delegation
```

## 2. `.build-state.json` Schema & `state_tool.py`

`.build-state.json` is the **primary machine lifecycle ledger**; `README.md` is a checkpoint projection; `QA.md` is the evidence ledger; `raw-markdown/source-map.md` holds source coordinates and `verified`/`unverified` boundary status only. Never store OCR text, note prose, or long logs in `.build-state.json`.

Minimal schema (strictly validated by `scripts/check_vault.py`):

```json
{
  "schema_version": "0.2.0",
  "course_status": "in_progress",
  "sources": {
    "raw-markdown/lec01.md": {
      "source_file": "slides/lec01.pdf",
      "sha256": null,
      "size_bytes": 48210
    }
  },
  "sections": [
    {
      "id": "ch01-sec01",
      "status": "pending",
      "source_map_ref": "Ch01 / 1.1 基本概念",
      "output_path": "notes/01-01-basic-concepts.md",
      "attempts": 0,
      "qa_ids": [],
      "updated_at": null
    }
  ]
}
```

- `course_status`: `in_progress` | `completed` | `completed_with_issues` | `interrupted`.
- `sources`: keyed by course-relative `raw-markdown/*.md`; `source_file` is course-relative; `sha256` is a real 64-hex digest or `null` (never fake placeholders); `size_bytes` is a non-negative integer.
- `sections`: unique stable `id` (does not change on minor title edits), `status` in 5 states, `source_map_ref` matching a row in `source-map.md`, `output_path` (course-relative `.md`), `attempts` (non-negative int counting started builds/substantive fixes), `qa_ids` (`list[str]`), optional ISO-8601 `updated_at` or `null`.
- **Retry cap is tracked per QA issue (max 2 substantive fixes in `QA.md`), not by total section `attempts`.**

**Prefer `scripts/state_tool.py` over hand-editing JSON** (atomic `os.replace`, auto SHA-256, transition guards):

```bash
python3 "$SKILL_DIR/scripts/state_tool.py" init --course "$COURSE_DIR"
python3 "$SKILL_DIR/scripts/state_tool.py" register-source --course "$COURSE_DIR" --raw raw-markdown/lec01.md --source slides/lec01.pdf
python3 "$SKILL_DIR/scripts/state_tool.py" upsert-section --course "$COURSE_DIR" --id ch01-sec01 --source-map-ref "Ch01 / 1.1 基本概念" --output notes/01-01.md --status processing --bump-attempts
python3 "$SKILL_DIR/scripts/state_tool.py" set-course-status --course "$COURSE_DIR" --status completed_with_issues
python3 "$SKILL_DIR/scripts/state_tool.py" summary --course "$COURSE_DIR" --json
```

## 3. Five-State Evidence & Transition Matrix

| State | Required Evidence | Allowed Automatic Transitions |
|---|---|---|
| `pending` | Not yet started; verify any unknown file at `output_path` before touching | `processing` |
| `processing` | Build/rework in progress; incomplete drafts ≠ pass | `qa_pending`; `failed` (log `QA.md` first) |
| `qa_pending` | Non-empty note on disk; awaiting L1/L2 QA | `completed` (QA passed); `processing` (grounded local fix within issue cap); `failed` (log `QA.md` first) |
| `completed` | Non-empty note + passed L1/L2 QA + no open core P0 | **Read-only snapshot by default.** Only a verified new core P0 triggers `completed → failed` (log `QA.md` & dependents first; **no body write permission**; never auto-revert to `pending`/`processing`) |
| `failed` | Real failure reason, coordinates, and downstream risk logged in `QA.md` | **No auto-retry this run**; requires explicit user instruction to resume |

- An `unverified` boundary in `source-map.md` keeps the section `pending` (logged in `QA.md`) rather than marking task `failed`.
- **Ghost `completed` metadata repair** (JSON says `completed` but file/QA is missing) is metadata correction, not permission to overwrite files: log the conflict, set `pending` if no file exists, `qa_pending` if a file exists with unclear QA, or `failed` if blocking failure evidence exists—never overwrite existing notes during repair.

## 4. Protected Completed State & Controlled Revision

Once a section meets all 4 conditions (`status == completed`, non-empty file, passed L1/L2, no open core P0), its body is **immutable** during auto-recovery, later chapters, backlinking, review embeds, or L3 checks.

**Only controlled revision entry:** When a trusted user **explicitly names the specific completed note and revision scope**:
1. Lock the authorized file path, revision scope, and QA ID—do not widen to unnamed chapters.
2. Back up the original to `<filename>.md.bak` (not `-backup.md`, so Obsidian does not index it as a second Markdown note) and verify backup integrity before editing. Abort if backup fails.
3. Log user authorization and backup path in `QA.md`, then unlock state via `state_tool.py upsert-section ... --status processing --controlled-revision --bump-attempts`.
4. Edit strictly within scope, preserving verified prose and user annotations.
5. Move to `qa_pending`, re-run L1 + necessary L2; restore `completed` only after passing. Retain `.md.bak` unless user approves deletion. Log downstream review needs in `QA.md` without cascading regenerations.

## 5. Safe Atomic Writes & Source Fingerprints

- Validate schema and transitions in memory, write `.build-state.json.tmp` in `COURSE_DIR`, commit via `os.replace()`, and verify readability (`state_tool.py` handles this automatically). Update to `qa_pending`/`completed`/`failed` only **after** the note/QA files are safely on disk.
- Record real SHA-256 + `size_bytes` via stdlib `hashlib` (`mtime` change alone ≠ content change). If a raw Markdown file's real content changes later, re-verify affected `source-map.md` ranges and re-check **incomplete** dependent sections only; keep `completed` notes read-only and log "underlying source changed; completed note preserved" in `QA.md`.

## 6. Section Loop & Minimal Recovery Context

### Single-Section Loop
1. Pick the next ready `pending`/resumable section from `.build-state.json`; verify `source-map.md` boundary is `verified`, then set `processing`.
2. Slice-read only the exact segments in `source-map.md` plus `## 核心速览` (and needed definitions) of prerequisites.
3. Write note + figures to disk; once non-empty on disk, set `qa_pending`.
4. Run L1 (`check_vault.py`) + required L2 (≤ 2 substantive fixes per QA issue). Set `completed` on pass, or write `QA.md` first then set `failed`. Sync `README.md` at checkpoints (every 2–3 completed sections, chapter end, major failure, or delivery).
5. On chapter end, run L3 and build/update `review/` hub, then proceed autonomously to the next chapter.

### Minimal Recovery Context (6-Step Evidence-First Resume)
On resume, load **only** what is needed for the active section (never reload the whole course):
1. Inspect `.build-state.json` (and verify any leftover `.build-state.json.tmp` before touching it).
2. Validate schema and 5-state integrity; repair corrupt metadata conservatively from disk + `QA.md` + `README.md`.
3. Identify actionable unfinished sections without re-running already-`failed` items.
4. Cross-check disk notes/drafts and `QA.md` evidence.
5. Consult `README.md` for navigation and `source-map.md` for source coordinates.
6. Arbitrate strictly by **disk artifacts & QA evidence > `.build-state.json` > `README.md`** (`processing` → resume from draft; `qa_pending` → run QA without regenerating; `completed` → skip read-only or repair ghost metadata; `failed` → skip this run).

## 7. Context Re-Anchoring & Final Delivery

- Reuse active-stage specs within a clean session; **re-read the active stage's core spec** after context compaction or across long chapter transitions. Never assume host support for context clearing, auto-new sessions, or background execution.
- If quota/limits interrupt execution while `pending` sections remain, flush current checkpoints, sync `README.md`, set `course_status` to `interrupted`, and report exact resume pointers.
- Once all planned sections reach `completed` or `failed` and chapter L3 checks complete:
  - Zero failures & complete structure → `completed`.
  - Documented isolated failures remain → `completed_with_issues` (**deliver immediately**; do not block the whole course).
- Final report must include real counts (ingested sources & coverage anomalies, planned/completed/failed/pending sections), open P0 QA IDs & dependency impacts, review hub paths, actual L1/L2/L3 verification scope, and concrete next-step pointers.
