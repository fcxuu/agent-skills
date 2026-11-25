# 05 · Knowledge Indexing, Syllabus Mapping & Review Hubs

> **Quick Index:** 1. File Splitting · 2. Incremental Syllabus Mapping (`source-map.md`) · 3. Cross-Slide Synthesis & Notation · 4. Course `README.md` Hub · 5. Links & Immutable Completed Notes · 6. Cross-Course Reuse · 7. Exam Review Hubs

## 1. File Splitting

- Default to **one teaching Markdown note per logical textbook/slide section**. Split only when a section spans multiple self-contained core topics, grows unwieldy, or contains a concept reused across chapters.
- Keep long proofs in folded callouts (`[!note]-`) rather than fragmenting into stub notes; spin off a standalone prerequisite/proof page only when genuinely reusable.
- Treat multiple slide decks in one course folder as one unified material set in source order; never invent fake textbook chapter numbers.

## 2. Incremental Syllabus Mapping (`raw-markdown/source-map.md`)

Maintain `COURSE_DIR/raw-markdown/source-map.md` incrementally after ingestion and before authoring each section. **Map logical knowledge sections, not files**: one deck may feed many sections, multiple decks may feed one section, and non-contiguous slices in one file are supported. This file stores **source coordinates and boundary verification status only**—never OCR body text, task 5-state progress, or a duplicate README.

### Fixed 4-Column Table & Coordinate Syntax

Keep the header starting with `逻辑章节 / 小节` (recognized by `scripts/check_vault.py`):

| 逻辑章节 / 小节 | 源课件与定位区间 | 边界状态 | 关联教学笔记 |
|---|---|---|---|
| Ch02 / 2.1 图的基本表示 | `lec02.pdf` → `raw-markdown/lec02.md` (`P.1-18`, `L10-L195`) | `verified` | `notes/02-01-graph-representation.md` |
| Ch02 / 2.2 随机游走 | `lec02.pdf` → `raw-markdown/lec02.md` (`P.19-32`, `L196-L340`); `lec03.pdf` → `raw-markdown/lec03.md` (`P.1-12`, `L1-L145`) | `verified` | `notes/02-02-random-walk.md` |
| Ch02 / 2.3 谱聚类（续） | `lec03.pdf` → `raw-markdown/lec03.md` (`P.13-28`, `L146-L310`) | `unverified` | - |

- **Segment syntax:** `<source-file> → raw-markdown/<file>.md (<page/slide range>, <optional line range>, <optional H:Heading>)`, separated by `;` in logical order. Represent non-contiguous slices in the same file as separate segments (1-based inclusive: `P.1-18`, `Slide.1-12`, `L10-L195`). All paths are relative to `COURSE_DIR`. Never fabricate missing page/line numbers.
- **Boundary states (`verified` / `unverified` only):** `verified` means source start/end boundaries were checked (it does **not** mean the note passed QA). Mark `unverified` and log the reason in `QA.md` when uncertain; keep linked note as `-` until created and verified.

### Right-Boundary Peek

1. After ingesting a source file or small batch, inspect headings, page/slide anchors, and adjacent boundaries to map confirmed sections—never preload the full course body.
2. If a deck ends mid-topic (incomplete derivation or explicit continuation), peek at the next deck's outline/opening pages (and ingest it first if safe) before authoring that section. An omitted proof alone does not automatically mean the unit is truncated.
3. If continuation material is unavailable, mark `unverified`, log in `QA.md`, postpone only affected sections, and continue independent ones.
4. Whenever a `raw-markdown/*.md` file is patched or edited, **re-verify every line range referencing it** in `source-map.md` before slicing.

## 3. Cross-Slide Synthesis & Notation Alignment

1. Read exact slices per `source-map.md`, retaining hypotheses, original equation numbers, captions, and transitions.
2. Reorganize logically (`motivation → definition → properties/theorems → derivation → algorithm/example`) without altering source hypotheses or inventing proofs.
3. Deduplicate overlapping slide coverage into one coherent note; split only if oversized or widely reused.
4. **Primary notation:** Pick one clearly sourced primary symbol system for genuinely equivalent objects; document alternate slide symbols in `[符号对照]` with provenance and dimensions. Never merge non-equivalent objects or rewrite `raw-markdown/`.
5. **Unresolved conflicts:** Keep both sources and coordinates visible, quarantine the disputed claim, and log in `QA.md`.

### Separation of Three Course-Level Files

- `README.md`: Student navigation hub (overview of sources, checkpoint progress summary, note links, selective keyword index, brief link to `source-map.md`).
- `raw-markdown/source-map.md`: Compact agent slicing map & two-state boundary status only.
- `QA.md`: Audit ledger for `unverified` boundaries, missing pages, stale line ranges, math/symbol conflicts, and verification evidence.

Under multi-agent execution, all three plus `.build-state.json` have **one single coordinator writer** (`references/08-multi-agent.md`).

## 4. Course `README.md` Navigation Hub

Place `README.md` alongside source slides in `COURSE_DIR`:
- **Checkpoint updates only:** Update at meaningful checkpoints (2–3 newly completed sections, chapter L3 completion, major failure/dependency shift, resume, or delivery)—not on every `processing`/`qa_pending` micro-transition.
- **Selective keyword index:** Include only high-value cross-chapter concepts, theorems, and algorithms pointing to concrete existing notes/headings.
- **Targeted reading:** Locate prerequisites via `README.md`, read `## 核心速览` first, and expand to exact definition/theorem sections only when needed.
- **Projection rule:** `README.md` may trail `.build-state.json` briefly between checkpoints, but must never report unverified sections as `completed`.

## 5. Links & Immutability of Completed Notes

- **Forward-only links from new notes:** When a new note relies on a completed prerequisite, add a relative Markdown link (`[马尔可夫性](../ch01/ch01-02-markov.md)`) in the **new note only**. Never edit a read-only `completed` note just to add a backlink—Obsidian's native Backlinks core plugin surfaces incoming links automatically.
- **Portable relative paths:** Compute all non-embed links relative to the referencing file's parent directory, verified inside `COURSE_DIR`.
- **Anti-overlinking:** Link each prerequisite once where pedagogically meaningful; avoid mass-creating broken `[[stub]]` links.
- **Post-completion risk notices:** If a P1/P0 issue is found in a completed note later, update `QA.md`, `.build-state.json`, and `README.md`/`review/` notices only—never silently overwrite the completed note body.

## 6. Cross-Course Sharing

Keep each course self-contained by default. Never automatically move or overwrite notes across courses; create shared notes only when genuinely reusable principles have clear payoff while preserving course-specific assumptions.

## 7. Exam Review Hubs (`review/`)

- Every teaching note has one self-contained `## 核心速览` (verified definitions, formulas, conditions, pitfalls; no subheadings, footnotes, or quarantined claims). Never duplicate full note bodies into `review/`.
- **Five Gates for Review Embeds:**
  1. Target `.md` exists and is non-empty.
  2. `## 核心速览` is unique and structurally compliant.
  3. `.build-state.json` status is `completed` and required L1/L2 QA passed.
  4. No open core P0 invalidates the summary conclusions.
  5. For native Obsidian `![[UniqueFileName#核心速览]]` embeds, the filename stem is **unique across the full `VAULT_DIR`** (if duplicate, fall back to a normal relative jump link `[查看核心速览](../notes/chXX/note.md#核心速览)` and log the collision in `QA.md`; never treat `![alt](note.md#heading)` as a verified heading embed).
- **Post-completion P0 demotion:** If a completed note is later demoted to `failed` for a core P0, remove/comment or annotate its embed line in `review/` with the QA ID—do not edit the protected note body.
- Do not fabricate "guaranteed exam topics"; label "课程重点" unless authoritative syllabus/exam evidence exists.
