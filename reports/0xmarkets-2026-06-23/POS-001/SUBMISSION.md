# POS-001 — Leverage-ladder concentration cap is enforced per-position, not per-account (trivially bypassed by splitting)

| | |
|---|---|
| **Severity** | **Medium** (defeats the protocol's headline concentration risk-control; raises insolvency risk) |
| **Category (HackenProof VRT)** | Business Logic Errors |
| **Target** | 0xMarkets (`0xMarkets_contract-main`, commit `e94daee6558f90e479c2c967dedae1d7cd06fb0c`) |
| **Contracts** | `contracts/position/LeverageLadderUtils.sol`, `contracts/position/PositionUtils.sol` |
| **Attacker** | Permissionless — any trader; cost is gas only |
| **PoC** | `poc/PoC_LeverageLadderBypass.ts` (Hardhat integration, on the standard `deployFixture`) |

## Summary

0xMarkets adds a custom "leverage ladder" (not present in upstream GMX) intended to force larger positions
into lower maximum leverage to discourage concentration. The cap is resolved from a **single position's**
post-trade notional and applied as one floor in `PositionUtils.willPositionCollateralBeSufficient`. Nothing
in the increase flow aggregates notional across an account's positions, so a trader who would be forced into
a low-leverage tier for one large position simply opens several smaller positions — across sub-account EOAs
(or distinct collateral/direction keys) — each individually small enough to qualify for the top, high-
leverage tier. The concentration control is defeated at gas cost only.

## Vulnerability detail

`LeverageLadderUtils.getMaxLeverageForNotional` keys the cap off the notional it is handed:

```solidity
function getMaxLeverageForNotional(DataStore dataStore, address market, uint256 notionalUsd)
    internal view returns (uint256)
{
    uint256 count = dataStore.getUint(Keys.leverageLadderTierCountKey(market));
    if (count == 0) return type(uint256).max;
    for (uint256 i = 0; i < count; i++) {
        uint256 maxNotional = dataStore.getUint(Keys.leverageLadderMaxNotionalKey(market, i));
        if (notionalUsd <= maxNotional) return dataStore.getUint(Keys.leverageLadderMaxLeverageKey(market, i));
    }
    ...
}
```

`PositionUtils.willPositionCollateralBeSufficient` passes the **single position's** size (`values.positionSizeInUsd`):

```solidity
uint256 ladderMaxLeverage = LeverageLadderUtils.getMaxLeverageForNotional(
    dataStore,
    market.marketToken,
    values.positionSizeInUsd            // <-- per-position notional, never an account aggregate
);
int256 minCollateralUsdForLadderTier = ladderMaxLeverage == type(uint256).max
    ? int256(0)
    : Precision.toFactor(values.positionSizeInUsd, ladderMaxLeverage).toInt256();
```

The only account-agnostic concentration term is the open-interest floor
(`getMinCollateralFactorForOpenInterest`), but it is keyed off **market-wide** OI (not the account) and is
inert when `minCollateralFactorForOpenInterestMultiplier == 0`, which is the default in the test config and
common in practice. Positions are keyed `keccak256(account, market, collateralToken, isLong)`, so a single
trader gets fresh, separately-capped positions from each sub-account EOA. There is no per-account
aggregate-notional or position-count cap anywhere in `IncreaseOrderUtils` / `PositionUtils`.

## Impact

The ladder's purpose — making whales de-lever as their footprint grows — is nullified. A trader can hold an
arbitrarily large aggregate position at the **top-tier** leverage by fragmenting it across wallets, restoring
exactly the concentrated, thinly-collateralized exposure the ladder was added to prevent. Under an adverse
move these fragmented high-leverage positions raise the protocol's bad-debt / insolvency risk borne by LPs.
No direct theft, hence Medium, but it neutralizes a core custom risk-control and is permissionless.

## Step-by-step (from the PoC)

Ladder configured on `ethUsdMarket`: `[ ≤$50k → 50x ] [ ≤$200k → 25x ] [ >$200k → 10x ]`; market
`max_leverage` 100x; OI multiplier 0 (so the ladder is the only binding concentration control).

1. A single **$300,000** long at 12.5x (collateral $24k) is **blocked**: $300k falls in the `>$200k → 10x`
   tier, which requires ≥ $30k collateral; the order is cancelled `InsufficientCollateralUsd`.
2. The same $300k of notional at the same 12.5x, **split into 6 × $50,000** positions from 6 sub-account
   EOAs (collateral $4k each), **all open**: each $50k is in the `≤$50k → 50x` tier (needs only ≥ $1k).
3. Result: $300,000 aggregate notional at 12.5x with the same $24k total collateral — exactly the position
   the ladder rejected as a single order — now live across wallets.
4. Control: with the ladder removed, the single $300k @ 12.5x opens fine, confirming the ladder (not some
   other floor) is the control being bypassed.

## Recommended fix

Aggregate notional per account when applying the ladder floor: sum the account's existing open-interest in
the market (and ideally across correlated markets) and evaluate `getMaxLeverageForNotional` against the
post-trade **account** notional, not the single position's. Alternatively enforce a per-account max-notional
cap, or set `minCollateralFactorForOpenInterestMultiplier > 0` and base it on per-account OI. Note that
sub-account EOAs make pure per-position caps fundamentally unenforceable.

## Re-verification note

Re-verified end-to-end on the project's own `deployFixture` (full GMX stack), driving real `MarketIncrease`
orders through `handleOrder` with keeper execution. See `poc/run_output.txt` for the passing run.
