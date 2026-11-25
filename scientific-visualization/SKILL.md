---
name: scientific-visualization
description: |
  Design, plot, audit, and export publication-grade scientific figures from experimental or statistical datasets (Matplotlib, Seaborn, Plotly), including colorblind-safe palettes, journal sizing presets, and metadata verification.
  Use when plotting real research data, reviewing existing scientific charts, or preparing journal-ready figure exports. Skip for conceptual statistics Q&A or general color theory chat.
---

# Scientific Visualization

Confirm the dataset, scientific claim, error-bar definition, and target publication requirements before coding.

## Path & Runtime Contract

Resolve `SKILL_DIR` from the directory containing this `SKILL.md`. Keep your working directory in the user's project folder and probe the isolated Python runtime first:

```bash
PY="$HOME/.local/share/agent-skill-runtimes/scientific-visualization/bin/python"
[ -x "$PY" ] || PY=python3
```

Requires Python 3.11+ with `matplotlib`, `pillow`, and `pypdf` as needed (Plotly static image export also requires Chrome/Chromium).

## Non-Negotiable Integrity Guardrails

1. **Data faithfulness first:** Never alter, hide, invent, or selectively smooth data to make a figure look cleaner. Preserve raw tables, exclusions, missing-value handling, normalization, binning, and random seeds.
2. **Explicit uncertainty & sample sizes:** Every error bar or ribbon must state its exact statistic (SD, SEM, 95% CI, IQR) and sample size $n$. Never treat a palette contrast check as full accessibility certification.
3. **Never guess journal specifications:** Inspect presets via `export_plan.py --list` / `assets/publisher_profiles.json` and remind the author to confirm against the target journal's latest live author guidelines.

## Complete Script Routing Table

| Task | Script (under `$SKILL_DIR/scripts/`) | Purpose |
|---|---|---|
| Audit palette contrast & grayscale separation | `palette_audit.py` | e.g. `--palette okabe_ito_on_white` |
| Inspect / apply scoped Matplotlib style presets | `style_presets.py` | Scoped publication/journal styling |
| Render quick style comparison preview | `style_preview.py` | `--output <path>/preview --formats png` |
| Check publisher width / DPI / format targets | `export_plan.py` | `--list` or `--publisher <name>` |
| Export compliant multi-format figures + provenance | `figure_export.py` | Explicit vector/raster export with sizing |
| Verify exported figure DPI, dimensions, fonts, color | `image_metadata.py` | **Required post-export audit** |

## Standard Export & Verification Loop

1. **Plan & style:** Check `export_plan.py --list` and pick a colorblind-safe palette from `assets/color_palettes.py` + scoped style (`assets/publication.mplstyle`, `assets/nature.mplstyle`, `assets/presentation.mplstyle`). Audit custom colors with `palette_audit.py`.
2. **Plot & export:** Generate with explicit physical dimensions and export via `figure_export.py` (or Matplotlib with verified `dpi` and `bbox_inches='tight'`).
3. **Verify metadata & visually inspect:** Run `image_metadata.py` on the exported file(s) to confirm true DPI, physical width/height, and color mode—then open the rendered PNG to visually check overlapping labels, clipped axes, and font legibility.

## References & Assets

- `UPSTREAM.md` — Full 6-stage scientific visualization workflow and guardrails.
- `references/matplotlib_examples.md` — Ready-to-adapt publication plotting patterns.
- `references/publication_guidelines.md`, `references/journal_requirements.md`, `references/color_palettes.md` — Deep typography, journal, and accessibility guides.

Upstream: `K-Dense-AI/scientific-agent-skills`, commit `ec59a29a03d5c40f73ab40878df04860bc00e876`, MIT ([LICENSE.md](LICENSE.md)).
