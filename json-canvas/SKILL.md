---
name: json-canvas
description: |
  Create, edit, lay out, or repair Obsidian JSON Canvas (.canvas) files—nodes, groups, spatial layout, colors, and directed edges.
  Use when generating or modifying a .canvas file. Skip for conceptual discussions about relationships without producing or editing a .canvas file.
---

# JSON Canvas

Read the target `.canvas` file first when editing an existing board, confirm the requested change scope, and preserve unrelated nodes, edges, and custom fields.

## Path Contract

Resolve `SKILL_DIR` from the directory containing this `SKILL.md` (never assume `pwd` is `SKILL_DIR`).

## Minimal JSON Canvas 1.0 Schema Cheat Sheet

A `.canvas` file is UTF-8 JSON with top-level `nodes` (array) and `edges` (array):

- **All nodes require:** `id` (unique string), `type`, `x`, `y`, `width` (> 0), `height` (> 0).
- **Type-specific required fields:**
  - `text`: `text` (Markdown string)
  - `file`: `file` (vault-relative path; optional `subpath` starting with `#`)
  - `link`: `url` (HTTP/HTTPS URL)
  - `group`: optional `label`, `background`, `backgroundStyle`
- **All edges require:** `id` (unique string), `fromNode`, `toNode` (both must match existing node IDs). Optional: `fromSide`/`toSide` (`top` | `right` | `bottom` | `left`), `fromEnd`/`toEnd` (`none` | `arrow`), `color`, `label`.
- **Layout heuristics (avoid overlaps):** default text/file cards to `width: 320–400`, `height: 140–220`; leave `≥ 80px` horizontal/vertical gutter between sibling cards; place `group` containers earlier in `nodes` (so they render behind children) with `40px` padding around enclosed nodes.

## References

- **`UPSTREAM.md`** — Full JSON Canvas 1.0 attribute reference, colors, and common edit workflows.
- **`references/EXAMPLES.md`** — Complete multi-node/group/edge canvas examples.

## Write & Validate Loop

Always serialize with a JSON writer (`json.dump(..., ensure_ascii=False, indent=2)`)—never hand-concatenate JSON strings. Validate every created or edited `.canvas` before finishing:

```bash
python3 "$SKILL_DIR/scripts/validate_canvas.py" path/to/board.canvas --json
```

Fix every `error` (invalid JSON, duplicate IDs, dangling edges, missing required fields) and resolve unintended non-group node overlaps reported as `warning`. If you cannot open the board in Obsidian, explicitly note that live visual rendering was not verified.

Upstream: `obsidianmd/obsidian-skills`, commit `b110b2f8e9eb1f287892f937050dfd40af862cbb`; license in [LICENSE](LICENSE).
