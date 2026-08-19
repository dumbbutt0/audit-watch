# AR-001 — gmBalance * gmPrice / 1e30 truncates the GM TVL leg to 0 for small GM balances or low prices, zeroing the deployed value out of share pricing

> **DISPOSITION: MERGED — duplicate.** This is the same root cause as another finding; it is kept here for traceability only and should NOT be submitted separately (see Triage reasoning for the primary).

- **Severity (recommended):** High
- **Category (HackenProof VRT):** Business Logic Errors
- **Triage status:** merged
- **Confidence:** Medium
- **ICE:** Impact=Medium · Confidence=Medium · Exploitability=Permissionless (structural mispricing; magnitude depends on market token price/scale)
- **Location(s):** `src/libraries/PoolDeployLib.sol:97-109; src/CarthaVault.sol:938-945`
- **Vulnerable files (bundled in `sources/`):** `PoolDeployLib.sol`, `CarthaVault.sol`

## Description

PoolDeployLib.gmValueInUsdc returns (gmBalance * uint256(gmPrice)) / GM_PRICE_PRECISION with GM_PRICE_PRECISION = 1e30 (PoolDeployLib.sol:20,108). gmPrice from getMarketTokenPrice is in GMX-v2's 1e30 USD fixed-point. Integer division by 1e30 truncates toward zero: the GM leg evaluates to 0 whenever gmBalance * gmPrice < 1e30. With an 18-decimal GM token and a $1 price (gmPrice ~ 1e30 per 1e18 token), the product gmBalance(1e18 units) * 1e30 only crosses 1e30 once gmBalance >= 1 wei of GM at unit price — but for any LOW per-token price, or a market token priced well below $1, or partially-filled tiny deposits, the product can fall below 1e30 and the WHOLE GM TVL leg silently becomes 0. More structurally, the same division is the mechanism behind the scale concern in TI-001: if the intended output is 6-decimal USDC, the divisor should be 1e30 * 1e12 (or the result multiplied to 6 decimals), and the current /1e30 yields an 18-decimal-scaled number — so 'truncate to 0' and 'over-count by 1e12' are two faces of the same un-normalized division. A zeroed GM leg means _totalValueLocked = idle USDC only while real GM value exists -> redeemers underpaid (their share of a now-smaller TVL) and the next depositor over-minted, exactly the EA-001/DT-001 dilution direction but caused by precision truncation rather than the async window.

## Impact

GM TVL leg can truncate to 0 (low price / tiny balance), dropping all deployed value from _totalValueLocked and mispricing every deposit/redeem (under-pay redeemers, over-mint depositors). With normal GM balances at ~$1 the truncation floor is sub-wei so the practical trigger is a low-priced market token or a near-zero GM balance; the un-normalized 1e30 divisor (vs the 1e6 USDC target) is the root issue.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Zero or mis-scale the GM TVL leg via integer-division truncation so share pricing ignores deployed value.
- **Technique:** When gmBalance * gmPrice < 1e30 (low price or tiny balance), gmValueInUsdc returns 0; _totalValueLocked omits the deployed GM; _convertToShares/_convertToAssets misprice.
- **Evasion:** Division by 1e30 with no rounding-up and no 18->6 normalization; result fed directly into TVL alongside 6-decimal USDC.

## Reachability / follow-up

merged into CARTHA-SEAM-001.

## Triage reasoning

Same root cause as CARTHA-SEAM-001 (the gmBalance*gmPrice/1e30 GM-TVL leg scaling). AR-001 is the small-balance truncation-to-zero face; CARTHA-SEAM-001 is the 1e12 over-count face. Merged into CARTHA-SEAM-001.
