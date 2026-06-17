# P151 — Gate 3/5: Severity Recommendation (reject-first)

## Bucket: **Design / privileged-only** (for the fee-binding mismatch)
Reject-first logic: do not assign Medium/High unless there is an attacker-influenceable production path AND a
concrete unauthorized value movement. Here:
- **No attacker-influenceable path:** the router builds `packedInfo` from the user's `fees`; no public entrypoint
  accepts an independent `packedInfo` (call_path_table.md). Only the privileged `onlyUtb` caller could mismatch.
- **No concrete unauthorized value movement under intended operation:** the executed fee is the signed fee.
⇒ **No Medium/High.** The missing re-bind in `collectFees` is a **defense-in-depth / robustness** recommendation
(re-bind `fees` to `packedInfo` inside `collectFees` as belt-and-suspenders, so a future/compromised caller can't
mismatch). `submission_ready=false`.

## Separate bucket: **Replay-only (distinct issue)**
The signed `(instructions, fees)` blob omits nonce / chainid / contract address / deadline (signed_vs_executed_
table.md). A signer-issued signature may be replayable (repeat, cross-deployment, cross-chain). This is a
**separate** finding; it does **not** amplify the fee mismatch (the fee is bound). Severity undetermined →
human review; `submission_ready=false`. (Whether it is exploitable depends on the backend's signing policy and
whether instructions themselves bound a unique operation — out of local scope.)

## What is NOT claimed
- Not "High/Medium candidate" (no unprivileged unauthorized fee transfer).
- Not "Low/QA via fee mismatch as a live exploit" — the live mismatch requires privileged UTB.
- No novelty (`duplicate_unknown` = no local record only); no submission.

## Mechanism preserved
P150's `runtime_confirmed` (contract-level: collectFees executes unbound `fees`) stands as **mechanism evidence**;
P151 only resolves that it is **not externally reachable** and therefore not bounty-grade as exploited.
