# P205 — positive-control PoC → HARNESS_INCONCLUSIVE (documented obstacle, not fabricated)

## Target: H-01 `ILOPool.claim` (genuine awarded High — fee-share loss). Fallback: M-03 `ILOPool.buy` cap-bypass.

## Outcome: HARNESS_INCONCLUSIVE for all src/ awarded findings.
Every awarded `src/` finding (H-01 claim-fee-loss, H-03 launch-DoS, M-03 cap-bypass) lives in **ILOPool** or
**ILOManager**. Both require, under **solc 0.7.6**:
- `@uniswap/v3-core` 0.7.6 — `IUniswapV3Pool` (+ sub-interfaces), `FixedPoint128`, `FullMath`, `TickMath`;
- `@uniswap/v3-periphery` 0.7.6 — pulled transitively by `base/LiquidityManagement.sol` →
  `PeripheryPayments`, `PoolAddress`, `IUniswapV3MintCallback`, `IWETH9`, `TransferHelper`, `CallbackValidation`;
- `@openzeppelin/contracts` **3.4.x** (`>=0.6.0 <0.8.0`) — `ERC721` (with built-in enumerable for
  `tokenOfOwnerByIndex`) + its dep tree.

**Local availability check (all refuted for 0.7.6):** every vendored OZ found locally
(revert-lend / sentiment-v2 / quantamm `lib`+`node_modules`) is `^0.8.0`/`^0.8.20`; revert-lend's vendored
v3-core/v3-periphery are re-pragma'd to `^0.8.0`. No version-compatible 0.7.6 OZ-3.4 / canonical v3-core /
v3-periphery is vendored in the repo. Assembling the full 0.7.6 V3 dependency web (forge-install + remapping
resolution of the periphery callback/payments chain) is beyond bounded prototype scope and was **pre-registered as a
feasibility risk in `CORPUS_VIABILITY.md`**.

## Important EVM-semantics note (so the obstacle is scoped honestly)
The blocker is **purely the compile dependency web**, not the attack semantics:
- `ILOPool.buy` (M-03 cap-bypass) reads only stored `saleInfo` + SQRT-ratio constants + **pure** libs
  (`LiquidityAmounts`, `FullMath`) + ERC721 + ERC20 — it **never calls the live pool**. So M-03 is *logically*
  drivable once ILOPool compiles; only the dependency assembly prevents execution here.
- H-01 (`claim`) additionally needs a faithful V3 pool returning `positions()/burn()/collect()` fee growth — the
  hardest of the three.

## Consequence for the decision
Without an executed positive-control material-impact harness, P205 **cannot** reach
`L3_STANDARD_VALIDATED_SECOND_CORPUS`. The positive (HIGH-confirmation) side of L3 was already executed on decent in
**P204 (H-01 / DcntEth setRouter, 1e6-ether unbacked mint, PASS)**; P205 leaves it `HARNESS_INCONCLUSIVE` on
vultisig. → decision `L3_STANDARD_PARTIAL` (see `P205_RECOMMENDATION.md`).
