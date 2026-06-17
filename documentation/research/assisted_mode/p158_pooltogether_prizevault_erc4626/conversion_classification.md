# P158 — H6 Conversion Classification

Candidate: `H6-pooltogether-prizevault-erc4626-rate-mismatch`

| field | value |
|---|---|
| mechanism_confirmed | **false** (refuted at source) |
| attacker_reachable | true (deposit/withdraw are unprivileged, no keeper) — but moot, mechanism absent |
| severity_bearing | **false** (guarded; no value movement on this axis) |
| novelty_clear | unknown (`_sealed_answer_key` not opened; duplicate_unknown → no novelty inference) |
| reportable | **false** |
| runtime_status | **not_run** (deploy_too_heavy: real PrizeVault needs un-vendored pt-v5 TwabController/PrizePool) |
| reachability_verdict | unprivileged_user_reachable (entrypoints) — but mechanism guarded |
| severity_class | none / static_false_positive |
| duplicate_status | duplicate_unknown |
| conversion_outcome | **static_false_positive** |
| primary_blocker | **mechanism_absent_guard_present** (LossyDeposit guard + debt-aware withdraw/redeem); runtime separately deploy_too_heavy |
| human_review_required | false |
| routing_allowed | false |
| submission_ready | false |

## Why static_false_positive (not runtime_refuted, not reportable)
The ERC4626 "1:1 `previewDeposit` vs debt-aware convert" smell is a **static suspicion that does not survive
source reading**: `_depositAndMint` reverts `LossyDeposit` if a deposit would create/extend a lossy state,
and `previewWithdraw`/`previewRedeem` are debt-aware. So there is no unprivileged rate-mismatch value path.
Runtime was not run because (1) the source guard is dispositive and (2) a faithful real-contract harness is
`deploy_too_heavy` (un-vendored pt-v5 deps). The correct label is therefore **static_false_positive** with a
secondary `deploy_too_heavy` note for any future runtime follow-up.

## Recording decision (sidecar vs ledger)
H6 had **no runtime PoC**, so it is recorded in the **campaign ledger only**. The value-provenance runtime
sidecar (`runtime_status.jsonl`) is left **byte-identical** (H1–H5 unchanged) — it stays the canonical store
of *runtime-tested* rows; a source-refuted/not-run candidate does not belong there.

## Honest campaign value
This is a useful datapoint: selection correctly moved toward a **no-keeper, direct-value** target (H5 lesson
applied), but the target was (a) well-guarded on the obvious axis and (b) not deploy-light. Two of the
campaign's stated learnings — *what refutes* and *what was too expensive* — in one candidate.
