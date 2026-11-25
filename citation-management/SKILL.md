---
name: citation-management
description: |
  Verify academic citations, search scholarly databases (OpenAlex, PubMed, Google Scholar), convert DOIs/PMIDs/arXiv IDs to BibTeX, format/deduplicate .bib libraries, and validate reference accuracy.
  Use when verifying concrete citations, building/cleaning BibTeX files, or extracting bibliographic metadata. Skip for general paper content summaries or conceptual Q&A.
---

# Citation Management

Verify every source and identifier before citing; distinguish verified metadata from missing fields, and **never fabricate DOIs, authors, titles, venues, or BibTeX entries from memory**.

## Path & Runtime Contract

Resolve `SKILL_DIR` from the directory containing this `SKILL.md`. Keep your working directory in the user's project folder (so relative `.bib` paths resolve naturally) and probe the isolated Python runtime first:

```bash
PY="$HOME/.local/share/agent-skill-runtimes/citation-management/bin/python"
[ -x "$PY" ] || PY=python3
```

Requires Python 3.9+, `requests`, and network access for live lookups (`search_google_scholar.py` additionally requires `scholarly`).

## Complete Script Routing Table

| Task | Script (under `$SKILL_DIR/scripts/`) | Notes |
|---|---|---|
| Multidisciplinary paper search (preferred) | `search_openalex.py` | Fast REST API; optional `OPENALEX_API_KEY` |
| Biomedical / life sciences search | `search_pubmed.py` | Authoritative PubMed E-utilities |
| Fallback broad search | `search_google_scholar.py` | Scraped & rate-limited; use only if OpenAlex/PubMed insufficient, and re-verify results |
| Quick DOI(s) → BibTeX | `doi_to_bibtex.py` | Direct DOI content negotiation |
| Multi-ID metadata extraction (DOI/PMID/PMCID/arXiv) | `extract_metadata.py` | Supports `--doi`, `--pmid`, `--pmcid`, `--format json\|bibtex` |
| Clean, sort, rekey, deduplicate `.bib` | `format_bibtex.py` | Write to a new output file (`-o clean.bib`) rather than overwriting blindly |
| Audit & validate `.bib` completeness/DOIs | `validate_citations.py` | **Required closing check** before delivering a `.bib` file |

Run `"$PY" "$SKILL_DIR/scripts/<script>.py" --help` for exact CLI options, or consult `$SKILL_DIR/references/script_reference.md`.

## Standard Verification Loop

1. **Discover / extract** via `search_openalex.py` / `search_pubmed.py` / `extract_metadata.py` / `doi_to_bibtex.py` (never rely on a single database when completeness matters; never copy unverified metadata blindly).
2. **Format & deduplicate:**
   ```bash
   "$PY" "$SKILL_DIR/scripts/format_bibtex.py" input.bib -o clean.bib --sort year --deduplicate
   ```
3. **Validate before delivery:**
   ```bash
   "$PY" "$SKILL_DIR/scripts/validate_citations.py" clean.bib
   ```
   Report any unresolved DOIs, missing required fields, or suspected duplicates honestly.

## References & Assets

- `references/script_reference.md` — Detailed CLI arguments and examples for all 7 scripts.
- `references/core_workflow.md` & `UPSTREAM.md` — Full multi-phase citation and enrichment workflow.
- `assets/bibtex_template.bib` & `assets/citation_checklist.md` — Entry templates and pre-submission checklist.

Upstream: `K-Dense-AI/scientific-agent-skills`, commit `ec59a29a03d5c40f73ab40878df04860bc00e876`, MIT ([LICENSE.md](LICENSE.md)).
