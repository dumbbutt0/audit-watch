# P286 — POC_RESULTS

Source: `outputs/poc_results.json`, `outputs/p286_run_output.txt`, `outputs/l2governor_regression_log.txt`.

## claim_many — Tier-C, 3/3 PASS (mechanism: recipient_divergence)
| layer | test | result |
|---|---|---|
| L1 entry | (all) `vm.prank(attacker)` EOA call, no privileged setup | ✔ |
| reference | `test_claim_routes_to_original_owner_PASS_SUPPORTED` | ✔ claim pays getOriginalOwner; ownerOf gets 0 |
| **L2 state-flip (the bug)** | `test_claim_many_misroutes_to_ownerOf_PASS_SUPPORTED` | ✔ claim_many credits `avmHolder`(=ownerOf) by AMOUNT; `originalOwner` stays 0 |
| L3 control | `test_control_non_avm_token_routes_same` | ✔ non-AVM lock: claim and claim_many pay the SAME owner |

`Suite result: ok. 3 passed; 0 failed; 0 skipped.`

**Named state-flip (L2):** for the AVM-managed `TOKEN_ID`, `balanceOf(avmHolder)` goes 0 → AMOUNT and
`balanceOf(originalOwner)` stays 0 under `claim_many`, whereas `claim` produces the inverse. Same input (one tokenId,
same EOA caller, same expired-non-permanent lock), different recipient — the divergence is exactly the omitted AVM
`getOriginalOwner` correction.

**L3 outcome:** `claim_many` permanently strands an AVM-managed lock's reward at `ownerOf` (the AVM / current NFT holder)
instead of the original locker. Permissionless (anyone can call `claim_many`). The control proves the divergence is the
AVM branch, not a harness artifact.

## L2Governor.execute — regression, 2/2 PASS
`test_control_pending_proposal_rejected` ✔ · `test_state_machine_defeated_proposal_executes_PASS_SUPPORTED` ✔
(`Suite result: ok. 2 passed`). Unchanged from P281 — still PASS_SUPPORTED.

## Summary
READY-set PoC-supported: **2/2** (claim_many newly proven; L2Governor confirmed). Fabricated passes: 0. Severe
concluded/reportable FP: 0.
