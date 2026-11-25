# Choosing Test Oracles

Start with one question: *what concrete observation would change our verdict on this patch?* One discriminating small check beats blindly re-running an unrelated suite.

| Target Behavior | Discriminating Observation | Evidence Scope Notes |
|---|---|---|
| File or API output | Read output from the real entry point and compare against ticket samples, spec, or baseline. | Cite actual lines, fields, or status/errors—process exit code alone only proves termination. |
| UI flow | Click, retry, or use keyboard navigation in an available browser; inspect visible state or downloaded file. | Record browser/version; in code-only sessions, separate static findings from unverified platforms. |
| Data processing | Sample recomputation, nulls, duplicate inputs, or failure recovery state. | State exact sample scope and input snapshot. |
| Numerical / ML change | Compare against trustworthy baseline with fixed formula, seed, and data split. | Single run proves one run; list missing repeats if stability is required. |
| Multi-module interface | Run an adjacent caller regression. | Add integration, compatibility, or rollback checks when blast radius is high. |

During debugging, log `input → symptom → hypothesis → discriminating next check`. When re-running only repeats a missing-dependency error, preserve the latest output for handoff and continue verifying independent parts. Always attribute observations cleanly (`author-observed`, `user-reported`, `reviewer-observed`).
