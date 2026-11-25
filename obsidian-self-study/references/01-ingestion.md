# 01 · Tool-Agnostic Document Ingestion

## Goal & Output Contract

Convert course PDFs, PPT/PPTX decks, textbooks, handouts, or existing structured text into **source-traceable, verifiable raw Markdown** for downstream teaching reconstruction. This module is **not bound to any specific OCR vendor**. Leave all source files untouched in place.

- **One complete Markdown per source file** under `raw-markdown/`; do not pre-split raw captures by section. Final teaching notes are organized by logical section and slice-read on demand.
- Preserve heading hierarchy, full text, LaTeX math, tables, key figures with provenance, and **reliable original page numbers (`P.12`), slide numbers (`Slide.12`), and heading anchors**; mark missing coordinates honestly instead of guessing.
- Outputs must answer: *which source file, which pages/slides were parsed, where omissions or uncertainties exist, where extracted images live, and which method ran*.
- If inputs are already readable Markdown/LaTeX, verify and normalize directly—do not run pointless OCR.

## Tiered Capability Discovery & Quality-Driven Routing

- **Tier 0 — Reuse verified artifacts:** Check existing `raw-markdown/<source>.md`. Verify non-empty content, match to the current source (prefer SHA-256 hash, else path/size/history/QA), and credible coverage notes. If evidence is insufficient, mark "needs verification" rather than assuming completeness.
- **Tier 1 — Mounted document-parsing / OCR MCP tools:** Dynamically inspect callable tools, parameters, accepted formats, page mapping, and math/image fidelity. Never assume a named tool exists or handles PPTX.
- **Tier 2 — Existing local CLIs/libraries:** In shell-enabled hosts, check already-installed parsers (e.g., MinerU, Marker, PyMuPDF, python-pptx/docx extractors). Do not install heavy packages, mutate system Python, or overwrite sources for convenience.
- **Tier 3 — Host native multimodal vision:** If the host supports reading pages/images natively, transcribe in small controlled page batches and write to disk with explicit page markers; never load an entire textbook into one turn.

**Tiers govern discovery order, not a rigid quality ranking.** Choose the most reliable, cost-effective available method for the file's actual layout. If one tool fails on specific pages, patch only those pages with an alternate capability and merge into the single raw Markdown for that source. Do not re-parse the whole course just to compare tools.

### File-Type Routing Hints

| Source Characteristics | Preferred Capabilities | Key Risks |
|---|---|---|
| Selectable-text PDF, simple layout | Direct text/structure extraction; math parser if formula-heavy | Reading order, sub/superscripts, multi-column, vector equations |
| Scanned PDF, image slides, math-heavy PDF | Layout analysis + math OCR / dedicated document parser | Dropped pages, hallucinated formulas, figure-text misalignment |
| Native PPTX / DOCX | Structured extraction of text, shapes, embedded images; supplement complex slides with rendered vision/OCR | Equation objects, SmartArt, grouped shapes, reading order, speaker notes |
| Handwritten or unusual layouts | Dedicated OCR or page-by-page multimodal verification | Misread symbols, detached figure captions |
| Existing Markdown / LaTeX | Direct structural and link/image audit | Broken local paths, incomplete source |

Structured XML extraction from PPTX/DOCX does not guarantee fidelity for embedded equations or text inside images—supplement with visual checks when samples reveal gaps.

### 1–2 Page Probe (New Tools or Large/Complex Files)

Before batch parsing, probe **1–2 representative pages rich in equations and figures** to inspect math notation, table/layout fidelity, image extraction, and reading order. Short files or already-proven tool/format pairs may skip probing with stated rationale. **Probe success does not prove full-document success.**

## Post-Ingestion Lightweight Acceptance Gate (Does Not Replace L2 QA)

1. **Coverage:** Record total source pages `N_src` when reliably obtainable and the set of actually parsed pages `P_parsed`; check for missing or duplicated pages. Anchor count alone is insufficient—empty shell pages do not count as parsed (genuine cover or image-only pages are documented exceptions). If page mapping is unavailable, state "page-level coverage unverified" instead of claiming `N_parsed = N_src`.
2. **Density:** Flag unexpectedly short non-cover/non-image pages, garbled text runs, or huge blank gaps for targeted re-check/re-scan. Do not fail genuine diagram-only slides on a rigid char count.
3. **Sanity:** Spot-check math-heavy pages for fractions, sub/superscripts, matrices, operators, quantifiers, plot numbers, replacement chars ``, broken math delimiters, or vanished core equations. State clearly that spot-checks cover only sampled pages.

**Exit code 0 or a non-empty file ≠ passed ingestion.** Attempt targeted page recovery first; preserve error evidence, isolate unrecoverable ranges in `QA.md`, and continue other reliable sections without treating damaged passages as verified prerequisites.

## Storage, Anchors & Logging

- Save one full Markdown per source under `COURSE_DIR/raw-markdown/` (using stable, collision-safe filenames).
- Insert lightweight anchors when page/slide numbers are reliable (e.g., `<!-- source-page: 12 -->`); never fabricate page numbers. When `raw-markdown/*.md` is patched or edited later, re-verify every line range referencing it in `raw-markdown/source-map.md`.
- Archive reliably extracted original figures under `assets/original/` with source filename and page/slide provenance, verifying each file exists and is readable (see `references/04-images.md`).
- **Keep `README.md` concise:** log only `source → raw-markdown → coverage status → brief anomaly/QA ID`. Put tool names, probe/fallback notes, missing-page details, and OCR correction evidence into `QA.md`.
- Confirmed OCR corrections verified against the original source are recorded with evidence and applied during teaching reconstruction—never silently guess fixes.

## Permissions, Cost & Safety

- Prefer pre-existing authorized local tools; never assume an external service is free or available.
- Obtain explicit approval before installing heavy dependencies, incurring material API cost, changing environment configs, or uploading private course files externally.
- Make every ingestion artifact resumable on disk without building a general live-sync engine.
