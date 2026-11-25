# Component Reference

All components are defined in `assets/beamerthemewarmpaper.sty`. Square brackets denote optional arguments.

## Containers

| Component | Appearance | Purpose | Quota |
|---|---|---|---|
| `\begin{warmcard}[width][fixed-height]{Title}` | Sand fill + 1pt warm border | Default content card: explanations, formulas, steps | ≤ 6 containers/slide |
| `\begin{callout}[width][fixed-height]{Title}` | Sand fill + terracotta left bar | Definitions, framing, figure reading guides | Same pool |
| `\begin{papercard}[width][fixed-height]{Title}` | Paper fill + thin border | Secondary nested layer or auxiliary note | Use sparingly |
| `\begin{takeaway}[width]` | Terracotta tint + left bar, no title | Single-slide conclusion (1–2 sentences) | ≤ 1/slide |
| `\begin{fignote}[width]` | Top thin rule + `7pt` muted gray | Footnote: errata, omissions, caveats, definitions | ≤ 1/slide, precede with `\vfill` |

- Leave `{}` empty to omit the card title line.
- Provide fixed height only when aligning side-by-side cards; overflowing text spills below without a LaTeX error—always inspect the rendered image.
- Default card text is `\bodysize`; put `\densesize` at the start of a card for dense content.
- Never nest identical card types; if layering is needed, put `papercard` inside `warmcard`.

## Equations

| Syntax | Purpose |
|---|---|
| `\eqline{formula}` | Centered display equation inside a card; auto-scales down if wider than `\linewidth` |
| `$...$` | Inline math |
| `\begin{align*}...\end{align*}` | Multi-line aligned derivation (wide cards only) |

- At most 3 `\eqline` entries per card; split into another card if more are needed.
- Add a one-line explanation under an equation with `{\densesize ...\par}`.
- Math font is STIX Two Math (calibrated to match PingFang SC stroke weight); do not revert to Computer Modern.

## Figures

```latex
\safeimg[height=.6\textheight]{path}{Caption. Source: ...}
\safeimg[width=.92\linewidth,height=.30\textheight]{wide.png}{Caption. Source: ...}
\figsrc{...}   % standalone caption when figure and caption sit in separate columns
```

- `\safeimg` defaults to `width=\linewidth,height=.42\textheight,keepaspectratio` inside `beamerthemewarmpaper.sty`. **`height=` is required** so images never push into the footer; pass explicit `width=` only when narrower than `\linewidth`.
- Caption width tracks the rendered image width (minimum 60% of column width), left-aligned.
- Prefer vector PDFs; raster images should be ≥ 150 dpi at displayed size.
- Display filenames containing underscores in prose via `\file{name_with_underscore.pdf}`.

## Inline Emphasis

| Macro | Visual Effect | Purpose |
|---|---|---|
| `\key{...}` | Terracotta bold | Core term, operator, or headline conclusion |
| `\speedup{...}` | Terracotta bold `11pt` | Hero metric (speedup, accuracy gain) |
| `\muted{...}` | Muted gray | Caveats, baselines, parenthetical context |
| `\textbf{...}` | InkMain bold | Small inline card labels ("Input:", "Output:") |
| `\textit{...}` | Italic | Paper titles, venues |

Combined `\key` + `\speedup` count must not exceed 4 per slide.

## Connectors & Badges

| Macro | Purpose |
|---|---|
| `\stepnum{n}` | Solid terracotta circular badge placed before step card titles |
| `\gaparrow[height]` | Horizontal arrow in a narrow column between adjacent cards |
| `\downarrowc` | Centered vertical arrow between stacked cards |
| `\flowarrow` | Inline long arrow (`A \flowarrow B`) |
| `\contrastbar{OldLabel}{OldDesc}{NewLabel}{NewDesc}` | Single "old → new" comparison bar (old side auto-muted) |
| `\dotsep` | Middle dot separator between names or metadata items |

## Tables

```latex
{\densesize\warmrule
\begin{tabular}{@{}lrrH@{}}
  \toprule
  \textbf{Col 1} & \textbf{Col 2} & \textbf{Col 3} & \textbf{Highlight}\\
  \midrule
  ... \\
  \bottomrule
\end{tabular}\par}
```

- Use `\toprule`, `\midrule`, `\bottomrule` only—no vertical rules.
- `H` is a right-aligned terracotta-tinted highlight column (at most one per table).
- Theme sets `\arraystretch` to `1.45`; locally reduce to `1.2` for tables with > 8 rows.
- Constrain wide text columns with `>{\raggedright\arraybackslash}p{.2\textwidth}`.

## Lists

- `itemize` uses terracotta small squares (level 1) and muted gray squares (level 2).
- Add `\setlength{\itemsep}{4pt}` (4–6pt) for readability.
- Cap lists at 5 items and 2 nesting levels; switch to Layout F (parallel cards) for richer items.

## Slide-Level Macros

| Macro | Purpose |
|---|---|
| `\bititle{English}{中文}` | Frame title (first line inside frame) |
| `\statementpage{Sentence}[Small note]` | Statement slide (Layout G) |
| `\decksections{A,B,C}` | Footer section bar list (must match `\section{}` order) |
| `\setaccent{HEX}` | Change accent color once for the entire deck |
| `\renewcommand{\decktotal}{16}` | Override auto-counted footer total page number |
