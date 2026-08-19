# PYO-001 — PythHermesFeedProvider performs NO signature or staleness verification on price data and, with no Chainlink ref feed configured in production, has zero on-chain integrity cross-check (full keeper-trust price authority)

- **Severity (recommended):** Medium
- **Category (HackenProof VRT):** Business Logic Errors
- **Confidence:** High
- **ICE:** Impact=Mispriced positions: wrongful liquidation, position open/close at off-market price, GM/GLV deposit/withdraw at manipulated price -> fund loss to traders/LPs · Confidence=- · Exploitability=-
- **Location(s):** `/home/dummy/clones/0xMarkets_contract-main/contracts/oracle/PythHermesFeedProvider.sol:18-46`
- **Vulnerable files (bundled in `sources/`):** `PythHermesFeedProvider.sol`

## Description

PythHermesFeedProvider.getOraclePrice (PythHermesFeedProvider.sol:18-46) decodes (uint256 price, uint256 conf, int32 expo, uint256 publishTime) directly from caller-supplied `data` with abi.decode and builds min/max prices from it. There is no signature verification, no Pyth on-chain price-feed read, no publishTime sanity check inside the provider, and no comparison to any independent source. The only validations applied downstream in Oracle._validatePrices are: (a) isOracleProviderEnabled / provider==oracleProviderForToken, (b) validatedPrice.timestamp + MAX_ORACLE_PRICE_AGE >= now (publishTime freshness, 5-60 min per config/oracle.ts), and (c) the Chainlink _validateRefPrice deviation check -- but (c) only runs when ChainlinkPriceFeedUtils.getPriceFeedPrice returns hasRefPrice=true, which requires Keys.priceFeedKey(token) to be a non-zero address. In config/tokens.ts, the base and baseSepolia networks configure priceFeed ONLY in hardhat/localhost; the live Pyth-priced tokens (EUR, GBP, GOLD, XAG, JPY, WTI, TAO, USDC, WBTC, WETH) have NO Chainlink priceFeed. Therefore on production networks getPriceFeedPrice returns (false,0) and _validateRefPrice is never executed. Net result: when PythHermes is the provider for a token, the entire price (both min and max) is whatever the keeper passes in `data`, bounded only by a 5-60 minute staleness window. Unlike GMX's ChainlinkDataStreamProvider (which cryptographically verifies a signed report via the Data Streams verifier), PythHermes has no such verification -- it is a thin abi.decode of fully keeper-controlled bytes. This is a single-point-of-failure: a compromised, misconfigured, or buggy keeper can set an arbitrary price for a Hermes-priced token with no on-chain check, enabling mispriced opens/closes, unfair liquidations, and GM/GLV pool draining at the wrong price.

## Impact

If any funded token is assigned PythHermesFeedProvider as its oracleProviderForToken, the keeper (CONTROLLER) becomes the sole, unverified price authority for that token. A keeper compromise or bug yields arbitrary mispricing -> wrongful liquidations, mint/redeem of GM/GLV at manipulated prices, and direct LP/trader fund loss. No independent on-chain source can catch the bad price because no Chainlink ref feed is configured for these tokens in production.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Set an arbitrary price for a Hermes-priced token to mis-liquidate a victim position or extract value from the GM/GLV pool at an off-market price.
- **Technique:** Keeper calls an exchange handler (e.g. LiquidationHandler.executeLiquidation) with oracleParams.providers[i]=PythHermesFeedProvider and data = abi.encode(price', conf', expo, now). withOraclePrices -> Oracle.setPrices -> _validatePrices -> PythHermesFeedProvider.getOraclePrice abi.decodes the attacker-chosen price; staleness passes (publishTime=now); ref-price check is skipped (no Chainlink feed); price is stored as primaryPrice and consumed by the liquidation/mint/redeem logic.
- **Evasion:** The intended defense is the Oracle._validateRefPrice Chainlink deviation cross-check, but it is gated on hasRefPrice which is false for all Pyth-priced tokens in production config (no priceFeedKey set), so the guard never executes; Pyth's own signature verification (present in the Lazer provider) is entirely absent in the Hermes provider.
