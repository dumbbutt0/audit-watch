# Minimal reproduction hypothesis

Candidate: `phi-2024-08 :: CuratorRewardsDistributor.distribute`.

## Source-backed hypothesis attempt

Read CuratorRewardsDistributor.distribute — a genuinely PERMISSIONLESS reward distributor (the corrected ranking surfaced this instead of P114's privileged dead-ends). Two source-visible, nameable hypotheses: (1) UNBOUNDED-LOOP DoS — it loops twice over `credContract.getCuratorAddresses(credId,0,0)` (all curators) and `phiRewardsContract.depositBatch(...)` over the whole array; if an attacker can cheaply add many sybil curators (Cred.buyShareCred), the loops/batch exceed gas and rewards become undistributable — matching phi's awarded H-03 reward-distribution DoS. (2) ROYALTY-TO-CALLER — `_msgSender().safeTransferETH(royaltyfee + dust)` sends the withdrawRoyalty to whoever calls distribute (the authors even slither-disable `arbitrary-send-eth`); if the royalty is meant for the protocol, a permissionless keeper harvests it. NEITHER is closable from source alone: the DoS needs the cross-contract curator-growth cost + a runtime gas measurement; the royalty needs intent/spec (keeper-fee vs protocol-leak). I did not fabricate a trace. Truthful terminal: NEEDS_CONTEXT with a strong, specific hypothesis (next step: confirm curator-array growth cost in Cred + measure depositBatch gas; confirm intended royalty recipient).

## What runtime evidence would be required

A falsifiable runtime check could not be specified from source alone for this candidate (see rationale). Resolving it would require execution-backed evidence — e.g. a fork/local deployment plus a differential or invariant test across the cross-contract boundary named above — not further source reasoning. Absent that, the truthful terminal is `NEEDS_CONTEXT`; no exploit is claimed and no finding is promoted.
