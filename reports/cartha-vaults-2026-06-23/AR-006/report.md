# AR-006 — getUtilization can exceed 10000 bps (>100%) when GM loss makes TVL < totalLockedAmount; value is meaningful and non-reverting but unbounded

- **Severity (recommended):** Info
- **Category (HackenProof VRT):** Business Logic Errors
- **Triage status:** downgraded
- **Confidence:** High
- **ICE:** Impact=Low · Confidence=High · Exploitability=Permissionless (market-driven) but no on-chain consumer
- **Location(s):** `src/CarthaVault.sol:1153-1158; src/CarthaParentVault.sol:384-390,98-99,318-321`
- **Vulnerable files (bundled in `sources/`):** `CarthaVault.sol`, `CarthaParentVault.sol`

## Description

getUtilization() = ($.totalLockedAmount * 10000) / tvl where tvl = _totalValueLocked() (CarthaVault.sol:1153-1158), returning 0 if tvl == 0. totalLockedAmount is the sum of deposited PRINCIPAL (incremented by `amount` on each deposit, decremented by released principal) — it does NOT track PnL. tvl reflects current value (idle USDC + GM value). If the GM pool LOSES value (GM price drops, or the AR-001/TI-001 truncation zeros the GM leg, or recall slippage), tvl can fall BELOW totalLockedAmount, so the ratio exceeds 10000 (>100%). The computation does not revert (tvl>0 guarded) and the >100% reading is arithmetically meaningful (it signals the pool is underwater: locked principal exceeds realizable value). Consumers: CarthaParentVault.getPoolUtilization just forwards it; rebalanceConfig.utilizationThreshold = 8000 is stored but NOT read by any executed rebalance path (_rebalanceToWeights ignores utilization, rebalancing purely by weight). So a >100% utilization does not corrupt rebalancing logic. The risk is informational/monitoring: an off-chain keeper or UI reading utilization may not anticipate values >10000 and could mis-handle them. No on-chain misbehavior. Also note getUtilization mixes scales if AR-001/TI-001 are real (totalLockedAmount is 6-decimal USDC principal; tvl includes the possibly-18-decimal-scaled GM leg) — another reason the ratio can read far from 100%.

## Impact

getUtilization returns >10000 bps when the pool is underwater (TVL < locked principal). Non-reverting and arithmetically correct, but an off-chain consumer assuming a 0-10000 range may mis-handle it. No on-chain logic depends on the value (utilizationThreshold is unused by executed code).

## Attack path (Intent / Technique / Evasion)

- **Intent:** Produce an out-of-expected-range utilization that an off-chain consumer mishandles.
- **Technique:** GM loss / GM-leg truncation drives tvl < totalLockedAmount -> getUtilization > 10000.
- **Evasion:** Function guards only tvl==0; no upper clamp; utilizationThreshold (8000) stored but never enforced on-chain.

## Reachability / follow-up

reachable: view only. no_privileged_keys: n/a. state_before_after: returns >10000. why_guards_fail: no cap. scope_match: informational.

## Triage reasoning

getUtilization can exceed 10000 bps (>100%) when GM loss makes TVL < totalLockedAmount. Non-reverting view; utilizationThreshold is stored but unused, so no on-chain consumer. Informational.
