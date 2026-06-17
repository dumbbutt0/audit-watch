# bakerfi — Phase 3: Five-operation routine (PRE-REVEAL, FROZEN)

Same five ops as P254. Labels + chain status + **plausible mechanisms considered (pre-reveal)** per locus.

## L4 — `StrategyLeverage._getPosition` staleness OR-logic → **PARTIAL_CHAIN** · plausible mechanisms considered: **2**
Enumerated: (a) OR-should-be-AND ⇒ one stale feed tolerated ⇒ stale price used in valuation ⇒ deposit/withdraw/
harvest misprice the position; (b) moot if `getSafeLatestPrice(priceMaxAge)` itself reverts on stale (then the
manual gate is dead code and there is no bug).
- **STS — PASS.** De Morgan: `revert iff priceMaxAge>0 AND ethStale AND collStale`. Pre-state: collateral feed stale, eth feed fresh, priceMaxAge>0 ⇒ no revert ⇒ `totalCollateralInEth` computed from a **stale** collateral price.
- **AAS — UNCLEAR.** Attacker can't force a feed stale, but can *act during* a window where one feed is stale (feeds update independently) and call withdraw/deposit to mint/burn shares at a mispriced valuation.
- **TSE — PASS.** Terminal: shares minted/burned against a stale collateral valuation ⇒ value transfer between the actor and other vault holders.
- **IDC — CANDIDATE_STRENGTHENED.** Invariant: valuation uses only fresh prices. Delta: a stale collateral price (drifted from market) ⇒ totalAssets wrong ⇒ deposit gets too many / withdraw too few shares.
- **CCIT — NO_EFFECT.**
- Selected mechanism: (a) OR-tolerates-one-stale-feed. **Key dependency flagged pre-reveal:** if `getSafeLatestPrice` reverts on stale, mechanism (a) is void → would be SAME_AREA. **Completing op: STS/IDC.**

## L5 — `StrategyLeverage.harvest` P&L gap → **PARTIAL_CHAIN** · plausible mechanisms considered: **2**
Enumerated: (a) debt-adjustment harvest (deltaDebt≠0) updates `_deployedAmount` but reports `balanceChange=0` ⇒
no performance fee minted on real gains realized via rebalance; (b) harmless because adjustment harvests net to
no real P&L.
- **STS — PASS.** ltv>max branch sets deltaDebt≠0; then both P&L branches are gated `&& deltaDebt == 0` ⇒ skipped; `_deployedAmount = newDeployedAmount` still applied.
- **AAS — UNCLEAR.** `harvest` is `onlyOwner` (not permissionless) ⇒ no external attacker; limits severity to owner/fee-receiver accounting.
- **TSE — PASS.** Terminal: protocol fee-receiver under-collects fees on adjustment harvests; vault NAV moves with no P&L event.
- **IDC — CANDIDATE_STRENGTHENED.** Delta: perf-fee shares un-minted on deltaDebt≠0 harvests; loser = fee receiver/protocol; bounded, owner-gated.
- **CCIT — NO_EFFECT.**
- Selected mechanism: (a) no-fee/no-P&L on adjustment harvest. **Completing op: IDC; AAS bounds severity (owner-gated).**

## L6 — `StrategyLeverage._undeploy` stale `_pendingAmount` → **NO_CHAIN (UNCLEAR)** · plausible mechanisms considered: **2**
Enumerated: (a) `_pendingAmount` read stale from a prior tx ⇒ wrong `_deployedAmount`/undeploy; (b) harmless
because every `_undeploy` sets `_pendingAmount` via its own flashloan callback before reading it.
- **STS — UNCLEAR.** Within a single `_undeploy`, the flashloan callback `_repayAndWithdraw` sets `_pendingAmount` before L517 reads it ⇒ no stale read in the normal path.
- **AAS — NO_EFFECT.** `undeploy` is `onlyOwner`.
- **TSE — NO_EFFECT.** No stranded/extra funds traced.
- **IDC — NO_EFFECT.**
- **CCIT — UNCLEAR.** No cross-principal mismatch found.
- Selected outcome: cannot complete a chain blind; the not-cleared comment is a code-smell but the single-tx path refreshes it. **NO_CHAIN (honest).**

## Pre-reveal summary (frozen)
| locus | chain status | completing op | plausible mechs | blind sev |
|---|---|---|---|---|
| L4 _getPosition staleness | PARTIAL_CHAIN | STS/IDC | 2 | Med/High |
| L5 harvest P&L gap | PARTIAL_CHAIN | IDC | 2 | Low/Med |
| L6 _undeploy _pendingAmount | NO_CHAIN | — | 2 | — |

0 COMPLETED, 2 PARTIAL, 1 NO_CHAIN. **FREEZE** before key opened; hashes in bakerfi_REVEAL_AND_SCORE.md.
