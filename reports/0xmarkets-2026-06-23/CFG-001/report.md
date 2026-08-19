# CFG-001 — ConfigValidatorUtils drops canonical GMX range bounds (LIQUIDATION_FEE_FACTOR, RESERVE_FACTOR, OPEN_INTEREST_RESERVE_FACTOR) while keys stay allowlisted — unbounded liquidation fee / reserve factor

- **Severity (recommended):** Medium
- **Category (HackenProof VRT):** Violation of Secure Design Principles
- **Confidence:** High
- **ICE:** Impact=Liquidations seize outsized collateral; open interest can exceed pool backing -> pool insolvency · Confidence=- · Exploitability=-
- **Location(s):** `contracts/config/ConfigValidatorUtils.sol:129-134 (LIQUIDATION_FEE_FACTOR check commented out); RESERVE_FACTOR / OPEN_INTEREST_RESERVE_FACTOR absent entirely; allowlisted at contracts/config/ConfigAllowedKeys.sol:146,162,163`
- **Vulnerable files (bundled in `sources/`):** `ConfigValidatorUtils.sol`, `ConfigAllowedKeys.sol`

## Description

ConfigValidatorUtils.validateRange (the 0xMarkets replacement for canonical ConfigUtils.validateRange) omits three range checks that canonical GMX enforces, even though the corresponding base keys are still in ConfigAllowedKeys and therefore writable via Config.setUint by CONFIG_KEEPER:

1. LIQUIDATION_FEE_FACTOR: canonical GMX bounds it to <= 1% (gmx-synthetics ConfigUtils.sol:410-415: `value > Precision.FLOAT_PRECISION / 100`). In 0xMarkets the check is COMMENTED OUT (ConfigValidatorUtils.sol:129-134) but LIQUIDATION_FEE_FACTOR remains allowlisted (ConfigAllowedKeys.sol:146). The value is consumed in PositionPricingUtils.getLiquidationFees:582 as `liquidationFeeUsd = Precision.applyFactor(sizeInUsd, liquidationFeeFactor)`, i.e. it directly scales the fee seized from a position's collateral on liquidation. With no upper bound a keeper can set this to >> 1% (e.g. 100%+ of size), so a liquidation seizes far more collateral than the canonical cap allows.
2. RESERVE_FACTOR and OPEN_INTEREST_RESERVE_FACTOR: canonical bounds both to <= 10x (1000%) (gmx-synthetics ConfigUtils.sol:448-456). 0xMarkets has NO check for either in validateRange, yet both are allowlisted (ConfigAllowedKeys.sol:162-163). The value is consumed in MarketUtils.validateReserve:1485-1496 as `maxReservedUsd = applyFactor(poolUsd, reserveFactor)`; an arbitrarily large reserve factor lets reserved (open-interest-backing) USD exceed the pool, undermining the solvency guard.

The range checks in GMX are a deliberate defense-in-depth guardrail that caps the blast radius of a mis-configured or compromised config keeper. Removing them while keeping the keys writable is a security regression vs the forked baseline. Note the keys are only reachable by CONFIG_KEEPER (a trusted role) — LIMITED_CONFIG_KEEPER is locked out (see CFG-004) — so this is a privileged/centralization-bounded issue, not a permissionless one.

## Impact

A compromised or fat-fingered CONFIG_KEEPER can set the per-market liquidation fee factor and reserve factors to values far above canonical GMX's caps. Consequences: liquidations can seize an outsized share (up to and beyond 100%) of a victim's collateral; reserve factors above 10x can let open interest exceed pool backing and break the solvency invariant. Blast radius is the entire blast radius of the keeper key, which canonical GMX deliberately bounded and 0xMarkets unbounded.

## Attack path (Intent / Technique / Evasion)

- **Intent:** As a compromised/malicious CONFIG_KEEPER, extract excess collateral from traders via liquidation fees (or break pool solvency) beyond the bounds canonical GMX enforces.
- **Technique:** Call Config.setUint(LIQUIDATION_FEE_FACTOR, abi.encode(market), value) with value >> 1e28 (1%). _validateKey passes (CONFIG_KEEPER + allowlisted). ConfigValidatorUtils.validateRange has no LIQUIDATION_FEE_FACTOR branch (commented out at 129-134) so any value is accepted and written to liquidationFeeFactorKey(market). On the next liquidation, PositionPricingUtils.getLiquidationFees:582 scales the fee by the unbounded factor. Same shape for RESERVE_FACTOR / OPEN_INTEREST_RESERVE_FACTOR via MarketUtils.validateReserve.
- **Evasion:** Canonical GMX bounds all three (ConfigUtils.sol:410-415 LIQUIDATION_FEE_FACTOR <=1%, 448-456 reserve factors <=10x). 0xMarkets lifted validateRange into ConfigValidatorUtils 'with no behavior change' per the file header, but the LIQUIDATION_FEE_FACTOR branch was commented out and the reserve-factor branch was not ported at all — the guardrail is silently missing while the keys stay writable.
