# P242 — Counterfactual: impact on P235 / P240 / P241

Estimate of awarded misses the two families would now recover (had they been active), based on the validated
detectors + anchors.

| Family | Phase | Awarded miss | Recovered now? | Notes |
|---|---|---|---|---|
| A create_time_reentrancy | P241 nextgen | **H-01** (mint reentrancy bypassing limits) | **YES** | NextGenCore.mint anchor recovered — this was MISSED in P241 (MinterContract/Core were unread); the detector finds it directly. +1 HIGH. |
| A | P235/P236 reNFT | H-03 (ERC1155 create-time reentrancy) | **NO** | Seaport/conduit-mediated cross-contract callback — Family A blind spot. |
| B erc4626_share_accounting | P240 pooltogether | **M-02** (`_maxYieldVaultWithdraw` convertToAssets) | **YES** | Anchor recovered — base stack MISSED it in P240. +1 MEDIUM. |
| B | P240 pooltogether | M-03 / M-06 (maxDeposit-vs-mint / funds-lock) | NO | Outside the narrowed external-max-wrapper shape. |
| B | P241 dittoeth/predy | (various) | NO | Not 4626 vaults. |

## Recall delta (estimated)
- **Family A:** +1 HIGH (nextgen H-01, P241) — a real recovery of a P241 miss.
- **Family B:** +1 MEDIUM (pooltogether M-02, P240) — recovers a P240 base miss.
- Combined weighted delta ≈ +3 (H) + 1 (M) = +4 weighted across the prior benchmarks — modest but real, and both
  are in-domain to the families' anchors. Neither recovers the cross-contract (reNFT H-03) or non-4626 misses.

Honest framing: the counterfactual gain is small in absolute terms (the P241 aggregate miss was COVERAGE-dominated,
not family-dominated). These families add precise recall on their specific shapes, not a broad recall lift.
