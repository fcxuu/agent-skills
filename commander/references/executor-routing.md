# Executor Routing Guide

Choose execution channels by **actual host capability, reliability, and total effort**—never by brand assumptions or fixed hierarchies.

## Capability-Based Execution Channels

| Channel | Best Suited For | Pre-Dispatch Verification |
|---|---|---|
| **Deterministic script / CLI** | Mechanical parsing, inventory, formatting, arithmetic, schema validation, repeatable builds | Verify input assumptions, error handling, and spot-check output |
| **Lead Agent (Commander)** | Problem framing, hard reasoning, architecture, ambiguous trade-offs, integration, critical checks | Account for remaining context budget, tools, and time |
| **Host-native subagent / worker tool** | Bounded parallel packages with disjoint file ownership, codebase research, isolated drafting/testing | Confirm the host actually exposes a callable subagent tool, workspace access, and clear return channel |
| **Manual handoff (external client via user)** | Specialized work requiring a separate tool/environment not connected to the current host | Clearly label as copy-paste handoff; do not assume shared files, chat history, or memory |

## Delegation Gate

Before splitting work off to another agent, verify:

1. **Bounded interface:** Clear deliverable, explicit inputs/constraints, and objective acceptance checks exist.
2. **Disjoint ownership:** Two executors will not edit the same file or make conflicting decisions concurrently.
3. **Positive net payoff:** Expected time/context/quality savings exceed prompt-writing, handoff, verification, and likely rework overhead.

If uncertainty about a channel's reliability is high, run a small low-risk probe with an explicit acceptance check before committing a large work package.

## Routing Formula

Compare candidate channels on expected total effort:
- Probability of first-pass correctness
- Severity of subtle errors and cost of detecting them
- Direct latency, compute/quota cost, and handoff friction
- Independent verification burden

Route to the lightest channel that is **reliable enough for the task's consequences**. Keep critical reasoning and final acceptance with the Commander for high-impact work.
