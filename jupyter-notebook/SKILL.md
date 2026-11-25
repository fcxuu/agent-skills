---
name: jupyter-notebook
description: |
  Create, scaffold, refactor, or validate reproducible Jupyter notebooks (.ipynb) for experiments and tutorials.
  Use when authoring, restructuring, or verifying an .ipynb notebook. Skip for general Python language Q&A without producing or modifying a notebook.
---

# Jupyter Notebook

Lock the notebook's goal, audience, data source, and target kernel before authoring. Preserve clean top-to-bottom reproducibility and never hardcode secrets or credentials in cells or outputs.

## Path & Runtime Contract

Resolve `SKILL_DIR` from the directory containing this `SKILL.md`. Keep your working directory in the **target project** and probe the isolated Python runtime (which includes `nbclient`, `nbformat`, and `ipykernel`):

```bash
PY="$HOME/.local/share/agent-skill-runtimes/jupyter-notebook/bin/python"
[ -x "$PY" ] || PY=python3
```

## Decision Tree: `experiment` vs. `tutorial`

- **Exploratory, analytical, hypothesis-driven, or benchmark work** → `--kind experiment` (`assets/experiment-template.ipynb`).
- **Instructional, step-by-step, or audience-onboarding guide** → `--kind tutorial` (`assets/tutorial-template.ipynb`).
- **Editing an existing `.ipynb`** → refactor in place while preserving author intent, cell IDs, and deterministic execution order.

## Workflow

1. **Scaffold via helper script** (avoid hand-authoring raw notebook JSON):
   ```bash
   python3 "$SKILL_DIR/scripts/new_notebook.py" --kind tutorial --title "Example Tutorial"
   ```
   By default this writes to `<repo-root>/output/jupyter-notebook/<slug>.ipynb` (preserving Unicode/Chinese titles unescaped with valid cell IDs). Pass `--out path/to/file.ipynb` to target an explicit path (`--force` to overwrite).
2. **Author structured cells:** Follow `references/notebook-structure.md` and `references/experiment-patterns.md` or `references/tutorial-patterns.md`—keep imports/config at the top, deterministic seeds, concise Markdown narrative between code cells, and clear takeaways.
3. **Execute top-to-bottom & verify:** Run the notebook cleanly from cell 1 to the end against the project's matching kernel (or isolated runtime):
   ```bash
   "$PY" -c "import nbformat; from nbclient import NotebookClient; nb = nbformat.read('path/to/file.ipynb', as_version=4); NotebookClient(nb, timeout=120).execute(); nbformat.write(nb, 'path/to/file.ipynb')"
   ```
   Check `references/quality-checklist.md` before finishing; if execution is blocked by missing project data or GPU/env dependencies, state explicitly which cells ran and which were not executed.

## References

- `UPSTREAM.md` — Full workflow, output conventions, and dependency rules.
- `references/notebook-structure.md`, `references/experiment-patterns.md`, `references/tutorial-patterns.md`, `references/quality-checklist.md`.

Upstream: `openai/skills`, commit `49f948faa9258a0c61caceaf225e179651397431`, Apache 2.0 ([LICENSE.txt](LICENSE.txt)). Local adaptations: project-relative default output, Unicode filenames/JSON (`ensure_ascii=False`), and explicit cell IDs in templates.
