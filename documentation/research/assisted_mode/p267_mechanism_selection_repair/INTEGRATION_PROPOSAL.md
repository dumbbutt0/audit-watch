# P267 — INTEGRATION_PROPOSAL (proposed, NOT wired — no production authority)

The selector is a research module. This proposes how a FUTURE full-path run could use it. Nothing here is wired;
adopting it is a separate human decision.

## Proposed location
`B/C top-2 mechanisms → pairwise selector → completion/PoC queue`. The selector sits between ranking and the
five-op completion / PoC stage, exactly where P266 dropped the awarded mechanism.

## Dashboard display (advisory only)
Show the selector decision as an advisory label on the existing standalone P266 advisory surface:
`SELECT_M1 / SELECT_M2 / KEEP_BOTH / REFUTE_*_FIRST / INSUFFICIENT_EVIDENCE`, plus the anti_easy_poc_flag and the
decisive dimensions. **No** confirmed / reportable / severity state — same advisory contract as P266.

## PoC-queue behavior (proposed)
- `SELECT_M1` / `SELECT_M2` → queue the selected mechanism for completion/PoC.
- `KEEP_BOTH` → queue **both** mechanisms for completion/PoC if budget allows (this is the P266 fix in action).
- `REFUTE_M1_FIRST` / `REFUTE_M2_FIRST` → require refuting the flagged mechanism before it consumes PoC budget.
- `INSUFFICIENT_EVIDENCE` → route to human review (do not auto-queue).

## Budgeting note
KEEP_BOTH costs an extra PoC slot. The P266 cap was 2–4 PoCs; KEEP_BOTH on one high-value pair is well within that.
The selector should be applied to the highest-value pair(s) first so KEEP_BOTH spends budget where exact recovery
matters most.

## Rollback
Remove the selector stage, or run the module in a disabled/no-op mode. Because it is un-wired and advisory, removing
it returns the pipeline to the exact P266 behavior with zero residue. No production file changes are required to
adopt or remove it.

## What this does NOT change
No severity/routing/submission/confirmation-gate logic; no dashboard confirmed paths; no recall/PoC plumbing; no
run_pipeline defaults. Production authority is unchanged and remains withheld.
