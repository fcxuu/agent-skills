---
name: obsidian-self-study
description: |
  Build structured Obsidian self-study notes from course PDFs, PPT/PPTX slides, textbooks, and lecture handouts—covering document ingestion, math derivation bridging, original figure archiving, course indexing, exam review hubs, graded QA, and checkpoint resume.
  Use for batch-building or resuming a course inside an existing Obsidian vault. Skip for one-off Q&A, interactive tutoring, or live note-sync watchers.
metadata:
  version: "0.2.0"
---

# Obsidian Self-Study Course Builder

## Non-Negotiable Invariants

1. **One-shot batch build:** Decoupled from later reading. Do not configure file watchers, live sync, auto-regeneration of completed notes, or user-annotation merging.
2. **Existing Vault boundary:** Work strictly inside the user's `VAULT_DIR` and `COURSE_DIR` (`COURSE_DIR == VAULT_DIR` is allowed). Never create extra `ObsidianVault/` or `Courses/` wrappers, move/overwrite source slides, or edit `.obsidian/`.
3. **Unified course & note style:** Treat all decks/handouts in `COURSE_DIR` as one course in source order. Emit **one full Markdown per source** in `raw-markdown/`; author final notes by logical section. Blend concise lecture-note scannability with self-study textbook depth in one unified note set (never two copies, never tutor banter).
4. **Native Obsidian formatting:** Keep core definitions, essential diagrams, assumptions, and understanding bridges expanded; fold long proofs, solutions, and optional extensions (`[!note]-`). Preserve source equation numbers (`\tag{...}`); leave added bridge equations unnumbered.
5. **Verify facts, quarantine doubts:** Never guess past OCR damage, missing figures, or missing theorem premises. Isolate unverified claims locally (`> [!warning] [待核验隔离]`), log in `QA.md`, and keep them out of `## 核心速览`.
6. **Autonomous checkpointed progress:** Checkpoint every section in `.build-state.json`, summarize at chapters, skip blocked items without halting independent sections, and deliver `completed_with_issues` when appropriate. Never fabricate background runs, tool calls, or passed checks.

## Path & Link Contract

- **`SKILL_DIR`:** Directory containing this `SKILL.md` (from host path or verified `.agents/skills/obsidian-self-study/`). **Never treat `pwd` as `SKILL_DIR`**, and never write course outputs into `SKILL_DIR`.
- **`COURSE_DIR`:** All outputs (`.build-state.json`, `README.md`, `QA.md`, `raw-markdown/`, `notes/`, `assets/`, `review/`) live under `COURSE_DIR`.
- **Portable links:** Compute image links (`![caption|550](../../assets/...)`) and note/README links (`[title](../note.md)`) relative to the **containing Markdown file's parent** (`os.path.relpath`, POSIX `/`, inside `COURSE_DIR`). Review embeds use native `![[UniqueFileName#核心速览]]` only when vault-wide unique; on collision, emit a normal relative link and log in `QA.md`.
- **Missing specs:** Verify existence before reading; if a required stage file is missing, pause only dependent actions and log the blocker.

## Stage-Gated Module Loading

Load references **by stage**—never bulk-load `references/`. Reuse loaded specs within the same stage; after context compaction or across chapters, **re-read the active stage's core spec** rather than relying on memory.

| Layer | When to Load | Files (relative to `$SKILL_DIR`) | Key Outputs / Tools |
|---|---|---|---|
| **Baseline** | Start, resume, delivery, rule loss | `references/00-preflight.md`, `references/07-execution.md` | Preflight note, `.build-state.json` |
| **Ingestion** | Parsing PDF/PPT/handouts | `references/01-ingestion.md` | `raw-markdown/*.md`, `assets/original/` |
| **Mapping & Writing** | Syllabus map & note authoring | `references/05-knowledge.md`, `references/02-pedagogy.md`, `references/03-obsidian-style.md` | `raw-markdown/source-map.md`, `notes/**/*.md` |
| **Figures** *(cond.)* | Extraction, redraw, Mermaid/plots | `references/04-images.md` | `assets/original/`, `assets/generated/` |
| **QA** | L1/L2 section or L3 chapter checks | `references/06-quality.md` | `QA.md`, `scripts/check_vault.py` |
| **Multi-Agent** *(cond.)* | Worker contract, Commander request, or callable subagent + clear parallel payoff | `references/08-multi-agent.md` | `handoffs/<task-id>.md` (single shared writer) |
| **Templates** *(cond.)* | First creation of each artifact only | `templates/{note,README,QA,review}.template.md` | Skeleton only |

**Data slicing:** Keep full `raw-markdown/` on disk. Author each section by reading only its `source-map.md` segments plus `## 核心速览` (and needed definitions) of prerequisites.

## Pipeline Summary

1. **Preflight (`00-preflight.md`, `07-execution.md`):** Check paths, inputs, existing state/QA/README, ingestion tools, and permissions. Default is **single-agent**; only load `08-multi-agent.md` when criteria above hold.
2. **Ingest (`01-ingestion.md`):** Reuse verified `raw-markdown/`, or dynamically probe available MCP/local/multimodal parsers (1–2 representative math/figure pages first for new tools or large files). Run **coverage, density, and math/encoding checks** before declaring ingestion done.
3. **Map & Author (`05-knowledge.md`, `02-pedagogy.md`, `03-obsidian-style.md`):** Incrementally map logical sections in `raw-markdown/source-map.md` (peek next deck if a topic cuts off). Every note starts with one standalone `## 核心速览` (no subheadings, footnotes, `\label`, or unverified claims). Use structured native Obsidian callouts purposefully; tag substantive additions (`[推导补全]`, `[直觉桥接]`, `[拓展补充]`), cross-slide notation (`[符号对照]`), and unresolved conflicts (`[待核验隔离]`).
4. **Figures (`04-images.md`):** Prefer clear `[原图]`; deterministically produce `[忠实重绘]` (archiving originals when extractable) or labeled `[教学示意]`. Never fabricate curves/data.
5. **State, QA & Resume (`06-quality.md`, `07-execution.md`):**
   - Atomic state CLI: `python3 "$SKILL_DIR/scripts/state_tool.py" summary --course "$COURSE_DIR" --json` (`init`, `register-source`, `upsert-section`, `set-course-status`, `summary`).
   - Read-only L1 check: `python3 "$SKILL_DIR/scripts/check_vault.py" --vault "$VAULT_DIR" --course "$COURSE_DIR" --json` (exit 0 checks deterministic structure only; `not_checked` lists math/OCR/visual/L2/L3/live rendering).
   - Recovery precedence: **disk artifacts + QA evidence > `.build-state.json` > `README.md`**. `completed` notes are read-only snapshots. Max **2 substantive auto-fixes** per QA issue; log P0 in `QA.md` before marking `failed`.
6. **Deliver:** Once all planned sections reach `completed`/`failed` and chapter L3 completes, deliver (`completed` or `completed_with_issues`); if interrupted with `pending` left, flush checkpoints and mark `interrupted`. Report real counts, coverage anomalies, open P0s & dependency impacts, review hub paths, actual QA scope, and concrete next steps.
