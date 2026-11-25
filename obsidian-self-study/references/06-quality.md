# 06 · Graded QA, Local Rework & Risk Propagation

> **Quick Index:** 1. Three QA Tiers (L1/L2/L3) · 2. Deterministic L1 Scope (Summary, Links, Images, Source Map) · 3. Pedagogy & Quarantine Checks · 4. Defect Severity (P0/P1/P2) · 5. Local Rework Cap · 6. Post-Completion Risk Handling · 7. `check_vault.py` Boundaries

## 1. Three QA Tiers

| Tier | Trigger | Required Checks |
|---|---|---|
| **L1 (Baseline)** | Every formal note | Unique `## 核心速览` right after title with no subheadings/`\label`/`\eqref`/footnotes; valid `source-map.md`, LaTeX, relative links/images inside `COURSE_DIR`, image file existence & provenance label, intact Callout/Mermaid quote prefixes |
| **L2 (Risk Review)** | Suspect OCR/ingestion, dense math, cross-slide synthesis, multi-step `[推导补全]`, key plots / `[忠实重绘]` | Cross-check `source-map.md` and original source formulas/hypotheses/notation; verify added derivations step by step; verify key curves, `[忠实重绘]` (against `assets/original/` when extractable), and topology diagrams against formulas/data |
| **L3 (Chapter)** | End of each chapter | Chapter source coverage vs. `source-map.md`, cross-slide boundaries, dependency risk propagation, duplicate/conflicting concepts, notation consistency, chapter review hub, navigation & figure completeness |

Static checks never replace mathematical verification or live Obsidian reading-view inspection. Never report checks you did not run.

## 2. Deterministic L1 Acceptance Scope

- **Summary & math tags:** Exactly one `## 核心速览` between `# Title` and the next `## ` heading; no `###+`, no `\label{}`/`\eqref{}`, no footnotes `[^1]`, no stray block IDs `^...`. Native review embeds (`![[UniqueFileName#核心速览]]`) require vault-wide filename uniqueness; collisions must use normal relative links and be logged in `QA.md`. Original textbook numbers use `\tag{...}`; added equations stay unnumbered.
- **Images & links:** All relative Markdown image/note links resolve from the containing `.md` directory and stay strictly inside `COURSE_DIR` (and `VAULT_DIR`); OS absolute paths or course escapes are errors. Image targets exist and carry one provenance tag (`[原图]`/`[忠实重绘]`/`[教学示意]`). Callout-nested Mermaid fences and blank lines preserve `> ` prefixes.
- **Source map:** Every `source-map.md` entry cites real source/raw-markdown files and valid coordinate syntax (`verified` means boundary-checked only, never QA-passed). Stale line ranges after `raw-markdown/` edits must be re-verified before reuse.
- **L2 image verification:** For key math/stat plots, geometry/graph diagrams, and all `[忠实重绘]`, cross-check against archived originals (`assets/original/`) and verified formulas/data; check light/dark theme contrast (opaque light background, title ≥ 12 pt, labels ≥ 10 pt). If an original was unextractable, state explicitly that no visual original comparison occurred.

## 3. Pedagogical Addition & Quarantine Checks

- Faithful synthesis needs no per-sentence tag; substantive additions use `[推导补全]`, `[直觉桥接]`, `[拓展补充]`. Complex multi-step additions trigger L2.
- Distinguish explicit non-source illustrative assumptions from missing core theorem hypotheses (missing core hypotheses must be quarantined, not patched over).
- Verify `[符号对照]` traces to real source pages and genuinely equivalent objects/dimensions.
- Quarantine (`[待核验隔离]`) applies only to real substance risks (missing core premise, undefined symbol, corrupted source, irreconcilable conflict, unjustified derivation)—never merely because slides omitted a proof. Every quarantine block must link to a `QA.md` entry and stay out of `## 核心速览`.

## 4. Defect Severity

- **P0 (Blocker):** Wrong or unconfirmable core formula/theorem, wrong key data plot, or missing source preventing verification of a main conclusion. Cannot be offset by good formatting; quarantine affected claim and dependencies; note cannot be marked `completed`.
- **P1 (Major):** Missing key comprehension bridge, essential diagram, review item, or important link. Fix locally when possible; otherwise log clearly.
- **P2 (Minor):** Minor heading inconsistency, slight redundancy, minor formatting polish. Fix opportunistically; never loop endlessly.
- **Unverifiable** is its own evidence state—never disguise it as confirmed-true or confirmed-false.

## 5. Local Auto-Repair & Stop-Loss

1. Pinpoint the exact source file, page/line (if known), section, formula, or callout and log observed evidence.
2. Repair locally only when grounded in solid evidence (source check, verified OCR fix, link/path/callout fix)—never guess unconfirmable source text.
3. **Cap at 2 substantive auto-repair attempts per QA issue**; if still unresolved, stop retrying, quarantine/record in `QA.md`, and move on.
4. Re-check the edited passage and immediate context without spilling edits into unrelated completed files.
5. On unresolvable P0: write `QA.md` **first**, then record `failed` in `.build-state.json` (with failure evidence), sync `README.md` at checkpoints, and propagate downstream risk while continuing independent sections.

## 6. Post-Completion Risk Handling (Protected `completed` Notes)

A protected `completed` note (`status == completed`, non-empty disk file, passed L1/L2, no open core P0) is **read-only**. When new issues surface later, update **metadata and external navigation only—never overwrite the completed body automatically**:

| New Finding | `QA.md` & Dependencies | `.build-state.json` | `README.md` / `review/` | Completed Note Body |
|---|---|---|---|---|
| **P2** minor polish | Log issue & evidence | Keep `completed` | No extra notice needed | Do not modify |
| **P1** local gap (main claim holds) | Log QA ID, location, scope | Keep `completed`, append `qa_ids` | Add brief risk note where helpful | Do not modify |
| **P0** core definition/premise/claim error | **First** log source evidence, QA ID, and downstream dependents | **Demote `completed → failed`** and append `qa_ids` (never `pending`/`processing`) | Remove/warn affected embeds and stop treating as verified prerequisite | **Never auto-overwrite or regenerate** |

Trace downstream risk via actual links/dependencies (not mere keyword overlap). **Status demotion is NOT body-write permission.** Distinguish genuine post-QA P0 demotion from corrupt "ghost completed" metadata (missing file/QA). Controlled body edits require explicit user naming of the note and scope plus `.md.bak` backup (`references/07-execution.md`).

## 7. Static Checker (`scripts/check_vault.py`) & Its Limits

Run from any directory using verified `$SKILL_DIR`:

```bash
python3 "$SKILL_DIR/scripts/check_vault.py" --vault "$VAULT_DIR" --course "$COURSE_DIR" --json
```

- **Exit codes:** `0` = no deterministic errors (warnings or uninitialized vault allowed); `1` = deterministic error(s); `2` = invalid arguments or out-of-bounds path.
- **Deterministic output:** `issues` sorted by `(severity, file, line, code)`; `not_checked` explicitly lists `mathematical_correctness`, `ocr_fidelity`, `visual_chart_accuracy`, `obsidian_runtime_rendering`, and `qa_l2_l3_evidence`.
- **Do not equate** static `error` with QA `P0` or static `warning` with `P1`; assess pedagogical impact separately. `completed_with_issues` is a delivery status, not a certificate of zero defects.
