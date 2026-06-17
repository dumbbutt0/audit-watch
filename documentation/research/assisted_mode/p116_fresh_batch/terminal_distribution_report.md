# P114 — Fresh-candidate terminal-state distribution

**OVERALL PASS: True**  ·  research-only, un-wired. 3 mechanically-selected fresh candidates run to truthful terminal states.

## Terminal distribution
- {"NEEDS_CONTEXT": 3}

## Per candidate
| Candidate | score | terminal | harness | validation | runtime tried | package allowed |
|---|---|---|---|---|---|---|
| munchables-2024-07::MigrationManager.burnRemainingPurchasedNFTs | 3.0 | NEEDS_CONTEXT | HARNESS_COMPLEX | NEEDS_MORE_CONTEXT | False | False |
| phi-2024-08::CuratorRewardsDistributor.distribute | 3.0 | NEEDS_CONTEXT | HARNESS_MODERATE | NEEDS_MORE_CONTEXT | False | False |
| munchables-2024-07::MigrationManager.burnNFTs | 2.9912 | NEEDS_CONTEXT | HARNESS_COMPLEX | NEEDS_MORE_CONTEXT | False | False |

## Safety
- all safety assertions pass: True
- all terminals in allowed set: True
- no unsafe package (package only on CONFIRMED_RUNTIME): True

## Honest interpretation
- A distribution dominated by NEEDS_CONTEXT / HARNESS_UNAVAILABLE is NOT failure — it is the pipeline preserving precision and naming the next bottleneck.
- Observed next bottleneck: the recommended ranking's body-only `actor_clarity` signal misses access MODIFIERS declared in the function signature (`onlyBorrower`, `onlyPhiFactory`), so privileged functions can rank as 'permissionless'. Honest validation caught this; a future ranking iteration should read signature modifiers. Ranking chose the order; it did not validate anything.

## Per-candidate rationale
- **munchables-2024-07__MigrationManager_burnRemainingPurchasedNFTs**: Read MigrationManager.burnRemainingPurchasedNFTs. `external override`, gated by a `seal` flag and a caller guard (`_user == msg.sender` OR the target user has already chosen a migration action). It sets `_userPurchasedAction[_user]=LOCKED_BURN` then burns the user's UNLOCKED, unclaimed purchased NFTs in a bounded paginated loop (_skip..SKIP_AMOUNT). A possible griefing path — calling for another `_user` who has set an action, forcing a burn/choice — depends on the full migration state machine (`_userPurchasedAction` semantics) and would need runtime to confirm or refute. No source-provable exploit; not provably safe. Truthful terminal: NEEDS_CONTEXT.
- **phi-2024-08__CuratorRewardsDistributor_distribute**: Read CuratorRewardsDistributor.distribute — a genuinely PERMISSIONLESS reward distributor (the corrected ranking surfaced this instead of P114's privileged dead-ends). Two source-visible, nameable hypotheses: (1) UNBOUNDED-LOOP DoS — it loops twice over `credContract.getCuratorAddresses(credId,0,0)` (all curators) and `phiRewardsContract.depositBatch(...)` over the whole array; if an attacker can cheaply add many sybil curators (Cred.buyShareCred), the loops/batch exceed gas and rewards become undistributable — matching phi's awarded H-03 reward-distribution DoS. (2) ROYALTY-TO-CALLER — `_msgSender().safeTransferETH(royaltyfee + dust)` sends the withdrawRoyalty to whoever calls distribute (the authors even slither-disable `arbitrary-send-eth`); if the royalty is meant for the protocol, a permissionless keeper harvests it. NEITHER is closable from source alone: the DoS needs the cross-contract curator-growth cost + a runtime gas measurement; the royalty needs intent/spec (keeper-fee vs protocol-leak). I did not fabricate a trace. Truthful terminal: NEEDS_CONTEXT with a strong, specific hypothesis (next step: confirm curator-array growth cost in Cred + measure depositBatch gas; confirm intended royalty recipient).
- **munchables-2024-07__MigrationManager_burnNFTs**: Read MigrationManager.burnNFTs. `external override`, `seal`-gated, caller guard (`_user == msg.sender` OR target user chose an action); bounded paginated loop burning the user's LOCKED, unclaimed NFTs and awarding points. Same class as burnRemainingPurchasedNFTs — a force-burn/wrong-choice griefing path is conceivable but needs the full migration lifecycle + runtime to confirm/refute. No source-provable exploit; not provably safe. Truthful terminal: NEEDS_CONTEXT.

