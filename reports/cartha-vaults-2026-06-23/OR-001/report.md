# OR-001 — GM price for valuing held GM uses the DEPOSIT PnL cap (MAX_PNL_FACTOR_FOR_DEPOSITS) and MIN price for ALL operations incl. redemption — wrong/asymmetric PnL basis biases share price

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** Business Logic Errors
- **Triage status:** downgraded
- **Confidence:** High
- **ICE:** Impact=Medium · Confidence=High · Exploitability=Conditional (no single-tx manipulation; bias is structural and depends on live PnL-factor config)
- **Location(s):** `src/libraries/PoolDeployLib.sol:111-127,97-109; src/CarthaVault.sol:299-337,395-416,576-598,847-873,928-945`
- **Vulnerable files (bundled in `sources/`):** `PoolDeployLib.sol`, `CarthaVault.sol`

## Description

_getGmPrice (PoolDeployLib.sol:111-127) calls reader.getMarketTokenPrice(dataStore, mkt, indexPrice, longPrice, shortPrice, MAX_PNL_FACTOR_FOR_DEPOSITS, false). Two design choices, analyzed against GMX-v2 semantics:

(1) maximize=false => the MIN market-token price. For valuing GM the vault HOLDS, using the MIN price is conservative (undervalues the asset), which is the SAFE direction for the share rate on the DEPOSIT side (a depositor receives shares against a conservatively-low TVL, so they are never over-minted DUE TO PRICING). HOWEVER the same MIN price is also used on the REDEMPTION side (_convertToAssets in release/forceExit/processQueuedWithdrawals/withdrawToParent all flow through _totalValueLocked -> _gmValueInUsdc). On the redemption side a conservative-LOW valuation UNDERPAYS the exiting user and leaves the surplus to remaining holders. So the single MIN price is not symmetric to the action: it is conservative-for-vault on deposit but adverse-to-user on exit. A correct ERC4626-style design values held GM at a single fair mid for both, or values held inventory at the price the vault would actually realize on withdrawal.

(2) pnlFactorType = MAX_PNL_FACTOR_FOR_DEPOSITS. In GMX-v2 the market-token price depends on which PnL factor cap is applied (deposits vs withdrawals can be capped differently to discourage gaming open-interest PnL). Cartha applies the DEPOSIT cap to ALL valuations, including when pricing GM that is being effectively redeemed (recall) or when the parent reads child TVL for parent withdrawals. Using the deposit-side PnL cap to value GM that backs WITHDRAWALS is the wrong basis: if MAX_PNL_FACTOR_FOR_WITHDRAWALS < MAX_PNL_FACTOR_FOR_DEPOSITS (the usual GMX config to protect LPs on exit), held GM is valued HIGHER than it could actually be withdrawn for, so exiting users (and the parent on a child withdrawal) are credited a TVL that the pool cannot fully honor on a real recall — over-paying early exiters at the expense of those who remain / of the protocol's idle USDC buffer. The two effects (MIN price vs MAX-deposit-PnL-cap) push in opposite directions and do not cancel cleanly; the net bias depends on the live 0xM PnL-factor config, which is exactly the kind of consistency error that should be Medium and human-verified.

## Impact

Systematic share-price bias: exiting users are mispriced relative to the true realizable GM value. Direction (over- vs under-pay) depends on the 0xM market's deposit-vs-withdrawal PnL-factor configuration; either way it is a consistent transfer between exiting and remaining holders and a divergence from the value the vault can actually realize on recall. Not flash-exploitable (price is keeper-signed; see OR-002), so Medium.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Mis-value held GM so that one cohort of holders (exiters vs stayers) is systematically over- or under-paid versus the realizable GM value.
- **Technique:** Normal deposit then exit; the MIN-price + deposit-PnL-cap valuation differs from the withdrawal-PnL-cap value the pool would actually pay, so _convertToAssets pays a price the recall cannot honor (or underpays).
- **Evasion:** The developer values held GM with the DEPOSIT pricing tuple (maximize=false, MAX_PNL_FACTOR_FOR_DEPOSITS), apparently treating all valuation as a deposit; GMX-v2 distinguishes deposit and withdrawal PnL caps precisely to prevent this.

## Reachability / follow-up

reachable: any valuation read while PnL cap binds. no_privileged_keys: n/a. state_before_after: held GM valued slightly low. why_guards_fail: deposit-factor used for a held/withdrawal basis. scope_match: oracle valuation nuance.

## Triage reasoning

gmValueInUsdc values HELD GM using MAX_PNL_FACTOR_FOR_DEPOSITS + maximize=false (MIN price). The seam diff confirmed deposits-vs-withdrawals PnL factors differ (default 90% vs 70%), but marking held GM at the DEPOSITS factor is the conservative/lower direction (it under-states, never over-states GM value) and only bites when the cap binds. Not a drain vector; a mild stayer-vs-exiter mispricing. Downgraded to Low (safety-net oracle code; reasoning given, not a silent clear).
