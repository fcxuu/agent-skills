# The Seven Page Layouts

Each layout has a complete working example in `assets/starter.tex`. Copy its skeleton when authoring a new slide and replace only the content.

## Layout Decision Tree

Ask in order:
1. Is it slide 1? → **A (Cover)**
2. Does the slide hold only a single sentence (section divider or core thesis)? → **G (Statement Page)**
3. Does the slide have a figure?
   - Aspect ratio > 2.5 (very wide)? → **C (Wide Figure Top + Cards Bottom)**
   - Primarily experimental results (table, bar chart, curves)? → **E (Data Slide)**
   - Other figure? → **B (Figure Left + Cards Right)**
4. No figure: do items follow a sequential order?
   - Yes (steps, pipeline, derivation chain)? → **D (Card Flow)**
   - No (parallel causes, comparisons, definitions)? → **F (Parallel Cards)**

Pacing tip: avoid using the same layout for more than 3 consecutive slides—insert a Layout G divider or vary the structure.

## A · Cover

```latex
\title{English Paper Title}
\subtitle{中文标题 \muted{——}\ 课程名\dotsep 论文研讨汇报}
\coverkicker{PAPER SEMINAR}           % uppercase small label, terracotta
\covermeta{汇报小组：…\metasep 小组成员：A\dotsep B\metasep 汇报日期：…}
\coverref{Author A\dotsep Author B (2025), \textit{Venue}\par\muted{DOI: …}}
...
\begin{frame}[plain]\titlepage\end{frame}
```

- If the title wraps beyond two lines, insert manual `\\` at semantic breaks.
- Place paper provenance in `\coverref`; separate author names with `\dotsep` rather than Chinese `、`.

## B · Figure Left + Cards Right

```latex
\begin{columns}[T,onlytextwidth]
  \column{.54\textwidth}
    \safeimg[width=\linewidth,height=.62\textheight]{fig.pdf}{Caption. Source: ...}
  \column{.42\textwidth}
    \begin{callout}{Target}...\end{callout}
    \begin{warmcard}{Result}\eqline{...}\end{warmcard}
\end{columns}
\vfill
\begin{fignote}Note...\end{fignote}
```

- Column split: figure `.50–.58`, text `.38–.46`, sum `.96–.97`.
- For square or portrait figures, narrow the figure column to `.45–.50` to give cards more width.
- Right column holds 2–4 cards (typically `callout` first for definition/context, then `warmcard`).
- Figure `height=.55–.65\textheight` (use the lower end when a `fignote` is present).

## C · Wide Figure Top + Cards Bottom

```latex
\safeimg[width=.92\linewidth,height=.30\textheight]{wide.png}{Caption. Source: ...}
\begin{columns}[T,onlytextwidth]
  \column{.485\textwidth}\begin{callout}[\linewidth][1.3cm]{Reading Guide}...\end{callout}
  \column{.485\textwidth}\begin{warmcard}[\linewidth][1.3cm]{Key Formula}...\end{warmcard}
\end{columns}
```

- Wide figure `height=.26–.34\textheight`.
- Bottom cards **must share the same fixed height** (`[1.3cm]`, etc.).
- Also supports 3 columns (`.32\textwidth` each) when explaining three parts of a wide diagram.

## D · Card Flow

```latex
\begin{columns}[T,onlytextwidth]
  \column{.3\textwidth}\begin{warmcard}[\linewidth][2.3cm]{\stepnum{1}\ Step}...\end{warmcard}
  \column{.035\textwidth}\gaparrow
  \column{.3\textwidth}\begin{warmcard}[\linewidth][2.3cm]{\stepnum{2}\ Step}...\end{warmcard}
  \column{.035\textwidth}\gaparrow
  \column{.3\textwidth}\begin{warmcard}[\linewidth][2.3cm]{\stepnum{3}\ Step}...\end{warmcard}
\end{columns}
\contrastbar{Old Approach}{...}{New Approach}{...}     % optional contrast bar
```

- Column widths: 3 steps `.3 / .035`, 4 steps `.22 / .03`, 2 steps `.46 / .04`.
- Keep all step cards equal height; default `\gaparrow[1.2cm]` vertically centers against a `2.3cm` card (increase for taller cards).
- Split pipelines with > 4 steps into two rows or two slides; use `\downarrowc` for vertical flow.

## E · Data Slide

```latex
\begin{columns}[T,onlytextwidth]
  \column{.5\textwidth}
    {\densesize\warmrule
    \begin{tabular}{@{}lrrH@{}}\toprule ... \midrule ... \bottomrule\end{tabular}\par}
    \figsrc{Table note...}
    \begin{takeaway}Peak speedup \speedup{33.6$\times$}...\end{takeaway}
  \column{.46\textwidth}
    \safeimg[height=.6\textheight]{result.png}{Source: ...}
\end{columns}
```

- Booktabs three-line tables only (`\toprule`, `\midrule`, `\bottomrule`) styled with `\warmrule`.
- Use column type `H` (terracotta tint + bold terracotta, right-aligned) for at most one highlighted column per table.
- Right-align numbers; put units in headers or notes rather than repeating them in every cell.
- Plot-only variant (no table): plot on left `.58\textwidth`, 1–2 interpretation cards + `takeaway` on right.

## F · Parallel Cards

```latex
\begin{columns}[T,onlytextwidth]
  \column{.32\textwidth}\begin{warmcard}[\linewidth][2.6cm]{Title\\\muted{中文}}...\end{warmcard}
  \column{.32\textwidth}...
  \column{.32\textwidth}...
\end{columns}
\begin{takeaway}One-sentence synthesis.\end{takeaway}
```

- Column widths: 2 cards `.485`, 3 cards `.32`, 4 cards `.235` (use `\densesize` for 4 cards).
- Card titles may use two lines: `English\\\muted{中文}`.
- Never place arrows between parallel cards (if ordered, use Layout D).

## G · Statement Page

```latex
\begin{frame}
  \statementpage{One clear thesis sentence with a \key{key term}.}[Optional source or caveat]
\end{frame}
```

- Keep within ~40 Chinese characters (or concise equivalent) and at most one `\key`.
- Omit `\bititle`; the bottom navigation bar remains visible.

## Dimension Cheat Sheet

| Property | Value |
|---|---|
| Canvas | 16:9, `160mm × 90mm`, `10pt` base |
| Horizontal margins | `0.9cm` |
| Usable height (header to footer) | ~`\textheight`; cap figure `height` at `.65\textheight` |
| Card padding / gap | `6pt` / `5pt` |
| Sum of column widths | `.96–.97\textwidth` (`onlytextwidth`) |
