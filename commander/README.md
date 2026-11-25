# Commander Skill

A client-agnostic orchestration skill that enables **any AI agent** to operate as a task Commander: framing complex goals, choosing between direct execution, deterministic scripts, host-native subagents, or manual cross-client handoffs, independently verifying deliverables, and integrating the final result.

## Installation

Copy or symlink the entire `commander/` folder into your agent client's skills directory (preserving `SKILL.md`, `references/`, and `templates/`):

```text
~/.agents/skills/commander/
├── SKILL.md
├── README.md
├── references/
│   ├── executor-routing.md
│   └── evaluation-rubric.md
└── templates/
    ├── dispatch-prompt.md
    ├── correction-prompt.md
    └── final-report.md
```

Reload skills (or open a new session) and invoke the skill by name when starting a complex multi-part task.

## When to Use

- Multi-module projects requiring decomposition, parallel execution, or independent verification.
- Cross-agent workflows where the lead agent coordinates subagents, scripts, or manual handoffs.
- Pair with `coding-task-contract`, `verified-coding-loop`, and `agent-code-handoff` for software engineering tasks.

Skip for single-step requests, general Q&A, or small self-contained edits.
