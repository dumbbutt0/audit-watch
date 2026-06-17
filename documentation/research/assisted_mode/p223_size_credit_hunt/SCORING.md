# P223 — Scoring vs sealed answer key (Step 9, post-freeze)

Blindness proven: sealed-key sha256 at scoring == precheck/freeze witness (`8eacd80…a9c23`), unchanged and
unread until this step. Focused key = **4 High + 9 Medium** rows (lending/liquidation/collateral-debt/
health-factor/oracle/multicall-invariant/fee-accounting; gas/QA excluded).

## Candidate → key mapping
| candidate | my sev | key row | key sev | result | severity |
|-----------|--------|---------|---------|--------|----------|
| SC-04 compensate fragmentation-fee waiver | Medium | **M-05/M-13** (Compensate fragmentation fee skipped) | Med | **HIT** | **MATCH** |
| SC-02 min-credit check on cash | Low | **M-02** (min-credit threshold vs cash not credit) | Med | **HIT** | UNDER |
| SC-06 getCreditAmountIn no-trade gap | Low | H-01 (getCreditAmountIn wrong swap-fee formula) | High | **PARTIAL** (right fn, wrong mechanism) | UNDER |
| SC-11 LiquidateWithReplacement transient REPAID event | Low | H-02 (Repay+LiqWithReplacement missing borrower validation) | High | **PARTIAL** (right fns, wrong mechanism) | UNDER |
| SC-08 borrowATokenCap multicall skip/overshoot | Low | M-01 (multicall validates cap via balanceOf not totalSupply) | Med | **PARTIAL** (right area, adjacent mechanism) | UNDER |
| SC-10 SellCreditMarket cash-vs-credit guard | Low | M-02 (adjacent — same validate units issue) | Med | ADJACENT | UNDER |
| SC-01 executeDeposit address(this).balance ETH sweep | High (L3 PASS) | — (not in focused key) | — | **REAL EXTRA, out-of-focused-scope** (not FP — L3-proven) | n/a |
| SC-03 negative-APR offer DoS | Medium | — | — | MISS (not in key) | — |
| SC-05 scaled-token dust | Low | — | — | MISS | — |
| SC-07 selfLiquidate CR band | Low | — | — | MISS | — |
| SC-09 withdraw silent clamp | Low | — | — | MISS | — |
| SC-12 claim sequential rounding | Low | — | — | MISS | — |

## Key rows not found (MISS)
H-03 (Liquidate collateralRemainderCap CR math), H-04 (liquidator reward on debt- not collateral-token),
M-03 (wrong Aave liquidity source bricks ops), M-04 (oracle sequencer-uptime validation), M-06 (forSale flag
not checked), M-09 (underwater borrower can't compensate), M-11 (swap fee not charged on replacement),
M-12 (buyCreditMarket over-estimates pool check). The liquidation-math Highs (H-03/H-04) were the
liquidation cluster's blind spot; oracle (M-04) was out of my pruned scope (no oracle specialist run).

## Tally (vs 13 focused key rows)
- **Full HIT: 2** (M-02, M-05/M-13) — one at correct severity (M-05/M-13), one under-rated (M-02).
- **PARTIAL: 3** (H-01, H-02, M-01 — right function/area, wrong specific mechanism).
- **MISS: 8** (H-03, H-04, M-03, M-04, M-06, M-09, M-11, M-12).
- **Real extra outside focused key: 1** (SC-01 — executed L3-PASS PoC; custody/ETH, outside the focused
  lending/liquidation scope; **not** a false positive — source-verified all payable + msg.value-ignoring + L3
  theft proof).
- **Fabricated false positives: 0.** **False-Highs (fabricated): 0** (SC-01, the only High, is L3-proven real).
- **Severity: UNDER ×4 (SC-02/06/08/11), MATCH ×1 (SC-04), OVER ×0.**

## Reading
- **Matches the key's own expectation** ("expose a new family ... not a recall win; liquidation fns → PARTIAL;
  Compensate → PARTIAL; everything else → MISS"). Blind deep_trace clusters actually beat that: M-02 and
  M-05/M-13 came through as full HITs and H-01/H-02/M-01 as PARTIALs — more than the frozen production detector
  families would have routed.
- **The over-rating guard held** (0 fabricated false-Highs; the only High is L3-executed). **The under-rating
  pattern recurs** (P212/P215): SC-02 (→M-02) and the PARTIALs were calibrated Low where the key is Med/High —
  driven by conservative triage + un-harnessed mechanisms, not by the L3 gate.
- **Clean reportable produced:** SC-04 is a permissionless, source-confirmed Medium HIT at correct severity
  (M-05/M-13); SC-01 is an executed-L3-PoC permissionless custody finding (real, though outside this focused
  key) — proving the Solidity+Foundry pipeline can route a bug to an executed clean reportable, the phase's goal.
- **Recall gaps to close (human follow-on):** liquidation-math Highs (H-03/H-04) need a dedicated liquidation
  accounting/CR lens; oracle (M-04) needs the oracle specialist (pruned here); several Mediums (M-03/M-06/M-09/
  M-11/M-12) are distinct mechanisms a broader specialist pass (/ite-audit) would likely surface vs the bounded
  5-cluster deep_trace.
