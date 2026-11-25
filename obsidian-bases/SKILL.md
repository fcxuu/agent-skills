---
name: obsidian-bases
description: |
  Create, edit, or repair Obsidian Bases (.base) files and embedded ```base views—covering filters, formulas, property configs, summaries, and table/cards/list/map layouts.
  Use when authoring or debugging a .base file or embedded base block in an Obsidian vault. Skip for general Obsidian note-taking chat or conceptual Q&A.
---

# Obsidian Bases

Inspect the target `.base` file (or embedding note), actual frontmatter property names across the vault's notes, and the user's exact filtering/view intent before editing. Preserve unrelated views and settings.

## Path Contract

Resolve `SKILL_DIR` from the directory containing this `SKILL.md` (never assume `pwd` is `SKILL_DIR`).

## Critical Syntax Rules (Avoid Silent Failures)

Obsidian Bases uses a specialized YAML + formula dialect where mistakes often fail silently:

1. **Always prefix note properties with `note.` inside `properties:`** (e.g., `note.status:`, not `status:`)—unprefixed keys under `properties:` are silently ignored by Obsidian. Use `file.` for built-in file metadata and `formula.` for computed properties.
2. **Date subtraction returns a `Duration`, not a number:** always access a unit property (e.g., `(now() - file.ctime).days.round(0)`), never `(now() - file.ctime).round(0)`.
3. **Scope `filters` intentionally:** top-level `filters` apply to **all** views in the `.base`; per-view `filters` narrow only that view.
4. **Never guess formula functions:** before writing any formula, check `$SKILL_DIR/references/FUNCTIONS_REFERENCE.md`—do not invent JavaScript or Excel function names.

## Required References

- **`UPSTREAM.md`** — **Must read** when creating a new `.base` from scratch or configuring `views`, `filters` (`and`/`or`/`not`), `groupBy`, `summaries`, or `cards`/`map` view options.
- **`references/FUNCTIONS_REFERENCE.md`** — **Must read** whenever adding or editing `formulas` or filter expressions.

## Deterministic Validation Loop

Always validate every created or modified `.base` file before finishing:

```bash
python3 "$SKILL_DIR/scripts/validate_base.py" path/to/view.base --json
```

Fix all `error` items and review all `warning` items (such as missing `note.` prefixes or raw `Duration` math). If you can open the vault in Obsidian, verify live rendering; otherwise explicitly note that in-app Obsidian rendering was not verified.

Upstream: `obsidianmd/obsidian-skills`, commit `b110b2f8e9eb1f287892f937050dfd40af862cbb`; license in [LICENSE](LICENSE).
