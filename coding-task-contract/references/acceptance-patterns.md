# Acceptance Criteria Patterns

Pick the closest pattern for the ticket; adapt or omit any input, metric, or check as needed.

| Task Type | Observable Criterion Example | Trustworthy Oracle / Baseline |
|---|---|---|
| Bug fix | Submitting an empty name renders the ticket-specified error beside the name field. | User report as clue; compare same input before vs. after patch when baseline is available. |
| API | Empty payload returns HTTP `422` with the documented error field name. | API spec, real caller, one valid request, and one representative invalid request. |
| Refactor | Identical input produces identical records preserving the documented ordering. | Pre-refactor output, golden fixture, or caller-visible response. |
| Performance | Compare latency/memory under agreed input size and environment while confirming output parity. | Record measurement method and variance; deliver baseline numbers if target threshold is not yet set. |
| UI | Submit, retry, or navigate via keyboard from the real user entry point; describe visible state/download. | Target browser/device specified in ticket; representative screenshot if requested. |
| Data / SQL | Re-running the same batch preserves primary keys and expected row counts. | Small-sample recomputation, independent query, boundary dates/nulls, rollback plan for writes. |
| ML / Modeling | Compare against named baseline on agreed split with metric definition and variance. | Dataset version, random seed, evaluation script, sample predictions. |

Vague goals like "improve success rate" are not verifiable yet. If the denominator is undefined, deliver the confirmed event scope, list which metric docs you checked, and leave denominator sign-off to the data owner.
