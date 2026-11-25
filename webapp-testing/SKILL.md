---
name: webapp-testing
license: Apache-2.0
description: |
  Launch, inspect, and verify local web applications in a real browser (Playwright or host browser tools) to check rendering, interactive flows, downloads, console errors, and network requests.
  Use when reproducing UI bugs or validating web app behavior. Skip for general frontend/browser theory Q&A.
---

# Webapp Testing

## Path & Runtime Contract

Resolve `SKILL_DIR` from the directory containing this `SKILL.md`. Keep your working directory in the target web project and probe the isolated Playwright runtime first:

```bash
PY="$HOME/.local/share/agent-skill-runtimes/webapp-testing/bin/python"
[ -x "$PY" ] || PY=python3
```

On macOS with Chrome installed, launch headless Chrome via `p.chromium.launch(channel="chrome", headless=True)`. Use the host's built-in interactive browser tool for quick manual exploration when available; write a Playwright script when repeatable verification, console/network capture, or regression checks are needed.

## Decision Tree

1. **Static HTML file (no dev server needed)?** Read the HTML directly to locate selectors, then run a quick Playwright check (`examples/static_html_automation.py`).
2. **Dynamic web app / SPA (server not running)?** Start and cleanly tear down the server(s) with `$SKILL_DIR/scripts/with_server.py` (run `--help` first; only pass trusted server commands):
   ```bash
   "$PY" "$SKILL_DIR/scripts/with_server.py" --server "npm run dev" --port 5173 -- "$PY" your_test.py
   ```
3. **Server already running?** Connect directly and follow the Reconnaissance-Then-Action pattern below.

## Critical Pitfall & Pattern (Read Before Scripting)

- **Wait for hydration/network idle on dynamic apps:** **Never** query DOM elements immediately after `page.goto(...)` on SPAs—call `page.wait_for_load_state("networkidle")` (or wait for a concrete semantic locator) first.
- **Reconnaissance-Then-Action:** Before clicking/filling forms, take a screenshot or dump visible buttons/inputs/links (`examples/element_discovery.py`) to inspect **real** DOM selectors instead of guessing.
- **Clean up:** Always use `sync_playwright()` with `browser.close()` (and `with_server.py` for managed servers) so no orphaned processes remain.

## Ready-to-Use Examples (`$SKILL_DIR/examples/`)

| File | Use For |
|---|---|
| `examples/element_discovery.py` | Discovering real buttons, links, and form inputs on a rendered page |
| `examples/console_logging.py` | Capturing browser console logs and page errors during interaction |
| `examples/static_html_automation.py` | Opening and testing local `file://` static HTML pages |

Consult `UPSTREAM.md` for full multi-server command examples (`--server` repeated for backend + frontend). Record exact reproduction steps, observed UI/console/network results, and any unverified browser/platform gaps.

Upstream: [anthropics/skills/skills/webapp-testing](https://github.com/anthropics/skills/tree/e4bb5d960d87126ff3b3a8af1a104b7db67560ba/skills/webapp-testing), commit `e4bb5d960d87126ff3b3a8af1a104b7db67560ba`; license in [LICENSE.txt](LICENSE.txt).
