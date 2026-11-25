# Troubleshooting

## Compilation

| Symptom | Cause | Fix |
|---|---|---|
| `File 'beamerthemewarmpaper.sty' not found` | Theme file not in deck directory or `TEXINPUTS` | Use `lint_deck.py` (auto-injects `$SKILL_DIR/assets//`), copy the `.sty` next to `deck.tex`, or set `TEXINPUTS="$SKILL_DIR/assets//:"` |
| `The font "PingFang SC" cannot be found` | Non-macOS host | Before `\usetheme{warmpaper}`, define `\newcommand{\warmcjkfont}{Noto Sans CJK SC}` and `\newcommand{\warmlatinfont}{Noto Sans CJK SC}` (Windows: `Microsoft YaHei`). Adjust `\warm@latinfeatures` if the font lacks Regular/Semibold sub-names |
| `Missing character` | Font lacks glyph (common with emoji or bare Unicode math symbols) | Remove emoji; wrap math symbols in `$...$` |
| Footer total page shows `??` or wrong number | Compiled only once | Run `xelatex` twice (`lint_deck.py` runs 2 passes automatically) |
| Underscore error `Missing $ inserted` | Unescaped `_` in filenames | Wrap filenames in `\file{...}` |
| `\safeimg` reports `File not found` | Path resolved relative to compile dir / `\graphicspath` | Verify `\graphicspath{{...}}` or pass path relative to `deck.tex` |

## Layout

| Symptom | Fix |
|---|---|
| `Overfull \hbox` | Line too wide. Switch equations to `\eqline` (auto-scales); add `\allowbreak` in long English tokens; set explicit `p{...}` column widths in tables |
| Content touches or overlaps footer | Does not always emit a LaTeX error—only visible by inspecting images. Cut text or split the slide first; next try `\densesize`; shrink figure height last |
| Side-by-side cards have uneven heights | Give every card in the row the same fixed height: `\begin{warmcard}[\linewidth][2.4cm]{...}` |
| Text overflows a fixed-height card | Increase fixed height or trim text |
| `\gaparrow` vertically misaligned with cards | Tune `\gaparrow[height]` to roughly half the card's fixed height |
| Caption wider than a narrow figure | Intentional minimum caption width (`60%` of column width); enlarge the figure if it looks loose |
| Crowded Chinese punctuation between names | Use `\dotsep` instead of mixing `、` and spaces |
| Single orphan character on a wrapped title line | Shorten the subtitle or insert a manual `\\` in the English title |
| Columns overflow page width | Keep column widths summing to `0.96–0.97\textwidth` inside `columns[T,onlytextwidth]` |

## Visual Inspection Close-Ups

Use `lint_deck.py --page` to render 110 dpi single-page PNGs directly:

```bash
python3 "$SKILL_DIR/scripts/lint_deck.py" deck.tex --page 5
python3 "$SKILL_DIR/scripts/lint_deck.py" deck.tex --page 3,5 --no-build   # if deck.pdf already exists
```

Or run `pdftoppm` manually:

```bash
pdftoppm -r 110 -f 5 -l 5 -png deck.pdf /tmp/p
```

The contact sheet (`deck_sheet.png`) is low-resolution for pacing and obvious overflow checks; always zoom in on dense tables, formulas, or tight cards.
