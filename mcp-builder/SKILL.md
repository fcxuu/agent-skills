---
name: mcp-builder
license: Apache-2.0
description: |
  Design, implement, modify, or debug a Model Context Protocol (MCP) server (Python or TypeScript/Node) with well-scoped tools, schemas, error handling, and local verification.
  Use when building or updating an MCP server for a concrete project. Skip for conceptual MCP protocol Q&A or merely calling existing MCP tools.
---

# MCP Server Builder

Understand the target API/service, existing codebase, authentication model, and required tools before writing code. Design clear input/output schemas, actionable error messages, and least-privilege access matching the project's language and SDK version.

## Path & Runtime Contract

Resolve `SKILL_DIR` from the directory containing this `SKILL.md`. For local Python tooling/evaluation, probe the isolated runtime first:

```bash
PY="$HOME/.local/share/agent-skill-runtimes/mcp-builder/bin/python"
[ -x "$PY" ] || PY=python3
```

Other machines can install `$SKILL_DIR/scripts/requirements.txt` in an isolated virtualenv. **SDK compatibility note:** `$SKILL_DIR/scripts/evaluation.py` requires **MCP Python SDK 1.x** (`mcp>=1.1.0,<2`); SDK 2.x imports are incompatible with the upstream evaluation script.

## Mandatory Documentation Routing (`$SKILL_DIR/reference/` — Note Singular Folder Name)

Load **only** the guide matching your active phase and language (verify against current official SDK docs if the project uses a newer release):

| Phase / Stack | File to Read (under `$SKILL_DIR/reference/`) |
|---|---|
| Tool naming, pagination, error & security design | `reference/mcp_best_practices.md` |
| Python MCP server (`FastMCP` / `mcp`) | `reference/python_mcp_server.md` |
| TypeScript / Node MCP server (SDK v1.x) | `reference/node_mcp_server.md` |
| TypeScript / Node MCP server (SDK v2.x) | `reference/node_mcp_server_v2.md` |
| Authoring XML evaluation suites | `reference/evaluation.md` |

Consult `UPSTREAM.md` for the full 4-phase research → implement → test → evaluate guide.

## Verification Strategy (Free Local Smoke Test First)

1. **Local stdio smoke test (default, zero API cost):** Start the server locally over `stdio`, confirm `tools/list` returns valid JSON schemas, and execute at least one read-only tool call with valid and invalid inputs.
2. **Model-backed evaluation (`scripts/evaluation.py`, opt-in only):** `evaluation.py` connects to the server and calls an external LLM API, incurring **network requests, token cost, and output files**—run it only when explicitly requested and authorized.

Record any blocked auth/environment dependencies and continue independent implementation or schema checks.

Upstream: [anthropics/skills/skills/mcp-builder](https://github.com/anthropics/skills/tree/e4bb5d960d87126ff3b3a8af1a104b7db67560ba/skills/mcp-builder), commit `e4bb5d960d87126ff3b3a8af1a104b7db67560ba`; license in [LICENSE.txt](LICENSE.txt).
