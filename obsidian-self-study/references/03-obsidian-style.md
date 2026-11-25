# 03 · Obsidian Structured Callout & Math Formatting

> **Quick Index:** Callout Semantics · `## 核心速览` Contract · Provenance & Isolation Callouts · Math Tag/Reference Boundaries · Mermaid & Image Nesting · Math & Syntax Example

## Core Principle

Use **native Obsidian** Markdown, Callouts, wikilinks/relative links, and MathJax—no CSS snippets or third-party plugins required. Keep notes readable for students and cleanly editable by agents. Never leak internal style codenames into generated student notes.

## Callout Semantics

| Content Role | Callout Type | Default State |
|---|---|---|
| Section quick summary | `[!abstract]` | Expanded |
| Definitions, theorems, core formulas | `[!info]` | Expanded |
| Key intuition, essential bridges, core figures | `[!tip]` | Expanded |
| Assumptions, limits, pitfalls, quarantine | `[!warning]` | Expanded |
| Long proofs or full derivations | `[!note]-` | Folded |
| Worked examples | `[!example]` + `[!example]-` solution | Problem expanded, solution folded |
| Extra background / extensions | `[!note]-` | Folded |

Give each card one main job; group tightly coupled formulas in one card rather than boxing every single equation. Avoid deep callout nesting. Place essential images, captions, and explanations **inside** their governing callout.

## Stable `## 核心速览` Boundary (Exam Review Contract)

Every formal teaching note must have **one and only one** level-2 heading `## 核心速览`, placed right after YAML frontmatter and `# Note Title`, before all detailed body sections. The review embed stops at the next `## ` heading:
- **Forbidden inside `## 核心速览`:** any subheadings (`###` through `######`), a second `## 核心速览`, MathJax `\label{}`/`\eqref{}`, Markdown footnotes (`[^1]`), unnecessary block IDs (`^block-id`), long derivations, folded extensions, quarantined claims, or dangling references ("see proof below", "as in the figure later").
- Use **bold bullet items** or callout titles for internal grouping so review outlines stay clean.
- Review hubs embed completed notes via Obsidian native `![[UniqueFileName#核心速览]]` (omitting `.md`) **only after confirming filename uniqueness across the full vault**. On collision, emit a normal relative link `[查看核心速览](../notes/ch05/target.md#核心速览)` and log the collision in `QA.md`—never pass `![alt](note.md#heading)` off as a verified native heading embed, and never rename read-only completed notes to resolve collisions.

## Provenance Tags & Quarantine Callouts

- **Short additions (1–2 sentences):** Inline `**[推导补全]** ...` or `**[直觉桥接]** ...` without forcing a separate card.
- **Multi-step derivations / deep intuition:** Expanded `> [!tip] [推导补全] ...` or `> [!tip] [直觉桥接] ...`.
- **Extensions:** Folded `> [!note]- [拓展补充] ...`.
- **Unverified quarantine:** Expanded `> [!warning] [待核验隔离] ...` with source file, page/line, risk, and QA ID. Never hide unverified risks inside folded blocks.
- **Cross-source symbol mapping:** Use a `[符号对照]` table/list mapping source symbol, primary note symbol, mathematical object, and provenance.

Every line and blank separator inside a callout must keep the `> ` blockquote prefix:

````markdown
> [!tip] [推导补全] 为什么成立？
> 在已核实的前提下，由前式和标准定理得到：
>
> $$
> A=B
> $$

> [!tip] [直觉桥接] 几何意义
> 可以这样理解……（仅为直觉，不替代证明）。

> [!note]- [拓展补充] 相关理论
> 经核实且有必要的延伸内容。

> [!warning] [待核验隔离] 来源：lec04.pdf P.18
> 主结论的核心假设尚不明确，暂不将其作为已证实结论；详见 QA.md。
````

## Math Identifier & Equation Reference Boundaries

- **Do not use `\label{...}` or `\eqref{...}` by default** in notes or `## 核心速览`—embedding multiple notes on one review page can trigger duplicate-label or unresolved-reference failures in MathJax.
- Preserve original textbook numbering via `\tag{3.7}` and reference it in prose ("由式 (3.7) 可得"); leave agent-added bridge equations unnumbered. Do not renumber an entire course.

## Images, Relative Links & Mermaid inside Callouts

- Compute all local image paths (`![caption|550](../../assets/original/P05/fig.png)`) and ordinary note links (`[title](../ch04/note.md)`) relative to the **current Markdown file's directory**, strictly inside `COURSE_DIR`.
- Tag each figure caption with **exactly one** image provenance label (`[原图]`, `[忠实重绘]`, or `[教学示意]`)—do not stack redundant `[直觉桥接]` cards around a figure.
- When placing a Mermaid block inside a callout, **every line—opening fence, diagram edges, internal blank lines, and closing fence—must start with `> `** so the callout does not break.
- Static PNG/SVG assets must maintain high contrast across both light and dark Obsidian themes (details in `references/04-images.md`).

## Math Formatting & Reference Example

Use `$...$` inline, `$$...$$` display, and `\begin{aligned}...\end{aligned}` for multi-line math; use `\boxed{}` sparingly for hero results. Never claim Obsidian rendering is verified unless actually inspected in Obsidian.

````markdown
## 核心速览

> [!abstract] 核心结论
> 若 $Z\sim N(0,1)$、$U\sim\chi^2_\nu$ 且独立，则
> $$T=\frac{Z}{\sqrt{U/\nu}}\sim t_\nu.$$

## 定义与理解

> [!info] t 分布定义
> 上式中 $\nu$ 是自由度。

> [!tip] 关键图解
> 由于分母具有随机性，t 分布具有更厚的尾部。
>
> ![t 分布与正态分布对比|550](../../assets/generated/t-vs-normal.svg)
>
> **图 1.1 [教学示意]**：对比尾部随 $|t|$ 变大时的密度。

> [!warning] 适用条件
> 精确的经典单样本 t 结论需要独立正态样本等假设。

> [!note]- 相关推导
> 教材原有推导与必要关键桥接。

> [!example] 练习
> 写出样本均值的 t 统计量。

> [!example]- 参考解答
> 这里给出完整解法。
````

Always compute actual relative paths from the current note's parent directory; never leave links to non-existent image files.
