# 04 · Deterministic Figures, Visual Truthfulness & Provenance

## Semantics → Tool Selection (Probe Real Capabilities First)

| Figure Semantics | Preferred Available Tool | Hard Constraint |
|---|---|---|
| Clear textbook/slide original | Extract from source & embed | Never alter data, scales, or conclusions |
| Math functions, PDF/CDF, statistical curves | Python + Matplotlib / deterministic SVG or PNG from verified formulas/data | Explicit formula, parameters, domain; never eyeball or fabricate data curves |
| Algorithm control flow, logical steps | Native Obsidian Mermaid (or Graphviz if complex) | Preserve exact steps, branches, and arrow directions |
| Graphs, trees, FSMs, topologies | NetworkX + Matplotlib, Graphviz, or deterministic SVG | Exact node/edge counts, directions, weights, labels |
| Geometry, vectors, projections | Deterministic SVG / Python plotting | Verify geometric relations; never claim schematic ratios as exact measurements |
| Conceptual illustration (no exact data/topology) | Available drawing tool / controlled illustration | Must label `[教学示意]`; never pass off as source or experimental figure |

**Always prefer deterministic, verifiable graphics for numerical, mathematical, or topological content.** Never invent tools or auto-install packages (`brew`/`apt`/`pip`) without permission.

## Four-Tier Original-First Decision Rule

1. **Clear, trustworthy original:** Extract to `assets/original/` and embed directly—never redraw merely for uniform aesthetics.
2. **Blurry original with verifiable basis:** Redraw faithfully to `assets/generated/` from exact formulas, data, or topology. **Whenever the original or blurry crop can be extracted, archive it in `assets/original/`** for L2 comparison and cite its path in the caption. If unextractable, state so explicitly—never claim visual side-by-side verification.
3. **Pedagogically needed, no original exists:** Produce a clearly grounded `[教学示意]`, explicitly stating it is not from the source and not real experimental data (note any chosen demo parameters).
4. **Critical basis missing:** Never guess numbers, arrow directions, weights, or trends. Keep usable partial crops, log the gap in `QA.md`, and continue independent sections.

## Three Image Provenance Labels (Inline in Caption Only)

- **`[原图]`**: Extracted directly from course material; cite source file and page/slide.
- **`[忠实重绘]`**: Saved in `assets/generated/`; cite formula/data/topology basis, source location, and archived `assets/original/` comparison path (or explicitly state if unextractable).
- **`[教学示意]`**: Generated in `assets/generated/` or native Mermaid; explicitly state "non-experimental / illustrative" and demo parameters.

Use **exactly one** image provenance label per figure caption—do not wrap figures in extra redundant provenance cards.

## Archiving & Portable Relative Links

- Store files strictly under `COURSE_DIR/assets/original/` and `COURSE_DIR/assets/generated/`; never move/rename existing user assets or introduce external image hosts.
- Compute image paths relative to the **containing note's parent directory** via `os.path.relpath(target, start=note.parent)` with POSIX `/`, verified inside `COURSE_DIR` (e.g., `![caption|550](../../assets/original/P05/fig.png)` from `notes/ch05/note.md`—recompute for different depths, never hardcode `../../`). Properly URL-encode spaces/parentheses/`#`. Remove any embed whose image file does not exist.
- Place essential figures expanded inside their governing callout right next to the equation/definition they explain.

````markdown
> [!tip] 主成分方向与投影
> 数学条件：$\max_{\|w\|=1} w^\top S w$。
>
> ![PC1 投影示意|550](../../assets/generated/pca.svg)
>
> **图 2.1 [教学示意]**：以教学示例数据说明 PC1 投影方向；并非原课件实验结果。
> **观察**：沿 PC1 的投影方差较大。
````

## Deterministic Plotting & Light/Dark Theme Readability

- **Matplotlib / PNG / SVG:** Verify formulas, units, domain, and data before plotting. Use an opaque light background (`facecolor='white'` or warm light gray), title ≥ 12 pt, axis/legend ≥ 10 pt, and `bbox_inches='tight'` so dark-mode Obsidian users never see black text on a transparent background.
- **Mermaid inside Callouts:** Prefix **every line** (opening fence, edges, blank lines, closing fence) with `> `:

````markdown
> [!tip] 算法流程图 [教学示意]
> 分支方向必须与算法一致。
>
> ```mermaid
> flowchart TD
> A[输入] --> B{条件成立？}
> B -- 是 --> C[执行步骤]
> B -- 否 --> D[返回]
> ```
>
> **图注 [教学示意]**：流程示意，不代表实际运行测量。
````

- **Standalone SVGs:** Must be static and self-contained—no `<script>`, external fonts/images, or interactive handlers.

## Truthfulness QA & Safe Fallback

- **L1 (deterministic structure):** File exists and is readable, relative path stays inside `COURSE_DIR` and `VAULT_DIR`, caption has a valid provenance label, callout/Mermaid fences are intact.
- **L2 (substantive verification):** Cross-check key math/stat curves, all `[忠实重绘]`, and topology/geometry plots against archived originals, verified formulas, or data—never equate exit code 0 or L1 pass with mathematical accuracy or live Obsidian rendering.
- **When plotting tools are unavailable:** Fall back in order: clear original → available deterministic alternative (Mermaid or concise ASCII structure) → omit figure rather than faking it, log gap and fix hint in `QA.md`, and continue independent sections.
