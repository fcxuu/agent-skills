# Obsidian Self-Study Skill (v0.2)

A batch-oriented Agent Skill for turning course PDFs, PPT/PPTX slides, textbooks, and handouts into structured Obsidian self-study notes—complete with source-traceable raw Markdown, derivation bridging, original figure archiving, exam review hubs, graded QA, and crash-safe checkpoint recovery.

Defaults to **single-agent execution**; loads multi-agent coordination rules only when explicitly assigned as a Worker, requested as Commander, or when callable subagent tools and clear parallel payoff both exist.

## Installation

Copy or symlink the entire `obsidian-self-study/` directory into your client's skills folder (e.g., `~/.agents/skills/obsidian-self-study/` or project `.agents/skills/obsidian-self-study/`), preserving `SKILL.md`, `references/`, `templates/`, and `scripts/`.

## Structure

- `SKILL.md` — Compact entrypoint, invariants, path contract, and stage-gated routing table.
- `references/00-preflight.md` — Lightweight preflight checks and execution mode routing.
- `references/01-ingestion.md` — Tool-agnostic tiered document ingestion, probes, and coverage/sanity gates.
- `references/02-pedagogy.md` — Lecture-note + self-study textbook fusion, provenance tags, and isolation rules.
- `references/03-obsidian-style.md` — Structured native Obsidian callouts, `## 核心速览` contract, math & embed rules.
- `references/04-images.md` — Original figure priority, deterministic plotting, and visual readability QA.
- `references/05-knowledge.md` — Incremental syllabus mapping (`source-map.md`), README hub, links, and review embeds.
- `references/06-quality.md` — L1/L2/L3 graded QA, defect severity, protected-completed risk handling.
- `references/07-execution.md` — `.build-state.json` schema, 5-state transitions, controlled revision, and minimal recovery context.
- `references/08-multi-agent.md` — On-demand Commander delegation gate, worker contracts, and single-writer shared state.
- `templates/` — Reference skeletons for notes, README, QA, and review hubs.
- `scripts/check_vault.py` — Stdlib-only, read-only L1 static checker with deterministic JSON output and `not_checked` disclosures.
- `scripts/state_tool.py` — Stdlib-only atomic `.build-state.json` CLI manager matching `check_vault.py`'s schema.
- `tests/` — Unit test suites for both scripts.

## Bundled CLI Tools & Tests

```bash
# Run read-only L1 static check
python3 "$SKILL_DIR/scripts/check_vault.py" --vault "$VAULT_DIR" --course "$COURSE_DIR" --json

# Manage .build-state.json atomically
python3 "$SKILL_DIR/scripts/state_tool.py" --help

# Run all unit tests (stdlib only)
python3 -B -m unittest discover -s "$SKILL_DIR/tests" -v
```

## Known Scope Boundaries

- Not an interactive tutoring mode and does not run background file-sync watchers.
- Static checks (`check_vault.py`) verify structure, links, and state schema only—they do not verify mathematical truth, OCR fidelity, chart accuracy, or live Obsidian rendering.
- End-to-end verification in a live Obsidian desktop/mobile reading view depends on the user's runtime environment.
