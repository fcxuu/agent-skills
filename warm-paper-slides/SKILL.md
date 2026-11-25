---
name: warm-paper-slides
description: |
  Build clean, restraint-focused Chinese-English bilingual academic presentations using LaTeX Beamer in the "Warm Paper" visual system (warm paper background, single terracotta accent, flat thin-bordered cards).
  Covers typography and color tokens, 7 page layouts (A-G), figure-text balance, card hierarchy, equation and table styling, xelatex compilation, and visual contact-sheet inspection.
  Use when the user asks to create paper seminar, midterm/final, course presentation, or group meeting slides in Beamer/LaTeX, or convert lecture notes/scripts into compilable xelatex slides. Skip for PowerPoint (.pptx) files or general LaTeX syntax Q&A.
---

# Warm Paper Slides

Goal: every slide should read like a well-typeset academic magazine page—quiet paper background, a single accent color, clear typographic hierarchy, and zero visual clutter.

The theme file already implements all visual styling. Your job is to **choose the right layout, keep per-slide density controlled, use the provided components**, then compile and visually inspect the rendered pages.

## Path Contract

- **`SKILL_DIR`**: the directory containing this `SKILL.md` file. Resolve it from the host-provided skill path (never assume `pwd` is `SKILL_DIR`).
- Keep your working directory in the user's target project folder; invoke bundled scripts via `"$SKILL_DIR/scripts/..."`.

## Bundled Files

| Path (relative to `$SKILL_DIR`) | Purpose |
|---|---|
| `assets/beamerthemewarmpaper.sty` | Theme: fonts, colors, header/footer, cards, figures, tables, macros |
| `assets/starter.tex` | Working starter deck with one page for each of the 7 layouts (A–G) |
| `assets/starter.pdf` | Reference rendered output of `starter.tex` |
| `assets/placeholders/` | Three aspect-ratio placeholder images (`wide_2to1.png`, `wide_5to1.png`, `tall_2to3.png`) |
| `scripts/lint_deck.py` | Static rule lint + 2-pass `xelatex` build + contact sheet (`_sheet.png`) + single-page zoom (`--page`) |
| `references/design-principles.md` | Aesthetic rationale and prohibited patterns |
| `references/layouts.md` | Selection rules, dimensions, and LaTeX skeletons for layouts A–G |
| `references/components.md` | Component reference, arguments, and per-slide quotas |
| `references/troubleshooting.md` | Compilation, font, and layout fixes |

## Workflow

1. **Digest material and plan pagination.** One slide = one claim. Draft a slide plan first: page number, English title, Chinese subtitle, layout letter (`A`–`G`), and figure(s). If content exceeds what comfortably fits in 16:9, split the slide—never shrink body text to cram.
2. **Initialize the deck.** Start from `$SKILL_DIR/assets/starter.tex`. Copy `$SKILL_DIR/assets/beamerthemewarmpaper.sty` into the deck directory if the user needs a self-contained source tree (`lint_deck.py` also auto-injects `$SKILL_DIR/assets//` into `TEXINPUTS` during local checks). Declare 3–5 section names in `\decksections{...}` matching the exact order of `\section{...}` commands in the body.
3. **Author slides from the 7 layouts.** Pick one layout per slide from `references/layouts.md` and adapt its skeleton. Do not invent ad-hoc layouts.
4. **Lint and compile.** Run:
   ```bash
   python3 "$SKILL_DIR/scripts/lint_deck.py" deck.tex
   ```
   Optional flags: `--no-build` (static checks only), `--page 3,5` (also render 110 dpi zoom PNGs for specific pages), `--json` (machine-readable output). Fix every `FAIL` before proceeding.
5. **Visually inspect.** Open `deck_sheet.png` and review every slide against the visual checklist below (use `--page N` to inspect dense pages at 110 dpi). Return to step 3 for any layout defect.

## The Seven Layouts

| ID | Name | When to Use |
|---|---|---|
| A | Cover | Slide 1: `\titlepage` inside `\begin{frame}[plain]` |
| B | Figure Left + Cards Right | Near-square or aspect ratio 1.2–2.5 figure + 2–4 interpretation cards |
| C | Wide Figure Top + Cards Bottom | Wide figure (aspect ratio > 2.5) full-width on top + 2–3 cards below |
| D | Card Flow | Sequential 2–4 step pipeline/derivation connected with arrows |
| E | Data Slide | Table and/or experimental plot + a single `takeaway` conclusion |
| F | Parallel Cards | 2–4 parallel concepts, motivations, or comparisons (no arrows) |
| G | Statement Page | Section transition or single core thesis (one sentence on the whole slide) |

See `references/layouts.md` for exact column widths, fixed card heights, and skeletons.

## Hard Rules

Most of these are checked automatically by `lint_deck.py`:

- **Single accent color.** Use only the 6 theme tokens (`BgPaper`, `InkMain`, `InkMuted`, `AccentTerra`, `CardSand`, `BorderWarm`) plus derived `TerraTint`. Never write raw color names (`red`, `blue`, etc.).
- **At most 4 inline highlights per slide** (`\key` + `\speedup` combined) and **at most 1 `takeaway`**.
- **Standard bilingual slide titles:** `\bititle{English Title}{中文副标题}`. Use Title Case for English; keep the Chinese subtitle to ≤ 12 characters.
- **Typography tokens only:** `\bodysize` (default card body), `\densesize` (dense math or 4+ cards), `\notesize` (footnotes), `\capsize` (captions). Never use `\tiny`, `\scriptsize`, `\Large`, `\LARGE`, `\huge`, `\Huge`.
- **Safe figures only:** use `\safeimg[...]{path}{caption and source}`—never raw `\includegraphics`. `width` defaults to `\linewidth` inside the theme macro; **`height=` is required** (pass explicit `width=` only when narrower than `\linewidth`). Always cite the figure source in the caption.
- **Equations inside cards:** use `\eqline{...}` (auto-scales if over-wide). Never use `\[ ... \]` or `equation`.
- **No default Beamer blocks, shadows, rounded corners, gradients, icons, or emoji.**
- **Bottom caveats/errata/disclaimers** belong in `fignote` (pushed down with `\vfill`), not inside main content cards.

## Visual Inspection Checklist

When reviewing `deck_sheet.png` (and `--page N` close-ups), verify on every slide:

1. Content never collides with the footer; at least one line of breathing room remains above the bottom bar.
2. Side-by-side cards align at the top and share identical height (use fixed height parameter `[height]`).
3. Images are unstretched (`keepaspectratio`) and captions left-align with the image edge.
4. One focal takeaway or `\key` immediately draws the eye.
5. Left and right columns feel visually balanced; adjust column widths or switch layouts if lopsided.
6. No orphan single character wraps onto a new line in titles or card headers.
7. Footer active section highlights accurately and page numbers are consecutive.

## Allowed Customizations

Only two customizations are permitted:
1. `\setaccent{HEX}` to change the single accent color once per deck (medium saturation, ≥ 4.5:1 contrast on `#FAF8F5`, e.g., deep blue `2F5D8A` or forest green `3F6B4E`).
2. Font overrides on non-macOS systems (see `references/troubleshooting.md`).

Do not alter the other color, spacing, or size tokens—they are calibrated as a system.
