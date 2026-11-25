# 02 · Pedagogy, Depth Adaptation & Gap Bridging

## Unified Teaching Style

Fuse two complementary qualities into **one single note set** (never two duplicate copies):
- **Concise lecture notes:** Surface core definitions, formulas, necessary conditions, and common pitfalls for rapid lookup and exam review.
- **Systematic self-study textbook:** Preserve full conceptual flow, original derivations, and key examples; bridge jumps that block comprehension with brief, rigorous steps.

Write in a self-study reference tone—never interactive tutoring chatter or conversational quizzes.

## Adapting Depth to Section Information Density

Adapt reconstruction depth per **logical section's information density**, not file extension:
- **Outline-heavy slides/handouts:** When supported by sound foundations, supply essential context, conditions, intermediate equations, algorithm steps, and intuition; tag substantive additions honestly so they are never mistaken for original textbook proofs.
- **Detailed textbooks:** Stay faithful to definitions, hypotheses, derivations, and worked examples; bridge only real comprehension jumps without mechanically re-proving every theorem or padding prose.
- **Mixed sources:** Adapt section by section. **An omitted proof in slides is not by itself a content error.**

## Four Provenance Categories

| Category | Tag | Boundary |
|---|---|---|
| Faithful source synthesis | *(no per-sentence tag)* | Distilling existing definitions, assumptions, conclusions, derivations, and examples from course sources |
| Substantive rigorous addition | `[推导补全]` | New intermediate steps strictly implied by stated premises and standard theorems |
| Pedagogical intuition aid | `[直觉桥接]` | Geometric/probabilistic/algorithmic intuition; never a substitute for proof |
| Beyond-source extension | `[拓展补充]` | Verifiable, high-value enrichment; folded by default (`[!note]-`) |

Tag only **substantive new knowledge/derivations**—never polish, heading edits, or transitions. Use inline bold prefixes (`**[推导补全]**`, `**[直觉桥接]**`) for 1–2 sentence additions; use expanded `[!tip]` for multi-step math, folded `[!note]-` for extensions, and expanded `[!warning] [待核验隔离]` for unverified doubts (see `references/03-obsidian-style.md`). **Never disguise unverified claims as proven facts.**

## Five Admission Criteria for Derivation Bridging

1. State premises and notation explicitly (independence, invertibility, convergence, dimensions).
2. Ensure each added step follows verifiably from source formulas or standard theorems.
3. Never smuggle undeclared strong assumptions. An **auxiliary working assumption for a special-case illustration** must be explicitly marked as extra and non-source; if a **core theorem hypothesis** is missing and unverifiable, isolate the claim instead of patching over it.
4. Keep original textbook equation numbers (`\tag{3.7}`); leave agent-added intermediate equations unnumbered and consistent with the primary notation.
5. Multi-step added derivations or critical added conditions trigger L2 mathematical verification.

## Five Substantive Grounds for Local Quarantine

Quarantine **only the specific affected claim** (never abandon the whole section) when reliable sources/standard theorems cannot resolve:
1. Missing core hypothesis required for the main claim.
2. Undefined key variable or operator with multiple incompatible interpretations.
3. Corrupted OCR, missing figure, or missing page making a core formula/number unrecoverable.
4. Irreconcilable contradiction across course sources on definitions, conditions, or main claims.
5. Important agent-added argument lacking rigorous mathematical justification.

Keep all reliable knowledge in the section; mark the suspect spot inline with `> [!warning] [待核验隔离]` citing source file, page/line, risk, and QA ID, log evidence & downstream dependencies in `QA.md`, and keep moving. **`## 核心速览` must contain only verified claims, necessary conditions, and concise reliable summaries—never long additions, folded extensions, or quarantined claims.**

## Source Traceability & Primary Notation System

Trace cross-slide content via `raw-markdown/source-map.md` (see `references/05-knowledge.md`). For **genuinely equivalent** mathematical objects, pick one clearly sourced primary notation across the note and added steps; list alternative slide symbols in a `[符号对照]` table/list with source provenance and dimensions while preserving each source's original numbering and unique assumptions. Never merge formulas with different hypotheses; never rewrite `raw-markdown/` to force unified notation.

## Reconstruction Rules

1. **Stay faithful to sources:** Preserve mathematical meaning, hypotheses, and conclusions; cite evidence if the source itself contains an error.
2. **Bridge only real jumps:** Explain the theorem, algebraic identity, independence condition, or domain constraint connecting step A to step B (usually 1–3 sentences or one intermediate equation)—do not narrate trivial algebra line by line.
3. **Unproved theorems in slides:** State the theorem, its hypotheses, and why it is invoked here; fold full proofs or split to a dedicated page only when pedagogically worthwhile.
4. **Match knowledge type:** Concepts → boundaries & examples; theorems → hypotheses & conclusion; algorithms → core idea & steps; statistical methods → assumptions & applicability. Keep key source examples and diagrams.
5. **Restraint:** Add figures, examples, or notes only when they remove real friction; avoid filler storytelling or graduate-level detours.
6. **No rigor shortcuts:** Intuition aids understanding; never present loose analogy as proof.

## Teaching Note Structure

- Standalone `## 核心速览`: verified core conclusions, formulas, conditions, and pitfalls only.
- Main body follows logical course flow with purposeful definition/formula, intuition, and condition callouts.
- Figures essential for comprehension remain expanded inside their corresponding callout.
- Long proofs and exercise solutions fold by default; **bridges required for later reasoning stay expanded**.
- Link to existing prerequisite notes rather than spawning thin stub pages for every term.

## Example: Bridging Only the Critical Step

Source formula:

$$
M_{Z^2}(t)=\frac{1}{\sqrt{2\pi}}\int_{-\infty}^{\infty}e^{-(1-2t)z^2/2}\,dz=(1-2t)^{-1/2}.
$$

**[推导补全]** Apply the Gaussian integral $\int_{-\infty}^{\infty}e^{-ax^2}dx=\sqrt{\pi/a}$ with $a=(1-2t)/2$, requiring $t<1/2$. No need to re-derive moment generating functions from scratch; link to an existing prerequisite note if present. Verify whether a statement is a *definition* vs. a *theorem* before attempting to "prove" it.
