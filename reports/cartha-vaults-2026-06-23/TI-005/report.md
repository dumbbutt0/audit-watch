# TI-005 — poolToken (valuation) and marketToken (router send/recall) are two independent ADMIN-set addresses — if they diverge, TVL is priced on a different token than the vault actually mints/holds

- **Severity (recommended):** Medium
- **Category (HackenProof VRT):** Business Logic Errors
- **Triage status:** submit
- **Confidence:** High
- **ICE:** Impact=Medium · Confidence=High · Exploitability=Privileged (ADMIN) — but triggerable by ordinary mis-config, not only malice
- **Location(s):** `src/CarthaVault.sol:71-72,713-728,943-945; src/libraries/PoolDeployLib.sol:97-127`
- **Vulnerable files (bundled in `sources/`):** `CarthaVault.sol`, `PoolDeployLib.sol`

## Description

The GM token is referenced through TWO separate ADMIN-settable storage fields with NO equality constraint: $.poolToken (CarthaVault.sol:71, set by setPoolToken:713-718) is used as the balanceOf source for VALUATION (gmValueInUsdc reads IERC20(poolToken).balanceOf(this), PoolDeployLib.sol:102), while $.marketToken (CarthaVault.sol:72, set by setMarketToken:723-728) is the market address sent to the router on deploy and recall (PoolDeployLib.deploy/recall use `market`=marketToken; createDeposit/createWithdrawal mint/burn the GM token for that market, received by the vault). In GMX-v2 the market token IS the GM (LP) token, so poolToken and marketToken MUST be the same address. Nothing in the code enforces poolToken == marketToken: they are set by two independent setters, each only zero-checked. If an ADMIN sets them to different addresses (mis-config or malice), the vault MINTS/HOLDS marketToken GM but PRICES poolToken's balance (likely 0 -> gmValueInUsdc returns 0 -> entire deployed leg vanishes from TVL -> share price collapses for redeemers and over-mints for the next depositor), or prices a DIFFERENT token's balance the vault happens to hold. Also note _gmValueInUsdc passes BOTH $.marketToken (to the reader as the market key, PoolDeployLib.gmValueInUsdc(...,$.marketToken,...)) AND $.poolToken (as the balanceOf token) — so the price comes from marketToken's market but the quantity comes from poolToken's balance; if they differ the price/quantity are mismatched. This is the same trust seam flagged by DT-004 (ADMIN pricing control) but is a distinct, concrete two-field-consistency bug: even a non-malicious ADMIN who sets only setMarketToken (and forgets setPoolToken, or vice-versa) zeroes or mis-scales the GM TVL leg.

## Impact

Divergent poolToken/marketToken makes the GM TVL leg price the wrong token's balance: most likely poolToken.balanceOf == 0 so the entire deployed GM value drops out of _totalValueLocked, crashing share price for redeemers (under-paid) and over-minting the next depositor; or it prices a different held token. Triggered by ordinary ADMIN mis-configuration (two independent setters), not just malice. ADMIN-gated so Medium.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Corrupt GM TVL valuation by pricing a different token than the vault actually mints/holds for its pool position.
- **Technique:** setMarketToken(realGM) but setPoolToken(otherAddr) (or only one of them) -> gmValueInUsdc reads poolToken.balanceOf (0 or wrong token) while createDeposit mints realGM -> deployed value mis-priced/zeroed.
- **Evasion:** Two independent ADMIN setters, each only zero-address-checked; no require(poolToken == marketToken); valuation token (poolToken) decoupled from the minted/sent token (marketToken).

## Reachability / follow-up

reachable: setMarketToken without matching setPoolToken. no_privileged_keys: NO (ADMIN config). state_before_after: GM leg reads wrong token -> TVL wrong. why_guards_fail: no equality/derivation constraint. scope_match: accounting/config.

## Triage reasoning

poolToken (used for balanceOf valuation) and marketToken (sent to the router and used as the reader market key) are two independent ADMIN setters with no equality constraint. If they diverge (ordinary misconfig: set one, forget the other), valuation prices the wrong token (typically 0), zeroing deployed value out of TVL and corrupting share math. Distinct from DT-004 (this is a missing-invariant, not just trust). Fix: derive poolToken from marketToken or enforce equality.
